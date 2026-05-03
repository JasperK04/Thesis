import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

print("CUDA available:", torch.cuda.is_available())
print("Device:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")

if not torch.cuda.is_available():
    raise SystemError("GPU is not available")

model_name = "Qwen/Qwen3.5-9B"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float16).to("cuda")


def run_prompt(prompt, description):
    print("\n" + "=" * 60)
    print(description)
    print("=" * 60)

    messages = [{"role": "user", "content": prompt}]

    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    inputs = tokenizer(text, return_tensors="pt").to("cuda")

    outputs = model.generate(
        **inputs, do_sample=True, temperature=0.7, eos_token_id=tokenizer.eos_token_id
    )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(result)


# ---- TEST CASES ----

# 1. Simple instruction
run_prompt("Write an efficient Python sorting algorithm.", "TEST 1: Simple instruction")

# 2. Strong instruction forcing structure
run_prompt(
    "Write a complete answer. Include explanation and Python code for a stable O(n log n) sorting algorithm.",
    "TEST 2: Explicit structured instruction",
)

# 3. With misleading prior text (tests completion behavior)
run_prompt(
    """One efficient algorithm is Merge Sort. It works by dividing the array.
Continue the explanation.""",
    "TEST 3: Completion-style prompt (should continue text)",
)

# 4. Explicit override of completion behavior
run_prompt(
    """Ignore any partial text. Write a completely new answer from scratch.
Provide a stable, in-place O(n log n) sorting algorithm with explanation and Python code.""",
    "TEST 4: Forced instruction override",
)

# 5. System-style behavior simulation
messages = [
    {
        "role": "system",
        "content": "You are a precise computer science assistant. Always give complete structured answers.",
    },
    {
        "role": "user",
        "content": "Give a Python implementation of an efficient sorting algorithm.",
    },
]

text = tokenizer.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)

inputs = tokenizer(text, return_tensors="pt").to("cuda")

outputs = model.generate(
    **inputs, do_sample=True, temperature=0.7, eos_token_id=tokenizer.eos_token_id
)

print("\n" + "=" * 60)
print("TEST 5: With system prompt")
print("=" * 60)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
