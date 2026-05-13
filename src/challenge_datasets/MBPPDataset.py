# Copyright (c) 2024 Md. Ashraful Islam — Licensed under the MIT License. See LICENSE.
from constants.paths import MBPP_DATA_PATH
from evaluations.func_evaluate import evaluate_functional_correctness, evaluate_io

from .Dataset import Dataset


class MBPPDataset(Dataset):
    def __init__(
        self,
        path: str = MBPP_DATA_PATH,
    ):
        super().__init__(path)
        self.id_key = "name"

    def evaluate(
        self,
        item: dict,
        cur_imp: str,
        language: str,
    ):
        # result, _ = evaluate_io(item['test_list'],cur_imp,5,True)
        # return result
        return evaluate_functional_correctness(problem=item, completion=cur_imp)

    def evaluate_sample_io(
        self,
        item: dict,
        cur_imp: str,
        language: str,
    ):
        if "sample_io" not in item:
            return True, ""
        if len(item["sample_io"]) == 0:
            return True, ""
        status, test_log = evaluate_io(
            sample_io=item["sample_io"],
            completion=cur_imp,
        )
        return status == "passed", test_log

    @staticmethod
    def get_prompt(item):
        # function_signature = item['code'].split('\n')[0].strip()
        # return f"{item['text']}\nFunction Signature: {function_signature}"
        return item["prompt"]
