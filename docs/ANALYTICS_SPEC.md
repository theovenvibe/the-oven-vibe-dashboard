# Analytics spec — The Oven Vibe decision dashboard

This is the contract between `analytics.py` (produces the payload) and
`template.html` (renders it). Both sides build against this file. Key names here
are exact.

The dashboard's job is not to report KPIs. Its job is to answer six questions a
restaurant owner asks every Monday:

1. What should I expect next week, and how should I staff for it?
2. Which items should I drop?
3. Which items can carry a price rise?
4. What sells with what — which combos should I create?
5. Which customers are slipping away?
6. What is hurting my ratings and my fulfilment, and why?

## Ground truth and its limits

Say these out loud in the UI wherever they affect a recommendation. A number a
user can't audit is a number they won't act on.

- **No cost data exists.** The warehouse has prices, not COGS. Therefore
  "profitability" is never claimed. The menu matrix's vertical axis is **unit
  price**, and every margin-flavoured recommendation is phrased as revenue, not
  profit. If `data/item_costs.csv` exists (columns: `item_name,unit_cost`), load
  it and switch the vertical axis to contribution margin per unit, labelling it
  as such. Absent that file, show a one-line prompt telling the user that adding
  it upgrades the analysis.
- **Item prices are inferred, not given.** See below. Every inferred price
  carries a `confidence` and the UI shows it.
- **The basket data is thin** — 51 multi-item orders out of 273; top pair counts
  are 2–4. Every pair rule ships with its raw count and a `strength` of
  `indicative` (n < 5) or `solid` (n >= 5). Never render a lift figure without
  its n beside it.
- **Revenue means `order_status = 'Delivered'`.** Order counts include
  rejections and timeouts.
- **A missing CSV is not a quiet week.** The week of 8 Jun 2026 has no source
  file. Weeks whose order count is 0 are marked `no_data: true` and excluded
  from averages and forecasts rather than dragging them down.

## Price inference

1. Seed: for each item, take orders containing exactly that item, quantity 1.
   Unit price = the **mode** of `bill_subtotal` across those orders (mode, not
   mean — promo-inflated outliers exist). `confidence: "observed"`,
   `sample_n` = that count.
2. Iterate: for orders where exactly one item's price is unknown and every other
   item's price is known, solve
   `price = (bill_subtotal - Σ known_price × qty) / qty`. Take the mode across
   all such orders. `confidence: "derived"`. Repeat until no new price resolves.
3. Anything left: `unit_price: null`, `confidence: "unknown"`. Exclude from
   revenue attribution and show it as "price unknown" in the item table.

`item_revenue = unit_price × units_sold`, over delivered orders only.

## Payload schema

`build.py` writes one JSON object into `__DASHBOARD_DATA__`:

