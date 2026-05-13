# Copyright (c) 2024 Md. Ashraful Islam — Licensed under the MIT License. See LICENSE.
import re

from promptings import (
    DirectStrategy,
    MapCoder,
    PACEcoding,
)


def normalize(prompting_name):
    return re.sub(r"[^a-zA-Z0-9]", "", prompting_name).lower()


class PromptingFactory:
    @staticmethod
    def get_prompting_class(prompting_name):
        prompting = normalize(prompting_name)
        if prompting in ["pacecoding", "pace"]:
            return PACEcoding
        elif prompting in ["mapcoder", "map"]:
            return MapCoder
        elif prompting in ["direct"]:
            return DirectStrategy
        else:
            raise Exception(f"Unknown prompting name {prompting_name}")
