"""Embed cases, prompts and scored results into demo/template.html -> demo/index.html."""
from __future__ import annotations

import json
from pathlib import Path


def _jl(path: Path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def build(root: Path) -> Path:
    prompts = {}
    for fmt in ("plain", "dated", "dated_policy"):
        for r in _jl(root / "data" / "prompts" / f"{fmt}.jsonl"):
            prompts[f"{fmt}|{r['id'].split('|', 1)[1]}"] = r["system"]
    data = {"cases": _jl(root / "data" / "cases.jsonl"), "prompts": prompts,
            "results": json.loads((root / "data" / "results.json").read_text(encoding="utf-8"))}
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = (root / "demo" / "template.html").read_text(encoding="utf-8").replace("/*DATA*/", blob)
    out = root / "demo" / "index.html"
    out.write_text(html, encoding="utf-8")
    return out
