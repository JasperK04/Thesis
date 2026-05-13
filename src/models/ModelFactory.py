# Copyright (c) 2026 Jasper Kleine — Licensed under the MIT License. See LICENSE-SECOND.
import re

from models.OpenAI import GPT4, GPT5
from models.Qwen import Qwen35, Qwen35_FineTuned


def normalize(model_name):
    return re.sub(r"[^a-zA-Z0-9]", "", model_name).lower()


class ModelFactory:
    @staticmethod
    def get_model_class(model_name):
        model = normalize(model_name)
        if model in ["qwen", "qwen35"]:
            return Qwen35
        elif model in ["qwenft", "qwenfinetuned", "qwen35finetuned"]:
            return Qwen35_FineTuned
        elif model in ["gpt5", "gpt54", "gpt54nano", "gpt5nano"]:
            return GPT5
        elif model in ["gpt4", "gpt41", "gpt41mini"]:
            return GPT4
        else:
            raise Exception(f"Unknown model name {model_name}")
