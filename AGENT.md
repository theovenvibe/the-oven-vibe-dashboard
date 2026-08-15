# AGENT.md

Agent-facing operating notes for this repo.

## Purpose

Render the DuckDB warehouse built by `../the-oven-vibe-data-pipeline` as one
self-contained HTML dashboard (`dashboard.html`), plus a machine-readable
`weekly_brief.md` and an agent-run weekly review workflow.

## Key commands

- `uv run build.py` — rebuild `dashboard.html` and `weekly_brief.md` from the
  pipeline's warehouse (calls `analytics.py` and `weekly_brief.py`)
- `uv run build.py --db PATH --out PATH` — build against another warehouse/output
- Screenshot check (headless Chromium ships with Playwright's cache):
  `~/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome --headless --no-sandbox --disable-gpu --virtual-time-budget=4000 --window-size=1280,4200 --screenshot=out.png file://$PWD/dashboard.html`
- `/weekly-review` skill (`.claude/skills/weekly-review/`) — rebuilds, reads
  `weekly_brief.md` and the last file in `reviews/`, writes a new
  `reviews/YYYY-MM-DD.md`.

## Constraints

- Edit `template.html`; `dashboard.html` is generated and any hand edit is lost
  on the next build.
- `template.html` must keep the `__DASHBOARD_DATA__` placeholder — `build.py`
  hard-fails without it.
- `analytics.py` is the contract in `docs/ANALYTICS_SPEC.md` made real — key
  names in the `analytics` payload are exact; the UI is built against them
  independently, so renaming one breaks the other side silently.
- `analytics.py` is stdlib + duckdb only — no pandas/numpy/scipy.
- Weeks with zero orders are `no_data` and dropped from weekly series/averages
  rather than emitted as a zero row.
- Never emit a rupee `impact_value` (in `actions` or elsewhere) built on an
  extrapolation from a handful of data points without a minimum-evidence gate
  and a cap at what the item/window has actually proven it can do. See
  `revive` in `analytics.py`'s `compute_actions` for the pattern: minimum
  sample thresholds, capped at best observed performance, `confidence: "low"`
  below a higher bar, `impact_value: null` + "too few sales to estimate"
  below the minimum gate.
- `gold.item_prices` / `silver.menu_items` / `gold.data_quality` /
  `gold.combined_weekly_sales` are optional at read time — `build.py`'s
  `fetch_if_exists` checks `information_schema.tables` first, so pointing
  `--db` at an older warehouse degrades to local computation (or an absent
  section) instead of crashing.
- `analytics.direct_vs_zomato` (Phase 8, backend PRD §11 row 8) is `None`
  until the pipeline repo has run `pipeline.direct` at least once. Rendered
  on the Plan tab (`directVsZomatoCard` in `template.html`) and in
  `weekly_brief.md` (`_direct_vs_zomato_section`). It's a channel-revenue
  comparison, not a merged customer view — direct and Zomato orders are
  never joined on identity (see the pipeline repo's `pipeline/direct.py` for
  why), so don't build a feature here that assumes one combined customer
  list across both sources.
- The page has no `<!doctype>`, `<html>`, `<head>` or `<body>` wrapper, so it can
  be published as a Claude Artifact as-is. Keep it that way.
- Everything must stay inline: no CDN scripts, no external fonts, no remote
  images. A CSP blocks them when published.
- The warehouse is opened read-only with a copy-on-lock fallback, so a build
  works even while a VS Code DB viewer or the pipeline holds DuckDB's lock.
- `pandas` isn't installed in either repo — use `.fetchall()`, not `.fetchdf()`.
- Dark mode is defined explicitly under both `prefers-color-scheme: dark` and
  `[data-theme="dark"]`. If you add a colour, add it to all three blocks.
- Keep `CLAUDE.md`, this file, `README.md`, and memory updated after each
  completed task.
