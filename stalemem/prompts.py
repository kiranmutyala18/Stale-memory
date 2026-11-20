"""Build prompts: each case under three memory formats (plain, dated, dated_policy).

The user message is identical across formats, so any difference in a reply comes from how
memory is presented. Notes for update cases are listed oldest first in every format.
"""
from __future__ import annotations

import json
from pathlib import Path

from .cases import CASES

TODAY = "14 November 2026"
INTRO = f"You are a helpful personal assistant with a memory of the user. Today's date is {TODAY}."
POLICY = (
    "Memory can go out of date. Stable facts and recent facts can be used directly. "
    "If a remembered fact is old and the kind of thing that changes, briefly confirm it instead of assuming. "
    "If a newer note contradicts an older one, go with the newer one. "
    "Do not treat an event whose date has passed as upcoming."
)
LIMIT = "Keep your reply under 120 words."


def fmt_date(d):
    return f"{d.day} {d.strftime('%B %Y')}"


def system_prompt(case, fmt):
    if fmt == "plain":
        notes = "\n".join(f"- {m.text}" for m in case.memory)
    else:
        notes = "\n".join(f"- {m.text} (noted {fmt_date(m.date)})" for m in case.memory)
    parts = [INTRO, "What you remember about the user:\n" + notes]
    if fmt == "dated_policy":
        parts.append(POLICY)
    parts.append(LIMIT)
    return "\n\n".join(parts)


def build(root: Path) -> dict[str, int]:
    pdir = root / "data" / "prompts"
    pdir.mkdir(parents=True, exist_ok=True)
    counts = {}
    for fmt in ("plain", "dated", "dated_policy"):
        with open(pdir / f"{fmt}.jsonl", "w", encoding="utf-8") as f:
            for c in CASES:
                f.write(json.dumps({"id": f"{fmt}|{c.id}", "system": system_prompt(c, fmt), "user": c.query},
                                   ensure_ascii=False) + "\n")
        counts[fmt] = len(CASES)
    return counts
