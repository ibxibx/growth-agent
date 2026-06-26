"""
advisor.py — assemble the parallel swarm and aggregate into one advisor report.

Builds the agent list from the candidate + market data, runs them all in
parallel (each in its own sandbox), and merges the outputs into a single
"complete advisor" result.
"""
from .agents import (
    per_role_gap_agent, salary_delta_agent,
    time_to_ready_agent, competitiveness_agent,
)
from .courses import best_course_for_skill
from .market import aggregate_market_demand
from .swarm import run_swarm

# Rough Berlin salary signal per skill (EUR, annual). Curated, not scraped.
# Stand-in for Kugiro's salary data; swap to real salary fields when available.
SALARY_BY_SKILL = {
    "kubernetes": 78000, "aws": 80000, "terraform": 76000, "go": 75000,
    "machine learning": 82000, "llm": 85000, "system design": 80000,
    "docker": 70000, "ci/cd": 68000, "react": 65000, "typescript": 66000,
    "sql": 62000, "data analysis": 64000, "product management": 75000,
}


def _missing_from_roles(role_results: list) -> list[str]:
    seen, missing = set(), []
    for r in role_results:
        for m in r["result"].get("missing", []):
            if m["skill"] not in seen:
                seen.add(m["skill"])
                missing.append(m["skill"])
    return missing


def build_agent_list(candidate: dict, jobs_by_role: dict, market: dict) -> list:
    """Construct the full parallel swarm for this candidate."""
    agents = []
    # One gap agent per target role (real fan-out).
    for role, role_demand in jobs_by_role.items():
        if role_demand:
            agents.append(per_role_gap_agent(role, candidate["skills"], role_demand))
    # Cross-cutting agents.
    missing = [s for s in market if s not in candidate["skills"]]
    agents.append(salary_delta_agent(missing, SALARY_BY_SKILL))
    courses = []
    for s in missing:
        c = best_course_for_skill(s)
        if c:
            courses.append({"skill": s, "weeks": c["weeks"], "cost_eur": c["cost_eur"]})
    agents.append(time_to_ready_agent(courses))
    agents.append(competitiveness_agent(candidate["skills"], market))
    return agents


def aggregate(results: list, candidate: dict) -> dict:
    """Merge all parallel agent outputs into one advisor report."""
    by_name = {r["name"]: r for r in results if r["ok"]}
    role_results = [r for n, r in by_name.items() if n.startswith("per_role_gap:")]

    report = {
        "candidate": candidate,
        "per_role": [r["result"] for r in role_results],
        "salary": by_name.get("salary_delta", {}).get("result", {}),
        "timeline": by_name.get("time_to_ready", {}).get("result", {}),
        "competitiveness": by_name.get("competitiveness", {}).get("result", {}),
        "agent_count": len(results),
        "agents_ok": sum(1 for r in results if r["ok"]),
        "timings": {r["name"]: r.get("seconds") for r in results},
    }
    return report
