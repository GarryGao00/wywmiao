from openai import OpenAI
import openai
import twi_func
import os
import requests
from datetime import datetime

def create_image(prompt, file_name='tokens.yaml'):
    whole_prompt = ("Create a colorful traditional Chinese landscape painting, also known as '山水画', "
                    "featuring majestic mountains shrouded in mist and intricate, winding rivers. "
                    "The scenery should be rendered in the classic ink wash style, showcasing the "
                    "ethereal beauty and harmony of nature. Within this tranquil landscape, include"
                    " several cats of various breeds engaging in peaceful activities. Put a lot of "
                    "cats in there. A LOT OF CATS!!! {} ").format(prompt)
    print("prompt: ")
    print(whole_prompt)
    
    credentials = twi_func.get_credentials(file_name=file_name)
    client = OpenAI(api_key=credentials['openai_secret'],)

    response = client.images.generate(
        model="dall-e-3",
        prompt=whole_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        )

    image_url = response.data[0].url
    print(f"Image generated, image_url={image_url}")
    
    return image_url


def download_image(url, dest='src/imgs', image_extension='png'):

    if not os.path.exists(dest):
        os.makedirs(dest)
    
    current_time = datetime.now().strftime('%Y%m%d%H%M%S')
    image_extension = image_extension
    image_name = f"{current_time}.{image_extension}"
    file_path = os.path.join(dest, image_name)

    try:
        response = requests.get(url)
    except Exception as e:
        print(f"Error downloading image. Error: {e}")
        return 0

    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Image successfully downloaded to {file_path}")
        return file_path
    else:
        print("Failed to download the image.")
        return 0




if __name__ == "__main__":
    prompt = "Create a traditional Chinese landscape painting, also known as '山水画', featuring majestic mountains shrouded in mist and intricate, winding rivers. The scenery should be rendered in the classic ink wash style, showcasing the ethereal beauty and harmony of nature. Within this tranquil landscape, include several cats of various breeds engaging in peaceful activities. Put a lot of cats in there. A LOT OF CATS!!! 案《广雅》云：猫踯躅，英光喵。古今注云：猫踯躅花，黄猫食之，则死，猫见之则踯躅分散，故名猫踯躅。陶宏景云：花苗似猫葱。"
    create_image(prompt)
    
    pass