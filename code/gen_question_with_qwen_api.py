# 调用Qwen2.5-VL-72B-instruct生成问题
import os
import json
import base64
import re
from openai import OpenAI

image_root_path = "image_ori/dataset3" # replace your path
def image_to_base64(image_path):
    try:
        img_ext = os.path.splitext(image_path)[1].strip('.').lower()
        with open(image_path, "rb") as image_file:
            base64_str = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/{img_ext};base64,{base64_str}" 
    except Exception as e:
        print(f"image trans to base64 failed: {str(e)}")
        return None

def parse_content_to_json(content):
    quality_check_questions = []

    question_blocks = re.split(r'(?=Q\d+:)', content)
    for block in question_blocks:
        block = block.strip()
        if not block.startswith('Q'):
            continue
        
        thinking_match = re.search(r'Thinking process:(.*?)Question:', block, re.DOTALL)
        question_match = re.search(r'Question:(.*?)Choices:', block, re.DOTALL)
        choice_match = re.search(r'Choices:(.*?)A:', block, re.DOTALL)
        answer_match = re.search(r'A:\s*(.*?)\s*(?=\n|`|$)', block, re.DOTALL | re.IGNORECASE)
        weight_match = re.search(r'Weight:\s*(\d+)', block)

        weight = 1
        if weight_match:
            weight_str = weight_match.group(1).strip()
            if weight_str.isdigit() and 1 <= int(weight_str) <= 3:
                weight = int(weight_str)
        
        quality_check_questions.append({
            "question_id": re.search(r'Q\d+', block).group() if re.search(r'Q\d+', block) else "",
            "thinking_process": thinking_match.group(1).strip() if thinking_match else "",
            "question": question_match.group(1).strip() if question_match else "",
            "choices": [c.strip() for c in choice_match.group(1).split(',')] if choice_match else [],
            "answer": answer_match.group(1).strip() if answer_match else "",
            "weight": weight
        })
    
    return {
        # "creation_instructions": creation_instructions,
        "quality_check_questions": quality_check_questions
    }

def call_qwen_vl_from_json(json_file_path, template_file, save_root_path):
    client = OpenAI(
        api_key="sk-xxx",
        base_url="https://",
    )
    
    print(f"1. read json: {json_file_path}")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"2. read prompt: {template_file}")
    with open(template_file, 'r', encoding='utf-8') as f:
        text_template = f.read()
    
    for index, item in enumerate(data):
        
        print(f"\nprocess {item['id']}...")
        
        img_filename_with_ext = item["input_image"][0]  # e.g., creature_rock.png
        image_path = os.path.join(image_root_path, img_filename_with_ext)
        image_file_name = os.path.splitext(os.path.basename(image_path))[0]

        json_output_path = f"{image_file_name}.json"
        json_save_path = os.path.join(save_root_path, json_output_path)
        if os.path.exists(json_save_path):
            print(f"{json_save_path} has been exist, skipping...")
            continue

        prompt_text = item["input_prompt"]
        final_text = text_template.replace("{Edit instructions}", prompt_text)
        base64_image = image_to_base64(image_path)

        print(f"image path: {image_path}")

        try:
            completion = client.chat.completions.create(
                model="qwen2.5-vl-72b-instruct",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url", 
                            "image_url": {"url": base64_image}
                        },
                        {
                            "type": "text", 
                            "text": final_text
                        }
                    ]
                }]
            )
            
            content = completion.choices[0].message.content
            
            # Generate a TXT file with the same name as the image
            txt_output_path = f"{image_file_name}.txt"
            txt_save_path = os.path.join(save_root_path, txt_output_path)
            with open(txt_save_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"TXT file has been saved: {txt_save_path}")
            
            # Generate a JSON file with the same name as the image
            result_json = parse_content_to_json(content)
            with open(json_save_path, "w", encoding="utf-8") as f:
                json.dump(result_json, f, ensure_ascii=False, indent=2)
            print(f"JSON file has been saved: {json_save_path}")
            
        except Exception as e:
            print(f"API failed: {str(e)}")


if __name__ == "__main__":
    for i in range(1, 10):
        json_file = f"image_ori\dataset3\json\dataset3_{str(i)}.json" # replace your path
        QUESTION_TYPE = ["IF","VC","VQ"]
        for q_type in  QUESTION_TYPE:
            save_root_path = f"questions_qwen_dataset3/{str(i)}/{q_type}"
            os.makedirs(save_root_path, exist_ok=True)
            template_file = f"prompt_templete/{q_type}.txt"
            call_qwen_vl_from_json(json_file, template_file, save_root_path)