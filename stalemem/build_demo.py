"""Embed cases, prompts and scored results into demo/template.html -> demo/index.html.

Run:  python3 -I build_demo.py   (after build_data, build_prompts, score_responses)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def jl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


prompts = {}
for fmt in ("plain", "dated", "dated_policy"):
    for r in jl(ROOT / "data" / "prompts" / f"{fmt}.jsonl"):
        case_id = r["id"].split("|", 1)[1]
        prompts[f"{fmt}|{case_id}"] = r["system"]

data = {
    "cases": jl(ROOT / "data" / "cases.jsonl"),
    "prompts": prompts,
    "results": json.loads((ROOT / "data" / "results.json").read_text(encoding="utf-8")),
}
blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
html = (ROOT / "demo" / "template.html").read_text(encoding="utf-8").replace("/*DATA*/", blob)
(ROOT / "demo" / "index.html").write_text(html, encoding="utf-8")
print(f"wrote demo/index.html ({len(html)//1024} KB)")
