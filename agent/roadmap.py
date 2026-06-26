"""
roadmap.py — the core engine.

Flow:
  1. Take the candidate's skills + the market's required skills (from Kugiro jobs).
  2. Ask Claude to GENERATE a deterministic Python scoring program.
  3. Run that generated program inside a Daytona sandbox (the keystone:
     untrusted generated code executes in isolation, never on our machine).
  4. Parse the auditable result and attach concrete courses.

The Daytona sandbox is load-bearing here: the scoring logic is generated code,
and it runs isolated. The output is auditable - we can show the exact program
and the numbers it produced, not a black-box LLM guess.
"""
import json
import os

from anthropic import Anthropic
from daytona import Daytona, DaytonaConfig

from .courses import best_course_for_skill

_anthropic = Anthropic()  # reads ANTHROPIC_API_KEY


CODEGEN_SYSTEM = """You write small, self-contained, deterministic Python programs.
Output ONLY raw Python code - no markdown fences, no prose, no explanation.
The program must read a JSON object from stdin and print ONE JSON object to stdout."""


def _codegen_prompt(candidate: dict, market: dict) -> str:
    return f"""Write a Python program that computes a skills-gap learning roadmap.

It reads this JSON from stdin:
{{
  "candidate_skills": [...],        // skills the candidate already has
  "market_demand": {{"skill": count, ...}}  // how many target jobs want each skill
}}

The program must:
1. Lowercase/normalize all skills for comparison.
2. covered = candidate skills that appear in market_demand.
3. missing = market_demand skills the candidate lacks, sorted by demand count desc.
4. For each missing skill, compute:
   - demand_count: from market_demand
   - appears_in_pct: round(demand_count / total_jobs * 100) where
     total_jobs = max demand count across all skills (proxy for job set size)
   - projected_score_uplift: a 0-30 integer = round(min(30, appears_in_pct * 0.3)),
     representing how much closing this gap lifts fit (deterministic, explainable).
5. Print ONE JSON object:
   {{"covered": [...], "missing": [
       {{"skill": str, "demand_count": int, "appears_in_pct": int,
         "projected_score_uplift": int}}
     ]}}

Sample input the program must handle:
{json.dumps({"candidate_skills": candidate["skills"][:3],
             "market_demand": dict(list(market.items())[:3])}, indent=2)}

Output ONLY the Python code."""


def _generate_scoring_code(candidate: dict, market: dict) -> str:
    msg = _anthropic.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=CODEGEN_SYSTEM,
        messages=[{"role": "user", "content": _codegen_prompt(candidate, market)}],
    )
    code = "".join(b.text for b in msg.content if b.type == "text").strip()
    # Strip accidental fences if the model adds them.
    if code.startswith("```"):
        code = code.split("```", 2)[1]
        if code.startswith("python"):
            code = code[len("python"):]
        code = code.strip()
    return code


def _run_in_sandbox(code: str, payload: dict) -> dict:
    """Run generated scoring code in an isolated Daytona sandbox."""
    daytona = Daytona(DaytonaConfig(api_key=os.environ["DAYTONA_API_KEY"]))
    sandbox = daytona.create()
    try:
        # Feed the payload by embedding it as a stdin replacement, so the
        # generated program (which reads stdin) runs unmodified.
        runner = (
            "import sys, io, json\n"
            f"sys.stdin = io.StringIO({json.dumps(json.dumps(payload))})\n"
            + code
        )
        resp = sandbox.process.code_run(runner)
        if resp.exit_code != 0:
            raise RuntimeError(f"Sandbox scoring failed: {resp.result}")
        return json.loads(resp.result.strip().splitlines()[-1])
    finally:
        sandbox.delete()


def build_roadmap(candidate: dict, market: dict) -> dict:
    """
    candidate: {"skills": [...], "target_roles": [...], ...}
    market: {"skill": demand_count, ...}  (aggregated from Kugiro jobs)
    Returns the ranked roadmap with auditable scoring + concrete courses.
    """
    code = _generate_scoring_code(candidate, market)
    payload = {"candidate_skills": candidate["skills"], "market_demand": market}
    scored = _run_in_sandbox(code, payload)

    roadmap = []
    for item in scored.get("missing", []):
        course = best_course_for_skill(item["skill"])
        roadmap.append({
            "skill": item["skill"],
            "demand_count": item["demand_count"],
            "appears_in_pct_of_target_jobs": item["appears_in_pct"],
            "projected_score_uplift": item["projected_score_uplift"],
            "course": course["name"] if course else "No curated course yet",
            "provider": course["provider"] if course else None,
            "cost_eur": course["cost_eur"] if course else None,
            "weeks": course["weeks"] if course else None,
        })

    # Rank by uplift, then by lowest cost as tiebreak.
    roadmap.sort(key=lambda r: (-r["projected_score_uplift"],
                                r["cost_eur"] if r["cost_eur"] is not None else 9999))
    return {
        "gap_summary": {"covered": scored.get("covered", []),
                        "missing": [r["skill"] for r in roadmap]},
        "roadmap": roadmap,
        "_generated_code": code,  # kept for the "auditable" demo moment
    }
