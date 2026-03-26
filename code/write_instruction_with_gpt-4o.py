# import requests
from openai import OpenAI
from PIL import Image
import cv2
import base64
from io import BytesIO
import numpy as np
import os
import json
import shutil

client = OpenAI(
    api_key='<KEY>'
)
client.api_key = 'sk-xx'
client.base_url = 'https://'

def encode_image(image, image_format):
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    buffered = BytesIO()
    pil_image.save(buffered, format=image_format)  # Save in the original format of the image
    return base64.b64encode(buffered.getvalue()).decode('utf-8')
 
def get_image_format(image):
    return image.format  # Directly return the format from the PIL.Image object
 
image_format_dict = {
    'JPEG': 'image/jpeg',
    'PNG': 'image/png',
    'GIF': 'image/gif',
    'bmp': 'image/bmp',
    "WEBP": "image/webp"
}

def write_instruction(image_dir, output_image_dir, output_json_dir, class_description, class_id):
    filenames = os.listdir(image_dir)
    index = 0
    with open("prompt_templete/write_instruction.txt", "r", encoding="utf-8") as f:
        input_prompt_temp = f.read()
    for filename in filenames:
        index += 1
        print(f"process {filename}")
        image_path = os.path.join(image_dir, filename)

        output_json_path = os.path.join(output_json_dir, os.path.splitext(filename)[0]+".txt")
        if os.path.exists(output_json_path):
            continue

        examples = None
        with open(f'prompt_templete\exa\{class_id}.txt', 'r', encoding='utf-8') as fe:
            examples = fe.read()

        image = Image.open(image_path)
        image_format = image.format
        image = cv2.cvtColor(np.asarray(Image.open(image_path)), cv2.COLOR_RGB2BGR)
        base64_image = encode_image(image, image_format)
        system_prompt_content = ""
        
        input_prompt_temp = input_prompt_temp.replace("class_description", class_description).replace("{Examples}", examples)
        # print(input_prompt_temp)
        response = client.chat.completions.create(
            # model='ui-tars-1.5-7b',
            model='gpt-4o',
            messages=[
                {
                    "role": "system",  # system
                    "content": [
                        {
                            "type": "text",  
                            "text": system_prompt_content 
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": input_prompt_temp
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image_format_dict[image_format]};base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                ],
                },
            ],
            max_tokens=2000,
        )

        # print(response)
        response = response.choices[0].message.content
        print(response)

        with open(output_json_path, 'w', encoding='utf-8') as fo:
            json.dump(response, fo, ensure_ascii=False, indent=2)

        shutil.copy2(image_path, output_image_dir)

if __name__ == "__main__":
    # Replace all parameters with your own
    class_id = "8"
    image_dir = f"dataset3/{class_id}"
    output_image_dir = "image_ori/dataset3/image" 
    os.makedirs(output_image_dir, exist_ok=True)
    output_json_dir = f"image_ori/dataset3/text/{class_id}" 
    os.makedirs(output_json_dir, exist_ok=True)
    with open("Category.json", 'r', encoding='utf-8') as f:
        categ = json.load(f)
    class_description = None
    for item in categ:
        if item.get('id') == int(class_id):  # match id=class_id
            class_description = item.get('Description')
            break
    write_instruction(image_dir, output_image_dir, output_json_dir, class_description, class_id)