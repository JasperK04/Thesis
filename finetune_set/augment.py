import ast
import json
import re
from pathlib import Path

CODE_DATASET = Path("raw_solutions.jsonl")
AOC_DATASET = Path("../data/AoC/aoc.jsonl")
OUTPUT_FILE = Path("train.jsonl")

EFFICIENCY_INSTRUCTION = (
    "Solve this Advent of Code problem in Python using a "
    "computationally efficient and scalable approach. "
    "Avoid unnecessary brute force solutions.\n\n"
)


def load_aoc_problems():
    problems = {}

    with open(AOC_DATASET, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            entry = json.loads(line)

            year, day, part = entry["id"].split("_")

            problems[(year, day, part)] = entry

    return problems


def build_prompt(problem_description):
    augmented_problem = EFFICIENCY_INSTRUCTION + problem_description

    return f"<|im_start|>user\n{augmented_problem}\n<|im_end|>\n<|im_start|>assistant\n"


def has_explicit_part_markers(code):
    lowered = code.lower()

    return ("part 1" in lowered and "part 2" in lowered) or (
        "part1" in lowered and "part2" in lowered
    )


def count_top_level_prints(code):
    try:
        tree = ast.parse(code)
    except Exception:
        return 0

    count = 0

    for node in tree.body:
        if isinstance(node, ast.Expr):
            value = node.value

            if isinstance(value, ast.Call):
                if isinstance(value.func, ast.Name):
                    if value.func.id == "print":
                        count += 1

    return count


def has_multiple_solver_invocations(code):
    try:
        tree = ast.parse(code)
    except Exception:
        return False

    calls = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                name = node.func.id

                args = []

                for arg in node.args:
                    if isinstance(arg, ast.Constant):
                        args.append(repr(arg.value))
                    else:
                        args.append(ast.dump(arg))

                args = tuple(args)

                calls.setdefault(name, set()).add(args)

    for name, variants in calls.items():
        if len(variants) >= 2:
            return True

    return False


def filename_indicates_part(path):
    lowered = path.lower()

    part2_patterns = [
        r"sol2",
        r"part2",
        r"[-_]2\.py$",
        r"/2\.py$",
        r"day[-_]\d+[-_]2",
    ]

    for pattern in part2_patterns:
        if re.search(pattern, lowered):
            return "2"

    part1_patterns = [
        r"sol1",
        r"part1",
        r"[-_]1\.py$",
        r"/1\.py$",
        r"day[-_]\d+[-_]1",
    ]

    for pattern in part1_patterns:
        if re.search(pattern, lowered):
            return "1"

    return None


def classify_solution(entry):
    code = entry["code"]
    path = entry["path"]

    explicit_markers = has_explicit_part_markers(code)
    multiple_invocations = has_multiple_solver_invocations(code)
    multiple_prints = count_top_level_prints(code) >= 2

    if explicit_markers:
        return "combined"

    if multiple_invocations:
        return "combined"

    if multiple_prints:
        return "combined"

    filename_part = filename_indicates_part(path)

    if filename_part == "2":
        return "part2"

    if filename_part == "1":
        return "part1"

    return "unknown"


def determine_part(classification):
    if classification == "part1":
        return "1"

    if classification in ["part2", "combined"]:
        return "2"

    return None


def main():
    problems = load_aoc_problems()

    written = 0
    skipped = 0

    stats = {
        "part1": 0,
        "part2": 0,
        "combined": 0,
        "unknown": 0,
    }

    with (
        open(CODE_DATASET, "r", encoding="utf-8") as infile,
        open(OUTPUT_FILE, "w", encoding="utf-8") as outfile,
    ):
        for line in infile:
            if not line.strip():
                continue

            try:
                entry = json.loads(line)
            except Exception:
                skipped += 1
                continue

            classification = classify_solution(entry)

            stats[classification] += 1

            if classification == "unknown":
                skipped += 1
                continue

            year = str(entry["year"])
            day = f"{int(entry['day']):02d}"

            part = determine_part(classification)

            if part is None:
                skipped += 1
                continue

            key = (year, day, part)

            if key not in problems:
                skipped += 1
                continue

            problem = problems[key]

            prompt = build_prompt(problem["description"])

            full_text = prompt + entry["code"] + "\n<|im_end|>"

            output_entry = {
                "text": full_text,
                "metadata": {
                    "year": year,
                    "day": day,
                    "part": part,
                    "classification": classification,
                    "language": entry.get("language"),
                    "repo": entry.get("repo"),
                    "path": entry.get("path"),
                    "label": entry.get("label"),
                    "problem_name": problem.get("name"),
                },
            }

            outfile.write(json.dumps(output_entry, ensure_ascii=False) + "\n")

            written += 1

    print()
    print("Dataset generation complete")
    print("---------------------------")
    print(f"Written: {written}")
    print(f"Skipped: {skipped}")
    print()

    print("Classification stats:")
    for key, value in stats.items():
        print(f"{key}: {value}")

    print()
    print(f"Output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
