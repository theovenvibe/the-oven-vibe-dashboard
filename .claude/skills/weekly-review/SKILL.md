---
name: weekly-review
description: Runs the data pipeline and dashboard build, reads the freshly generated weekly_brief.md, compares it against last week's saved review, and writes this week's plain-language review with a ranked plan of action. Use when the user asks for a "weekly review", "what should I do this week", "review the numbers", "how's the restaurant doing", or wants a Monday-morning check-in.
---

# Weekly review

Produces `reviews/YYYY-MM-DD.md` (today's date) — a plain-language read of
`weekly_brief.md` for a restaurant owner, plus a follow-up on whether last
week's plan got actioned.

## Steps

1. **Refresh the data.** From the repo root:
   ```
   cd ../the-oven-vibe-data-pipeline && uv run python main.py
   cd ../the-oven-vibe-dashboard && uv run build.py
   ```
   If the pipeline step fails or there's no new source CSV, continue anyway —
   `build.py` works off whatever is already in `warehouse.duckdb`, and
   `weekly_brief.md` will just reflect the same week as before. Say so in the
   output rather than silently repeating stale numbers as if they were new.

2. **Read `weekly_brief.md`** (repo root, just regenerated). It has: headline
   numbers, what changed vs. the prior week, ranked actions with evidence and
   expected impact, and appendix tables (menu, pairs, forecast, win-back).

3. **Read the most recent file in `reviews/`** (sort by filename — they're
   `YYYY-MM-DD.md`, so lexical sort is chronological). This is last week's
   plan. If `reviews/` is empty, skip this step and say so — there's nothing
   to follow up on yet.

4. **Write `reviews/YYYY-MM-DD.md`** (today's date, `date +%F`) with these
   sections:

   - **Summary** — 3-5 plain-language sentences on how the week actually
     went: orders, revenue, rating, and the one thing that mattered most.
     No jargon, no unexplained numbers — every figure gets its sample size
     inline (e.g. "6 rated orders", "n=273").
   - **What changed** — pull straight from `weekly_brief.md`'s "what changed"
     section; add one line of interpretation if something moved a lot.
   - **This week's plan** — the ranked action list from `weekly_brief.md`,
     re-ranked or trimmed only if something in the data clearly supersedes
     it (e.g. an action from last week is now moot). Keep the impact figures
     and their basis intact — don't restate them without the arithmetic.
   - **Follow-up on last week** — for each action in the previous
     `reviews/*.md` file's plan, say whether the data suggests it was
     actioned (e.g. a price actually moved, a dormant item started selling
     again, the forecast/quality trend for that lever improved) or not, and
     whether it's still worth doing. If there's no previous review, write
     "No prior review to follow up on — this is the first one."

5. Keep the whole file short enough to read in two minutes. It's for a
   restaurant owner on a Monday morning, not an analytics report.

## Notes

- Never invent numbers. Every figure in the review must trace back to
  `weekly_brief.md` or the `analytics` payload in `dashboard.html`.
- If `data/item_costs.csv` still doesn't exist, keep repeating the one-line
  nudge that adding it upgrades the menu analysis from price to margin —
  don't drop it just because it's been said before.
- Small samples stay small: never state a number as if it were solid when
  its n is under 5. Say "indicative" or "early signal" instead.
