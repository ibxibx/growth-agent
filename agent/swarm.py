"""
swarm.py — run many analysis agents in PARALLEL, each in its own Daytona sandbox.

Each agent: Claude generates a program, a fresh sandbox runs it, result parsed.
The agents are independent, so we run them concurrently. This is the Daytona
showcase: N isolated sandboxes executing N generated programs at once.

Uses asyncio.to_thread so the synchronous Anthropic + Daytona SDK calls run in
parallel threads without blocking each other.
"""
import asyncio
import json
import os
import time

from anthropic import Anthropic
from daytona import Daytona, DaytonaConfig

_anthropic = Anthropic()
_daytona = Daytona(DaytonaConfig(api_key=os.environ.get("DAYTONA_API_KEY", "")))

CODEGEN_SYSTEM = """You write small, self-contained, deterministic Python programs.
Output ONLY raw Python code - no markdown fences, no prose.
The program reads a JSON object from stdin and prints ONE JSON object to stdout."""


def _strip_fences(code: str) -> str:
    code = code.strip()
    if code.startswith("```"):
        code = code.split("```", 2)[1]
        if code.startswith("python"):
            code = code[len("python"):]
        code = code.strip()
    return code


def _run_one_agent(agent: dict) -> dict:
    """Blocking: generate code for one agent and run it in its own sandbox."""
    t0 = time.time()
    msg = _anthropic.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1200,
        system=CODEGEN_SYSTEM,
        messages=[{"role": "user", "content": agent["prompt"]}],
    )
    code = _strip_fences("".join(b.text for b in msg.content if b.type == "text"))

    sandbox = _daytona.create()
    try:
        runner = (
            "import sys, io, json\n"
            f"sys.stdin = io.StringIO({json.dumps(json.dumps(agent['payload']))})\n"
            + code
        )
        resp = sandbox.process.code_run(runner)
        if resp.exit_code != 0:
            return {"name": agent["name"], "ok": False,
                    "error": resp.result, "seconds": round(time.time() - t0, 1)}
        out = json.loads(resp.result.strip().splitlines()[-1])
        return {"name": agent["name"], "ok": True, "result": out,
                "code": code, "seconds": round(time.time() - t0, 1)}
    finally:
        sandbox.delete()


async def run_swarm(agents: list[dict], on_done=None) -> list[dict]:
    """Run all agents in parallel. Returns results in completion order."""
    results: list[dict] = []

    async def _wrapped(agent):
        res = await asyncio.to_thread(_run_one_agent, agent)
        results.append(res)
        if on_done:
            on_done(res)
        return res

    await asyncio.gather(*(_wrapped(a) for a in agents))
    return results
