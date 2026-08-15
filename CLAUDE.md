# CLAUDE.md

Project instructions for Claude.

## Overview

Static analytics dashboard for The Oven Vibe (Zomato order history). Consumes
`../the-oven-vibe-data-pipeline/warehouse.duckdb` and emits one self-contained
HTML file. No server, no framework, no runtime dependencies — the only build-time
dependency is `duckdb`.

Files that matter:

- `build.py` — queries `silver.orders` / `silver.order_items`, enriches each
  order with `is_first_order`/`items_count`, loads `data/item_costs.csv` if
  present, calls `analytics.py`, serialises the whole payload to JSON,
  substitutes it for the `__DASHBOARD_DATA__` placeholder in `template.html`,
  writes `dashboard.html`, and writes `weekly_brief.md` via `weekly_brief.py`.
- `analytics.py` — pure Python (stdlib + duckdb, no pandas/numpy) that turns
  the raw orders/items rows into the `analytics` payload defined in
  `docs/ANALYTICS_SPEC.md`: price inference, menu quadrants, actions, pairs,
  attach rate, forecast, demand/closure options, quality, customers,
  discounts, dormant items. That spec is the contract — key names are exact,
  the UI is built against them independently.
- `weekly_brief.py` — renders `analytics` + `meta` as `weekly_brief.md`, prose
  and appendix tables for an AI agent or the owner to read.
- `template.html` — the whole UI: CSS custom properties, hand-rolled SVG charts,
  filters. Edit this, never `dashboard.html`.
- `dashboard.html` — generated output. Not hand-edited; rebuild instead.
- `.claude/skills/weekly-review/` — a skill that rebuilds, reads
  `weekly_brief.md`, and writes a dated file under `reviews/` with a plan and
  a follow-up on the previous week's plan.
- `data/item_costs.csv` (optional, gitignored; `.example` has the schema and
  current item names) — upgrades the menu matrix from unit price to
  contribution margin when present. Wins over `silver.menu_items.unit_cost`
  where both exist.

`analytics.py` prefers three warehouse tables when present, added 13 Aug
2026, and falls back to local computation for each independently when a
table is missing (an older `--db` warehouse never crashes a build):
`gold.item_prices` (source of truth for item prices; `analytics.price_source`
says which path ran), `silver.menu_items` (`category` drives the attach
main/side split and appears on every `menu[]` row), `gold.data_quality`
(passed through as `analytics.data_quality` and rendered in
`weekly_brief.md`).

A fourth, `gold.combined_weekly_sales`, was added 16 Aug 2026 (backend PRD
§11 row 8, Phase 8): direct D1 orders from `../the-oven-vibe-backend` next to
Zomato orders, by week and `source`. `analytics.compute_direct_vs_zomato`
turns it into `analytics.direct_vs_zomato` (`None` when the table is
absent — an older warehouse, or one where `the-oven-vibe-data-pipeline`'s
`pipeline.direct` hasn't run yet). Rendered as a "Direct vs Zomato" card on
the Plan tab and a matching section in `weekly_brief.md`. Deliberately a
channel comparison, not a merged customer view: direct and Zomato orders are
never joined on customer identity (the two systems key it differently — see
the pipeline repo's `pipeline/direct.py`).

## Setup

```
uv sync
uv run build.py
```

## Conventions

- All aggregation happens in the browser, not in SQL. The dataset is small
  (hundreds of orders), so `build.py` ships raw rows and `template.html`
  recomputes every metric against the current filter. That is what lets the date
  and status filters rescope every chart consistently. If the data grows past a
  few thousand orders, move aggregation back into `gold.*` and ship summaries.
- Charts are hand-written SVG in `template.html` — no chart library, so the page
  stays self-contained and CSP-safe. Reuse `columnChart`, `stackedColumnChart`,
  `lineChart`, `barChart` rather than adding a fifth pattern.
- Charts in half-width cards pass `compact: true`; that switches to a smaller
  viewBox so the 11px axis type scales up with the card instead of shrinking.
- Colour comes from the dataviz skill's validated palette, as CSS custom
  properties (`--series-1..3`, status, ink, grid). Light and dark are both
  defined explicitly — dark under both `prefers-color-scheme` and
  `[data-theme="dark"]`. Never hardcode a hex in chart code.
- Untrusted strings (item names, complaint tags) go into the DOM via
  `textContent`, never `innerHTML`.
- Revenue means `order_status = 'Delivered'`. Keep that consistent with
  `pipeline/gold.py`.
- The brief has no knowledge of the live menu. `build.py` reads the warehouse
  only, so its price and drop recommendations go stale the moment
  `../theovenvibe.github.io/menu.json` changes. Check any action against the
  current menu before acting on it, and say so when reporting one.
- Analysis is written down, not just reported. Anything concluded from this data
  gets a dated file in `../marketing/findings/` the same day, with sample sizes
  and stated limits — that folder is the brief a future session inherits.
- Update this file, `AGENT.md`, `README.md`, and memory after completing each
  task — keep docs in sync with the current state, not just the code.
