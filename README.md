# 11667-NLP2SQL

## Setup

- Python=3.11

## Datasets

- [b-mc2/sql-create-context](https://huggingface.co/datasets/b-mc2/sql-create-context)

  - split in `./datasets/sql-create-context-split`

  - ```python
    from datasets import load_from_disk
    split_dataset = load_from_disk("./datasets/sql-create-context-split")
    ```


## Models

- [defog/sqlcoder-7b-2](https://huggingface.co/defog/sqlcoder-7b-2)
