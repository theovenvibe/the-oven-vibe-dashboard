# MEMORY.md

Memory index for this project.

- Pricing decisions live in `docs/PRICING_STRATEGY.md` and are applied to
  `../theovenvibe.github.io/menu.json` (the local menu; Zomato prices are
  separate and higher). Aug 2026: demand-tiered rise, three anchor prices held,
  combos at ~10% off parts, 11 SKUs dropped when the wok station was retired
  after the gas price rise.
- `menu.json` uses CRLF line endings — rewriting it with LF produces a
  900-line diff that hides the real change.

- Payload units are not all the same shape: `trend_pct` arrives already in
  percent (-85.71 means -86%), so the UI formats it directly instead of passing
  it through `pct()`, which multiplies by 100. That mismatch printed "-8571%".
- The heatmap's SVG viewBox is ~400 units wide, so an uncapped `max-width`
  scaled its 11px labels to ~24px in a 900px card. `.heatmap-wrap svg` caps at
  560px for that reason.
- A closure window with zero revenue is not necessarily a window with zero
  orders — orders that were rejected or timed out leave revenue at ₹0. The two
  cases get different verdict wording.

- Dashboard is generated: `build.py` + `template.html` -> `dashboard.html`.
  Never hand-edit the output.
- `analytics.py` computes the `analytics` payload per `docs/ANALYTICS_SPEC.md`
  (the exact contract with the UI). `weekly_brief.py` renders it as
  `weekly_brief.md`. `.claude/skills/weekly-review` turns that into a dated
  `reviews/YYYY-MM-DD.md` with a plan and last week's follow-up.
- Sanity checks that must hold against the real warehouse (see spec's "Known
  headline findings"): prep time >25min rated orders average 2.17★ (n=6) vs
  **4.16★ fast** (n=44, kpt<=25min strictly — a 3rd "unknown kpt" bucket, n=1,
  is dropped from `rating_drivers` entirely as too small to be a "driver",
  not folded into fast; the spec's old "45 @ 4.18" number folded that
  unknown order into fast and was loose); 14 items dormant since Mar-May
  2026 (none currently clear the revive evidence bar - see below); repeat
  rate 14% (30/215 customers with 2+ orders). Herb Paneer Delight Pizza +
  Classic French Fries (n=4) is the highest-*n* pair but **not** the top
  pair anymore once `pairs` is sorted by lift (its lift is only 1.12, barely
  above chance) — the highest-lift pairs with n>=3 lead instead (see pairs
  sorting below).
- `data/item_costs.csv` (gitignored; `.example` tracked) is optional and wins
  over `silver.menu_items.unit_cost` where both exist. Either source present
  -> menu quadrant/`unit_margin` use contribution margin and
  `meta.has_cost_data` is true (computed by checking whether any menu row got
  a margin, not by checking file existence). Absent -> quadrant uses unit
  price only, called out in the UI/brief rather than silently assumed.
- Upstream tables added to the warehouse 13 Aug 2026, all optional at read
  time (build.py checks `information_schema.tables` first and degrades to
  local computation if a table is missing — never crashes on an older
  warehouse): `gold.item_prices` (source of truth for `prices`; local mode
  inference is the fallback; `analytics.price_source` records which ran),
  `silver.menu_items` (`category` drives the attach main/side split and is
  exposed on every `menu[]` row; `unit_cost` feeds contribution margin),
  `gold.data_quality` (passed through verbatim as `analytics.data_quality`
  and rendered in `weekly_brief.md`'s "Data you can and cannot trust"
  section).
- `revive` actions require `units_lifetime>=5` AND `>=3` distinct active
  weeks before they get a rupee figure — below that bar an item stays in the
  `dormant` list but the action (if any) carries `impact_value: null` and
  "too few sales to estimate". `weekly_rate_when_active` divides by the
  item's full observed span (first_sold to earlier of last_sold+30d and the
  dataset end), not by the few weeks it happened to sell in — dividing by a
  short window turns a fluke burst into a confident-looking rate. Any revive
  impact is capped at the item's own best observed 4-active-week revenue
  (`_best_window_revenue`) and confidence is `low` unless the item cleared 15
  lifetime units.
- Every action with fewer than 5 underlying observations carries
  `confidence: "low"` and the sample size in its `evidence` string, or isn't
  emitted at all. The action-ranking score only gives a "qualitative" boost
  (huge effect size, no rupee figure) to the prep-time ops action
  (`_qualitative_priority`); every other null-impact action (e.g. a
  below-evidence-bar dormant note) scores near zero, never outranking a real
  numeric action.
- `menu[].trend_pct` is null when the prior 4-active-week base totals fewer
  than 3 units (no meaningful base for a percentage) and is clamped to
  ±200% otherwise; `trend_units_prior`/`trend_units_recent` (additive fields)
  always carry the raw counts so the UI can show "3 units → 0 units" instead
  of a nonsense percentage.
