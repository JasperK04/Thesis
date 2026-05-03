# Copyright (c) 2026 Jasper Kleine — Licensed under the MIT License. See LICENSE SECOND.
import os

import dotenv
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .Base import BaseModel

dotenv.load_dotenv()

if __name__ == "__main__":
    print("CUDA available:", torch.cuda.is_available())
    print(
        "Device:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    )


class QwenBaseModel(BaseModel):
    """Minimal base model for local Qwen implementations.

    Stores common model parameters used by local HF-backed models.
    """

    def __init__(
        self,
        model_name: str | None = None,
        temperature: float = 0.32,
        top_p: float = 0.95,
        max_tokens: int | None = None,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
        **kwargs,
    ):
        self.model_params = {}
        self.model_params["model"] = model_name
        self.model_params["temperature"] = temperature
        self.model_params["top_p"] = top_p
        self.model_params["max_tokens"] = max_tokens
        self.model_params["frequency_penalty"] = frequency_penalty
        self.model_params["presence_penalty"] = presence_penalty


class QwenLocal(QwenBaseModel):
    """Local Qwen interface using Hugging Face Transformers.

    - Uses `tokenizer.apply_chat_template(...)` to build the prompt from messages.
    - Calls `model.generate(...)` and returns only the assistant's generated text.

    The `prompt` method accepts `processed_input` as a list of messages where each
    message is a dict with `role` and `content` keys.
    """

    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
        max_new_tokens: int = 4096,  # 8192
        trust_remote_code: bool = True,
        **kwargs,
    ):
        if not torch.cuda.is_available():
            raise SystemError("GPU is not available")
        if not model_name:
            raise ValueError("model_name must be set")
        super().__init__(model_name=model_name, **kwargs)
        expanded_model_name = os.path.expanduser(model_name)
        if os.path.exists(expanded_model_name):
            self.model_name = expanded_model_name
        else:
            self.model_name = model_name
        self.device = device or "cuda"
        self.max_new_tokens = max_new_tokens

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, trust_remote_code=trust_remote_code
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            trust_remote_code=trust_remote_code,
            dtype=torch.float16,
        )

    def prompt(self, processed_input: list[dict]):
        """Generate a reply for the assistant and return only the assistant text.

        Args:
            processed_input: list of {'role': ..., 'content': ...}

        Returns:
            str: assistant generated text (no prompt included)
        """
        # Build the chat-style prompt using the tokenizer helper
        prompt = self.tokenizer.apply_chat_template(
            processed_input, tokenize=False, add_generation_prompt=True
        )

        # Tokenize into tensors and move to CUDA
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=int(self.max_new_tokens),
            do_sample=True,
            temperature=self.model_params.get("temperature", 0.32),
            eos_token_id=self.tokenizer.eos_token_id,
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


class Qwen36(QwenLocal):
    def __init__(self, **kwargs):
        model_name = "Qwen/Qwen3.6-27B"  # 27B params
        super().__init__(model_name=model_name, **kwargs)


class Qwen3_Coder(QwenLocal):
    def __init__(self, **kwargs):
        model_name = "Qwen/Qwen3-Coder-30B-A3B-Instruct"  # 31B params
        super().__init__(model_name=model_name, **kwargs)


class Qwen36_FineTuned(QwenLocal):
    def __init__(self, **kwargs):
        raise NotImplementedError("Qwen3.6_FineTuned is not implemented yet")
        model_name = "jasperK04/Qwen3.6-Finetuned-AoC"  # 27B params
        super().__init__(model_name=model_name, **kwargs)
