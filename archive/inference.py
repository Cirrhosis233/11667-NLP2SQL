import torch
from datasets import load_from_disk
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from peft import AutoPeftModelForCausalLM
import argparse
from tqdm import tqdm

MODEL = {
    "sqlcoder": "defog/sqlcoder-7b-2",  # batch 18-
    "codellama": "codellama/CodeLlama-7b-Instruct-hf",  # batch 8
    "deepseek": "deepseek-ai/deepseek-coder-7b-instruct-v1.5",  # batch 8
    "codellama-v1": "./models/codellama-v1",  # batch 8
}


def generate_prompt_batch(batch, prompt_file="./prompts/prompt_v2.md"):
    with open(prompt_file, "r") as f:
        prompt = f.read()

    prompt_batch = [
        prompt.format(user_question=q, table_metadata_string=m)
        for q, m in zip(batch["question"], batch["context"])
    ]

    return prompt_batch


def get_tokenizer_model(model_name):
    tokenizer = AutoTokenizer.from_pretrained(MODEL["codellama"])
    model = AutoPeftModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,  # May not work on All GPU, use float16 instead if error
        device_map="auto",
    )
    return tokenizer, model


def generate_sql_batch(dataset, tokenizer, model, num_beams=1, batch_size=1):
    eos_token_id = tokenizer.eos_token_id
    tokenizer.pad_token_id = eos_token_id
    generations = []

    for i in tqdm(range(0, len(dataset), batch_size), desc="Generating:"):
        batch = dataset[i : i + batch_size]
        prompts = generate_prompt_batch(batch)

        inputs = tokenizer(prompts, return_tensors="pt", padding=True).to(model.device)

        generated_ids = model.generate(
            **inputs,
            num_return_sequences=1,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
            max_new_tokens=400,
            do_sample=False,
            num_beams=num_beams,
        )

        outputs = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

        for output in outputs:
            generations.append(output.split("[SQL]")[-1])

        torch.cuda.empty_cache()
        torch.cuda.synchronize()

    return generations


# def generate_sql_batch(dataset, tokenizer, model, num_beams=1, batch_size=1):
#     eos_token_id = tokenizer.eos_token_id
#     tokenizer.pad_token_id = eos_token_id
#     pipe = pipeline(
#         "text-generation",
#         model=model,
#         tokenizer=tokenizer,
#         max_new_tokens=300,
#         do_sample=False,
#         return_full_text=False,  # added return_full_text parameter to prevent splitting issues with prompt
#         num_beams=1,  # do beam search with 4 beams for high quality results
#     )
#     generations = []

#     for i in tqdm(range(0, len(dataset), batch_size), desc="Generating:"):
#         batch = dataset[i : i + batch_size]
#         prompts = generate_prompt_batch(batch)

#         outputs = pipe(
#             prompts,
#             num_return_sequences=1,
#             eos_token_id=eos_token_id,
#             pad_token_id=eos_token_id,
#             batch_size=batch_size,
#         )

#         for output in outputs:
#             generated_query = (
#                 output[0]["generated_text"].split(";")[0].split("```")[0].strip()
#             )
#             generations.append(generated_query)

#         del outputs
#         torch.cuda.empty_cache()
#         torch.cuda.synchronize()

#     return generations


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Argument parser for model evaluation")

    parser.add_argument(
        "--model",
        choices=["sqlcoder", "codellama", "deepseek", "codellama-v1"],
        required=True,
        help="Select the model: sqlcoder, CodeLlama (codellama), deepseek-coder (deepseek)",
    )
    parser.add_argument(
        "--data",
        choices=["train", "val", "test"],
        required=True,
        help="Select the data type: train, validation (val), test",
    )
    parser.add_argument(
        "--num_beams", type=int, default=1, help="Number of beams, default is 1"
    )
    parser.add_argument(
        "--batch_size", type=int, default=8, help="Batch size, default is 8"
    )

    args = parser.parse_args()
    model_name = MODEL[args.model]
    data_split = args.data
    num_beams = args.num_beams
    batch_size = args.batch_size

    output_path = f"{data_split}_eval_{num_beams}beam_{args.model}.json"

    dataset = load_from_disk("./datasets/sql-create-context-split")
    data = dataset[data_split].take(2)
    tokenizer, model = get_tokenizer_model(model_name)

    generations = generate_sql_batch(
        data, tokenizer, model, num_beams=num_beams, batch_size=batch_size
    )
    output = data.add_column("generation", generations)
    output.to_json(output_path)