- `demand.closure_options`: candidates are contiguous 2-4 hour weekday-hour
  blocks (not the stricter `quiet_windows` list — bottom-decile, >=2-hour-run
  — which stays spec-exact as its own descriptive field but was too strict to
  drive closure ranking on ~8 orders/week of data). A zero-order block ranks
  first, not disqualified. The "exclude a weekday carrying a peak window"
  rule applies **only to the `weekday` scope** (closing a whole day always
  costs something, so nothing is excluded there — rank all 7, cheapest 5
  win). For `weekly`/`monthly` scopes a block is excluded only if it
  *overlaps* that weekday's own peak window(s) — a dinner rush on Monday
  says nothing about whether Monday 2-4pm is safe to close. (First cut of
  this got it backwards: excluding the whole weekday for all three scopes,
  which meant every scope came back empty since every weekday has some peak
  hour at this volume — fixed by the coordinator's correction.) Every
  `verdict` states both the rupee cost and its share of revenue, and says so
  explicitly when a block has zero historical orders ("no orders ever
  recorded in this window") rather than reporting ₹0. Current top options:
  weekly/monthly best = Mondays 22:00-24:00 (₹0, 0% — genuinely zero
  history); weekday best = close every Monday (~₹1,834/mo, 12% of revenue).
- The `REVIVE_MIN_UNITS`/`REVIVE_MIN_ACTIVE_WEEKS` (5/3) evidence gate is
  shared between the `revive` action AND `dormant[].estimated_lost_revenue`
  itself (`compute_dormant` applies it directly; `compute_actions` reads the
  gate result off `dormant[i]["estimated_lost_revenue"] is not None` rather
  than recomputing it — single source of truth). Below the gate,
  `estimated_lost_revenue` is null and the additive `dormant[].reason` field
  explains why ("N units in M days - too little history to size"); the row
  stays in the table either way. As of the current warehouse, **none** of
  the 14 dormant items clear the bar (max 3 units / 3 active weeks), so the
  whole `dormant` table currently shows null rupee figures across the board
  — that's correct, not a bug, given the data.
- `pairs[]` is sorted by `lift` descending (n as tiebreak), not by `n` —
  sorting by n alone buried a 6.5x-lift pair below a sub-1x one.
  `suggested_combo_price` (and any `combo`-kind action) only fires when
  `lift >= 1.2` AND `n >= 3`; pairs with `lift < 1` (co-occur *less* than
  chance) get the additive `reads_as: "less often than chance"` instead of a
  price, so the UI can't accidentally present anti-correlated items as a
  recommendation.
- `attach[]` excludes mains with <5 delivered orders entirely (counted in
  the sibling `analytics.attach_excluded` list, not silently dropped), and
  the `best_observed_attach_rate` behind every row's `gap_value` only
  considers mains with >=10 orders — a first cut let a 2-order main set a
  50% "benchmark" and inflated the total opportunity figure to ~₹13,780;
  capped, the real total is ~₹961 across all mains.
- `actions[].impact_period` (`"monthly"` | `"one_time"`) is required on
  every action — the win-back estimate is the only `"one_time"` one
  (everything else recurs monthly); without it the UI had no way to know
  not to append "/mo" to a one-off figure.
- Generated text (evidence/verdict/detail/headline strings in `analytics.py`
  and `weekly_brief.py`) uses `_rupees()`/`_fmt_money()` — ₹, comma
  thousands, whole rupees — never "Rs." or raw unrounded floats. The only
  "Rs." left in the payload is inside literal `discount_construct` source
  strings ("50% off upto Rs.100"), which are raw data and correctly
  untouched.
- `quality.rating_drivers` drops any bucket with n<2 (a single order isn't a
  "driver", and sat next to n=44 it visually read as one). `quality.funnel`
  stage labels are human text ("Rated 4★ or above"), not codes.
- `discounts[].verdict` is built per-row from that construct's own
  AOV-vs-baseline and repeat-rate-vs-baseline numbers (no shared stub
  sentence anymore), and the additive `discounts[].funded_by`
  (restaurant/platform/mixed/none) makes explicit whose money
  `discount_funded` counts, since the field name alone doesn't say — 5 of 6
  constructs show `discount_funded: 0` because they're Gold/platform-funded,
  not because the number is wrong.
- The dashboard is six tabs (Plan, Menu, Combos, Customers, Quality, Demand)
  behind a filter row (date presets, custom from/to, status, weekday
  multi-select). Light client-side aggregates (weekly revenue, the demand
  heatmap, the quality trend charts, the item table's units/orders/revenue
  columns) recompute from `orders`+`items` and stay filter-reactive; the
  heavier derived views (prices, menu quadrants, pairs, forecast, actions,
  RFM/cohorts, funnel/drivers) render straight from `analytics` and carry a
  "full history" quiet-note since the payload is precomputed over everything.
- `template.html`'s chart engine (`template.html`) covers columns/stacked/line/
  bar plus newer forms added for the six-view surface: `scatterChart` (menu
  matrix), `heatmapChart` (weekday×hour, reused for the demand heatmap and the
  Plan prep-hour plan), `forecastBandChart` (forecast columns + interval
  band), `cohortGrid`, `sparkline` (table rows), and `actionCard`
  (headline/impact/evidence/confidence chip — `impact_value` can be null and
  must render with no rupee line, not "₹0").
- `docs/sample_analytics.json` is a hand-built mock of the `analytics` payload
  (derived from the real orders in `dashboard.html`) kept as schema
  documentation; it is not read by `build.py`.
- Colour, mark and interaction specs come from the `dataviz` skill's validated
  palette; the categorical slots in use are blue / orange / aqua, plus the
  sequential blue ramp (`--seq-100`..`--seq-700`) for the heatmap and cohort
  grid, and warning/serious added alongside good/critical for status chips.
- The warehouse path (`../the-oven-vibe-data-pipeline/warehouse.duckdb`) is a
  contract with the pipeline repo — changing it means changing both repos.
- Docs (`CLAUDE.md`, `AGENT.md`, `README.md`, this file) get updated at the end
  of every task.
