# Copyright (c) 2024 Md. Ashraful Islam — Licensed under the MIT License. See LICENSE.
from constants.paths import XCODE_VALIDATION_DATA_PATH
from evaluations.evaluate import contest_evaluate_public_tests, xcode_evaluate

from .Dataset import Dataset


class XCodeDataset(Dataset):
    def __init__(
        self,
        path: str = XCODE_VALIDATION_DATA_PATH,
    ):
        super().__init__(path)
        self.id_key = "src_uid"

    def evaluate_sample_io(
        self,
        item: dict,
        cur_imp: str,
        language: str,
    ):
        sample_io = []

        for input, output in zip(item["sample_inputs"], item["sample_outputs"]):
            sample_io.append({"input": input, "output": [output]})

        return contest_evaluate_public_tests(
            generated_code=cur_imp, id=item[self.id_key], tests=sample_io, lang=language
        )

    def evaluate(
        self,
        item: dict,
        cur_imp: str,
        language: str,
    ):
        return xcode_evaluate(
            generated_code=cur_imp, src_uid=item["src_uid"], lang=language
        )

    @staticmethod
    def get_prompt(item):
        return f"Problem Description:\n{item['description']}\nInput Specification:\n{item['input_spec']}\nOutput Specification:\n{item['output_spec']}\nSample Inputs: {item['sample_inputs']}\nSample Outputs: {item['sample_outputs']}\nNote: {item['notes']}\nTake input from: {item['input_from']}\nGive output to: {item['output_to']}\nTime Limit: {item['time_limit']}\nMemory Limit: {item['memory_limit']}\n\nNote: If you are writing a function then after the function definition take input from using `input()` function, call the function with specified parameters and finally print the output of the function."
