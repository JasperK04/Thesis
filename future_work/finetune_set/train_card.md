# Dataset Card train.jsonl

## Original Dataset

This dataset is derived from a raw corpus of Advent of Code solutions created by **Joris van Bruggen**. The original dataset contains Python solutions collected from public repositories associated with participants of Advent of Code.

The original dataset includes:

* source code solutions,
* repository metadata,
* author metadata,
* file path information.

The exact collection methodology of the original dataset is not fully documented in this dataset card because the raw dataset was externally provided.

---

## Transformation Process

This dataset extends the original solutions dataset by transforming raw code solutions into instruction-tuning examples suitable for supervised fine-tuning of language models.

The transformation pipeline:

1. pairs solutions with Advent of Code problem statements,
2. formats samples into chat-style instruction–response pairs,
3. heuristically classifies solutions by puzzle part,
4. filters incomplete or ambiguous entries,
5. exports the resulting dataset in JSONL format.

The transformation process is implemented in `augment.py`. 

---

# Dataset Construction

## Prompt Generation

Each prompt is constructed by:

* prepending an efficiency-oriented instruction,
* appending the corresponding Advent of Code problem description,
* formatting the sample using chat-style tokens.

The instruction prefix used during augmentation is:

> “Solve this Advent of Code problem in Python using a computationally efficient and scalable approach.” 

---

# Solution Classification

Solutions are heuristically classified into:

* `part1` - The first problem of the day in the AoC dataset
* `part2` - The Second problem of the day in the AoC dataset
* `combined` - Both solutions are in the same file, append part 2 as the problem to solve
* `unknown` - Could not infer what part the solution is, these are discarded

The classification pipeline uses:

* explicit part markers in source code,
* multiple solver invocation detection,
* print statement analysis,
* filename pattern matching. 

---

# Filtering

The transformation pipeline excludes:

* malformed entries,
* unclassified solutions,
* entries without matching problem statements,
* solutions from years prior to 2021. 

The script notes that filtering older years is intended to mitigate potential benchmark leakage, as the finetuned model will be tested on the earlier year problems. 

