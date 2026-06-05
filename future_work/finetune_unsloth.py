import unsloth  # noqa: F401
from datasets import load_dataset
from transformers import TrainingArguments
from trl import SFTTrainer
from unsloth import FastLanguageModel

MODEL_NAME = "Qwen/Qwen3.5-9B"

MAX_SEQ_LENGTH = 4096

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,  # type: ignore
    bias="none",
    target_modules=[
        "q_proj",
        "v_proj",
    ],
    use_gradient_checkpointing="unsloth",  # type: ignore
)

dataset = load_dataset(
    "json",
    data_files={"train": "finetune_set/train.jsonl"},
)["train"]

dataset = dataset.train_test_split(test_size=0.05)

train_dataset = dataset["train"]
eval_dataset = dataset["test"]

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    packing=True,
    args=TrainingArguments(
        output_dir="./qwen3.5-finetune",
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=16,
        num_train_epochs=12,
        learning_rate=2e-5,
        warmup_steps=100,
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=200,
        save_steps=200,
        save_total_limit=3,
        load_best_model_at_end=True,
        bf16=True,
        bf16_full_eval=True,
        tf32=True,
        optim="paged_adamw_8bit",
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        prediction_loss_only=True,
    ),
)

trainer.train()

model.save_pretrained("./JasperK04/Qwen3.5-Finetuned-AoC")
tokenizer.save_pretrained("./JasperK04/Qwen3.5-Finetuned-AoC")
