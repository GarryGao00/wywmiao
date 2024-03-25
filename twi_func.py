import yaml
from requests_oauthlib import OAuth1Session
import json
import logging

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
    _oauth1_authentication_helper(credentials=credentials)
    
    # write the access token and secret
    with open(file_name, 'w') as file:
        yaml.dump(credentials, file)
    
    print('Credentials Updated!')
    return credentials


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

   
    
if __name__ == "__main__":  
    # Posting a tweet
    file_name = 'tokens.yaml'
    tweet_text = "Testing if credential works"
    payload1 = {"text": tweet_text}
    payload2 = {"text": '... and also in sequence'}
    id = "1772021210240684071"
    my_id = "wywmiao"
    list_id = 'elonmusk'
    payload3 = {"list_id": list_id}
    
    # credentails = get_credentials(file_name=file_name)
    create_tweet(file_name=file_name, payload=payload1)
    # create_tweet(credentails, payload2)
    # delete_tweet(credentails, id)  
    follow_list(file_name=file_name, id=my_id,payload=payload3)
    
    pass