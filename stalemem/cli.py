"""Command line: `stalemem validate | prompts | score | demo | all`."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import dataset, demo, prompts, scoring

DEFAULT_ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="stalemem", description=__doc__)
    ap.add_argument("command", choices=["validate", "prompts", "score", "demo", "all"])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="project folder holding data/ and demo/")
    a = ap.parse_args(argv)
    cmds = {
        "validate": lambda: print(json.dumps(dataset.build(a.root), indent=1)),
        "prompts": lambda: print(prompts.build(a.root)),
        "score": lambda: print(json.dumps(
            {k: {kk: vv for kk, vv in v.items() if kk != "outcomes"} for k, v in scoring.run(a.root)["summary"].items()}, indent=1)),
        "demo": lambda: print("wrote", demo.build(a.root)),
    }
    for name in (["validate", "prompts", "score", "demo"] if a.command == "all" else [a.command]):
        cmds[name]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
