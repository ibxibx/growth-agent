"""
run_swarm.py — the parallel advisor showcase.

Fans out many analysis agents AT ONCE, each generating code and running it in
its own isolated Daytona sandbox. Prints each agent as it finishes so you can
see the parallelism live, then the aggregated complete-advisor report.

  python run_swarm.py            -> offline fixture (no Kugiro)
  python run_swarm.py --kugiro   -> live data from Kugiro over MCP
"""
import asyncio
import sys
import time

from dotenv import load_dotenv

load_dotenv()

from agent.market import aggregate_market_demand, demand_by_role  # noqa: E402
from agent.advisor import build_agent_list, aggregate  # noqa: E402
from agent.swarm import run_swarm  # noqa: E402

FIXTURE_PROFILE = {
    "target_roles": ["AI Product Manager", "Backend Engineer", "Platform Engineer"],
    "keywords": ["python", "fastapi", "sql", "rest", "postgresql"],
    "seniority": ["senior"],
}
FIXTURE_JOBS = [
    {"role": "AI Product Manager", "industry": "AI", "notes": "python llm product management aws"},
    {"role": "AI Product Manager", "industry": "SaaS", "notes": "product management llm sql aws"},
    {"role": "Backend Engineer", "industry": "SaaS", "notes": "python kubernetes docker aws postgresql"},
    {"role": "Backend Engineer", "industry": "E-commerce", "notes": "python sql aws kubernetes react"},
    {"role": "Platform Engineer", "industry": "Fintech", "notes": "kubernetes terraform aws ci/cd go"},
    {"role": "Platform Engineer", "industry": "AI", "notes": "kubernetes docker aws terraform system design"},
]


def candidate_from(profile: dict) -> dict:
    return {"skills": [k.lower() for k in profile.get("keywords", [])],
            "target_roles": profile.get("target_roles", []),
            "seniority": profile.get("seniority", [])}


def on_agent_done(res: dict) -> None:
    status = "OK " if res["ok"] else "ERR"
    print(f"  [{status}] {res['name']:<32} ({res['seconds']}s)")


def print_report(report: dict, wall: float) -> None:
    print("\n" + "=" * 64)
    print("  COMPLETE ADVISOR REPORT")
    print("=" * 64)
    comp = report.get("competitiveness", {})
    if comp:
        print(f"  Competitiveness: {comp.get('competitiveness_pct', '?')}% "
              f"| biggest gaps: {', '.join(comp.get('biggest_gaps', []))}")
    for role in report["per_role"]:
        top = role.get("missing", [])[:3]
        gaps = ", ".join(f"{m['skill']}(+{m['uplift']})" for m in top)
        print(f"\n  {role['role']}")
        print(f"     top gaps: {gaps}")
    sal = report.get("salary", {}).get("salary", [])
    if sal:
        print("\n  Salary uplift (top 3):")
        for s in sal[:3]:
            print(f"     {s['skill']}: +EUR {s['expected_uplift_eur']:,}")
    tl = report.get("timeline", {})
    if tl:
        print(f"\n  Full plan: {tl.get('total_weeks', '?')} weeks, "
              f"EUR {tl.get('total_cost_eur', '?'):,} total")
    print("\n" + "-" * 64)
    print(f"  {report['agents_ok']}/{report['agent_count']} agents succeeded, "
          f"each in its own isolated Daytona sandbox.")
    print(f"  Wall-clock: {wall:.1f}s (parallel). Sequential would be the SUM")
    print(f"  of every agent's time - parallelism is the whole point.")
    print("=" * 64 + "\n")


async def main() -> None:
    if "--kugiro" in sys.argv:
        from agent.kugiro_client import kugiro_session, get_search_profile, list_jobs
        print("Pulling profile + jobs from Kugiro over MCP...")
        async with kugiro_session() as s:
            profile = await get_search_profile(s)
            jobs = await list_jobs(s, limit=50)
    else:
        print("Running offline fixture (no Kugiro needed)...")
        profile, jobs = FIXTURE_PROFILE, FIXTURE_JOBS

    candidate = candidate_from(profile)
    market = aggregate_market_demand(jobs, extra_skills=candidate["skills"])
    jobs_by_role = demand_by_role(jobs, candidate["target_roles"],
                                  extra_skills=candidate["skills"])

    agents = build_agent_list(candidate, jobs_by_role, market)
    print(f"\nFanning out {len(agents)} agents in parallel, "
          f"each in its own Daytona sandbox:\n")

    t0 = time.time()
    results = await run_swarm(agents, on_done=on_agent_done)
    wall = time.time() - t0

    report = aggregate(results, candidate)
    print_report(report, wall)


if __name__ == "__main__":
    asyncio.run(main())
