import os
import json

def calculate_final_score_average(folder_path):
    # Initialize variables: store total score and number of valid files
    total_score = 0.0
    valid_file_count = 0
    error_files = []  # Record file read failures (such as formatting errors, missing fields)

    # Traverse all files in the folder
    for filename in os.listdir(folder_path):
        # Only process files with .json suffix
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            try:
                # resd JSON files
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # acquire final_score，ensure it is of numeric type
                score = data.get("final_score")
                if score is None:
                    error_files.append(f"{filename} - lack of 'final_score'")
                    continue
                if not isinstance(score, (int, float)):
                    error_files.append(f"{filename} - 'final_score' is not a number (current type: {type(score).__name__})")
                    continue
                
                # accumulate score and count
                total_score += score
                valid_file_count += 1

            except json.JSONDecodeError:
                error_files.append(f"{filename} - JSON format error (file corruption or illegal content)")
            except Exception as e:
                error_files.append(f"{filename} - Other errors:{str(e)}")

    # calculate average score
    if valid_file_count == 0:
        print("No valid data found, unable to calculate the average.")
        average = 0.0
    else:
        average = total_score / valid_file_count
        # print result
        print(f"=== Calculating results ===")
        print(f"Number of valid JSON files:{valid_file_count}")
        print(f"Final Score:{total_score:.2f}")
        print(f"Final Score Average:{average:.2f}")

    # Printing error files (if any)
    if error_files:
        print(f"\n=== Read failed files {len(error_files)} 个===")
        for err in error_files:
            print(f"- {err}")

    return average

# --------------------------
#Please modify the folder path here!!!
# --------------------------
target_folder = r"answer_gpt/IF/seedream4-0"  # 示例：r"D:/data/json_files"
calculate_final_score_average(target_folder)