"""Score replies with transparent rules, then (separately) audit them by hand.

For each reply two things are detected:
  check   - the reply confirms or hedges a remembered fact ("are you still at...?", "if that's still the case")
  markers - whether it mentions the stale or fresh fact (case-insensitive prefix match on the case's markers)

Outcome by gold action:
  use      ok | over_verify
  verify   ok (checked) | assumed (used the fact without checking) | generic (neither used nor checked)
  update   ok | stale_error | over_verify (checks the newer fact) | asked_instead | generic
  expired  ok | stale_error (treats the past event as current)

Run:  python3 -I score_responses.py
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from stalemem.cases import CASES  # noqa: E402

FORMATS = ["plain", "dated", "dated_policy"]
HEDGE = re.compile(
    r"\blast (i|we) (knew|heard|spoke|discussed|noted)\b|\bcorrect me\b|\bin case (that|this|things|it)\b|"
    r"\bassuming\b|\bif (that|this|it)('s| is| has| hasn't| still)\b|\bjust to (check|confirm)\b|\bquick check\b|"
    r"\bis that (still|right|correct|current|the case)\b|\bgoing (by|off) (what|my)\b|\bfrom what I (have|remember|noted)\b|"
    r"\bI have you (noted|down)\b|\bif that's changed\b|\bhas (that|this|it) changed\b|\bhave things changed\b|"
    r"\bif (you're|you are|you've|you have) (still|since)\b|\bcheck(ing)? (that|this|whether|if)\b|\bmay have changed\b|"
    r"\bmight have changed\b|\bin case you('ve| have)\b|\bnoted (that )?(you|back)\b|"
    r"\bfrom a while (back|ago)\b|\bnot sure (my|that|these|whether)\b|"
    r"\bmy (notes?|memory)\b[^.?!]*\b(old|dated|older|out of date|current|outdated)\b|\bmy note is from\b|"
    r"\btell me if (you've|you have|that|this|anything)\b", re.I)
# a question only counts as a check if it expresses doubt about the fact (not "how old is she now?")
CONFIRM_Q = re.compile(r"\b(still|anymore|any more|changed|whether|since then|or (did|have|has|are|is|was)|did you (already|finish))\b", re.I)
MARKER_OR_Q = re.compile(r"\bor\b", re.I)
PAST = re.compile(
    r"\bhow (did|was|were|'d)\b|\bhow it went\b|\bhow did it go\b|\bhope (it|that|the|your)\b.*\b(went|go|was|were)\b|"
    r"\bis (now )?(over|done)\b|\bwas (over|done)\b|\bwere (over|done)\b|\bended\b|\bfinished\b|\bwrapped up\b|"
    r"\bbehind you\b|\bback from\b|\bjust (got back|finished)\b|\bafter (your|the)\b|\bhas passed\b|\bhave passed\b|"
    r"\bsince (your|the) (trip|interview|exam|visit|appointment)\b|\bhow are you feeling after\b|\bthat (was|'s) (last|a few)\b|"
    r"\bearlier this month\b|\blast (week|weekend)\b|\bno longer\b|"
    r"\b(were|was) (due|scheduled)\b|\bmay (be|have) (done|finished)\b|\bprobably (done|finished)\b|\bguessing you\b", re.I)
ACK_OLD = re.compile(r"\bno longer\b|\bused to\b|\bpreviously\b|\bformerly\b|\bmoved from\b|\bleft\b|\bhad been\b|\bwas (a|at|in)\b", re.I)


def sentences(t):
    return [s for s in re.split(r"(?<=[.!?])\s+|\n+", t) if s.strip()]


def has_check(text, markers):
    if HEDGE.search(text):
        return True
    for s in sentences(text):
        if "?" not in s:
            continue
        if CONFIRM_Q.search(s):
            return True
        if MARKER_OR_Q.search(s) and any(re.search(r"\b" + re.escape(m), s, re.I) for m in markers):
            return True
    return False


def has_marker(text, markers):
    return any(re.search(r"\b" + re.escape(m), text, re.I) for m in markers)


def outcome(case, reply):
    stale, fresh = case.stale_markers, case.fresh_markers
    check = has_check(reply, stale + fresh)
    s, f = has_marker(reply, stale), has_marker(reply, fresh)
    g = case.gold_action
    if g == "use":
        return "over_verify" if check else "ok"
    if g == "verify":
        if check:
            return "ok"
        return "assumed" if s else "generic"
    if g == "update":
        if s and not ACK_OLD.search(reply):
            return "stale_error"
        if f:
            return "over_verify" if check else "ok"
        return "asked_instead" if check else "generic"
    if g == "expired":
        if not s:
            return "ok"
        if PAST.search(reply) or check:
            return "ok"
        return "stale_error"
    raise ValueError(g)


def main():
    cases = {c.id: c for c in CASES}
    rows = []
    for fmt in FORMATS:
        with open(ROOT / "data" / "responses" / f"{fmt}.jsonl", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                cid = r["id"].split("|", 1)[1]
                c = cases[cid]
                oc = outcome(c, r["response"])
                rows.append({"format": fmt, "case": cid, "domain": c.domain, "gold": c.gold_action,
                             "outcome": oc, "response": r["response"]})
    assert len(rows) == 72

    overrides_path = ROOT / "data" / "audit_overrides.json"
    overrides = json.loads(overrides_path.read_text(encoding="utf-8")) if overrides_path.exists() else {}
    for r in rows:
        key = f"{r['format']}|{r['case']}"
        r["auto_outcome"] = r["outcome"]
        if key in overrides:
            r["outcome"] = overrides[key]["outcome"]
            r["audit_note"] = overrides[key]["why"]

    summary = {}
    for fmt in FORMATS:
        rs = [r for r in rows if r["format"] == fmt]
        by = defaultdict(Counter)
        for r in rs:
            by[r["gold"]][r["outcome"]] += 1
        ok = {g: by[g]["ok"] for g in ("use", "verify", "update", "expired")}
        stale = sum(1 for r in rs if r["gold"] in ("verify", "update", "expired") and r["outcome"] in ("assumed", "stale_error"))
        summary[fmt] = {
            "ok_by_action": ok, "ok_total": sum(ok.values()),
            "stale_errors": stale, "stale_denominator": 18,
            "over_verify_on_use": by["use"]["over_verify"], "use_n": 6,
            "verify_generic": by["verify"]["generic"],
            "outcomes": {g: dict(by[g]) for g in by},
        }
    out = {"summary": summary, "rows": rows, "n_overrides": len(overrides)}
    (ROOT / "data" / "results.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return rows, summary


if __name__ == "__main__":
    rows, summary = main()
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "outcomes"} for k, v in summary.items()}, indent=1))
