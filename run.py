from twi_func import *
from miao_func import *
from ai_func import *
import os
import random
from datetime import datetime
import schedule
import time

def main():
    file_name = "tokens.yaml"
    base_folder = "src/imgs/randoCat"
    base_dir = "src/古文原文"
    # generate prompt from given text

    file_path, replaced_text, replaced_num = traverse_directory(base_dir)
    prompt = replaced_text
    
    # generate image using OpenAI api
    try:
        img_url = create_image(prompt, file_name=file_name)
        img_path = download_image(img_url)
    except Exception as e:
        #if not working, choose a random image from base folder 
        print(f"Error: {e}")
        print(f"Choosing image from base library {base_folder}")
        valid_extensions = ('.jpg', '.jpeg', '.png')
        valid_files = [f for f in os.listdir(base_folder) if f.endswith(valid_extensions)]
        if not valid_files:
            raise Exception("No valid images found in the base folder.")
        img_path = os.path.join(base_folder, random.choice(valid_files))
        
        
    # create tweet payload and send the tweet
    media_id = upload_media(file_name, img_path)
    payload = payload_generate(prompt, media_id)
    
    create_tweet(file_name, payload)
    
    current_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    print(f"Tweet sent successfully at {current_time}")
    
    return

if __name__ == "__main__":
    while True:
        main()
        time.sleep(86400)

    pass