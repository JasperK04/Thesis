import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback,
    Trainer,
    TrainingArguments,
)

model_name = "Qwen/Qwen3.6-27B"

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

model = AutoModelForCausalLM.from_pretrained(
    model_name, device_map="auto", dtype=torch.bfloat16
)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)

dataset = load_dataset("json", data_files={"train": "finetune_set/train.jsonl"})

dataset = dataset["train"].train_test_split(test_size=0.05)

train_dataset = dataset["train"]
eval_dataset = dataset["test"]


def tokenize(example):
    return tokenizer(example["text"], truncation=True, max_length=8192)


train_dataset = train_dataset.map(tokenize, batched=True, remove_columns=["text"])
eval_dataset = eval_dataset.map(tokenize, batched=True, remove_columns=["text"])

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

training_args = TrainingArguments(
    output_dir="./qwen3.6-finetune",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    num_train_epochs=10,
    eval_strategy="steps",
    eval_steps=200,
    logging_steps=10,
    save_steps=200,
    bf16=True,
    optim="adamw_torch",
    learning_rate=2e-5,
    warmup_steps=100,
    save_total_limit=2,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=data_collator,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
)

trainer.train()

model.save_pretrained("./JasperK04/Qwen3.6-Finetuned-AoC")
tokenizer.save_pretrained("./JasperK04/Qwen3.6-Finetuned-AoC")
