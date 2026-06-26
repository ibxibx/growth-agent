# SETUP — get the demo running in 5 minutes

## You need two API keys for the OFFLINE demo

| Key | Where to get it | Goes in `.env` as |
|-----|-----------------|-------------------|
| Anthropic API key | console.anthropic.com → API keys | `ANTHROPIC_API_KEY` |
| Daytona API key | app.daytona.io → dashboard → keys | `DAYTONA_API_KEY` |

That's all the offline demo (`run_agent.py`) needs. It does NOT need Kugiro,
the dashboard, or a Kugiro key.

## Steps

```bash
# from the growth-agent folder
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

copy .env.example .env
# open .env and paste the two real keys above
```

Run it:

```bash
.\.venv\Scripts\python.exe run_agent.py
```

You should see a "GROWTH ROADMAP" table print, ending with a note that the
scoring code ran in an isolated Daytona sandbox. If you see that, you're ready
to demo.

## Troubleshooting

- **"KUGIRO_API_KEY is not set"** → you ran with `--kugiro`. For the offline
  demo, run `run_agent.py` with NO flags.
- **Install fails on `obstore` / Rust errors** → you're on Python 3.14. Use
  Python 3.13 (`py -3.13 -m venv .venv`).
- **Anthropic auth error** → the key is wrong or out of credit.
- **Daytona error** → check the key, and that you have sandbox quota.

## For the LIVE demo (optional, more moving parts)

Only if running against a live Kugiro. Adds two more `.env` values:

```
KUGIRO_BASE_URL=http://localhost:3000     # or an ngrok tunnel URL
KUGIRO_API_KEY=kgr_...                     # minted in Kugiro Settings → API keys
```

Then: `run_agent.py --kugiro`. Requires the dashboard running and at least one
scanned job in that account. If anything is shaky here, fall back to the
offline demo — it tells the same story.
