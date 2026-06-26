"""
agents.py — the swarm. Each agent is a distinct analysis that Claude turns into
a small deterministic program, run in its OWN isolated Daytona sandbox. The
agents are independent, so they run in parallel.

Each agent supplies:
  - name
  - a prompt that tells Claude what program to generate
  - the payload (data) the program reads from stdin

The runner (swarm.py) handles codegen + sandbox execution generically.
"""
import json


def _sample(d: dict, n: int = 3) -> str:
    return json.dumps(dict(list(d.items())[:n]), indent=2)


# --- Agent 1: per-role skill gap ----------------------------------------
def per_role_gap_agent(role: str, candidate_skills: list, role_demand: dict) -> dict:
    prompt = f"""Write a Python program for ONE target role: "{role}".

Reads JSON from stdin: {{"candidate_skills": [...], "role_demand": {{"skill": count}}}}
Compute:
 - covered = candidate skills present in role_demand
 - missing = role_demand skills not covered, sorted by count desc
 - for each missing: demand_count, appears_in_pct (count / max_count * 100, rounded),
   uplift = round(min(30, appears_in_pct * 0.3))
Print ONE JSON: {{"role": "{role}", "covered": [...], "missing": [
  {{"skill": str, "demand_count": int, "appears_in_pct": int, "uplift": int}}]}}
Sample input: {{"candidate_skills": {candidate_skills[:3]}, "role_demand": {_sample(role_demand)}}}
Output ONLY Python code."""
    return {
        "name": f"per_role_gap:{role}",
        "prompt": prompt,
        "payload": {"candidate_skills": candidate_skills, "role_demand": role_demand},
    }


# --- Agent 2: salary delta ----------------------------------------------
def salary_delta_agent(missing_skills: list, salary_by_skill: dict) -> dict:
    prompt = """Write a Python program estimating salary uplift per missing skill.

Reads JSON from stdin: {"missing_skills": [...], "salary_by_skill": {"skill": eur_avg}}
For each missing skill present in salary_by_skill, compute expected_uplift_eur as
the skill's value minus the median of all salary_by_skill values (floor at 0).
Print ONE JSON: {"salary": [{"skill": str, "expected_uplift_eur": int}]} sorted desc.
Output ONLY Python code."""
    return {
        "name": "salary_delta",
        "prompt": prompt,
        "payload": {"missing_skills": missing_skills, "salary_by_skill": salary_by_skill},
    }


# --- Agent 3: time-to-ready (course sequencing) -------------------------
def time_to_ready_agent(courses: list) -> dict:
    prompt = """Write a Python program that sequences courses into a learning plan.

Reads JSON from stdin: {"courses": [{"skill": str, "weeks": int, "cost_eur": int}]}
Sort by weeks asc (quick wins first). Compute cumulative_weeks and cumulative_cost.
Print ONE JSON: {"timeline": [{"skill": str, "weeks": int, "cumulative_weeks": int,
  "cumulative_cost_eur": int}], "total_weeks": int, "total_cost_eur": int}.
Output ONLY Python code."""
    return {
        "name": "time_to_ready",
        "prompt": prompt,
        "payload": {"courses": courses},
    }


# --- Agent 4: competitiveness -------------------------------------------
def competitiveness_agent(candidate_skills: list, market_demand: dict) -> dict:
    prompt = """Write a Python program scoring how competitive a candidate is.

Reads JSON from stdin: {"candidate_skills": [...], "market_demand": {"skill": count}}
competitiveness = round(sum(count for skill,count in market_demand if skill in
candidate_skills) / sum(market_demand.values()) * 100).
Also return the 3 highest-demand skills the candidate is MISSING as "biggest_gaps".
Print ONE JSON: {"competitiveness_pct": int, "biggest_gaps": [str, str, str]}.
Output ONLY Python code."""
    return {
        "name": "competitiveness",
        "prompt": prompt,
        "payload": {"candidate_skills": candidate_skills, "market_demand": market_demand},
    }
