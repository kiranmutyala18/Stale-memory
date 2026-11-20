"""Validate the seed cases and write data/cases.jsonl.

Run:  python3 -I build_data.py   (from the project root)
"""
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from stalemem.cases import CASES  # noqa: E402


def main():
    ids = [c.id for c in CASES]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    assert not dupes, f"duplicate ids: {dupes}"

    (ROOT / "data").mkdir(exist_ok=True)
    with open(ROOT / "data" / "cases.jsonl", "w", encoding="utf-8") as f:
        for c in CASES:
            f.write(c.model_dump_json() + "\n")

    print(f"cases: {len(CASES)}")
    print("by action:", dict(Counter(c.gold_action for c in CASES)))
    print("by domain:", dict(Counter(c.domain for c in CASES)))
    print("by class: ", dict(Counter(c.fact_class for c in CASES)))
    ages = sorted((c.query_date - c.memory[0].date).days for c in CASES)
    print(f"age of oldest entry (days): min {ages[0]}, median {ages[len(ages)//2]}, max {ages[-1]}")


if __name__ == "__main__":
    main()
