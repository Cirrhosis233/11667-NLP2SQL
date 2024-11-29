import sys
import logging
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    HfArgumentParser,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_from_disk
from dataclasses import dataclass, field
from typing import List, Union

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if len(sys.argv) == 1:
    raise ValueError("Missing configuration file.")

config_file = sys.argv[1]


@dataclass
class ModelConfig:
    model: str = field(default="codellama/CodeLlama-7b-Instruct-hf")
    dataset: str = field(default="./datasets/sql-create-context-split")
    prompt: str = field(default="./prompts/prompt_v2.md")
    seq_len: int = field(default=1024)
    bits: int = field(default=4)
    bnb_4bit_quant_type: str = field(default="nf4")
    r: int = field(default=16)
    lora_alpha: int = field(default=32)
    lora_dropout: float = field(default=0.1)
    target_modules: Union[List[str], str] = field(default_factory=lambda: ["q_proj", "v_proj"])
    bias: str = field(default="none")
    init_lora_weights: Union[bool, str] = field(default=True)
    task_type: str = field(default="CAUSAL_LM")


def prepare_dataset_for_training(dataset, tokenizer, seq_len, prompt_file):
    if not tokenizer.pad_token:
        tokenizer.pad_token = tokenizer.eos_token
    with open(prompt_file, "r") as f:
        prompt = f.read()
    columns = dataset["train"].features.keys()

    def preprocess_function(examples):
        prompts = [
            prompt.format(user_question=q, table_metadata_string=m)
            for q, m in zip(examples["question"], examples["context"])
        ]

        answers = [a if a.endswith(";") else a + ";" for a in examples["answer"]]

        model_inputs = tokenizer(
            prompts,
            truncation=True,
            max_length=seq_len,
            padding="max_length",
            add_special_tokens=True,
        )
        labels = tokenizer(
            answers,
            truncation=True,
            max_length=seq_len,
            padding="max_length",
            add_special_tokens=True,
        )
        labels["input_ids"] = [
            [-100 if token == tokenizer.pad_token_id else token for token in label]
            for label in labels["input_ids"]
        ]

        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    tokenized_dataset = dataset.map(
        preprocess_function,
        batched=True,
        remove_columns=columns,
    )
    return tokenized_dataset


if __name__ == "__main__":
    parser = HfArgumentParser((ModelConfig, TrainingArguments))
    model_config, training_args = parser.parse_json_file(json_file=config_file)
    torch_dtype = (
        torch.float16
        if training_args.fp16
        else (torch.bfloat16 if training_args.bf16 else torch.float32)
    )

    tokenizer = AutoTokenizer.from_pretrained(model_config.model)

    model = AutoModelForCausalLM.from_pretrained(
        model_config.model,
        device_map="auto",
        quantization_config=BitsAndBytesConfig(
            load_in_8bit=model_config.bits == 8,
            load_in_4bit=model_config.bits == 4,
            bnb_4bit_compute_dtype=torch_dtype,
            bnb_4bit_quant_type=model_config.bnb_4bit_quant_type,
        ),
        torch_dtype=torch_dtype,
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(
        model, use_gradient_checkpointing=training_args.gradient_checkpointing
    )
    lora_config = LoraConfig(
        r=model_config.r,
        lora_alpha=model_config.lora_alpha,
        target_modules=model_config.target_modules,
        lora_dropout=model_config.lora_dropout,
        bias=model_config.bias,
        init_lora_weights=model_config.init_lora_weights,
        task_type=model_config.task_type,
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    dataset = load_from_disk(model_config.dataset)
    dataset = prepare_dataset_for_training(
        dataset,
        tokenizer,
        seq_len=model_config.seq_len,
        prompt_file=model_config.prompt,
    )

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["val"],
        data_collator=data_collator,
    )

    trainer.train()
    trainer.save_model(training_args.output_dir)
