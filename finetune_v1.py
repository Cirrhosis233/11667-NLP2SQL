import os
import sys
import logging
from typing import List, Union
import torch
from dataclasses import dataclass, field
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    HfArgumentParser,
    BitsAndBytesConfig,
)
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_from_disk, disable_caching

disable_caching()

#! Wandb Project Name
os.environ["WANDB_PROJECT"] = "Text2SQL"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if len(sys.argv) == 1:
    raise ValueError("Missing configuration file.")

config_file = sys.argv[1]


@dataclass
class ModelConfig:
    model: str = field(default="codellama/CodeLlama-7b-Instruct-hf")
    dataset: str = field(default="./datasets/sql-create-context-split")
    prompt: str = field(default="./prompts/prompt_v2_train.md")
    max_seq_length: int = field(default=1024)
    bits: int = field(default=4)
    bnb_4bit_quant_type: str = field(default="nf4")
    r: int = field(default=16)
    lora_alpha: int = field(default=32)
    lora_dropout: float = field(default=0.1)
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])
    bias: str = field(default="none")
    init_lora_weights: Union[bool, str] = field(default=True)
    task_type: str = field(default="CAUSAL_LM")


def prepare_dataset_for_training(dataset, tokenizer):
    def preprocess_function(sample):
        sample["text"] += tokenizer.eos_token
        return sample

    train_dataset = dataset.map(preprocess_function)
    return train_dataset


if __name__ == "__main__":
    parser = HfArgumentParser((ModelConfig, TrainingArguments))
    model_config, training_args = parser.parse_json_file(json_file=config_file)
    torch_dtype = (
        torch.float16
        if training_args.fp16
        else (torch.bfloat16 if training_args.bf16 else torch.float32)
    )

    tokenizer = AutoTokenizer.from_pretrained(model_config.model)
    if not tokenizer.pad_token:
        # tokenizer.add_special_tokens({"pad_token": "<|pad|>"})
        tokenizer.pad_token = tokenizer.eos_token
    print(tokenizer.special_tokens_map)

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
        attn_implementation="flash_attention_2",
    )
    # model.resize_token_embeddings(len(tokenizer))
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
        # modules_to_save=["lm_head", "embed_tokens"],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    dataset = load_from_disk(model_config.dataset)["train"]
    dataset = prepare_dataset_for_training(dataset, tokenizer=tokenizer)

    response_template = "\n[SQL]"
    #! BUG: https://github.com/huggingface/trl/issues/598
    response_template_ids = tokenizer.encode(
        response_template, add_special_tokens=False
    )[1:]
    data_collator = DataCollatorForCompletionOnlyLM(
        response_template_ids, tokenizer=tokenizer, mlm=False
    )
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=data_collator,
        max_seq_length=model_config.max_seq_length,
    )

    trainer.train()
    trainer.save_model(training_args.output_dir)
