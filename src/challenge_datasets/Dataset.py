# Copyright (c) 2024 Md. Ashraful Islam — Licensed under the MIT License. See LICENSE.
from abc import ABC, abstractmethod

from utils.jsonl import read_jsonl


class Dataset(ABC):
    def __init__(
        self,
        path: str,
    ):
        self.path = path
        self.data = None
        self.id_key = ""
        self.load()

    def load(self):
        self.data = read_jsonl(self.path)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

    def evaluate(
        self,
        item: dict,
        cur_imp: str,
        language: str,
    ):
        raise NotImplementedError

    @staticmethod
    def get_prompt(item):
        raise NotImplementedError

    @abstractmethod
    def evaluate_sample_io(self, item, code, language) -> tuple[bool, str, str]:
        """Evaluate the generated code on sample input/output pairs.
        Returns a tuple of (passed: bool, feedback: str, reason: str)."""
        pass
