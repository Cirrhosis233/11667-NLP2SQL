import torch
from datasets import load_from_disk
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

from tqdm import tqdm


def generate_prompt_batch(batch, prompt_file="prompt.md"):
    with open(prompt_file, "r") as f:
        prompt = f.read()

    prompt_batch = [
        prompt.format(user_question=q, table_metadata_string=m)
        for q, m in zip(batch["question"], batch["context"])
    ]

    return prompt_batch


def get_tokenizer_model(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,  # May not work on All GPU, use float16 instead if error
        device_map="auto",
        use_cache=True,
    )
    return tokenizer, model


def generate_sql_batch(dataset, tokenizer, model, batch_size=1):
    eos_token_id = tokenizer.eos_token_id
    tokenizer.pad_token_id = eos_token_id
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=300,
        do_sample=False,
        return_full_text=False,
        num_beams=1,
    )
    generations = []

    for i in tqdm(range(0, len(dataset), batch_size), desc="Generating:"):
        batch = dataset[i : i + batch_size]
        prompts = generate_prompt_batch(batch)

        outputs = pipe(
            prompts,
            num_return_sequences=1,
            eos_token_id=eos_token_id,
            pad_token_id=eos_token_id,
            batch_size=batch_size,
        )

        for output in outputs:
            generated_query = (
                output[0]["generated_text"].split(";")[0].split("```")[0].strip()
            )
            generations.append(generated_query)

    return generations


if __name__ == "__main__":
    dataset = load_from_disk("./datasets/sql-create-context-split")
    test_data = dataset["val"]
    tokenizer, model = get_tokenizer_model("defog/sqlcoder-7b-2")

    generations = generate_sql_batch(test_data, tokenizer, model, batch_size=16)
    output = test_data.add_column("generation", generations)
    output.to_json("val_eval_1beam.json")
