#!/usr/bin/env python3
import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

INT_RE = re.compile(r"^\d+$")
FLOAT_RE = re.compile(r"^\d+(?:\.\d+)?$")


@dataclass(frozen=True)
class FileInfo:
    path: Path
    model: str
    strat: str
    dataset: str
    language: str
    temperature: str
    pass_k: str
    start: Optional[int]
    end: Optional[int]

    @property
    def key(self) -> Tuple[str, str, str, str, str, str]:
        return (
            self.model,
            self.strat,
            self.dataset,
            self.language,
            self.temperature,
            self.pass_k,
        )


def parse_filename(path: Path) -> Optional[FileInfo]:
    if path.suffix != ".jsonl":
        return None

    parts = path.stem.split("-")
    if len(parts) < 6:
        return None

    batch_tokens: List[str] = []
    # Collect optional batch tokens from the right, but keep at least 6 tokens
    while len(parts) > 6 and len(batch_tokens) < 2 and INT_RE.match(parts[-1]):
        batch_tokens.insert(0, parts.pop())

    pass_k = parts.pop()
    temperature = parts.pop()
    language = parts.pop()
    dataset = parts.pop()
    strat = parts.pop()
    model = "-".join(parts)

    if not (FLOAT_RE.match(temperature) and INT_RE.match(pass_k)):
        return None

    start = int(batch_tokens[0]) if len(batch_tokens) >= 1 else None
    end = int(batch_tokens[1]) if len(batch_tokens) >= 2 else None

    return FileInfo(
        path=path,
        model=model,
        strat=strat,
        dataset=dataset,
        language=language,
        temperature=temperature,
        pass_k=pass_k,
        start=start,
        end=end,
    )


def sort_key(info: FileInfo) -> Tuple[int, int, str]:
    start = info.start if info.start is not None else -1
    end = info.end if info.end is not None else -1
    return (start, end, info.path.name)


def combine_group(infos: List[FileInfo], output_path: Path) -> None:
    infos_sorted = sorted(infos, key=sort_key)
    with output_path.open("w", encoding="utf-8") as out_f:
        for info in infos_sorted:
            with info.path.open("r", encoding="utf-8") as in_f:
                for line in in_f:
                    out_f.write(line)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Combine batched JSONL files by shared metadata."
    )
    parser.add_argument(
        "--dir",
        default=".",
        help="Directory containing batch JSONL files (default: outputs)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List merges without writing output files",
    )
    args = parser.parse_args()

    base_dir = Path(args.dir).resolve()
    if not base_dir.is_dir():
        raise SystemExit(f"Directory not found: {base_dir}")

    groups: Dict[Tuple[str, str, str, str, str, str], List[FileInfo]] = {}

    for path in base_dir.iterdir():
        if not path.is_file():
            continue
        info = parse_filename(path)
        if info is None:
            continue
        # Only merge batched files (must have a start or end).
        if info.start is None and info.end is None:
            continue
        groups.setdefault(info.key, []).append(info)

    for key, infos in sorted(groups.items()):
        model, strat, dataset, language, temperature, pass_k = key
        output_name = (
            f"{model}-{strat}-{dataset}-{language}-{temperature}-{pass_k}.jsonl"
        )
        output_path = infos[0].path.parent / output_name
        if args.dry_run:
            batch_list = ", ".join(i.path.name for i in sorted(infos, key=sort_key))
            print(f"{output_name}: {batch_list}")
            continue
        combine_group(infos, output_path)
        print(f"Wrote {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
