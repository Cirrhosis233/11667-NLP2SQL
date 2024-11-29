import os
import argparse
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest
from transformers import AutoTokenizer
from datasets import load_from_disk

MODEL = {
    "sqlcoder": "defog/sqlcoder-7b-2",
    "codellama": "codellama/CodeLlama-7b-Instruct-hf",
    "deepseek": "deepseek-ai/deepseek-coder-7b-instruct-v1.5",
}

model_max_tokens = 2048
generation_token_budget = 512  # Tokens to reserve for generation
prompt_budget = model_max_tokens - generation_token_budget


def truncate_prompt(prompt, tokenizer, max_tokens):
    tokenized_prompt = tokenizer.encode(prompt)
    if len(tokenized_prompt) > max_tokens:
        tokenized_prompt = tokenized_prompt[:max_tokens]
    return tokenizer.decode(tokenized_prompt)


def make_prompts(dataset, tokenizer, prompt_file):
    with open(prompt_file, "r") as f:
        prompt = f.read()

    prompt_batch = [
        truncate_prompt(prompt.format(user_question=q, table_metadata_string=m), tokenizer, prompt_budget)
        for q, m in zip(dataset["question"], dataset["context"])
    ]

    return prompt_batch


def generate_sql_vllm(dataset, model_name, prompt_file, lora_path=None):
    if lora_path:
        llm = LLM(
            model_name,
            max_model_len=model_max_tokens,
            enable_lora=True,
            max_lora_rank=128,
        )
    else:
        llm = LLM(model_name, max_model_len=model_max_tokens)

    sampling_params = SamplingParams(
        n=1,
        temperature=0.0,
        top_p=1.0,
        max_tokens=generation_token_budget,
    )

    generations = []
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if not tokenizer.pad_token:
        tokenizer.pad_token = tokenizer.eos_token
    prompts = make_prompts(dataset, tokenizer, prompt_file)
    del tokenizer

    if lora_path:
        outputs = llm.generate(
            prompts,
            sampling_params,
            lora_request=LoRARequest("sql_adapter", 1, lora_path),
        )
    else:
        outputs = llm.generate(prompts, sampling_params)

    for output in outputs:
        generated_query = output.outputs[0].text.split(";")[0].split("```")[0].strip()
        # generated_query = output.split("[SQL]")[-1].split(";")[0].strip()
        generations.append(generated_query)

    return generations


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Argument parser for model evaluation")

    parser.add_argument(
        "--model",
        choices=["sqlcoder", "codellama", "deepseek"],
        required=True,
        help="Select the model: sqlcoder, CodeLlama (codellama), deepseek-coder (deepseek)",
    )
    parser.add_argument(
        "--data",
        required=True,
        help="Select the data type: train, validation (val), test, eval",
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Prompt Path",
    )
    parser.add_argument(
        "--output",
        required=False,
        default=".",
        help="Output Path",
    )
    parser.add_argument(
        "--lora",
        required=False,
        default=None,
        help="Lora Adapter Path",
    )

    args = parser.parse_args()
    model_name = MODEL[args.model]
    data_split = args.data
    prompt_file = args.prompt
    lora_path = args.lora
    os.makedirs(args.output, exist_ok=True)
    output_path = os.path.join(args.output, f"{data_split}_{args.model}_inference.json")

    dataset = load_from_disk("./datasets/sql-create-context-split")
    data = dataset[data_split]

    generations = generate_sql_vllm(data, model_name, prompt_file, lora_path=lora_path)
    output = data.add_column("generation", generations)
    output.to_json(output_path)
