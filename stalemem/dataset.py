"""Validate the seed cases and write data/cases.jsonl."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from .cases import CASES


def build(root: Path) -> dict:
    ids = [c.id for c in CASES]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    if dupes:
        raise ValueError(f"duplicate ids: {dupes}")
    (root / "data").mkdir(exist_ok=True)
    with open(root / "data" / "cases.jsonl", "w", encoding="utf-8") as f:
        for c in CASES:
            f.write(c.model_dump_json() + "\n")
    ages = sorted((c.query_date - c.memory[0].date).days for c in CASES)
    return {"cases": len(CASES),
            "by_action": dict(Counter(c.gold_action for c in CASES)),
            "by_domain": dict(Counter(c.domain for c in CASES)),
            "by_class": dict(Counter(c.fact_class for c in CASES)),
            "age_days": {"min": ages[0], "median": ages[len(ages) // 2], "max": ages[-1]}}
