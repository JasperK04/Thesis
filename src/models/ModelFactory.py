# Copyright (c) 2024 Md. Ashraful Islam — Licensed under the MIT License. See LICENSE.
from models.Gemini import Gemini
from models.OpenAI import GPT4, ChatGPT
from models.Qwen import Qwen3_Coder, Qwen36, Qwen36_FineTuned


class ModelFactory:
    @staticmethod
    def get_model_class(model_name):
        if model_name == "Qwen":
            return Qwen36
        elif model_name == "QwenCoder":
            return Qwen3_Coder
        elif model_name == "QwenFineTuned":
            return Qwen36_FineTuned
        elif model_name == "Gemini":
            return Gemini
        elif model_name == "ChatGPT":
            return ChatGPT
        elif model_name == "GPT4":
            return GPT4
        else:
            raise Exception(f"Unknown model name {model_name}")