```
{
  meta: { restaurant_name, city, subzone, first_order_at, last_order_at,
          order_count, generated_at, has_cost_data: bool },
  orders: [...],        // as today, plus: is_first_order (bool), items_count
  items: [...],         // as today: order_id, quantity, item_name
  analytics: {
    prices:      [{ item_name, unit_price, confidence, sample_n }],
    menu:        [{ item_name, units, orders, revenue, revenue_share,
                    unit_price, price_confidence, quadrant, first_sold, last_sold,
                    days_dormant, trend_pct, weekly_units: [...12],
                    avg_rating_with, avg_rating_without, rating_n,
                    attach_rate, discount_dependence }],
    actions:     [{ id, kind, item_name|null, headline, detail, evidence,
                    impact_value, impact_basis, confidence, priority }],
    pairs:       [{ a, b, n, support, confidence_ab, confidence_ba, lift,
                    strength, combined_value, suggested_combo_price }],
    attach:      [{ main_item, orders, with_side, attach_rate, gap_value }],
    forecast:    { week_start, orders_expected, orders_low, orders_high,
                   revenue_expected, revenue_low, revenue_high, method,
                   by_weekday: [{ weekday, orders_expected, orders_low,
                                  orders_high, revenue_expected }],
                   basis_weeks: [{ week_start, orders, revenue }] },
    demand:      { heatmap: [{ weekday, hour, orders, revenue, avg_kpt }],
                   peak_windows: [{ weekday, hour_start, hour_end, orders, share }],
                   prep_plan: [{ weekday, hour, orders_expected }],
                   quiet_windows: [{ weekday, hour_start, hour_end, orders,
                                     revenue_at_risk, monthly_revenue_at_risk }],
                   closure_options: [{ label, scope, weekday, hour_start, hour_end,
                                       orders_lost_per_month, revenue_at_risk_per_month,
                                       share_of_revenue, verdict }] },
    quality:     { funnel: [{ stage, orders, pct }],
                   rating_drivers: [{ factor, bucket, n, avg_rating, delta }],
                   slow_orders: { threshold_min, n, avg_rating, avg_rating_fast,
                                  items: [{ item_name, n, avg_kpt }] },
                   loss_reasons: [{ reason, n, lost_value }],
                   weekly: [{ week_start, cancel_rate, avg_kpt, avg_rider_wait,
                              complaints, avg_rating }] },
    customers:   { rfm: [{ segment, customers, revenue, avg_orders, avg_recency_days }],
                   cohorts: [{ cohort_month, customers, repeat_30, repeat_60, repeat_90 }],
                   winback: [{ customer_id, orders, spend, last_order_at,
                               days_since, favourite_item }],
                   weekly_split: [{ week_start, new_customers, returning_customers,
                                    new_revenue, returning_revenue }],
                   repeat_rate_trend: [{ week_start, repeat_share }] },
    discounts:   [{ construct, orders, aov, discount_funded, net_revenue,
                    aov_vs_undiscounted, repeat_rate, verdict }],
    dormant:     [{ item_name, units_lifetime, last_sold, days_dormant,
                    weekly_rate_when_active, estimated_lost_revenue }],
    data_quality: [{ check_name, status, detail, value }],
    price_source: "gold.item_prices" | "inferred"
  }
}
```

## Upstream tables (added to the warehouse 13 Aug 2026)

Read these when present; degrade to local computation when absent, since
`--db` may point at an older warehouse.

- **`gold.item_prices`** (`item_name, unit_price, confidence, sample_n, method`)
  — the source of truth for prices. Its `confidence` enum is the same one the
  `prices` payload uses. The local inference described above stays as fallback;
  `analytics.price_source` records which path ran.
- **`silver.menu_items`** (`item_name, category, subcategory, is_veg, size,
  list_price, unit_cost, active`) — `category` is one of pizza, side, beverage,
  rice, pasta, sandwich, maggi, combo, dessert, and drives the main-vs-side
  split in the attach analysis instead of name-guessing. `category` is exposed
  on every `menu[]` row. `unit_cost`, once populated, feeds the same
  contribution-margin path as `data/item_costs.csv`; the CSV wins where both
  exist, being the owner's local override.
- **`gold.data_quality`** (`check_name, status, detail, value`, status
  `ok`/`warn`/`fail`) — surfaced verbatim as `analytics.data_quality` and
  rendered as a trust panel. The missing 8–14 Jun 2026 week appears here as a
  `warn`, which is why it must never be read as a quiet trading week.

### Additive fields beyond this list

The object shapes above are the contract; nothing here should be renamed.
`analytics.py` has, over several correctness passes, added a small number of
extra fields alongside them where the literal shape had no room for an
honesty signal a fix required. These are additive only — safe to ignore, not
safe to rely on being absent:

- `prices[]`: `method` (free-text audit string from `gold.item_prices`,
  null when inferred).
- `menu[]`: `category` (from `silver.menu_items`, null if absent),
  `unit_margin` (contribution margin, only when cost data resolved),
  `trend_units_prior`/`trend_units_recent` (raw unit counts behind
  `trend_pct`, populated even when `trend_pct` itself is null).
- `pairs[]`: `reads_as` (set to `"less often than chance"` when `lift < 1`,
  so the UI can label a pair as a non-recommendation instead of implying
  one; `suggested_combo_price` is only ever set when `lift >= 1.2` and
  `n >= 3`).
