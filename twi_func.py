import yaml
from requests_oauthlib import OAuth1Session, OAuth2Session
import json
import logging
import requests
import secrets
import base64
import hashlib
import oauthlib

def get_credentials(file_name='tokens.yaml'):
    with open(file_name, 'r') as file:
        credentials = yaml.safe_load(file)
    return credentials


def _oauth1_authentication_helper(credentials):
    # Get request token
    consumer_key, consumer_secret = credentials['consumer_key'], credentials['consumer_secret']
    
    request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

    try:
        fetch_response = oauth.fetch_request_token(request_token_url)
    except ValueError:
        print(
            "There may have been an issue with the consumer_key or consumer_secret you entered."
        )

    resource_owner_key = fetch_response.get("oauth_token")
    resource_owner_secret = fetch_response.get("oauth_token_secret")
    print("Got OAuth token: %s" % resource_owner_key)

    # Get authorization
    base_authorization_url = "https://api.twitter.com/oauth/authorize"
    authorization_url = oauth.authorization_url(base_authorization_url)
    print("Please go here and authorize: %s" % authorization_url)
    verifier = input("Paste the PIN here: ")
    
    # Get the access token
    access_token_url = "https://api.twitter.com/oauth/access_token"
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    oauth_tokens = oauth.fetch_access_token(access_token_url)

    access_token = oauth_tokens["oauth_token"]
    access_token_secret = oauth_tokens["oauth_token_secret"]
    
    credentials['access_token'] = access_token
    credentials['access_token_secret'] = access_token_secret
    
    return credentials


def oauth1_authenticate(file_name='tokens.yaml'):
    credentials = get_credentials(file_name=file_name)
    credentials = _oauth1_authentication_helper(credentials=credentials)
    
    # write the access token and secret
    with open(file_name, 'w') as file:
        yaml.dump(credentials, file)
    
    print('Credentials Updated using OAuth 1.0!')
    return credentials


def _oauth2_authentication_helper(credentials):
    client_id, client_secret = credentials['client_id'], credentials['client_secret']
    callback_url = credentials['callback_url']
    token_url = 'https://api.twitter.com/2/oauth2/token'
    authorization_base_url = 'https://twitter.com/i/oauth2/authorize'
    
    # Generate Code Verifier & Code Challenge for PKCE
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=')
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier).digest()).rstrip(b'=')
    code_challenge_method = 'S256'
    
    scopes = ['tweet.read','tweet.write','follows.read','follows.write','block.write','offline.access']

    oauth = OAuth2Session(client_id, redirect_uri=callback_url, scope=scopes)
    authorization_url, state = oauth.authorization_url(authorization_base_url, 
                                                        code_challenge=code_challenge.decode(),
                                                        code_challenge_method=code_challenge_method)
    print('Please go here and authorize:', authorization_url)

    redirect_response = input('Paste the full redirect URL here: ')
    
    # Encode Client ID and Client Secret
    client_credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(client_credentials.encode('utf-8')).decode('utf-8')
    
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    body = {
        'grant_type': 'authorization_code',
        'code': redirect_response.split('code=')[1].split('&')[0],  # Extract the code parameter from the redirect response
        'redirect_uri': callback_url,
        'code_verifier': code_verifier.decode('utf-8'),  # Decode the code verifier used in PKCE
        'client_id': client_id  # Include if required by Twitter's OAuth documentation
    }

    # Make the request manually using requests library
    response = requests.post(token_url, headers=headers, data=body)
    if response.status_code == 200:
        token = response.json()
        print("Bearer Token:", token['access_token'])
        credentials['bearer_token'] = token['access_token']
        return credentials
    else:
        print(f"An error occurred: {response.text}")
        return None



def oauth2_authenticate(file_name='tokens.yaml'):
    credentials = get_credentials(file_name=file_name)
    credentials = _oauth2_authentication_helper(credentials=credentials)
    
    if credentials:
        # write the access token and secret
        with open(file_name, 'w') as file:
            yaml.dump(credentials, file)
        
        print('Credentials Updated using OAuth 2.0!')
        return credentials
    else: 
        print('Credentials Updated FAILED using OAuth 2.0!')
        return 0


def _create_tweet_helper(credentials, payload):
    consumer_key, consumer_secret = credentials['consumer_key'], credentials['consumer_secret']
    access_token, access_token_secret = credentials['access_token'], credentials['access_token_secret']
    # Make oauth
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    # Making the request
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

    if response.status_code != 201:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))
    
    return 1


def create_tweet(file_name, payload, max_attempts=3):
    attempts = 0
    while attempts < max_attempts:
        try:
            credentials = get_credentials(file_name=file_name)
            _create_tweet_helper(credentials, payload)
            print("Tweet created successfully.")
            return  
        except Exception as e:
            print(f"Attempt {attempts + 1} failed: {e}")
            oauth1_authenticate()  # Try to re-authenticate
            attempts += 1  # Increment the attempt counter

    print("Failed to create tweet after maximum attempts.")
    return


