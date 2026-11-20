from datetime import date

import pytest
from pydantic import ValidationError

from stalemem.cases import CASES
from stalemem.schemas import Case, MemoryEntry

Q = date(2026, 11, 14)


def mk(**kw):
    base = dict(id="t", domain="work", fact_class="slow", gold_action="use", query_date=Q,
                memory=[MemoryEntry(date=date(2026, 10, 1), text="x")], query="q", rationale="r")
    base.update(kw)
    return Case(**base)


def test_seed_set_is_balanced():
    assert len(CASES) == 24
    assert len({c.id for c in CASES}) == 24
    for action in ("use", "verify", "update", "expired"):
        assert sum(c.gold_action == action for c in CASES) == 6


def test_use_beyond_horizon_rejected():
    with pytest.raises(ValidationError):
        mk(memory=[MemoryEntry(date=date(2024, 1, 1), text="x")])


def test_stable_fact_may_be_old_and_use():
    mk(fact_class="stable", memory=[MemoryEntry(date=date(2020, 1, 1), text="x")])


def test_verify_within_horizon_rejected():
    with pytest.raises(ValidationError):
        mk(gold_action="verify")


def test_update_needs_two_entries_and_fresh_marker():
    with pytest.raises(ValidationError):
        mk(gold_action="update", fresh_markers=["a"])
    two = [MemoryEntry(date=date(2025, 1, 1), text="a"), MemoryEntry(date=date(2026, 1, 1), text="b")]
    with pytest.raises(ValidationError):
        mk(gold_action="update", memory=two)
    mk(gold_action="update", memory=two, fresh_markers=["b"])


def test_expired_needs_past_event():
    with pytest.raises(ValidationError):
        mk(gold_action="expired", fact_class="event", event_date=date(2026, 12, 1))
    mk(gold_action="expired", fact_class="event", event_date=date(2026, 11, 1))


def test_memory_must_be_oldest_first_and_not_future():
    a, b = MemoryEntry(date=date(2026, 1, 1), text="a"), MemoryEntry(date=date(2025, 1, 1), text="b")
    with pytest.raises(ValidationError):
        mk(memory=[a, b])
    with pytest.raises(ValidationError):
        mk(memory=[MemoryEntry(date=date(2027, 1, 1), text="a")])
