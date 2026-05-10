# Copyright (c) 2026 Jasper Kleine — Licensed under the MIT License. See LICENSE SECOND.
import os
import re

import dotenv
import torch
from lxml import etree  # type: ignore
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
        max_new_tokens: int = 8192,
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
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            trust_remote_code=trust_remote_code,
            dtype=torch.float16,
        )

    @staticmethod
    def remove_think_blocks(text: str) -> str:
        open_count = len(re.findall(r"<think>", text))
        close_count = len(re.findall(r"</think>", text))

        if open_count != close_count:
            # print(
            #     f"Warning: Unmatched <think> tags detected. Open: {open_count}, Close: {close_count}",
            #     file=sys.stderr,
            # ) # apparently this is normal in Qwen outputs
            if open_count > close_count:
                text += "</think>" * (open_count - close_count)
            else:
                text = ("<think>" * (close_count - open_count)) + text

        wrapped = f"<root>{text}</root>"

        try:
            root = etree.fromstring(wrapped)

            for think in root.xpath(".//think"):
                think.getparent().remove(think)

            cleaned = "".join(root.itertext()).strip()

        except etree.XMLSyntaxError:
            cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

            cleaned = re.sub(r"<think>.*$", "", cleaned, flags=re.DOTALL)

            if "</think>" in cleaned:
                thinking, cleaned = cleaned.split("</think>", 1)

            cleaned = cleaned.strip()

        return cleaned

    def prompt(self, processed_input: list[dict]):
        """Generate a reply for the assistant and return only the assistant text.

        Args:
            processed_input: list of {'role': ..., 'content': ...}

        Returns:
            str: assistant generated text (no prompt included)
        """
        # Build the chat-style prompt using the tokenizer helper
        processed_input[0]["content"] += (
            "\n\nPut your thinking process in <think>...</think> blocks."
        )
        prompt = self.tokenizer.apply_chat_template(
            processed_input, tokenize=False, add_generation_prompt=True
        )

        # Tokenize into tensors and move to CUDA
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        outputs = self.model.generate(  # type: ignore
            **inputs,
            max_new_tokens=int(self.max_new_tokens),
            do_sample=True,
            temperature=self.model_params.get("temperature", 0.32),
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        output_ids = outputs[0]
        prompt_tokens = int(inputs["input_ids"].shape[-1])
        completion_tokens = int(max(output_ids.shape[-1] - prompt_tokens, 0))

        # Return only the generated tokens to avoid echoing the prompt.
        generated_ids = output_ids[prompt_tokens:]
        decoded = self.tokenizer.decode(generated_ids, skip_special_tokens=True)

        # Remove any <think>...</think> blocks from the returned text.
        decoded = self.remove_think_blocks(decoded)

        return (decoded, prompt_tokens, completion_tokens)


class Qwen35(QwenLocal):
    def __init__(self, **kwargs):
        model_name = "Qwen/Qwen3.5-9B"  # 9B params
        super().__init__(model_name=model_name, **kwargs)


class Qwen3_Coder(QwenLocal):
    def __init__(self, **kwargs):
        raise NotImplementedError("Qwen3-Coder is much bigger and not tested yet")
        model_name = "Qwen/Qwen3-Coder-30B-A3B-Instruct"  # 30B params
        super().__init__(model_name=model_name, **kwargs)


class Qwen35_FineTuned(QwenLocal):
    def __init__(self, **kwargs):
        raise NotImplementedError("Qwen3.5_FineTuned is not implemented yet")
        model_name = "jasperK04/Qwen3.5-Finetuned-AoC"  # 9B params
        super().__init__(model_name=model_name, **kwargs)
