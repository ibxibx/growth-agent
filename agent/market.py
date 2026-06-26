"""
market.py — turn a candidate's real scanned Kugiro jobs into market demand.

We don't scrape. We read the jobs Kugiro already scanned for this candidate
(via the MCP client) and aggregate which skills the market is asking for, using
the candidate's own keyword universe plus a small canonical skill list.
"""
import re

# Canonical skills we look for in job text. Extend as needed; lowercased.
CANONICAL_SKILLS = [
    "python", "typescript", "javascript", "react", "node", "go", "java",
    "sql", "postgresql", "kubernetes", "docker", "aws", "gcp", "azure",
    "terraform", "ci/cd", "machine learning", "llm", "data analysis",
    "product management", "system design", "fastapi", "rest", "graphql",
]


def _text_of_job(job: dict) -> str:
    parts = [
        str(job.get("role", "")),
        str(job.get("industry", "")),
        str(job.get("notes", "")),  # Kugiro stores keyword matches here
    ]
    # get_job detail may include a description in raw_data/notes; include if present.
    raw = job.get("raw_data") or {}
    if isinstance(raw, dict):
        parts.append(str(raw.get("description", "")))
    return " ".join(parts).lower()


def _mentions(skill: str, text: str) -> bool:
    # Word-boundary match so "go" doesn't match "google", "ai" doesn't match "available".
    return re.search(rf"(?<![a-z]){re.escape(skill)}(?![a-z])", text) is not None


def aggregate_market_demand(jobs: list[dict],
                            extra_skills: list[str] | None = None) -> dict:
    """Return {skill: count} = how many of the candidate's jobs mention each skill."""
    skills = [s.lower() for s in CANONICAL_SKILLS]
    for s in (extra_skills or []):
        if s.lower() not in skills:
            skills.append(s.lower())

    demand: dict[str, int] = {}
    for job in jobs:
        text = _text_of_job(job)
        for skill in skills:
            if _mentions(skill, text):
                demand[skill] = demand.get(skill, 0) + 1
    # Drop zero-demand skills.
    return {k: v for k, v in demand.items() if v > 0}
