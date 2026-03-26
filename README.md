# CREval
[![arXiv paper](https://img.shields.io/badge/arXiv-paper-b31b1b.svg)](https://github.com/ChonghuinanWang/CREval)
[![Huggingface Dataset](https://img.shields.io/badge/Huggingface-Dataset-ffc107.svg)](https://huggingface.co/datasets/ChonghuinanWang/CREval)


**CREval** is a comprehensive benchmark for evaluating image editing models. It assesses model outputs across three key dimensions:

- **IF (Instruction Following)** - How well the edited image follows the given editing instructions
- **VC (Visual Coherence)** - The overall visual consistency of the edited image
- **VQ (Visual Quality)** - The visual quality of the edited image

## Features

- Automated evaluation using GPT-4o
- Support for multiple evaluation dimensions (IF, VC, VQ)
- Batch processing capabilities
- Detailed scoring with weighted questions
- Extensible prompt templates for custom evaluation criteria

## Project Structure

```
CREval-main/
├── run_eval.py               # Main evaluation script (ENTRY POINT)
├── scripts/                  # Utility scripts
│   └── generate_images.py    # Generate edited images via API
├── eval_core/               # Core evaluation modules
│   ├── evaluator.py          # ImageEvaluator class
│   └── models.py            # Configuration models
├── bench/                   # Benchmark data (download separately)
│   ├── image/               # Test images
│   ├── questions_all/       # Question JSON files (IF/VC/VQ)
│   ├── instruction.json     # Instruction data
│   └── utils/              # Utility scripts
├── code/                    # Legacy scripts (kept for compatibility)
└── prompt_templete/          # Prompt templates
```

```
CREval-main/
├─bench
│  ├─image                    # original image
│  ├─questiions_all           # questions root path
│  │  ├─IF                      # IF questions 
│  │  ├─VC                      # VC questions
│  │  └─VQ                      # VQ questions
│  └─instruction.json         # image-instruction annotation
└─code
    ├─prompt_templete         # Prompt templates
    │    └─exa                # context example for each category
    └─answer_with_gpt4o.py    # Evaluation script

```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Prepare your own API key and write it in the corresponding position in the code. 
```bash
API_KEY = "sk-xx", BASE_URL = "https:xx"
``` 
or 
```bash
client.api_key = 'sk-xx', client.base_url = 'https://'
```

### 3. Download Benchmark Data

Benchmark data must be downloaded separately. See [CREval-Bench](https://huggingface.co/datasets/ChonghuinanWang/CREval) for details.

### 4. Run Evaluation

put your edited images in CREval/outputs_images/{modelname}

```bash
cd code
```

```bash
python answer_with_gpt4o.py
```

That's it! Results will be saved to `../answers/`, then calculate the score

```bash
python avg.py
```


## Usage

### Build your own dataset

Prepare the original image, then generate image-instruction pairs and evaluation questions for different dimensions.

```bash
# generate instructions
python write_instruction_with_gpt-4o.py \

# Generate evaluation questions from different dimensions
python gen_question_with_qwen_api.py

```


## Evaluation Details

### Instruction Following (IF)

Evaluates whether the edited image correctly implements all editing instructions, including:
- Explicit requirements (e.g., "add red flowers")
- Implicit requirements derived from world knowledge (e.g., "ink painting style" implies specific visual characteristics)
- Object additions, deletions, and replacements
- Color, size, position, and material attributes
- Style transformations and constraints

### Visual Coherence (VC)

Assesses the overall visual consistency and coherence of edited images.

### Visual Quality (VQ)

Evaluates the visual quality of edited images.

## Output Format

For each evaluated image pair, the tool generates:

```json
{
  "filename": "image_name",
  "questions": [
    {
      "question_id": "Q1",
      "question": "Question text",
      "choices": ["Yes", "No"],
      "correct_answer": "Yes",
      "model_answer": "Yes",
      "explanation": "Detailed explanation...",
      "weight": 1.0,
      "is_correct": true
    }
  ],
  "final_score": 0.95
}
```

Results are saved as JSON files with corresponding `.txt` files containing raw model responses.

## Citation

If you use CREval in your research, please cite:

```bibtex
@inproceedings{creval2025,
  title={CREval: An Automated Interpretable Evaluation for Creative Image Manipulation under Complex Instructions},
  author={...},
  booktitle={CVPR},
  year={2026}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

For questions and issues, please open an issue on GitHub.