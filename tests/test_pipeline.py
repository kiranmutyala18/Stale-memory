import json

from stalemem import dataset, prompts, scoring
from stalemem.cases import CASES
from stalemem.cli import DEFAULT_ROOT, main


def test_prompt_formats_differ_only_in_memory_presentation():
    c = next(x for x in CASES if x.id == "work_update")
    plain, dated, policy = (prompts.system_prompt(c, f) for f in ("plain", "dated", "dated_policy"))
    assert "(noted" not in plain and "(noted 10 March 2025)" in dated
    assert prompts.POLICY in policy and prompts.POLICY not in dated
    assert plain.index("TCS") < plain.index("Microsoft")  # oldest first


def test_cli_roundtrip(tmp_path):
    (tmp_path / "data" / "responses").mkdir(parents=True)
    for f in ("plain", "dated", "dated_policy"):
        src = DEFAULT_ROOT / "data" / "responses" / f"{f}.jsonl"
        (tmp_path / "data" / "responses" / f"{f}.jsonl").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    assert dataset.build(tmp_path)["cases"] == 24
    assert prompts.build(tmp_path) == {"plain": 24, "dated": 24, "dated_policy": 24}
    out = scoring.run(tmp_path)
    assert len(out["rows"]) == 72
    assert json.loads((tmp_path / "data" / "results.json").read_text(encoding="utf-8"))["summary"]


def test_committed_results_match_scorer():
    stored = json.loads((DEFAULT_ROOT / "data" / "results.json").read_text(encoding="utf-8"))
    by_case = {c.id: c for c in CASES}
    for r in stored["rows"]:
        assert scoring.outcome(by_case[r["case"]], r["response"]) == r["auto_outcome"]


def test_cli_rejects_unknown_command():
    import pytest
    with pytest.raises(SystemExit):
        main(["nope"])
