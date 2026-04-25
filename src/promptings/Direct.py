# Copyright (c) 2024 Md. Ashraful Islam — Licensed under the MIT License. See LICENSE.

from .Base import BaseStrategy


class DirectStrategy(BaseStrategy):
    def run_single_pass(self, item: dict):
        processed_input = [
            {
                "role": "user",
                "content": f'{self.data.get_prompt(item)}\n\Generate {self.language} code to solve the above mentioned problem:',
            },
        ]
        return self.gpt_chat(processed_input=processed_input)
