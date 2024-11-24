import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import wandb

# Initialize Weights & Biases
wandb.init(project="text2sql-finetuning", name="lora_text2sql")

# Model and LoRa setup
MODEL_NAME = "codellama/CodeLlama-7b-Instruct-hf"  # Change as needed
TOKENIZER_NAME = MODEL_NAME
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load dataset
dataset = {
    split: load_dataset("json", data_files=f"./datasets/sql-create-context-split/{split}.json")
    for split in ["train", "val", "test"]
}

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    torch_dtype=torch.float16,  # Use mixed precision
    device_map="auto"
)

# Prepare model for training with LoRa
config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj"],  # Update based on the model architecture
    bias="none",
    task_type="CAUSAL_LM"
)
model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, config)

# Preprocessing
def preprocess_function(examples):
    prompts = [
        f"""### Task
Generate a SQL query to answer [QUESTION]{q}[/QUESTION]

### Instructions
The SQL query should end with ";" and must not include any explanation.

### Database Schema
{m}

### Answer
Given the database schema, here is the SQL query that answers [QUESTION]{q}[/QUESTION]
[SQL]"""
        for q, m in zip(examples["question"], examples["context"])
    ]
    labels = [
        sql + ";" if not sql.endswith(";") else sql
        for sql in examples["answer"]
    ]
    tokenized_inputs = tokenizer(prompts, text_target=labels, truncation=True, max_length=512)
    return tokenized_inputs

tokenized_datasets = {
    split: dataset[split].map(preprocess_function, batched=True)
    for split in ["train", "val"]
}

# Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="steps",
    logging_strategy="steps",
    logging_steps=50,
    save_strategy="steps",
    save_steps=500,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    weight_decay=0.01,
    max_steps=2000,
    save_total_limit=2,
    fp16=True,
    push_to_hub=False,
    report_to="wandb"
)

# Metrics
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = torch.argmax(logits, dim=-1)
    labels = labels[:, 1:].contiguous()  # Shift labels
    predictions = predictions[:, :-1]  # Shift predictions
    decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    exact_matches = sum(p == l for p, l in zip(decoded_preds, decoded_labels)) / len(decoded_labels)
    return {"exact_match": exact_matches}

# Trainer setup
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["val"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

# Train
trainer.train()

# Evaluate
results = trainer.evaluate()

# Log results
wandb.log(results)

# Save the model and tokenizer
model.save_pretrained("./finetuned_model")
tokenizer.save_pretrained("./finetuned_model")

# Finish Weights & Biases logging
wandb.finish()
