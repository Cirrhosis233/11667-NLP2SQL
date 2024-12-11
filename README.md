# 11667-NLP2SQL

## Setup

- Python=3.11

- ```bash
  $ pip install requirements.txt
  ```

## Datasets

- [b-mc2/sql-create-context](https://huggingface.co/datasets/b-mc2/sql-create-context): raw dataset for sql-create-context
- [sql-eval](https://github.com/defog-ai/sql-eval): raw data for defog data
- `datasets/sql-create-context-split`: local dataset created from b-mc2/sql-create-context
- `datasets/train_merge_150x5_750`: local dataset that merges b-mc2/sql-create-context and defog data
- `datasets/train_merge_150x5_750_diff_prompt` local dataset that merges b-mc2/sql-create-context and defog data, with unique prompt template incorporated
- `datasets/train_merge_150x5_750_diff_prompt_gold` local dataset that merges b-mc2/sql-create-context and defog data, with unique prompt template incorporated, with golden `{}` query issue fixed

## All versions of Prompts

Stored at `./prompts/*.md`

## How to Run:

### Inference:

```bash
$ python inference_vllm.py --model <base model> --data <data split> --prompt <prompt template file path> --output <output path> --lora <lora fineuned model path, not required>
```

- Example of usage can refer to `inference_vllm.sh`

### Finetuning:

#### Without Prompt Differentiation

```bash
$ python finetune.py ./configs/codellama-v0.json
```

Apply to:

- `datasets/sql-create-context-split`: local dataset created from b-mc2/sql-create-context
- `datasets/train_merge_150x5_750`: local dataset that merges b-mc2/sql-create-context and defog data

Only

#### With Prompt Differentiation

```bash
$ python finetune_1.py ./configs/codellama-v7.json
```

Apply to:

- `datasets/train_merge_150x5_750_diff_prompt` local dataset that merges b-mc2/sql-create-context and defog data, with unique prompt template incorporated
- `datasets/train_merge_150x5_750_diff_prompt_gold` local dataset that merges b-mc2/sql-create-context and defog data, with unique prompt template incorporated, with golden `{}` query issue fixed

Only

## Evaluation

Refer to `./evaluation/README.md`
