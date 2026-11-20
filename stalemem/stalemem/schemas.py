"""Schemas for StaleMem: when should an assistant trust, check, or drop a remembered fact?

A Case gives an assistant a small timestamped memory store, a query date, and a user
message. The gold label says what a careful assistant should do with the remembered fact:

  use      the fact is still reliable; answer with it directly (asking is an unnecessary check)
  verify   the fact is old and tends to change; answer, but confirm it first or hedge
  update   a newer memory entry replaces the old one; use the newer fact, never the old
  expired  the fact was tied to an event that has passed; do not treat it as current
"""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator

Action = Literal["use", "verify", "update", "expired"]
FactClass = Literal["stable", "slow", "fast", "event"]
Domain = Literal["work", "location", "family", "education", "health", "plans"]

# Assumed validity horizons in days. These are working assumptions, not measurements;
# human raters should check them in a later step. "event" facts expire on their event date.
HORIZON_DAYS: dict[str, int | None] = {"stable": None, "slow": 365, "fast": 90, "event": None}


class MemoryEntry(BaseModel):
    date: date
    text: str


class Case(BaseModel):
    id: str
    domain: Domain
    fact_class: FactClass
    memory: list[MemoryEntry] = Field(min_length=1, description="Oldest first")
    event_date: date | None = Field(default=None, description="For event facts: when the event ends")
    query_date: date
    query: str
    gold_action: Action
    rationale: str
    # Heuristic markers for automatic scoring (a later step). Matching is case-insensitive.
    stale_markers: list[str] = Field(default_factory=list, description="Words that signal the outdated fact is being used")
    fresh_markers: list[str] = Field(default_factory=list, description="Words that signal the newer fact is being used")

    @model_validator(mode="after")
    def _consistent(self) -> "Case":
        dates = [m.date for m in self.memory]
        if dates != sorted(dates):
            raise ValueError(f"{self.id}: memory must be oldest first")
        if dates[-1] > self.query_date:
            raise ValueError(f"{self.id}: memory entry after query date")
        age = (self.query_date - dates[0]).days
        h = HORIZON_DAYS[self.fact_class]

        if self.gold_action == "update":
            if len(self.memory) < 2:
                raise ValueError(f"{self.id}: update needs a newer entry")
            if not self.fresh_markers:
                raise ValueError(f"{self.id}: update needs fresh_markers")
        elif len(self.memory) != 1:
            raise ValueError(f"{self.id}: only update cases have two entries")

        if self.gold_action == "expired":
            if self.fact_class != "event" or not self.event_date or self.event_date >= self.query_date:
                raise ValueError(f"{self.id}: expired needs an event fact whose date has passed")
        if self.fact_class == "event" and self.gold_action != "expired":
            raise ValueError(f"{self.id}: event facts here are all expired")
        if self.gold_action == "use":
            if h is not None and age > h:
                raise ValueError(f"{self.id}: labelled use but {age} days exceeds the {h}-day horizon")
        if self.gold_action == "verify":
            if h is None or age <= h:
                raise ValueError(f"{self.id}: labelled verify but age {age}d is within the horizon {h}")
        return self
