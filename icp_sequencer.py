#!/usr/bin/env python3
"""
ICP Scoring & Personalized Sequencing
--------------------------------------
Scores accounts on firmographic, hiring, funding, and technographic signals,
then generates a 3-touch personalized email sequence for every account that
clears the qualification bar.

Two responsibilities on purpose, kept in one small tool:
  1. `score_icp_fit`     -- is this account worth sequencing at all?
  2. `generate_sequence` -- if yes, what should that sequence actually say?

Usage:
    python icp_sequencer.py --input accounts.csv --min-score 60
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, field
from typing import Any, Dict, List


# --------------------------------------------------------------------------
# Scoring rubric -- tune against your own ICP definition.
# --------------------------------------------------------------------------

TARGET_INDUSTRIES = {"Data Infrastructure", "Vertical SaaS", "Industrial Tech", "Fintech"}
TARGET_EMPLOYEE_BAND = (10, 250)
TARGET_FUNDING_STAGES = {"Seed", "Series A", "Series B"}
FUNDING_RECENCY_DAYS = 180
RELEVANT_TECH_KEYWORDS = ("clay", "hubspot", "smartlead", "apollo")

SCORE_WEIGHTS = {
    "industry_match": 25,
    "employee_band_fit": 20,
    "recent_target_stage_funding": 25,
    "has_hiring_signal": 15,
    "has_relevant_tech_signal": 15,
}


@dataclass
class ScoredAccount:
    company: str
    score: int
    reasons: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------

def load_accounts(path: str) -> List[Dict[str, Any]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _to_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------

def score_icp_fit(account: Dict[str, Any]) -> ScoredAccount:
    score = 0
    reasons: List[str] = []

    if account.get("industry") in TARGET_INDUSTRIES:
        score += SCORE_WEIGHTS["industry_match"]
        reasons.append(f"Industry match: {account.get('industry')}")

    employees = _to_int(account.get("employee_count"))
    lo, hi = TARGET_EMPLOYEE_BAND
    if lo <= employees <= hi:
        score += SCORE_WEIGHTS["employee_band_fit"]
        reasons.append(f"Employee count {employees} within target band {lo}-{hi}")

    funding_stage = (account.get("funding_stage") or "").strip()
    funding_days_ago = account.get("funding_days_ago")
    if funding_stage in TARGET_FUNDING_STAGES and funding_days_ago not in (None, ""):
        if _to_int(funding_days_ago, default=9999) <= FUNDING_RECENCY_DAYS:
            score += SCORE_WEIGHTS["recent_target_stage_funding"]
            reasons.append(f"Raised {funding_stage} {funding_days_ago}d ago")

    if (account.get("hiring_signal") or "").strip():
        score += SCORE_WEIGHTS["has_hiring_signal"]
        reasons.append(f"Hiring signal: {account.get('hiring_signal')}")

    tech_signal = (account.get("tech_signal") or "").lower()
    if any(kw in tech_signal for kw in RELEVANT_TECH_KEYWORDS):
        score += SCORE_WEIGHTS["has_relevant_tech_signal"]
        reasons.append(f"Tech signal: {account.get('tech_signal')}")

    return ScoredAccount(company=account["company"], score=score, reasons=reasons, raw=account)


def rank_accounts(accounts: List[Dict[str, Any]]) -> List[ScoredAccount]:
    scored = [score_icp_fit(a) for a in accounts]
    scored.sort(key=lambda a: a.score, reverse=True)
    return scored


# --------------------------------------------------------------------------
# Sequence generation
# --------------------------------------------------------------------------

def generate_sequence(account: Dict[str, Any]) -> List[Dict[str, str]]:
    company = account["company"]
    hiring_signal = account.get("hiring_signal") or "your team"
    pain_point = account.get("pain_point") or "scaling GTM without adding headcount"

    return [
        {
            "day": "Day 0",
            "subject": f"Saw {company} is hiring a {hiring_signal}",
            "body": (
                f"Hi there,\n\nNoticed {company} is hiring a {hiring_signal} -- usually a sign "
                f"you're scaling GTM execution right now. I help teams in that exact spot "
                f"automate the manual parts of outbound so the new hire starts from a running "
                f"system instead of a blank slate.\n\nWorth a quick chat?"
            ),
        },
        {
            "day": "Day 3",
            "subject": f"Re: the {hiring_signal} hire at {company}",
            "body": (
                f"Following up -- most teams at {company}'s stage tell me {pain_point}. "
                f"That's usually the first thing worth fixing before the new hire ramps up, "
                f"since it compounds every week it stays manual.\n\nHappy to show you how "
                f"that's solved in practice."
            ),
        },
        {
            "day": "Day 7",
            "subject": f"Closing the loop, {company}",
            "body": (
                f"I'll leave this here -- if fixing how {company} handles "
                f"'{pain_point}' becomes a priority later this quarter, happy to pick this "
                f"back up. Good luck with the {hiring_signal} search either way."
            ),
        },
    ]


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="ICP Scoring & Personalized Sequencing")
    parser.add_argument("--input", default="accounts.csv", help="Path to accounts CSV file")
    parser.add_argument("--min-score", type=int, default=60, help="Minimum ICP score to generate a sequence")
    args = parser.parse_args()

    accounts = load_accounts(args.input)
    ranked = rank_accounts(accounts)

    print(f"Scored {len(ranked)} accounts against ICP rubric (min-score={args.min_score})\n")
    for a in ranked:
        status = "QUALIFIED" if a.score >= args.min_score else "skip"
        print(f"[{status:9}] {a.company:20} score={a.score:3d}/100")
        for reason in a.reasons:
            print(f"             - {reason}")
    print()

    for a in ranked:
        if a.score < args.min_score:
            continue
        print(f"=== Sequence for {a.company} ===")
        for step in generate_sequence(a.raw):
            print(f"\n[{step['day']}] Subject: {step['subject']}\n{step['body']}")
        print()


if __name__ == "__main__":
    main()
