# Copyright (c) 2024 Md. Ashraful Islam — Licensed under the MIT License. See LICENSE.
# Copyright (c) 2026 Jasper Kleine — Licensed under the MIT License. See LICENSE SECOND.

import argparse
import os
from datetime import datetime

parser = argparse.ArgumentParser()

parser.add_argument(
    "--dataset",
    type=str,
    default="AoC",
    choices=[
        "AoC",
        "HumanEval",
        "MBPP",
        "APPS",
        "xCodeEval",
        "CC",
    ],
)
parser.add_argument(
    "--strategy",
    type=str,
    default="PACEcoding",
)
parser.add_argument(
    "--model",
    type=str,
    default="Qwen",
)

parser.add_argument("--temperature", type=float, default=0)
parser.add_argument("--pass_at_k", type=int, default=1)
parser.add_argument(
    "--language",
    type=str,
    default="Python3",
    choices=[
        "Python3",
    ],
)
parser.add_argument(
    "--local",
    "-l",
    action="store_true",
    help="Run code execution locally via subprocess instead of posting to an executor server",
)
parser.add_argument(
    "--start",
    type=int,
    default=0,
    help="Start index (0-based, inclusive) for dataset slicing",
)
parser.add_argument(
    "--end",
    type=int,
    default=float("inf"),
    help="End index (0-based, exclusive) for dataset slicing",
)

args = parser.parse_args()

# Respect the local execution flag as an environment variable before importing
if args.local:
    os.environ["EXECUTOR_LOCAL"] = "1"

# modules that may instantiate APICommunication at import time.
# Must be imported after setting the environment variable.
from challenge_datasets.DatasetFactory import DatasetFactory  # noqa: E402
from constants.paths import *  # noqa: F403,E402
from models.ModelFactory import ModelFactory  # noqa: E402
from promptings.PromptingFactory import PromptingFactory  # noqa: E402
from results.Results import Results  # noqa: E402

DATASET = args.dataset
STRATEGY = args.strategy
MODEL_NAME = args.model
TEMPERATURE = args.temperature
PASS_AT_K = args.pass_at_k
LANGUAGE = args.language
dataset = DatasetFactory.get_dataset_class(DATASET)()

start_idx = max(0, args.start)
end_idx = min(args.end, len(dataset))
num_total = len(dataset)
if end_idx is None or end_idx > num_total:
    end_idx = num_total
if end_idx < start_idx:
    raise ValueError(f"end-index ({end_idx}) must be >= start-index ({start_idx})")

range_suffix = ""
if start_idx != 0 or end_idx != num_total:
    range_suffix = f"-{start_idx}-{end_idx}"

RUN_NAME = f"{MODEL_NAME}-{STRATEGY}-{DATASET}-{LANGUAGE}-{TEMPERATURE}-{PASS_AT_K}{range_suffix}"
RESULTS_PATH = f"./outputs/{RUN_NAME}.jsonl"

print(
    f"#########################\nRunning start {RUN_NAME}, Time: {datetime.now()}\n##########################\n"
)

strategy = PromptingFactory.get_prompting_class(STRATEGY)(
    model=ModelFactory.get_model_class(MODEL_NAME)(temperature=TEMPERATURE),
    data=dataset,
    language=LANGUAGE,
    pass_at_k=PASS_AT_K,
    results=Results(RESULTS_PATH),
)

strategy.run(start_idx=start_idx, end_idx=end_idx)

print(
    f"#########################\nRunning end {RUN_NAME}, Time: {datetime.now()}\n##########################\n"
)
