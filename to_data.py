import json
from pathlib import Path


def read_file(path):
    return path.read_text(encoding="utf-8").strip()


def format_examples(examples):
    return [
        {
            "input": ex["input"],
            "output": [int(ex["answer"])] if ex["answer"].isdigit() else [ex["answer"]],
        }
        for ex in examples
    ]


def process_day(day_path, year):
    meta_path = day_path / "meta.json"
    if not meta_path.exists():
        return []

    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    title = meta.get("title", "")
    main_input = meta.get("input", "")

    part1 = meta.get("part1", {})
    part2 = meta.get("part2", {})

    part1_desc = read_file(day_path / "part1.txt")
    part2_desc = read_file(day_path / "part2.txt")

    day = int(day_path.name)

    problems = []

    problems.append(
        (
            year,
            day,
            1,
            {
                "id": f"{year}_{str(day).zfill(2)}_1",
                "name": title,
                "description": part1_desc,
                "sample_io": format_examples(part1.get("examples", [])),
                "test_list": [
                    {
                        "input": main_input,
                        "output": [int(part1.get("answer"))]
                        if part1.get("answer", "").isdigit()
                        else [part1.get("answer")],
                    }
                ],
            },
        )
    )

    problems.append(
        (
            year,
            day,
            2,
            {
                "id": f"{year}_{str(day).zfill(2)}_2",
                "name": title,
                "description": part1_desc + part2_desc,
                "sample_io": format_examples(part2.get("examples", [])),
                "test_list": [
                    {
                        "input": main_input,
                        "output": [int(part2.get("answer"))]
                        if part2.get("answer", "").isdigit()
                        else [part2.get("answer")],
                    }
                ],
            },
        )
    )

    return problems


def convert_aoc_dataset(root_dir, output_path):
    root = Path(root_dir)
    output = Path(output_path)

    output.parent.mkdir(parents=True, exist_ok=True)

    all_problems = []

    for year_path in root.iterdir():
        if not year_path.is_dir():
            continue

        year = int(year_path.name)

        for day_path in year_path.iterdir():
            if not day_path.is_dir():
                continue

            all_problems.extend(process_day(day_path, year))

    all_problems.sort(key=lambda x: (x[0], x[1], x[2]))

    with output.open("w", encoding="utf-8") as out_file:
        for _, _, _, problem in all_problems:
            out_file.write(json.dumps(problem) + "\n")


if __name__ == "__main__":
    convert_aoc_dataset("dataset", "data/AoC/aoc.jsonl")
