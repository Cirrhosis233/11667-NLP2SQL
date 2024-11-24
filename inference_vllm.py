from vllm import LLM, SamplingParams
import argparse

# from tqdm import tqdm
from datasets import load_from_disk

MODEL = {
    "sqlcoder": "defog/sqlcoder-7b-2",
    "codellama": "codellama/CodeLlama-7b-Instruct-hf",
    "deepseek": "deepseek-ai/deepseek-coder-7b-instruct-v1.5",
}


def make_prompts(dataset, prompt_file="prompt.md"):
    with open(prompt_file, "r") as f:
        prompt = f.read()

    prompt_batch = [
        prompt.format(user_question=q, table_metadata_string=m)
        for q, m in zip(dataset["question"], dataset["context"])
    ]

    return prompt_batch


def generate_sql_vllm(dataset, model_name):
    llm = LLM(model_name, max_model_len=1024)
    sampling_params = SamplingParams(
        n=1,
        temperature=0.0,
        top_p=1.0,
        max_tokens=300,
    )

    generations = []

    prompts = make_prompts(dataset)

    outputs = llm.generate(prompts, sampling_params)

    for output in outputs:
        generated_query = output.outputs[0].text.split(";")[0].split("```")[0].strip()
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
        choices=["train", "val", "test"],
        required=True,
        help="Select the data type: train, validation (val), test",
    )

    args = parser.parse_args()
    model_name = MODEL[args.model]
    data_split = args.data

    output_path = f"{data_split}_eval_{args.model}.json"

    dataset = load_from_disk("./datasets/sql-create-context-split")
    data = dataset[data_split]

    generations = generate_sql_vllm(data, model_name)
    output = data.add_column("generation", generations)
    output.to_json(output_path)
