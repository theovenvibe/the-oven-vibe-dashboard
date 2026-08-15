# the-oven-vibe-dashboard

A single-file analytics dashboard for The Oven Vibe, built from the DuckDB
warehouse produced by [`../the-oven-vibe-data-pipeline`](../the-oven-vibe-data-pipeline).

`build.py` reads the warehouse, inlines the orders and line items as JSON into
`template.html`, and writes `dashboard.html` — a self-contained page with no
server, no build step and no runtime dependencies. Open it in a browser, or mail
it to someone.

## Build

```
uv run build.py                     # reads ../the-oven-vibe-data-pipeline/warehouse.duckdb
uv run build.py --db PATH --out PATH
```

Then open `dashboard.html`.

Rebuild whenever the pipeline reloads new CSVs — the page is a snapshot, not a
live query.

## What's on it

Six tabs, each with one hero figure and a table under its charts so no number
is reachable only by hovering:

- **Plan** — next week's forecast with its interval, forecast by weekday, the
  ranked action cards (headline, expected impact, evidence, confidence), the
  prep-hour heatmap, kitchen-closure options, and (once
  `the-oven-vibe-data-pipeline` has pulled them) a direct-vs-Zomato channel
  comparison — direct WhatsApp/pickup orders from `the-oven-vibe-backend`
  next to Zomato, kept side by side rather than merged into one customer view.
- **Menu** — the menu matrix (units × price, quadrant-labelled, dot area =
  revenue), the item table with sparklines and trend, price-rise and drop
  candidates, and the dormant/revive list.
- **Combos** — item pairs with lift/n/strength, attach-rate per main, and
  suggested combo cards, plus which discount offers pay for themselves.
- **Customers** — RFM segments, a cohort retention grid, new vs returning
  revenue by week, the repeat-rate trend, and the win-back list.
- **Quality** — the fulfilment funnel, rating drivers (prep time first), slow-
  order items, loss reasons with lost value, and the weekly ops/ratings trend.
- **Demand** — a weekday × hour heatmap (switchable: orders / revenue / avg
  prep time) with maintenance-window candidates outlined, peak and quiet
  windows, and the closure options.

Filters (date-range presets, custom from/to, order status, a weekday
multi-select) sit above the tabs and scope every view. Charts computed live
from `orders`/`items` (weekly revenue, the demand heatmap, the quality trend
lines, the item table's units/orders/revenue) stay filter-reactive; the
heavier derived views (prices, menu quadrants, pairs, forecast, actions,
RFM/cohorts) render from the precomputed `analytics` payload and carry a
quiet note that they cover the full order history, not the filters above.

## Analytics engine

`analytics.py` (pure Python, stdlib + duckdb only) computes the `analytics`
payload embedded alongside the raw rows — price inference, the menu matrix,
ranked actions, pairs/combos, forecast, demand heatmap and closure options,
quality drivers, customer RFM/win-back, discounts, and dormant items. The
contract is `docs/ANALYTICS_SPEC.md`; read that before changing a key name.

`build.py` also writes `weekly_brief.md` (via `weekly_brief.py`) — the same
analysis as prose and appendix tables, meant for an AI agent or the owner to
read directly. The `.claude/skills/weekly-review` skill turns that into a
dated file under `reviews/` with a plan for the coming week and a follow-up
on the last one.

Drop `data/item_costs.csv` (see `data/item_costs.csv.example` for the
columns and the current 28 item names) to upgrade the menu matrix from unit
price to contribution margin; its absence is reported honestly in the
dashboard and the brief rather than silently assumed.

## Reading the brief after a menu change

`build.py` sees the warehouse only. It does not read the website's `menu.json`,
so after a menu or price change its ranked actions can name items that are no
longer sold and prices that no longer exist — the August 2026 relaunch produced
exactly that. Treat `Appendix: menu` as a record of what was charged then;
`../theovenvibe.github.io/menu.json` and `docs/AGGREGATOR_PRICING.md` are what is
charged now. Actions about operations (prep time) and customers (win-back)
survive a menu change; actions about prices, drops and combos do not.

## Notes

- Revenue counts `Delivered` orders only; order counts include rejections and
  timeouts, which is why the two disagree.
- Weeks start Monday. A week with zero orders (e.g. a missing source CSV) is
  `no_data` and is excluded from averages, trends and the forecast rather
  than being counted as a quiet week.
- The warehouse is opened read-only, and copied first if another process holds
  DuckDB's lock (a VS Code DB viewer, say), so a build never blocks the pipeline.
