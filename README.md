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


Module	Role in Transformer	Why Include It for Text2SQL?
q_proj	Query projections for attention	Helps map user queries to the relevant parts of the schema.
v_proj	Value projections for attention	Refines SQL syntax generation based on schema content.
k_proj	Key projections for attention	Enhances alignment between query tokens and schema tokens.
down_proj	Part of feed-forward network	Improves representation of query and schema after attention layers.
up_proj	Part of feed-forward network	Boosts capacity for handling token-to-token mappings in SQL syntax.
