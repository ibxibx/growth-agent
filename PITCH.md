# PITCH — narrating the growth-agent demo

A ~90-second narration for the live run, plus answers to the questions judges
will ask. Run `python run_agent.py` and talk over it.

## The one-line setup

> "Kugiro tells you how well you match the jobs you want today. This tells you
> exactly what to learn to match them tomorrow — and proves the payoff with
> code that runs in an isolated sandbox."

## While it runs (the 90 seconds)

1. **The problem.** "Every job-seeker gets the same useless advice: 'learn more
   skills.' Which ones? Worth the money? Worth the time? Nobody answers that
   with real data."

2. **What's happening on screen.** "Right now the agent took this candidate's
   real scanned jobs, found the skills the market is asking for that they don't
   have, and — this is the key part — Claude *wrote a scoring program*, and
   we're running it inside an isolated Daytona sandbox. Not on our laptop. In a
   fresh, throwaway machine."

3. **The result.** "And here's the roadmap. AWS is the single highest-ROI move:
   it's in 100% of this candidate's target jobs, costs 135 euros, six weeks.
   After that, Kubernetes. Then a free LLM course. Ranked by impact, every
   number backed by code we can show you."

4. **The close.** "The candidate's data and the generated code live and die in
   that sandbox. Nothing sensitive touches shared infrastructure. That's why
   it's built on Daytona."

## The auditable moment (strong — use it)

> "You don't have to trust the AI's numbers. Here's the actual program Claude
> generated and ran —" (show the generated code) "— so the +30 fit score is
> arithmetic you can check, not a black box."

(Run with `--show-code` to print the generated program.)

## Answers to the questions judges WILL ask

**"Why does this need a sandbox? Isn't it just an API call?"**
> "The scoring is *generated code* — Claude writes a fresh program each run.
> You never run untrusted generated code on your own machine, and you don't run
> one candidate's analysis where another's can touch it. The sandbox is the
> isolation boundary. Remove it and you're executing model-written code on your
> own infra."

**"Why not just scrape LinkedIn / job boards for the market data?"**
> "Because in 2026 that's a losing fight — those sites block bots by default.
> We don't scrape. We use the jobs Kugiro already scanned legally via official
> APIs, and read them over MCP. The hard data problem is already solved upstream."

**"How is this different from LinkedIn Learning's recommendations?"**
> "LinkedIn recommends courses from your profile with no idea what the market
> pays for or what it costs you. We combine *your* real target jobs + the skill
> gap + cost + time + projected fit-score uplift into one ranked answer. Nobody
> ties those together."

**"Is the uplift number real?"**
> "It's a deterministic, explainable formula — more market demand for a skill
> means more uplift — computed in code you can read, not an LLM vibe. With more
> of the candidate's real job data it gets sharper."

## If the live (--kugiro) path is up

Add one line: "And this isn't a fixture — it just pulled *my* real scanned jobs
out of Kugiro over MCP, live." (Only say this if you actually ran `--kugiro`.)

## If something breaks

Stay calm, fall back to the offline run — it tells the identical story. The
sandbox spin-up is the part that matters; the data source is interchangeable.
