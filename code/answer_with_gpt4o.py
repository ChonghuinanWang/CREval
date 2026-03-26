import os
import base64
import json
import re
import cv2
import numpy as np
from openai import OpenAI
from PIL import Image
from io import BytesIO

class ImageEvaluator:
    def __init__(self, api_key, base_url, prompt_path):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.single_prompt = self._load_single_prompt(prompt_path)
        self.supported_image_formats = {
            'JPEG': 'image/jpeg',
            'PNG': 'image/png',
            'GIF': 'image/gif',
            'BMP': 'image/bmp',
            'JPG': 'image/jpg',
            'WEBP': 'image/webp'
        }

    def _load_single_prompt(self, prompt_path):
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"prompt doesn't exists: {prompt_path}")
        
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _encode_image(self, image, image_format):
        try:
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            buffered = BytesIO()
            pil_image.save(buffered, format=image_format)
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"image encode faied: {str(e)}")
            return None

    def _load_image(self, image_path):
        try:
            pil_image = Image.open(image_path)
            image_format = pil_image.format
            
            image = cv2.cvtColor(np.asarray(pil_image), cv2.COLOR_RGB2BGR)
            return image, image_format
        except Exception as e:
            print(f"image load failed {image_path}: {str(e)}")
            return None, None

    def _find_image_path(self, root_path, base_name):
        for ext in [f'.{fmt.lower()}' for fmt in self.supported_image_formats.keys()]:
            image_path = os.path.join(root_path, f"{base_name}{ext}")
            if os.path.exists(image_path):
                return image_path
        return None

    def _parse_model_response(self, response_text):
        try:
            # acquire JSON
            json_strings = re.findall(r'\{.*?\}', response_text, re.DOTALL)
            parsed_responses = []
            
            for json_str in json_strings:
                json_str = json_str.replace('\n', '').replace('\r', '')
                try:
                    parsed = json.loads(json_str)
                    parsed_responses.append(parsed)
                except json.JSONDecodeError:
                    continue
                    
            return parsed_responses
        except Exception as e:
            print(f"parse model response failed: {str(e)}")
            return []
        
    def evaluate_pair(self, root_path_a, root_path_b, json_file, output_file):
        json_basename = os.path.splitext(os.path.basename(json_file))[0]
        detailed_result = {
            "filename": json_basename,
            "questions": [],  
            "final_score": 0.0, 
        }
        
        image_a_path = self._find_image_path(root_path_a, json_basename)
        image_b_path = self._find_image_path(root_path_b, json_basename)
        
        print("image_ori: ", image_a_path)
        print("image_edited: ", image_b_path)

        if not image_a_path:
            print(f"original image A doesn't exists: {json_basename} 在 {root_path_a}")
            detailed_result["error"] = "original image A doesn't exists"
            return detailed_result
        if not image_b_path:
            print(f"Edited image B doesn't exists: {json_basename} 在 {root_path_b}")
            detailed_result["error"] = "Edited image B doesn't exists"
            return detailed_result

        # load and encode image
        image_a, format_a = self._load_image(image_a_path)
        image_b, format_b = self._load_image(image_b_path)
        
        if image_a is None or image_b is None or format_a is None or format_b is None:
            detailed_result["error"] = "image load error"
            return detailed_result
            
        # trans to Base64
        base64_a = self._encode_image(image_a, format_a)
        base64_b = self._encode_image(image_b, format_b)
        
        if not base64_a or not base64_b:
            detailed_result["error"] = "image encode error"
            return detailed_result

        # build image URL
        image_url_a = f"data:{self.supported_image_formats[format_a]};base64,{base64_a}"
        image_url_b = f"data:{self.supported_image_formats[format_b]};base64,{base64_b}"

        # read "questions" in JSON
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"JSON parse error {json_file}: {str(e)}")
            detailed_result["error"] = f"JSON parse error: {str(e)}"
            return detailed_result
            
        questions = data.get("quality_check_questions", [])
        if not questions:
            print(f"can't find questions in JSON: {json_file}")
            detailed_result["error"] = "can't find questions in JSON"
            return detailed_result

        questions_text = "Please answer all questions regarding the edited image (second image) as follows:\n\n"
        for q in questions:
            questions_text += f"{q['question_id']}: {q['question']}\n"
            questions_text += "Choices: " + ", ".join(q['choices']) + "\n\n"
        
        final_prompt = self.single_prompt.replace("{Questions}", questions_text)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": "You are an image quality evaluator. Please assess the edited image based on the given questions."}]
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": image_url_a, "detail": "high"}},
                            {"type": "image_url", "image_url": {"url": image_url_b, "detail": "high"}},
                            {"type": "text", "text": final_prompt}
                        ]
                    }
                ],
                max_tokens=2000,
            )
            model_answer = response.choices[0].message.content.strip()

            txt_save_path = output_file[:-5] + ".txt"
            with open(txt_save_path,'w',encoding='utf-8') as ft:
                ft.write(model_answer)

        except Exception as e:
            print(f"API failed {json_basename}: {str(e)}")
            detailed_result["error"] = f"API failed: {str(e)}"
            return detailed_result
        
        # parse_model_response
        parsed_answers = self._parse_model_response(model_answer)
        if not parsed_answers:
            detailed_result["error"] = "can't parse model response"
            return detailed_result
        
        # calculate scores
        weighted_score = 0.0
        total_weight = 0.0

        for q in questions:
            question_id = q['question_id']
            weight = q.get('weight', 1.0)
            total_weight += weight
            
            # find model answers
            model_response = next(
                (ans for ans in parsed_answers if ans.get('Question', '').startswith(question_id)),
                None
            )
            
            if model_response:
                model_answer_text = model_response.get('answer', '').strip()
                correct_answer = q['answer'].strip()
                is_correct = str(model_answer_text.lower()) == str(correct_answer.lower())
                explanation = model_response.get('explanation', '')
                
                if is_correct:
                    weighted_score += weight
            else:
                model_answer_text = "don't find model answers"
                explanation = "don't find model explanation for this answer"
                is_correct = False
            
            # log detail infos
            detailed_result["questions"].append({
                "question_id": q['question_id'],
                "question": q['question'],
                "choices": q['choices'],
                "correct_answer": q['answer'],
                "explanation": explanation,
                "weight": weight,
                "model_answer": model_answer_text,
                "is_correct": is_correct
            })

        # calculate final scores
        if total_weight > 0:
            detailed_result["final_score"] = weighted_score / total_weight
        else:
            detailed_result["final_score"] = 0.0

        return detailed_result

    # read json, then find rootA and rootB
    def batch_evaluate(self, json_folder, root_path_a, root_path_b, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        json_files = [
            os.path.join(json_folder, f) 
            for f in os.listdir(json_folder) 
            if os.path.isfile(os.path.join(json_folder, f)) and f.lower().endswith('.json')
        ]

        for i, json_file in enumerate(json_files, 1):
            json_filename = os.path.basename(json_file)
            output_file = os.path.join(output_folder, json_filename)
            if os.path.exists(output_file):
                continue

            print(f"\nprocess {i}/{len(json_files)}: {json_filename}")
            result = self.evaluate_pair(root_path_a, root_path_b, json_file, output_file)
            print(f"Score: {result['final_score']:.4f}")

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\nresults have been save: {output_file}")


if __name__ == "__main__":
    API_KEY = "sk-xx"
    BASE_URL = "https:xx"
    PROMPT_PATH = "prompt_templete/answer.txt"  # answer prompt path
    TYPE = ["IF", "VC", "VQ"]

    output_root = "./answer_gpt"
    os.makedirs(output_root, exist_ok=True)
    ROOT_PATH_A = "./bench/image"  # original image A path
    model_names = ["OmniGen2, Bagel, Qwen-Image-Edit-2509"]

    for modelname in model_names:
        for tp in TYPE:
            JSON_FOLDER = f"./bench/questions_all/{tp}"  # questions json root_path
            ROOT_PATH_B = f"./outputs_images/{modelname}"  # Edited image B root_path
            OUTPUT_FOLDER = f"{output_root}/{tp}/{modelname}"  # output path
            evaluator = ImageEvaluator(API_KEY, BASE_URL, PROMPT_PATH)
            evaluator.batch_evaluate(JSON_FOLDER, ROOT_PATH_A, ROOT_PATH_B, OUTPUT_FOLDER)

