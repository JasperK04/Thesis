import ast
import json
import re
import warnings
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CODE_DATASET = SCRIPT_DIR / "raw_solutions.jsonl"
AOC_DATASET = SCRIPT_DIR.parent / "data" / "AoC" / "aoc.jsonl"
OUTPUT_FILE = SCRIPT_DIR / "train.jsonl"

EFFICIENCY_INSTRUCTION = (
    "Solve this Advent of Code problem in Python using a "
    "computationally efficient and scalable approach. "
    "Avoid unnecessary brute force solutions.\n\n"
)


def load_aoc_problems():
    """Load AoC problems indexed by (year, day, part).

    Reads the AoC JSONL dataset at AOC_DATASET where each line has an "id" in
    the form "YYYY_DD_P" and stores each full entry by (year, day, part).

    Returns:
        dict[tuple[str, str, str], dict]: Mapping of (year, day, part) to the
        parsed problem entry.
    """
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
    """Build the training prompt prefix for a single AoC problem.

    Args:
        problem_description (str): Full problem statement text.

    Returns:
        str: A model chat prompt with the efficiency instruction prepended and
        formatted using the expected chat tokens.
    """
    augmented_problem = EFFICIENCY_INSTRUCTION + problem_description

    return f"<|im_start|>user\n{augmented_problem}\n<|im_end|>\n<|im_start|>assistant\n"


def has_explicit_part_markers(code):
    """Check for explicit Part 1/Part 2 markers in the code.

    This looks for lowercase tokens "part 1" and "part 2" or compact forms
    "part1" and "part2" in the raw source string.

    Args:
        code (str): Python source code string.

    Returns:
        bool: True if both part markers appear, otherwise False.
    """
    lowered = code.lower()

    return (
        ("part 1" in lowered and "part 2" in lowered)
        or ("part1" in lowered and "part2" in lowered)
        or ("p1" in lowered and "p2" in lowered)
    )


def count_top_level_prints(code):
    """Count print calls at top-level, in main(), or under __main__ guard.

    A top-level print is a call expression directly in the module body. This
    also counts prints inside a function named "main" and inside any
    `if __name__ == "__main__":` block. Syntax warnings from invalid string
    escapes in dataset code are suppressed during parsing.

    Args:
        code (str): Python source code string.

    Returns:
        int: Number of qualifying print calls; 0 if parsing fails.
    """
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(code)
    except Exception:
        return 0

    def is_print_call(call_node):
        return (
            isinstance(call_node, ast.Call)
            and isinstance(call_node.func, ast.Name)
            and call_node.func.id == "print"
        )

    def count_prints_in_body(body_nodes):
        total = 0
        for body_node in body_nodes:
            if isinstance(body_node, ast.Expr) and is_print_call(body_node.value):
                total += 1
        return total

    def is_main_guard(test_node):
        if not isinstance(test_node, ast.Compare):
            return False
        if not isinstance(test_node.left, ast.Name) or test_node.left.id != "__name__":
            return False
        if len(test_node.ops) != 1 or not isinstance(test_node.ops[0], ast.Eq):
            return False
        if len(test_node.comparators) != 1:
            return False
        comparator = test_node.comparators[0]
        return isinstance(comparator, ast.Constant) and comparator.value == "__main__"

    count = count_prints_in_body(tree.body)

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            count += count_prints_in_body(node.body)
        if isinstance(node, ast.If) and is_main_guard(node.test):
            count += count_prints_in_body(node.body)

    return count


def has_multiple_solver_invocations(code):
    """Detect multiple distinct call signatures to the same function name.

    This is a heuristic for combined Part 1/Part 2 solutions where the same
    solver is invoked with different arguments. Syntax warnings from invalid
    string escapes in dataset code are suppressed during parsing.

    Args:
        code (str): Python source code string.

    Returns:
        bool: True if any function name is called with 2+ distinct arg tuples;
        False if parsing fails or no such pattern exists.
    """
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
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
    """Infer AoC part from a file path using naming conventions.

    Matches common patterns such as "part1", "part2", "sol1", "sol2", or
    day-number suffixes like "day-07-2". Returns None if no pattern matches.

    Args:
        path (str): File path string from the dataset entry.

    Returns:
        str | None: "1" for part 1, "2" for part 2, or None if unknown.
    """
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
    """Classify a solution as part1, part2, combined, or unknown.

    Heuristics are applied in this order:
    1) Explicit Part 1/Part 2 markers in code -> combined
    2) Multiple solver invocations -> combined
    3) Two or more top-level prints -> combined
    4) Filename hint -> part1 or part2
    5) Otherwise -> unknown

    Args:
        entry (dict): Parsed JSONL entry with at least "code" and "path".

    Returns:
        str: One of "part1", "part2", "combined", or "unknown".
    """
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
    """Map a classification to the AoC part to pair with problem text.

    Part 1 entries map to part "1". Part 2 and combined solutions are paired
    with part "2" problems. Unknown classifications return None.

    Args:
        classification (str): Output from classify_solution().

    Returns:
        str | None: "1" or "2" if resolvable, otherwise None.
    """
    if classification == "part1":
        return "1"

    if classification in ["part2", "combined"]:
        return "2"

    return None


def main():
    """Generate a training JSONL by pairing solutions with AoC problems.

    Loads the AoC problem index, classifies each solution in raw_solutions.jsonl,
    and writes chat-formatted training records to train.jsonl. Skips entries
    that are malformed, cannot be classified, or lack a matching AoC problem.
    Prints a small summary of counts at the end.
    """
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

            if int(year) < 2021:  # filter to mitigate leakage.
                skipped += 1
                continue

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
                    "author": entry.get("author"),
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
