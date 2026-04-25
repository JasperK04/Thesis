# Copyright (c) 2024 Md. Ashraful Islam — Licensed under the MIT License. See LICENSE.
from datasets.AoCDataset import AoCDataset
from datasets.APPSDataset import APPSDataset
from datasets.CodeContestDataset import CodeContestDataset
from datasets.Dataset import Dataset
from datasets.HumanEvalDataset import HumanDataset
from datasets.MBPPDataset import MBPPDataset
from datasets.XCodeDataset import XCodeDataset


class DatasetFactory:
    @staticmethod
    def get_dataset_class(dataset_name):
        if dataset_name == "AoC":
            return AoCDataset
        elif dataset_name == "APPS":
            return APPSDataset
        elif dataset_name == "MBPP":
            return MBPPDataset
        elif dataset_name == "XCode":
            return XCodeDataset
        elif dataset_name == "HumanEval":
            return HumanDataset
        elif dataset_name == "Human":
            return HumanDataset
        elif dataset_name == "CC":
            return CodeContestDataset
        else:
            raise Exception(f"Unknown dataset name {dataset_name}")
