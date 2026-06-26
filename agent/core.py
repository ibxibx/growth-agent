"""
core.py — the one function every demo tier calls.

generate_growth_roadmap() does the whole flow:
  Kugiro (profile + jobs over MCP) -> market demand -> Daytona-scored roadmap.

It accepts an optional pre-supplied profile/jobs so it can run WITHOUT Kugiro
(Tier-1 offline demo) using a fixture, or WITH Kugiro live (Tier-3).
"""
from .market import aggregate_market_demand
from .roadmap import build_roadmap


def _candidate_from_profile(profile: dict) -> dict:
    """Map a Kugiro search_profile into the candidate shape the engine needs."""
    return {
        "skills": [k.lower() for k in profile.get("keywords", [])],
        "target_roles": profile.get("target_roles", []),
        "seniority": profile.get("seniority", []),
    }


def generate_growth_roadmap(profile: dict, jobs: list[dict]) -> dict:
    """
    profile: a Kugiro search_profile dict (target_roles, keywords, seniority...)
    jobs:    list of Kugiro job dicts for this candidate
    Returns: {gap_summary, roadmap, _generated_code}
    """
    candidate = _candidate_from_profile(profile)
    market = aggregate_market_demand(jobs, extra_skills=candidate["skills"])
    if not market:
        return {"gap_summary": {"covered": [], "missing": []},
                "roadmap": [], "_generated_code": "",
                "note": "No market demand found in scanned jobs."}
    result = build_roadmap(candidate, market)
    result["candidate"] = candidate
    result["market_demand"] = market
    return result


async def generate_from_kugiro(profile_id: str | None = None) -> dict:
    """Tier-3 path: pull profile + jobs live from Kugiro over MCP, then build."""
    from .kugiro_client import kugiro_session, get_search_profile, list_jobs
    async with kugiro_session() as session:
        profile = await get_search_profile(session, profile_id)
        jobs = await list_jobs(session, profile_id, limit=50)
    return generate_growth_roadmap(profile, jobs)
