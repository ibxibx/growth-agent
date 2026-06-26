# RUN — how to run the agent

A complete reference for running every part of the agent. For first-time key
setup see **SETUP.md**; for the demo narration see **PITCH.md**.

## Prerequisites

- Python **3.13** (not 3.14 — it lacks wheels for a Daytona dependency).
- Dependencies installed and `.env` filled in (see SETUP.md).
- On Windows/PowerShell, call the venv Python directly:
  `.\.venv\Scripts\python.exe`. On macOS/Linux: `./.venv/bin/python`.

All commands below assume you are in the `growth-agent` folder.

---

## 1. Smoke test — prove the sandbox works (10 seconds)

Run this first. It confirms your Daytona key works and that generated code can
execute in an isolated sandbox — the foundation everything else depends on.

```bash
.\.venv\Scripts\python.exe smoke_test.py
```

Expected output ends with:

```
Sandbox output: GAP=['aws', 'kubernetes'] COVERAGE=33%
KEYSTONE PROVEN: generated code executed in isolation.
```

If you see `KEYSTONE PROVEN`, your Daytona setup is good. If it errors, fix that
before running the full agent — nothing else will work until it does.

Needs: `DAYTONA_API_KEY` only.

---

## 2. Offline demo — the full agent, no Kugiro needed (~30–60 s)

This is the **guaranteed demo path**. It runs the whole pipeline on a built-in
fixture (a senior backend dev pivoting to AI Product roles): Claude generates the
scoring code, runs it in a Daytona sandbox, and prints a ranked roadmap.

```bash
.\.venv\Scripts\python.exe run_agent.py
```

Needs: `DAYTONA_API_KEY` + `ANTHROPIC_API_KEY`. Does NOT need Kugiro, the
dashboard, or a Kugiro key.

### Reading the output

```
1. AWS  (+30 fit, in 100% of target jobs)
   -> AWS Solutions Architect Associate | Amazon Web Services | EUR 135 | 6w
```

- `+30 fit` — projected lift to the candidate's job-fit score if they close
  this gap (0–30, deterministic, computed in the sandboxed code).
- `in 100% of target jobs` — share of the candidate's scanned target jobs that
  ask for this skill.
- The second line — the concrete course: name | provider | cost | duration.

Roadmap is ranked highest-impact first, cheapest as the tiebreak.

---

## 3. Show the generated code — the "auditable" flag

Same as the offline demo, but also prints the exact Python program Claude wrote
and ran in the sandbox. Use this to prove the numbers aren't a black box.

```bash
.\.venv\Scripts\python.exe run_agent.py --show-code
```

The program is appended after the roadmap, under
`--- The exact program Claude generated and ran in the sandbox ---`.

---

## 4. Live demo — pull real data from Kugiro over MCP (optional)

Runs the same pipeline but pulls the candidate's **real** profile and scanned
jobs from a running Kugiro instance over MCP, instead of the fixture.

```bash
.\.venv\Scripts\python.exe run_agent.py --kugiro
```

Needs, in addition to the two keys above, in `.env`:

```
KUGIRO_BASE_URL=http://localhost:3000     # or an ngrok tunnel to a Kugiro host
KUGIRO_API_KEY=kgr_...                     # minted in Kugiro: Settings → API keys
```

And the Kugiro side must be live:
- the dashboard running (`npm run dev` in the dashboard repo, or a tunnel), and
- at least one **scanned job** in that account (otherwise there's no market data
  and the roadmap will be empty).

This path has more moving parts. If anything is shaky, fall back to the offline
demo (section 2) — it tells the same story.

---

## Flag summary

| Command | What it does | Needs Kugiro? |
|---------|--------------|---------------|
| `smoke_test.py` | Prove sandbox execution works | No |
| `run_agent.py` | Full agent on the built-in fixture | No |
| `run_agent.py --show-code` | …and print the generated program | No |
| `run_agent.py --kugiro` | Full agent on live Kugiro data | Yes |

---

## Troubleshooting (runtime)

| Symptom | Cause / fix |
|---------|-------------|
| `KUGIRO_API_KEY is not set` | You used `--kugiro` without the key. Drop the flag for the offline demo, or set the key. |
| Roadmap is empty / "No market demand" | Kugiro account has no scanned jobs, or the offline fixture was edited. Run a scan, or restore the fixture. |
| `Sandbox scoring failed` | The generated program errored in the sandbox. Re-run (codegen is non-deterministic); if it persists, check Daytona quota. |
| Anthropic auth / credit error | `ANTHROPIC_API_KEY` wrong or out of credit. |
| Connection refused on `--kugiro` | Dashboard isn't running at `KUGIRO_BASE_URL`, or the tunnel is down. |
| Install fails on `obstore` (Rust) | You're on Python 3.14. Rebuild the venv with `py -3.13`. |

---

## Quick reference

```bash
# one-time
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env          # then fill in keys

# every run
.\.venv\Scripts\python.exe smoke_test.py            # sanity check
.\.venv\Scripts\python.exe run_agent.py             # the demo
.\.venv\Scripts\python.exe run_agent.py --show-code # demo + generated code
.\.venv\Scripts\python.exe run_agent.py --kugiro    # live data (optional)
```
