import json
from openai import OpenAI
from PIL import Image
import cv2
import base64
from io import BytesIO
import numpy as np
import os

client = OpenAI(
    api_key='<KEY>'
)
client.api_key = 'sk-xx'
client.base_url = 'https://'

def encode_image(image, image_format):
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    buffered = BytesIO()
    pil_image.save(buffered, format=image_format)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def read_prompt_template(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def process_image_entry(entry, template_path, base_image_dir):
    try:
        # Read prompt word template and replace placeholders
        template_content = read_prompt_template(template_path)
        processed_prompt = template_content.replace("{original_instruction}", entry["input_prompt"])
        
        # Process image path
        image_relative_path = entry["input_image"][0]
        image_full_path = os.path.join(base_image_dir, image_relative_path)
        if not os.path.exists(image_full_path):
            print(f"Warning: Image file does not exist - {image_full_path}")
            return None
        
        # Loading and processing images
        image = Image.open(image_full_path)
        image_format = image.format
        image_cv = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
        base64_image = encode_image(image_cv, image_format)
        
        # Image format mapping
        image_format_dict = {
            'JPEG': 'image/jpeg',
            'PNG': 'image/png',
            'GIF': 'image/gif',
            'BMP': 'image/bmp'
        }
        
        # Ensure that the image format is in the supported list
        if image_format not in image_format_dict:
            print(f"Warning: Unsupported image format - {image_format}")
            return None
        
        # OpenAI API
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": processed_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image_format_dict[image_format]};base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000,
        )
        
        print(f"process ID finished: {entry['id']}")
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"process id {entry['id']} error: {str(e)}")
        return None

def main():
    json_file_path = "image_prompt.json"  # JSON file containing images and instructions
    template_file_path = "prompt_templete/rewrite_instruction.txt" 
    base_image_directory = "image_ori/images"  # Image Catalog
    output_json_file = "image_prompt_new.json"
    with open(json_file_path, 'r', encoding='utf-8') as f:
        entries = json.load(f)
        results = []
        for i,entry in enumerate(entries):
            if i>2:
                break
            result = process_image_entry(entry, template_file_path, base_image_directory)
            result_entry = entry.copy()
            result_entry["input_prompt"] = result
            results.append(result_entry)
        with open(output_json_file, "w", encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