- `attach[]`: mains under 5 delivered orders are dropped from the list
  entirely (too thin to state a rate) and counted instead in the sibling
  top-level `analytics.attach_excluded: [{main_item, orders}]`. The
  benchmark rate driving every row's `gap_value` only considers mains with
  >=10 orders, so a 2-order outlier can't inflate everyone else's gap.
- `dormant[]`: `reason` (one-line explanation, set only when
  `estimated_lost_revenue` is null - see the revive evidence bar below).
- `discounts[]`: `funded_by` (`"restaurant"`/`"platform"`/`"mixed"`/`"none"`
  - `discount_funded` alone doesn't say whose money it is; this does).
- `actions[]`: `impact_period` (`"monthly"` or `"one_time"` - required so
  the UI doesn't append "/mo" to a one-off figure like the win-back
  estimate).
- `quality.slow_orders`: `n_fast` (the pure kpt<=25min bucket size, so
  actions can cite it without hardcoding a count).

A dormant item only gets a rupee `estimated_lost_revenue` (and only a
`revive` action feeds off it) once it clears **>=5 lifetime units AND >=3
distinct active weeks** - `weekly_rate_when_active` divides by the item's
full observed span, not the short window it happened to sell in, and any
`revive` action impact is capped at the item's own best observed
4-active-week revenue. Below the bar, `estimated_lost_revenue` and the
action's `impact_value` are both null, with the reason stated in `reason`/
`evidence` rather than a number.

## Metric definitions

**Menu quadrant** — split on the median of `units` (demand) and the median of
`unit_price`. `star` = high demand, high price. `plowhorse` = high demand, low
price → price-rise candidate. `puzzle` = low demand, high price → promote or
reposition. `dog` = low demand, low price → drop candidate. An item that is a
frequent attachment (appears in `pairs` with `n >= 3`) is never labelled a drop
candidate — say why in its row.

**trend_pct** — last 4 active weeks' units vs the previous 4 active weeks'
(`no_data` weeks skipped). Null when fewer than 4 active weeks exist either side.

**discount_dependence** — share of an item's orders that carried a discount
construct. High dependence weakens a price-rise recommendation.

**attach_rate** — for a main (any pizza / rice / pasta / maggi / sandwich), the
share of its orders that also contain a side (fries, corn, potato pops). The
`gap_value` is `(best_observed_attach_rate − this_attach_rate) × orders ×
median_side_price`.

**Pair stats** — `support` = orders with both ÷ total orders. `confidence_ab` =
P(B | A). `lift` = support ÷ (P(A) × P(B)). Only emit pairs with `n >= 2`.
`suggested_combo_price` = 0.9 × (price A + price B), rounded to the nearest ₹10,
emitted only when both prices are known.

**Forecast** — per weekday, a recency-weighted mean of the last 4 *active*
occurrences of that weekday (weights 0.4 / 0.3 / 0.2 / 0.1). The interval is
±1 standard deviation of those same observations, floored at 0.
`revenue_expected` = `orders_expected` × trailing 4-week AOV. `method` is a short
human string ("recency-weighted mean of last 4 same weekdays") — the UI prints it.

**Peak and quiet windows** — build the full weekday × hour grid (Mon–Sun ×
whichever hours the restaurant actually trades). `peak_windows` are the
contiguous hour runs per weekday holding the top quartile of that weekday's
orders. `quiet_windows` are contiguous runs of ≥2 hours inside trading hours
whose combined share of orders is in the bottom decile — these are the
maintenance-window candidates.

**Closure options** — the answer to "when can I shut the kitchen for
maintenance without losing money". Emit three scopes:
`weekly` (one weekday-hour block every week), `weekday` (one full weekday every
week) and `monthly` (one weekday-hour block once a month). For each, rank by
lowest `revenue_at_risk_per_month`, computed as the historical revenue in that
window scaled to a month, and set `verdict` to a plain sentence naming both
the rupee cost and its share of revenue ("closing Tuesdays 3–6pm costs about
₹420 a month, under 1% of revenue"). Where a candidate has zero historical
orders, say so explicitly ("no orders ever recorded in this window") rather
than reporting ₹0 — those read very differently to an owner. Emit the 5 best
options per scope (fewer only if genuinely unfillable, with an explicit
reason string instead of an empty list).

The "exclude a weekday carrying a peak window" rule applies **only to the
`weekday` scope** — closing a whole day always costs something, so nothing
is excluded there; rank all 7 weekdays and let the price speak. For the
`weekly` and `monthly` scopes, a candidate 2–4 hour block is excluded only
if it *overlaps* that weekday's own peak window(s); a weekday having a
dinner rush says nothing about whether a different, quiet block on that same
day is safe to close. A zero-order block is the best possible candidate, not
a disqualified one, and must rank first.

**RFM segments** — recency = days since last order, frequency = order count.
`champion` (≥3 orders, ≤30 days), `loyal` (≥2 orders, ≤60 days),
`promising` (1 order, ≤30 days), `at_risk` (≥2 orders, 61–120 days),
`lost` (>120 days). One segment per customer, first match wins.

**Win-back list** — customers with ≥2 orders whose last order is >45 days old,
ranked by lifetime spend. `favourite_item` = their most-ordered item.

**Actions** — the ranked, plain-language list the whole dashboard exists to
produce. `kind` is one of `price_up`, `drop`, `revive`, `combo`, `ops`,
`winback`, `promo`. `impact_value` is a rupee estimate per month with
`impact_basis` naming the arithmetic ("18 units/month × ₹20 rise"). `confidence`
is `high` / `medium` / `low` and reflects sample size honestly. `priority` sorts
the list: impact × confidence. Cap at 8 actions; quality beats quantity.

## Known headline findings (sanity check your output against these)

Computed from the current warehouse — if the implementation disagrees, the
implementation is wrong:

- Orders with prep time > 25 min average **2.17★** across 6 rated orders, versus
  **4.18★** across 45 fast orders. Slow kitchen is the single biggest rating
  driver.
- 14 items have not sold since March–May 2026 while the menu still carries them.
- Herb Paneer Delight Pizza is 81 units and roughly a third of item revenue —
  concentration risk worth naming.
- Fries attach to pizzas in only a handful of orders; the attach gap is real
  money and the top pair (Herb Paneer + Classic Fries, n=4) is the combo lead.
- 96 of 215 customers arrived in March and most never returned; repeat rate is
  14% overall.

## The dashboard surface

Six views, switched by a tab row that sits under the filter row. Filters
(date-range presets, custom from/to, order status, and a weekday multi-select)
sit in one row above the tabs and scope every view.

The `analytics` payload is precomputed over the full history. Views that must
respond to filters (weekly revenue, demand heatmap, quality trend, item table)
recompute client-side from `orders` + `items`; the heavier derived analyses
(prices, pairs, forecast, actions) render from the payload and show a quiet note
that they are computed over the full history, so a filtered user is never
misled about which numbers moved.

1. **Plan** — the Monday-morning view. Next week's forecast with its interval,
   forecast by weekday, the ranked action list as cards (headline, expected
   impact, evidence, confidence), the prep-hour plan, and the kitchen-closure
   options table.
2. **Menu** — the menu matrix scatter (units × price, quadrant-labelled, dot
   area = revenue), the full item table with sparkline and trend, price-rise
   candidates, drop candidates, and the dormant/revive list.
3. **Combos** — pair table with lift, n and strength; attach-rate bars per main;
   suggested combo cards with a price.
4. **Customers** — RFM segments, cohort retention grid, new vs returning revenue
   by week, repeat-rate trend, and the win-back list.
5. **Quality** — the fulfilment funnel, rating drivers (prep time first, it is
   the strongest), slow-order items, loss reasons with lost value, and the
   weekly ops trend.
6. **Demand** — weekday × hour heatmap (orders, switchable to revenue and to
   average prep time), peak windows, quiet windows, and the closure options.

Every view keeps a table underneath its charts, or a "show numbers" disclosure,
so no value is reachable only by hovering.

## The weekly brief

`build.py` also writes `weekly_brief.md` — the same analysis as prose plus a
data appendix, written for an AI agent to read and turn into a plan. Structure:
headline numbers, what changed since last week, the ranked actions with evidence
and expected impact, then appendix tables (menu, pairs, forecast, win-back).
Plain markdown, no HTML, every number carrying its sample size.