def _delete_tweet_helper(credentials, id):
    consumer_key, consumer_secret = credentials['consumer_key'], credentials['consumer_secret']
    access_token, access_token_secret = credentials['access_token'], credentials['access_token_secret']
    # Make the request
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    # Making the request
    response = oauth.delete("https://api.twitter.com/2/tweets/{}".format(id))

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()
    print(json_response)
    
    return 
    
def delete_tweet(file_name, id, max_attempts=3):
    attempts = 0
    while attempts < max_attempts:
        try:
            credentials = get_credentials(file_name=file_name)
            _delete_tweet_helper(credentials, id)
            print("Tweet deleted successfully.")
            return 1
        except Exception as e:
            print(f"Attempt {attempts + 1} failed: {e}")
            oauth1_authenticate()  # Try to re-authenticate
            attempts += 1  # Increment the attempt counter

    print("Failed to delete tweet after maximum attempts.")
    return 0
    

def _follow_list_helper(credentials, id, payload):
    consumer_key, consumer_secret = credentials['consumer_key'], credentials['consumer_secret']
    access_token, access_token_secret = credentials['access_token'], credentials['access_token_secret']
    # Make the request
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    # Making the request
    response = oauth.post(
        "https://api.twitter.com/2/users/{}/followed_lists".format(id), json=payload
    )

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))
    return


def follow_list(file_name, id, payload, max_attempts=3):
    attempts = 0
    while attempts < max_attempts:
        try:
            credentials = get_credentials(file_name=file_name)
            _follow_list_helper(credentials, id, payload)
            print("List followed successfully.")
            return 1
        except Exception as e:
            print(f"Attempt {attempts + 1} failed: {e}")
            oauth1_authenticate()  # Try to re-authenticate
            attempts += 1  # Increment the attempt counter

    print("Failed to follow list after maximum attempts.")
    return 0


def _unfollow_list_helper(credentials, id, list_id):
    consumer_key, consumer_secret = credentials['consumer_key'], credentials['consumer_secret']
    access_token, access_token_secret = credentials['access_token'], credentials['access_token_secret']
    # Make the request
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    # Making the request
    response = oauth.delete(
        "https://api.twitter.com/2/users/{}/followed_lists/{}".format(id, list_id)
    )

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))
    return


def unfollow_list(file_name, list_id, max_attempts=3):
    attempts = 0
    while attempts < max_attempts:
        try:
            credentials = get_credentials(file_name=file_name)
            _unfollow_list_helper(credentials, list_id)
            print("List followed successfully.")
            return 1
        except Exception as e:
            print(f"Attempt {attempts + 1} failed: {e}")
            oauth1_authenticate()  # Try to re-authenticate
            attempts += 1  # Increment the attempt counter

    print("Failed to unfollow list after maximum attempts.")
    return 0


# fields = "created_at,description"
# params = {"user.fields": fields}
def get_my_id(file_name, params):
    credentials = get_credentials(file_name=file_name)
    consumer_key, consumer_secret = credentials['consumer_key'], credentials['consumer_secret']
    access_token, access_token_secret = credentials['access_token'], credentials['access_token_secret']
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    response = oauth.get("https://api.twitter.com/2/users/me", params=params)

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response code: {}".format(response.status_code))

    json_response = response.json()

    print(json.dumps(json_response, indent=4, sort_keys=True))
    
    return

# uses OAuth 2.0
def get_user_id(file_name, params):
    credentials = get_credentials(file_name=file_name)
    bearer_token = credentials['bearer_token']
    usernames = f"usernames={params['usernames']}"
    user_fields = f"user.fields={params['user.fields']}"
    
    def bearer_oauth(r):
        r.headers["Authorization"] = f"Bearer {bearer_token}"
        r.headers["User-Agent"] = "v2UserLookupPython"
        return r
    
    url = "https://api.twitter.com/2/users/by?{}&{}".format(usernames, user_fields)
    
    response = requests.request("GET", url, auth=bearer_oauth,)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )

    return
   
    
if __name__ == "__main__":  
    # Posting a tweet
    file_name = 'tokens.yaml'
    tweet_text = "Testing OAuth 1.0 still working"
    payload1 = {"text": tweet_text}
    payload2 = {"text": '... and also in sequence'}
    id = "1772002309087846400"
    my_id = "wywmiao"
    list_id = 'elonmusk'
    payload3 = {"list_id": list_id}
    fields = "created_at,description"
    params = {"user.fields": fields}
    params = {"usernames": "TwitterDev,TwitterAPI,wywmiao", "user.fields": fields}
    
    oauth2_authenticate()
    credentails = get_credentials(file_name=file_name)
    # create_tweet(file_name=file_name, payload=payload1)
    # create_tweet(credentails, payload2)
    # delete_tweet(credentails, id)  
    # follow_list(file_name=file_name, id=my_id,payload=payload3)
    # get_my_id(file_name=file_name, params=params)
    # get_user_id(file_name=file_name, params=params)
    
    pass