"""Build prompts: each case under three memory formats.

  plain         memory notes without dates (today's date is still given)
  dated         each note carries the date it was recorded
  dated_policy  dated notes plus a short instruction on how to treat old memory

The user message is identical across formats, so any difference in a reply comes from how
memory is presented. Notes for update cases are listed oldest first in every format.

Run:  python3 -I build_prompts.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from stalemem.cases import CASES  # noqa: E402

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


def main():
    pdir = ROOT / "data" / "prompts"
    pdir.mkdir(parents=True, exist_ok=True)
    for fmt in ("plain", "dated", "dated_policy"):
        with open(pdir / f"{fmt}.jsonl", "w", encoding="utf-8") as f:
            for c in CASES:
                f.write(json.dumps({"id": f"{fmt}|{c.id}", "system": system_prompt(c, fmt), "user": c.query},
                                   ensure_ascii=False) + "\n")
        print(fmt, len(CASES))


if __name__ == "__main__":
    main()
