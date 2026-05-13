# Copyright (c) 2024 Md. Ashraful Islam — Licensed under the MIT License. See LICENSE.
from constants.paths import HUMAN_WST_DATA_PATH
from evaluations.func_evaluate import evaluate_functional_correctness, evaluate_io

from .Dataset import Dataset


class HumanDataset(Dataset):
    def __init__(
        self,
        path: str = HUMAN_WST_DATA_PATH,
    ):
        super().__init__(path)
        self.id_key = "task_id"

    def evaluate(
        self,
        item: dict,
        cur_imp: str,
        language: str,
    ):
        return evaluate_functional_correctness(problem=item, completion=cur_imp)

    def evaluate_sample_io(
        self,
        item: dict,
        cur_imp: str,
        language: str,
    ):
        status, test_log = evaluate_io(
            sample_io=item["sample_io"],
            completion=cur_imp,
        )
        return status == "passed", test_log, status

    @staticmethod
    def get_prompt(item):
        if "prompt" in item:
            return f"{item['prompt']}"
        elif "text" in item:
            return f"{item['text']}"
        else:
            raise Exception("No prompt or text in item")
