"""24 hand-written seed cases: 6 domains x 4 gold actions. Query date for all: 2026-11-14.

Written by hand (not LLM-generated) so the gold labels are a trustworthy core. Facts are
synthetic. Stale/fresh markers are rough keyword heuristics for automatic scoring and
will need checking against real replies.
"""
from datetime import date

from .schemas import Case, MemoryEntry

Q = date(2026, 11, 14)


def M(y, m, d, text):
    return MemoryEntry(date=date(y, m, d), text=text)


CASES: list[Case] = [
    # ------------------------------ work ------------------------------
    Case(id="work_use", domain="work", fact_class="slow", gold_action="use", query_date=Q,
         memory=[M(2026, 10, 28, "Works as a data analyst at a logistics company in Pune")],
         query="Draft a short email to my manager asking for this Friday off.",
         rationale="Role stated 17 days ago; jobs rarely change in weeks. Just write the email."),
    Case(id="work_verify", domain="work", fact_class="slow", gold_action="verify", query_date=Q,
         memory=[M(2025, 4, 2, "Works as a backend developer at a fintech startup")],
         query="How big a salary hike is reasonable to ask for at my company?",
         rationale="Stated 19 months ago. People change jobs; confirm the role before benchmarking.",
         stale_markers=["fintech"]),
    Case(id="work_update", domain="work", fact_class="slow", gold_action="update", query_date=Q,
         memory=[M(2025, 3, 10, "Works as a developer at TCS"),
                 M(2026, 9, 1, "Joined Microsoft as a software engineer")],
         query="Any tips for my first performance review?",
         rationale="The newer entry replaces the old employer. Mentioning TCS would be a stale error.",
         stale_markers=["TCS"], fresh_markers=["Microsoft"]),
    Case(id="work_expired", domain="work", fact_class="event", gold_action="expired", query_date=Q,
         memory=[M(2026, 11, 2, "Has a job interview at Zoho on Nov 6")], event_date=date(2026, 11, 6),
         query="I'm feeling anxious today, any advice?",
         rationale="The interview was 8 days ago. Do not treat it as upcoming; at most ask how it went.",
         stale_markers=["Zoho", "interview"]),

    # ---------------------------- location ----------------------------
    Case(id="location_use", domain="location", fact_class="slow", gold_action="use", query_date=Q,
         memory=[M(2026, 9, 15, "Lives in Hyderabad")],
         query="Any weekend trip ideas nearby?",
         rationale="Stated 60 days ago; people rarely relocate within two months."),
    Case(id="location_verify", domain="location", fact_class="slow", gold_action="verify", query_date=Q,
         memory=[M(2024, 6, 10, "Lives in a rented flat in Gachibowli, Hyderabad")],
         query="Recommend a good gym near me.",
         rationale="Stated 29 months ago and a rental is a likely thing to change. Confirm the area.",
         stale_markers=["Gachibowli"]),
    Case(id="location_update", domain="location", fact_class="slow", gold_action="update", query_date=Q,
         memory=[M(2025, 1, 12, "Lives in Chennai"),
                 M(2026, 8, 20, "Moved to Bengaluru and lives in Indiranagar")],
         query="Where can I get good biryani near me?",
         rationale="The user moved. Chennai suggestions would be wrong.",
         stale_markers=["Chennai"], fresh_markers=["Bengaluru", "Indiranagar"]),
    Case(id="location_expired", domain="location", fact_class="event", gold_action="expired", query_date=Q,
         memory=[M(2026, 11, 1, "Is travelling to Goa from Nov 8 to Nov 10")], event_date=date(2026, 11, 10),
         query="Where should I go for dinner tonight?",
         rationale="The trip ended 4 days ago. Do not suggest Goa restaurants.",
         stale_markers=["Goa"]),

    # ----------------------------- family -----------------------------
    Case(id="family_use", domain="family", fact_class="stable", gold_action="use", query_date=Q,
         memory=[M(2023, 5, 12, "Has a younger sister named Anu")],
         query="Gift ideas for my sister's birthday?",
         rationale="A sibling is a stable fact. Old, but nothing to check."),
    Case(id="family_verify", domain="family", fact_class="slow", gold_action="verify", query_date=Q,
         memory=[M(2025, 2, 14, "Is dating someone named Rahul")],
         query="Help me plan something special for Saturday evening.",
         rationale="Relationship status stated 21 months ago can easily have changed. Do not assume Rahul.",
         stale_markers=["Rahul"]),
    Case(id="family_update", domain="family", fact_class="slow", gold_action="update", query_date=Q,
         memory=[M(2025, 6, 3, "Is single"),
                 M(2026, 10, 2, "Got engaged to Meera")],
         query="Help me write a short toast for my engagement party.",
         rationale="Engaged supersedes single. Use Meera.",
         stale_markers=["single"], fresh_markers=["Meera"]),
    Case(id="family_expired", domain="family", fact_class="event", gold_action="expired", query_date=Q,
         memory=[M(2026, 10, 20, "Mom is visiting for a week starting Oct 27")], event_date=date(2026, 11, 3),
         query="Plan my meals for the weekend.",
         rationale="The visit ended 11 days ago. Do not plan meals for a guest.",
         stale_markers=["mom", "mother", "visiting", "guest"]),

    # --------------------------- education ----------------------------
    Case(id="education_use", domain="education", fact_class="slow", gold_action="use", query_date=Q,
         memory=[M(2026, 8, 1, "Final-year B.Tech student, graduating in May 2027")],
         query="How should I plan my placement preparation?",
         rationale="Stated 3 months ago and the timeline is fixed. Use it."),
    Case(id="education_verify", domain="education", fact_class="fast", gold_action="verify", query_date=Q,
         memory=[M(2025, 3, 18, "Is learning Spanish")],
         query="Suggest a weekly routine for my language learning.",
         rationale="A hobby from 20 months ago may be dropped or swapped for another language.",
         stale_markers=["Spanish"]),
    Case(id="education_update", domain="education", fact_class="slow", gold_action="update", query_date=Q,
         memory=[M(2024, 8, 20, "Is a 2nd-year B.Tech student in Visakhapatnam"),
                 M(2026, 8, 25, "Started an MS at Purdue this August")],
         query="How do I balance coursework with a part-time job?",
         rationale="The user is now an MS student at Purdue, not a B.Tech student.",
         stale_markers=["B.Tech", "Visakhapatnam"], fresh_markers=["Purdue", "MS"]),
    Case(id="education_expired", domain="education", fact_class="event", gold_action="expired", query_date=Q,
         memory=[M(2026, 10, 28, "Semester exams start on Nov 5")], event_date=date(2026, 11, 12),
         query="Help me plan how to spend this week.",
         rationale="Exams ended two days ago. Do not plan around studying for them.",
         stale_markers=["exam"]),

    # ----------------------------- health -----------------------------
    Case(id="health_use", domain="health", fact_class="stable", gold_action="use", query_date=Q,
         memory=[M(2023, 2, 10, "Is vegetarian")],
         query="Suggest some dinner ideas for tonight.",
         rationale="A long-held diet is stable. Suggest vegetarian dishes without asking."),
    Case(id="health_verify", domain="health", fact_class="fast", gold_action="verify", query_date=Q,
         memory=[M(2025, 12, 1, "Is trying intermittent fasting, eating between 12 and 8 pm")],
         query="What should I eat for breakfast tomorrow?",
         rationale="A diet experiment from almost a year ago is likely over. Do not assume the fasting window.",
         stale_markers=["intermittent", "fasting", "12 pm", "noon"]),
    Case(id="health_update", domain="health", fact_class="slow", gold_action="update", query_date=Q,
         memory=[M(2024, 3, 5, "Eats non-veg and loves chicken"),
                 M(2026, 9, 12, "Turned vegetarian in September")],
         query="Give me some meal prep ideas for the week.",
         rationale="The user is now vegetarian. Chicken suggestions would be wrong.",
         stale_markers=["chicken"], fresh_markers=["vegetarian", "veg"]),
    Case(id="health_expired", domain="health", fact_class="event", gold_action="expired", query_date=Q,
         memory=[M(2026, 11, 5, "Has a dentist appointment on Nov 10")], event_date=date(2026, 11, 10),
         query="Help me plan my schedule for Monday.",
         rationale="The appointment was 4 days ago. Do not schedule it on Monday.",
         stale_markers=["dentist"]),

    # ----------------------------- plans ------------------------------
    Case(id="plans_use", domain="plans", fact_class="slow", gold_action="use", query_date=Q,
         memory=[M(2026, 9, 30, "Bought a Royal Enfield Classic 350")],
         query="What should I check before its first service?",
         rationale="A bike bought six weeks ago is certainly still owned."),
    Case(id="plans_verify", domain="plans", fact_class="fast", gold_action="verify", query_date=Q,
         memory=[M(2025, 8, 20, "Is training for a half marathon")],
         query="Suggest a good weekend workout.",
         rationale="Training goals from 15 months ago have usually ended. Do not assume the race plan.",
         stale_markers=["marathon"]),
    Case(id="plans_update", domain="plans", fact_class="fast", gold_action="update", query_date=Q,
         memory=[M(2025, 2, 9, "Plays cricket every Sunday with college friends"),
                 M(2026, 10, 25, "Hurt shoulder; doctor said no cricket or heavy lifting for three months")],
         query="What should I do this Sunday?",
         rationale="The newer entry says no cricket. Suggest something shoulder-friendly.",
         stale_markers=["play cricket", "playing cricket", "game of cricket", "deadlift", "heavy weights"], fresh_markers=["shoulder"]),
    Case(id="plans_expired", domain="plans", fact_class="event", gold_action="expired", query_date=Q,
         memory=[M(2026, 10, 15, "Planning a Diwali trip to Jaipur from Nov 8 to Nov 12")], event_date=date(2026, 11, 12),
         query="Suggest something fun to do tonight.",
         rationale="The trip ended two days ago. Do not plan around being in Jaipur.",
         stale_markers=["Jaipur"]),
]
