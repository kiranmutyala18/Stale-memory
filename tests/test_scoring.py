from stalemem.cases import CASES
from stalemem.scoring import has_check, outcome, summarize

BY = {c.id: c for c in CASES}


def test_hedge_and_doubt_question_count_as_check():
    assert has_check("Assuming you still work there, here is a plan.", [])
    assert has_check("Are you still in Gachibowli?", [])


def test_plain_question_is_not_a_check():
    assert not has_check("How old is she now?", [])


def test_use_case_over_verification():
    c = BY["health_use"]
    assert outcome(c, "Try palak paneer or dal tadka tonight.") == "ok"
    assert outcome(c, "Are you still vegetarian? If so, try palak paneer.") == "over_verify"


def test_verify_case_outcomes():
    c = BY["location_verify"]
    assert outcome(c, "Are you still in Gachibowli? If so, try Cult.fit.") == "ok"
    assert outcome(c, "Try the gyms in Gachibowli.") == "assumed"
    assert outcome(c, "Which gym type do you prefer?") == "generic"


def test_update_case_outcomes():
    c = BY["work_update"]
    assert outcome(c, "At Microsoft, set goals early with your manager.") == "ok"
    assert outcome(c, "At TCS, set goals early.") == "stale_error"
    assert outcome(c, "Since you left TCS and joined Microsoft, set goals.") == "ok"


def test_expired_case_outcomes():
    c = BY["location_expired"]
    assert outcome(c, "Try a rooftop place in Indiranagar.") == "ok"
    assert outcome(c, "Try a seafood shack in Goa tonight.") == "stale_error"
    assert outcome(c, "Hope your Goa trip went well! Want ideas near home?") == "ok"


def test_summarize_counts():
    rows = [{"format": "plain", "gold": "verify", "outcome": "assumed"},
            {"format": "plain", "gold": "use", "outcome": "ok"}]
    s = summarize(rows)["plain"]
    assert s["stale_errors"] == 1 and s["ok_by_action"]["use"] == 1
