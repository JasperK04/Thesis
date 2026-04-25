# Copyright (c) 2026 Jasper Kleine — Licensed under the MIT License. See LICENSE SECOND.
import os

import dotenv
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from utils.token_count import token_count

from .Base import BaseModel

dotenv.load_dotenv()


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
        max_new_tokens: int = 512,
        trust_remote_code: bool = True,
        **kwargs,
    ):
        model_name = model_name or os.getenv(
            "QWEN_LOCAL_MODEL", "Qwen/Qwen2.5-7B-Instruct"
        )
        super().__init__(model_name=model_name, **kwargs)
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.max_new_tokens = max_new_tokens

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, trust_remote_code=trust_remote_code
        )

        if "cuda" in self.device:
            # Let HF auto-place model across available GPUs
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name, trust_remote_code=trust_remote_code, device_map="auto"
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name, trust_remote_code=trust_remote_code
            )
            self.model.to(torch.device(self.device))

    def prompt(self, processed_input: list[dict]):
        """Generate a reply for the assistant and return only the assistant text.

        Args:
            processed_input: list of {'role': ..., 'content': ...}

        Returns:
            str: assistant generated text (no prompt included)
        """
        # Build the chat-style prompt using the tokenizer helper
        prompt = self.tokenizer.apply_chat_template(processed_input)

        # Tokenize into tensors
        inputs = self.tokenizer(prompt, return_tensors="pt")

        # Move tensors to model device
        model_device = next(self.model.parameters()).device
        input_ids = inputs["input_ids"].to(model_device)
        attention_mask = inputs.get("attention_mask")
        if attention_mask is not None:
            attention_mask = attention_mask.to(model_device)

        # Generation kwargs
        gen_kwargs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "max_new_tokens": int(self.max_new_tokens),
            "do_sample": False,
            "temperature": float(self.model_params.get("temperature", 0.0)),
            "top_p": float(self.model_params.get("top_p", 0.95)),
            "eos_token_id": self.tokenizer.eos_token_id,
            "pad_token_id": self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
        }

        # Remove None values to avoid HF errors
        gen_kwargs = {k: v for k, v in gen_kwargs.items() if v is not None}

        outputs = self.model.generate(**gen_kwargs)

        # outputs is (batch, seq_len); take first sequence
        output_ids = outputs[0]

        # Extract generated tokens (exclude the input prompt tokens)
        gen_tokens = output_ids[input_ids.shape[-1] :]

        assistant_text = self.tokenizer.decode(gen_tokens, skip_special_tokens=True)

        return assistant_text


class Qwen36(QwenLocal):
    def __init__(self, model_name: str | None = None, **kwargs):
        model_name = model_name or os.getenv("QWEN36_MODEL", "Qwen/Qwen36-Instruct")
        super().__init__(model_name=model_name, **kwargs)


class Qwen36_Coder(QwenLocal):
    def __init__(self, model_name: str | None = None, **kwargs):
        model_name = model_name or os.getenv(
            "QWEN36_CODER_MODEL", "Qwen/Qwen36-Coder-Instruct"
        )
        super().__init__(model_name=model_name, **kwargs)


class Qwen36_FineTuned(QwenLocal):
    def __init__(self, model_name: str | None = None, **kwargs):
        model_name = model_name or os.getenv(
            "QWEN36_FINETUNED_MODEL", "Qwen/Qwen36-Finetuned-Instruct"
        )
        super().__init__(model_name=model_name, **kwargs)
