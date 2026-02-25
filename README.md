# CREval

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

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file and edit with your credentials:

```bash
cp .env.example .env
# Edit .env with your API keys
```

Or set via environment variables:

```bash
export OPENAI_API_KEY="your-api-key-here"
export IMAGE_EDIT_API_KEY="your-image-edit-api-key-here"
```

### 3. Download Benchmark Data

Benchmark data must be downloaded separately. See [DATA_DOWNLOAD.md](DATA_DOWNLOAD.md) for details.

### 4. Run Evaluation

```bash
python run_eval.py \
  --root_path_a ./bench/image \
  --root_path_b ./outputs_images/YourModel \
  --type IF VC VQ
```

That's it! Results will be saved to `./results/`

## Usage

### Evaluate Image Editing Results

The recommended way is to use `run_eval.py`:

```bash
# Basic evaluation
python run_eval.py \
  --root_path_a ./bench/image \
  --root_path_b ./outputs_images/YourModel

# Evaluate specific dimensions only
python run_eval.py -a ./bench/image -b ./outputs --type IF VC

# Use short arguments
python run_eval.py -a ./bench/image -b ./outputs -t IF -o ./results

# Evaluate multiple models
python run_eval.py -a ./bench/image -b ./outputs -m Model1 Model2 Model3
```

**Arguments:**
| Argument | Short | Required | Description |
|----------|-------|----------|-------------|
| `--root_path_a` | `-a` | Yes | Directory containing original images |
| `--root_path_b` | `-b` | Yes | Directory containing edited images (or parent if using --model_names) |
| `--type` | `-t` | No | Evaluation type(s): IF, VC, VQ (default: all) |
| `--model_names` | `-m` | No | Model name(s) to evaluate (default: default) |
| `--output_root` | `-o` | No | Output directory for results (default: ./results) |
| `--api_key` | `-k` | No | API key (or set OPENAI_API_KEY env var) |
| `--base_url` | | No | API base URL |
| `--prompt_path` | `-p` | No | Path to prompt template |
| `--overwrite` | | No | Re-evaluate even if results exist |

### Generate Edited Images (Optional)

If you want to generate edited images using an API:

```bash
python scripts/generate_images.py \
  --api_key YOUR_API_KEY \
  --image_dir ./bench/image \
  --output_dir ./outputs_images
```

**Arguments:**
| Argument | Short | Description |
|----------|-------|-------------|
| `--api_key` | `-k` | API key (or set IMAGE_EDIT_API_KEY env var) |
| `--instruction_file` | `-i` | Path to instruction JSON (default: bench/instruction.json) |
| `--image_dir` | `-d` | Directory with input images (default: bench/image) |
| `--output_dir` | `-o` | Output directory (default: outputs_images/gpt-image-1) |
| `--model` | | Model name to use |
| `--size` | | Image size (default: 1024x1024) |
| `--quality` | | Image quality (high/medium/low/auto) |

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

## Documentation

- [DATA_DOWNLOAD.md](DATA_DOWNLOAD.md) - How to download benchmark data
- [CONFIG.md](CONFIG.md) - Configuration guide

## Citation

If you use CREval in your research, please cite:

```bibtex
@inproceedings{creval2025,
  title={CREval: A Comprehensive Benchmark for Image Editing Evaluation},
  author={...},
  booktitle={CVPR},
  year={2025}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

For questions and issues, please open an issue on GitHub.