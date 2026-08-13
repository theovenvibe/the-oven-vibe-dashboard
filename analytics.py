"""Analytics engine for The Oven Vibe decision dashboard.

Pure Python, stdlib only. Takes the `orders` and `items` rows exactly as
`build.py` fetches them (plain dicts, datetimes already ISO strings) and
returns the `analytics` dict defined in docs/ANALYTICS_SPEC.md.

Ground rules enforced everywhere in this file (see spec for the "why"):
  - Revenue = delivered orders only (`order_status == 'Delivered'`).
  - Order/unit *counts* (demand signals) use all orders regardless of status,
    unless a function's docstring says otherwise.
  - A week with zero orders is a `no_data` week (usually a missing source
    CSV) and is dropped from every weekly series and average rather than
    being emitted as a zero.
  - Every inferred number that could mislead at small n carries its n.
"""

import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta

DELIVERED = "Delivered"

MAIN_KEYWORDS = ("pizza", "fried rice", "pasta", "maggi", "sandwich")
SIDE_KEYWORDS = ("fries", "potato pops", "corn")

WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
# for display text only ("Thursdays", not "Thus") - the `weekday` field
# itself stays the 3-letter form used throughout the rest of the payload
WEEKDAY_PLURAL = {
    "Mon": "Mondays", "Tue": "Tuesdays", "Wed": "Wednesdays", "Thu": "Thursdays",
    "Fri": "Fridays", "Sat": "Saturdays", "Sun": "Sundays",
}
WEEKDAY_FULL = {
    "Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", "Thu": "Thursday",
    "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday",
}


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def _parse_dt(value):
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


def _week_start(dt):
    """Monday of the ISO week containing dt, as a date."""
    d = dt.date() if isinstance(dt, datetime) else dt
    return d - timedelta(days=d.weekday())


def _median(values):
    values = sorted(values)
    if not values:
        return None
    return statistics.median(values)


def _mode(values, ndigits=None):
    """Most common value; ties broken by the smallest value for determinism."""
    if not values:
        return None, 0
    if ndigits is not None:
        values = [round(v, ndigits) for v in values]
    counts = Counter(values)
    best_count = max(counts.values())
    candidates = sorted(v for v, c in counts.items() if c == best_count)
    return candidates[0], best_count


MAIN_CATEGORIES = {"pizza", "rice", "pasta", "maggi", "sandwich"}
SIDE_CATEGORIES = {"side"}


def _is_main(item_name, category_map=None):
    """True if item_name is a 'main' for attach analysis.

    Uses `silver.menu_items.category` when available (pizza/rice/pasta/
    maggi/sandwich); falls back to name-keyword guessing when the table
    wasn't loaded (older warehouse).
    """
    if category_map and item_name in category_map:
        return category_map[item_name] in MAIN_CATEGORIES
    n = item_name.lower()
    return any(k in n for k in MAIN_KEYWORDS)


def _is_side(item_name, category_map=None):
    if category_map and item_name in category_map:
        return category_map[item_name] in SIDE_CATEGORIES
    n = item_name.lower()
    if _is_main(item_name, category_map):
        return False
    return any(k in n for k in SIDE_KEYWORDS)


def _round2(x):
    return round(x, 2) if x is not None else None


def _rupees(x):
    """Whole-rupee, thousands-separated string for generated text (headline/
    detail/evidence/verdict). The UI renders ₹ everywhere else - "Rs." here
    read as disagreement, not a stylistic choice."""
    if x is None:
        return "n/a"
    return f"₹{x:,.0f}"


# --------------------------------------------------------------------------
# Indexing
# --------------------------------------------------------------------------

class Index:
    """Builds the lookup structures every sub-analysis needs, once."""

    def __init__(self, orders, items):
        self.orders = orders
        for o in orders:
            o["_dt"] = _parse_dt(o["order_placed_at"])
        self.orders_by_id = {o["order_id"]: o for o in orders}

        lines_by_order = defaultdict(lambda: defaultdict(int))
        for it in items:
            lines_by_order[it["order_id"]][it["item_name"]] += it["quantity"] or 0
        self.lines_by_order = {oid: dict(lines) for oid, lines in lines_by_order.items()}

        self.item_names = sorted({it["item_name"] for it in items})

        # orders (any status) containing each item -> list of order dicts
        orders_with_item = defaultdict(list)
        for oid, lines in self.lines_by_order.items():
            order = self.orders_by_id.get(oid)
            if order is None:
                continue
            for item_name in lines:
                orders_with_item[item_name].append(order)
        self.orders_with_item = orders_with_item

        self.delivered = [o for o in orders if o["order_status"] == DELIVERED]
        self.delivered_ids = {o["order_id"] for o in self.delivered}

        if orders:
            self.last_order_at = max(o["_dt"] for o in orders)
            self.first_order_at = min(o["_dt"] for o in orders)
        else:
            self.last_order_at = self.first_order_at = None

        # weekly order buckets (any status) -> used to find no_data weeks
        weeks = defaultdict(list)
        for o in orders:
            weeks[_week_start(o["_dt"])].append(o)
        self.weeks = weeks  # week_start(date) -> [orders]
        self.active_week_starts = sorted(w for w, os in weeks.items() if len(os) > 0)


# --------------------------------------------------------------------------
# 1. Price inference
# --------------------------------------------------------------------------

def infer_prices(idx):
    """Infer a unit price per item from bill_subtotal.

    Seed: orders that contain exactly one distinct item at quantity 1 ->
    unit price is the mode of bill_subtotal across those orders
    (`confidence: observed`). Then iterate: any order where exactly one
    item's price is still unknown and every other item's price is known
    lets us solve `price = (bill_subtotal - sum(known price*qty)) / qty`;
    take the mode of those solved values per item (`confidence: derived`).
    Repeat until no new item resolves. Anything left is `unknown`.
    Uses orders of any status - bill_subtotal reflects the priced basket
    regardless of fulfilment outcome.
    """
    price = {}
    confidence = {}
    sample_n = {}

    seed_candidates = defaultdict(list)
    for oid, lines in idx.lines_by_order.items():
        if len(lines) != 1:
            continue
        (item_name, qty), = lines.items()
        if qty != 1:
            continue
        order = idx.orders_by_id.get(oid)
        if order is None or order["bill_subtotal"] is None:
            continue
        seed_candidates[item_name].append(order["bill_subtotal"])

    for item_name, values in seed_candidates.items():
        mode_val, n = _mode(values, ndigits=2)
        price[item_name] = mode_val
        confidence[item_name] = "observed"
        sample_n[item_name] = n

    changed = True
    while changed:
        changed = False
        derived_candidates = defaultdict(list)
        for oid, lines in idx.lines_by_order.items():
            unknown = [name for name in lines if name not in price]
            if len(unknown) != 1:
                continue
            target = unknown[0]
            qty = lines[target]
            if not qty:
                continue
            order = idx.orders_by_id.get(oid)
            if order is None or order["bill_subtotal"] is None:
                continue
            known_sum = sum(price[name] * q for name, q in lines.items() if name != target)
            candidate = (order["bill_subtotal"] - known_sum) / qty
            if candidate <= 0:
                continue
            derived_candidates[target].append(candidate)

        for item_name, values in derived_candidates.items():
            if item_name in price:
                continue
            mode_val, n = _mode(values, ndigits=2)
            price[item_name] = mode_val
            confidence[item_name] = "derived"
            sample_n[item_name] = n
            changed = True

    prices = []
    for item_name in idx.item_names:
        if item_name in price:
            prices.append({
                "item_name": item_name,
                "unit_price": _round2(price[item_name]),
                "confidence": confidence[item_name],
                "sample_n": sample_n[item_name],
            })
        else:
            prices.append({
                "item_name": item_name,
                "unit_price": None,
                "confidence": "unknown",
                "sample_n": 0,
            })
    return prices


def resolve_prices(idx, item_prices_table=None):
    """Resolve per-item unit price: `gold.item_prices` if the warehouse has
    it, local mode-based inference (`infer_prices`) otherwise or for any
    item the table doesn't cover. Returns (prices, price_source) where
    price_source is "gold.item_prices" or "inferred" for the payload's
    top-level `analytics.price_source`.

    The extra `method` field (free-text audit string from the warehouse) is
    passed through when available - additive, not part of the spec's
    literal `prices` schema, but costs nothing and the UI can ignore it.
    """
    inferred = infer_prices(idx)
    if not item_prices_table:
        for p in inferred:
            p["method"] = None
        return inferred, "inferred"

    table_map = {r["item_name"]: r for r in item_prices_table}
    result = []
    used_table = False
    for p in inferred:
        row = table_map.get(p["item_name"])
        if row and row.get("unit_price") is not None:
            used_table = True
            result.append({
                "item_name": p["item_name"],
                "unit_price": row["unit_price"],
                "confidence": row.get("confidence") or "observed",
                "sample_n": row.get("sample_n") if row.get("sample_n") is not None else 0,
                "method": row.get("method"),
            })
        else:
            entry = dict(p)
            entry["method"] = None
            result.append(entry)
    return result, ("gold.item_prices" if used_table else "inferred")


# --------------------------------------------------------------------------
# 2. Pairs (needed by menu quadrant + attach + combos)
# --------------------------------------------------------------------------

def compute_pairs(idx, price_map):
    """Co-occurrence stats for every pair of distinct items in the same order.

    Only orders with >=2 distinct items count. Only pairs with n>=2 are
    emitted (n=1 pairs are noise, not a rule). `support`/`confidence`/`lift`
    all use *any-status* orders as the denominator - these are ordering
    patterns, not revenue.

    `suggested_combo_price` is only ever set when `lift >= 1.2` AND `n >= 3`
    - lift < 1 means the two items co-occur *less* than chance would predict,
    so pricing a combo for them would be recommending something the data
    says customers actively don't do. Below `lift < 1`, the additive
    `reads_as` field is set to "less often than chance" so the UI can label
    it as a non-recommendation instead of implying one. Sorted by lift
    descending (n as tiebreak) so a strong-but-rare pair isn't buried under
    a weak-but-common one.
    """
    total_orders = len(idx.orders)
    orders_containing = {name: len(orders) for name, orders in idx.orders_with_item.items()}

    pair_orders = defaultdict(int)
    pair_bill_totals = defaultdict(list)
    for oid, lines in idx.lines_by_order.items():
        names = sorted(lines.keys())
        if len(names) < 2:
            continue
        order = idx.orders_by_id.get(oid)
        bill = order["total"] if order else None
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                pair_orders[(a, b)] += 1
                if bill is not None and order["order_status"] == DELIVERED:
                    pair_bill_totals[(a, b)].append(bill)

    pairs = []
    for (a, b), n in pair_orders.items():
        if n < 2:
            continue
        support = n / total_orders if total_orders else 0
        p_a = orders_containing.get(a, 0) / total_orders if total_orders else 0
        p_b = orders_containing.get(b, 0) / total_orders if total_orders else 0
        confidence_ab = n / orders_containing[a] if orders_containing.get(a) else 0
        confidence_ba = n / orders_containing[b] if orders_containing.get(b) else 0
        lift = support / (p_a * p_b) if p_a and p_b else None
        strength = "solid" if n >= 5 else "indicative"
        bills = pair_bill_totals.get((a, b), [])
        combined_value = _round2(sum(bills) / len(bills)) if bills else None

        lift_r = _round2(lift) if lift is not None else None

        suggested_combo_price = None
        price_a, price_b = price_map.get(a), price_map.get(b)
        if price_a is not None and price_b is not None and lift_r is not None and lift_r >= 1.2 and n >= 3:
            raw = 0.9 * (price_a + price_b)
            suggested_combo_price = round(raw / 10) * 10

        reads_as = "less often than chance" if lift_r is not None and lift_r < 1 else None

        pairs.append({
            "a": a, "b": b, "n": n,
            "support": _round2(support),
            "confidence_ab": _round2(confidence_ab),
            "confidence_ba": _round2(confidence_ba),
            "lift": lift_r,
            "strength": strength,
            "combined_value": combined_value,
            "suggested_combo_price": suggested_combo_price,
            "reads_as": reads_as,
        })

    pairs.sort(key=lambda p: (-(p["lift"] or 0), -p["n"]))
    return pairs


def _frequent_attachment_items(pairs):
    """Items that show up in a pair with n>=3 - never a bare drop candidate."""
    freq = set()
    for p in pairs:
        if p["n"] >= 3:
            freq.add(p["a"])
            freq.add(p["b"])
    return freq


# --------------------------------------------------------------------------
# 3. Attach rate (mains -> sides)
# --------------------------------------------------------------------------

ATTACH_MIN_ORDERS_TO_LIST = 5
ATTACH_MIN_ORDERS_FOR_BENCHMARK = 10


def compute_attach(idx, category_map=None):
    """Attach rate of a side item to a 'main' (pizza/rice/pasta/maggi/sandwich).

    Computed over delivered orders only, since it feeds a revenue-shaped
    `gap_value`. Main/side split uses `silver.menu_items.category` when
    available; falls back to name keywords otherwise (see `_is_main`/
    `_is_side`).

    Two separate sample-size bars, because "list it" and "use it to set
    everyone else's target" are different questions:
    - Mains with fewer than `ATTACH_MIN_ORDERS_TO_LIST` (5) delivered
      orders are dropped from the list entirely (a 0%-or-100% attach rate
      off 1-2 orders isn't a rate). They're counted, not silently lost -
      see the returned `excluded` list.
    - The `best_observed_attach_rate` used to compute every row's
      `gap_value` is the best rate among mains with at least
      `ATTACH_MIN_ORDERS_FOR_BENCHMARK` (10) orders. A 50% rate set by a
      main with 2 orders is not a benchmark anyone else should be held to;
      it would inflate every other item's opportunity gap off noise.

    Returns (rows, excluded) where `excluded` is
    `[{main_item, orders}]` for mains that didn't clear the listing bar -
    additive, not part of the spec's literal `attach` schema, surfaced only
    in the weekly brief's footnote.
    """
    price_map = {p["item_name"]: p["unit_price"] for p in idx._prices}
    side_prices = [price_map[n] for n in idx.item_names
                   if _is_side(n, category_map) and price_map.get(n) is not None]
    median_side_price = _median(side_prices) or 0

    rows = []
    excluded = []
    for item_name in idx.item_names:
        if not _is_main(item_name, category_map):
            continue
        orders = [o for o in idx.orders_with_item[item_name] if o["order_status"] == DELIVERED]
        n_orders = len(orders)
        if n_orders == 0:
            continue
        if n_orders < ATTACH_MIN_ORDERS_TO_LIST:
            excluded.append({"main_item": item_name, "orders": n_orders})
            continue
        with_side = 0
        for o in orders:
            lines = idx.lines_by_order.get(o["order_id"], {})
            if any(_is_side(n, category_map) for n in lines if n != item_name):
                with_side += 1
        attach_rate = with_side / n_orders
        rows.append({
            "main_item": item_name,
            "orders": n_orders,
            "with_side": with_side,
            "attach_rate": _round2(attach_rate),
        })

    benchmark_candidates = [r["attach_rate"] for r in rows if r["orders"] >= ATTACH_MIN_ORDERS_FOR_BENCHMARK]
    best_rate = max(benchmark_candidates, default=0) or 0
    for r in rows:
        r["gap_value"] = _round2(max(0.0, best_rate - r["attach_rate"]) * r["orders"] * median_side_price)

    rows.sort(key=lambda r: -r["gap_value"])
    return rows, excluded


# --------------------------------------------------------------------------
# 4. Menu matrix
# --------------------------------------------------------------------------

def compute_menu(idx, prices, pairs, attach_rows, item_costs=None, category_map=None):
    """Per-item demand/price/quality summary + quadrant classification.

    `units`/`orders` count any order status (demand signal). `revenue` uses
    delivered orders and a known unit price only. Quadrant is a median split
    of units (demand) vs a vertical measure. That vertical measure is
    unit_price by default; if `item_costs` (item_name -> unit_cost) is
    supplied, it switches to contribution margin per unit
    (unit_price - unit_cost) instead, since that is closer to what "star"
    vs "dog" should mean once cost is known. The extra `unit_margin` field
    is additive - `unit_price` keeps its spec meaning either way.

    `category_map` (item_name -> category from silver.menu_items), when
    given, is exposed on every row as `category` and also stashed on `idx`
    for the attach/dormant/revive functions that need it.
    """
    price_map = {p["item_name"]: p["unit_price"] for p in prices}
    price_conf = {p["item_name"]: p["confidence"] for p in prices}
    attach_map = {r["main_item"]: r["attach_rate"] for r in attach_rows}
    freq_attach_items = _frequent_attachment_items(pairs)
    category_map = category_map or {}

    overall_rated = [o["rating"] for o in idx.orders if o["rating"] is not None]

    # last 12 calendar weeks, chronological
    all_weeks_sorted = sorted(idx.weeks.keys())
    last_12_weeks = all_weeks_sorted[-12:] if len(all_weeks_sorted) >= 12 else all_weeks_sorted

    active_weeks_sorted = idx.active_week_starts

    rows = []
    total_revenue_known = 0.0
    item_revenue = {}
    item_weekly_all = {}         # item -> {week_start: units}, any status
    item_weekly_delivered = {}   # item -> {week_start: units}, delivered only

    for item_name in idx.item_names:
        orders_any = idx.orders_with_item[item_name]
        units = sum(idx.lines_by_order[o["order_id"]].get(item_name, 0) for o in orders_any)
        orders_count = len(orders_any)

        unit_price = price_map.get(item_name)
        delivered_orders = [o for o in orders_any if o["order_status"] == DELIVERED]
        if unit_price is not None:
            revenue = sum(idx.lines_by_order[o["order_id"]].get(item_name, 0) * unit_price for o in delivered_orders)
        else:
            revenue = 0.0
        item_revenue[item_name] = revenue
        total_revenue_known += revenue

        first_sold = min(o["_dt"] for o in orders_any).isoformat()
        last_sold_dt = max(o["_dt"] for o in orders_any)
        last_sold = last_sold_dt.isoformat()
        days_dormant = (idx.last_order_at - last_sold_dt).days

        weekly_by_week = defaultdict(int)
        weekly_by_week_delivered = defaultdict(int)
        for o in orders_any:
            wk = _week_start(o["_dt"])
            qty = idx.lines_by_order[o["order_id"]].get(item_name, 0)
            weekly_by_week[wk] += qty
            if o["order_status"] == DELIVERED:
                weekly_by_week_delivered[wk] += qty
        item_weekly_all[item_name] = dict(weekly_by_week)
        item_weekly_delivered[item_name] = dict(weekly_by_week_delivered)
        weekly_units = [weekly_by_week.get(wk, 0) for wk in last_12_weeks]

        # trend_pct: last 4 active weeks vs previous 4 active weeks (skip
        # no_data weeks). Null when the prior period totals fewer than 3
        # units - a base that thin turns any change into a meaningless
        # percentage (e.g. 1 -> 0 unit is "-100%", 0 -> 1 unit is
        # undefined). trend_units_prior/recent are always populated when
        # there's enough week history, so the UI can show the raw counts
        # even when trend_pct itself is null. Clamped to +-200% so one
        # genuinely small-but-nonzero base can't blow out an axis.
        trend_pct = None
        trend_units_prior = None
        trend_units_recent = None
        if len(active_weeks_sorted) >= 8:
            last4 = active_weeks_sorted[-4:]
            prev4 = active_weeks_sorted[-8:-4]
            trend_units_recent = sum(weekly_by_week.get(w, 0) for w in last4)
            trend_units_prior = sum(weekly_by_week.get(w, 0) for w in prev4)
            if trend_units_prior >= 3:
                raw = (trend_units_recent - trend_units_prior) / trend_units_prior * 100
                trend_pct = _round2(max(-200.0, min(200.0, raw)))

        rated_with = [o["rating"] for o in orders_any if o["rating"] is not None]
        rating_n = len(rated_with)
        avg_rating_with = _round2(sum(rated_with) / rating_n) if rating_n else None
        without_ids = set(o["order_id"] for o in orders_any)
        rated_without_vals = [
            o["rating"] for o in idx.orders
            if o["rating"] is not None and o["order_id"] not in without_ids
        ]
        avg_rating_without = _round2(sum(rated_without_vals) / len(rated_without_vals)) if rated_without_vals else None

        discounted = sum(1 for o in orders_any if o.get("discount_construct"))
        discount_dependence = _round2(discounted / orders_count) if orders_count else 0

        unit_cost = (item_costs or {}).get(item_name)
        unit_margin = _round2(unit_price - unit_cost) if (unit_price is not None and unit_cost is not None) else None

        rows.append({
            "item_name": item_name,
            "category": category_map.get(item_name),
            "units": units,
            "orders": orders_count,
            "revenue": _round2(revenue),
            "unit_price": unit_price,
            "unit_margin": unit_margin,
            "price_confidence": price_conf.get(item_name, "unknown"),
            "first_sold": first_sold,
            "last_sold": last_sold,
            "days_dormant": days_dormant,
            "trend_pct": trend_pct,
            "trend_units_prior": trend_units_prior,
            "trend_units_recent": trend_units_recent,
            "weekly_units": weekly_units,
            "avg_rating_with": avg_rating_with,
            "avg_rating_without": avg_rating_without,
            "rating_n": rating_n,
            "attach_rate": attach_map.get(item_name),
            "discount_dependence": discount_dependence,
            "_is_frequent_attachment": item_name in freq_attach_items,
        })

    for r in rows:
        r["revenue_share"] = _round2(r["revenue"] / total_revenue_known) if total_revenue_known else 0.0

    use_margin = bool(item_costs)
    vertical_key = "unit_margin" if use_margin else "unit_price"
    priced_units = [r["units"] for r in rows if r[vertical_key] is not None]
    priced_values = [r[vertical_key] for r in rows if r[vertical_key] is not None]
    median_units = _median(priced_units) or 0
    median_value = _median(priced_values) or 0

    for r in rows:
        if r[vertical_key] is None:
            r["quadrant"] = None
            continue
        high_demand = r["units"] >= median_units
        high_price = r[vertical_key] >= median_value
        if high_demand and high_price:
            r["quadrant"] = "star"
        elif high_demand and not high_price:
            r["quadrant"] = "plowhorse"
        elif not high_demand and high_price:
            r["quadrant"] = "puzzle"
        else:
            r["quadrant"] = "dog"

    rows.sort(key=lambda r: -r["revenue"])

    # stashed for compute_dormant/compute_actions, which need per-week
    # history without recomputing it
    idx._item_weekly_all = item_weekly_all
    idx._item_weekly_delivered = item_weekly_delivered

    return rows


# --------------------------------------------------------------------------
# 5. Forecast
# --------------------------------------------------------------------------

def compute_forecast(idx):
    """Next-week forecast, per weekday, from a recency-weighted mean.

    For each weekday, take the last 4 calendar occurrences of that weekday
    that fall inside an *active* week (weeks with a source file / any
    orders), weighted 0.4/0.3/0.2/0.1 most-recent-first. Interval is +-1
    stdev of those same 4 values, floored at 0.
    """
    if not idx.orders:
        return {
            "week_start": None, "orders_expected": 0, "orders_low": 0, "orders_high": 0,
            "revenue_expected": 0, "revenue_low": 0, "revenue_high": 0,
            "method": "recency-weighted mean of last 4 same weekdays (insufficient data)",
            "by_weekday": [], "basis_weeks": [],
        }

    active_week_set = set(idx.active_week_starts)

    daily_orders = defaultdict(int)
    daily_revenue = defaultdict(float)
    for o in idx.orders:
        d = o["_dt"].date()
        daily_orders[d] += 1
        if o["order_status"] == DELIVERED and o["total"] is not None:
            daily_revenue[d] += o["total"]

    last_week_start = max(idx.active_week_starts)
    next_week_start = last_week_start + timedelta(days=7)

    weights = [0.4, 0.3, 0.2, 0.1]
    by_weekday = []
    total_expected = total_low = total_high = 0.0

    # trailing 4-week AOV over delivered orders, most recent 4 active weeks
    last4_active_weeks = idx.active_week_starts[-4:]
    delivered_in_window = [
        o for o in idx.delivered if _week_start(o["_dt"]) in set(last4_active_weeks)
    ]
    if delivered_in_window:
        aov = sum(o["total"] for o in delivered_in_window if o["total"] is not None) / len(delivered_in_window)
    else:
        aov = sum(o["total"] for o in idx.delivered if o["total"] is not None) / len(idx.delivered) if idx.delivered else 0

    for wd in range(7):  # 0=Mon
        target_date = next_week_start + timedelta(days=wd)
        # walk backwards from the day before target, collecting occurrences
        # of this weekday inside active weeks
        obs = []
        cursor = target_date - timedelta(days=7)
        guard = 0
        while len(obs) < 4 and cursor >= idx.first_order_at.date() and guard < 260:
            guard += 1
            if _week_start(cursor) in active_week_set:
                obs.append(daily_orders.get(cursor, 0))
            cursor -= timedelta(days=7)
        # obs[0] is most recent
        n = len(obs)
        if n == 0:
            expected = 0.0
            low = high = 0.0
        else:
            w = weights[:n]
            wsum = sum(w)
            w = [x / wsum for x in w]
            expected = sum(o * wi for o, wi in zip(obs, w))
            sd = statistics.stdev(obs) if n >= 2 else 0.0
            low = max(0.0, expected - sd)
            high = expected + sd

        by_weekday.append({
            "weekday": WEEKDAY_NAMES[wd],
            "orders_expected": _round2(expected),
            "orders_low": _round2(low),
            "orders_high": _round2(high),
            "revenue_expected": _round2(expected * aov),
        })
        total_expected += expected
        total_low += low
        total_high += high

    basis_weeks = []
    for wk in idx.active_week_starts[-8:]:
        wk_orders = idx.weeks[wk]
        wk_revenue = sum(o["total"] for o in wk_orders if o["order_status"] == DELIVERED and o["total"] is not None)
        basis_weeks.append({
            "week_start": wk.isoformat(),
            "orders": len(wk_orders),
            "revenue": _round2(wk_revenue),
        })

    return {
        "week_start": next_week_start.isoformat(),
        "orders_expected": _round2(total_expected),
        "orders_low": _round2(total_low),
        "orders_high": _round2(total_high),
        "revenue_expected": _round2(total_expected * aov),
        "revenue_low": _round2(total_low * aov),
        "revenue_high": _round2(total_high * aov),
        "method": "recency-weighted mean of last 4 same weekdays (0.4/0.3/0.2/0.1), +-1 stdev interval",
        "by_weekday": by_weekday,
        "basis_weeks": basis_weeks,
    }


# --------------------------------------------------------------------------
# 6. Demand: heatmap, peak/quiet windows, prep plan, closure options
# --------------------------------------------------------------------------

def compute_demand(idx):
    """Weekday x hour demand, and where the kitchen can safely close.

    `trading hours` = the set of hours that appear anywhere in the order
    history. Peak windows = contiguous hour runs per weekday holding that
    weekday's top-quartile order counts. Quiet windows = contiguous runs of
    >=2 trading hours in the bottom decile (a descriptive field, kept spec-
    exact; not what drives closure ranking below).

    Closure options rank candidate windows by lowest revenue put at risk,
    scaled to a month. The "never recommend a weekday carrying a peak
    window" exclusion applies only to the `weekday` scope (closing a whole
    day) - a weekday having a dinner rush says nothing about whether some
    other 2-4 hour block on that same day is safe to close, so `weekly`/
    `monthly` scopes instead exclude a candidate block only if it overlaps
    that weekday's own peak window(s). `weekday` scope excludes nothing:
    closing a whole day always costs something, and the option's job is to
    show the cost, not hide it behind an exclusion.
    """
    cell_orders = defaultdict(int)
    cell_revenue = defaultdict(float)
    cell_kpt = defaultdict(list)
    weekday_totals = defaultdict(int)
    trading_hours = set()

    for o in idx.orders:
        wd = o["_dt"].weekday()
        hr = o["_dt"].hour
        trading_hours.add(hr)
        cell_orders[(wd, hr)] += 1
        weekday_totals[wd] += 1
        if o["order_status"] == DELIVERED and o["total"] is not None:
            cell_revenue[(wd, hr)] += o["total"]
        if o["kpt_duration_min"] is not None:
            cell_kpt[(wd, hr)].append(o["kpt_duration_min"])

    trading_hours = sorted(trading_hours)

    heatmap = []
    for wd in range(7):
        for hr in trading_hours:
            n = cell_orders.get((wd, hr), 0)
            kpts = cell_kpt.get((wd, hr), [])
            heatmap.append({
                "weekday": WEEKDAY_NAMES[wd],
                "hour": hr,
                "orders": n,
                "revenue": _round2(cell_revenue.get((wd, hr), 0.0)),
                "avg_kpt": _round2(sum(kpts) / len(kpts)) if kpts else None,
            })

    def contiguous_runs(hours):
        hours = sorted(hours)
        runs = []
        cur = []
        for h in hours:
            if cur and h != cur[-1] + 1:
                runs.append(cur)
                cur = []
            cur.append(h)
        if cur:
            runs.append(cur)
        return runs

    peak_windows = []
    peak_weekdays = set()
    for wd in range(7):
        counts = [cell_orders.get((wd, h), 0) for h in trading_hours]
        if not counts or weekday_totals[wd] == 0:
            continue
        # top quartile threshold: 75th percentile of counts
        sc = sorted(counts)
        idx75 = max(0, int(round(0.75 * (len(sc) - 1))))
        q3 = sc[idx75]
        top_hours = [h for h, c in zip(trading_hours, counts) if c > 0 and c >= q3 and q3 > 0]
        for run in contiguous_runs(top_hours):
            orders_in_run = sum(cell_orders.get((wd, h), 0) for h in run)
            peak_windows.append({
                "weekday": WEEKDAY_NAMES[wd],
                "hour_start": run[0],
                "hour_end": run[-1] + 1,
                "orders": orders_in_run,
                "share": _round2(orders_in_run / weekday_totals[wd]),
            })
            peak_weekdays.add(wd)

    # `quiet_windows` (schema field): contiguous runs of >=2 hours in the
    # bottom decile of that weekday's order distribution - a descriptive
    # signal, kept exactly to spec. Closure *options* below are built
    # separately and more permissively (see the note there): with ~8
    # orders/week spread over a dozen trading hours, most weekday-hour
    # cells are legitimately zero, and requiring "bottom decile" plus a
    # 2-hour run threw most of them away, which is why closure_options
    # used to come back empty.
    quiet_windows = []
    for wd in range(7):
        counts = [cell_orders.get((wd, h), 0) for h in trading_hours]
        if not counts:
            continue
        sc = sorted(counts)
        idx10 = max(0, int(round(0.10 * (len(sc) - 1))))
        decile_thresh = sc[idx10]
        quiet_hours = [h for h, c in zip(trading_hours, counts) if c <= decile_thresh]
        for run in contiguous_runs(quiet_hours):
            if len(run) < 2:
                continue
            orders_in_run = sum(cell_orders.get((wd, h), 0) for h in run)
            revenue_in_run = sum(cell_revenue.get((wd, h), 0.0) for h in run)
            monthly_revenue = revenue_in_run / max(1, len(idx.active_week_starts)) * 4.33
            quiet_windows.append({
                "weekday": WEEKDAY_NAMES[wd],
                "hour_start": run[0],
                "hour_end": run[-1] + 1,
                "orders": orders_in_run,
                "revenue_at_risk": _round2(revenue_in_run),
                "monthly_revenue_at_risk": _round2(monthly_revenue),
            })

    quiet_windows.sort(key=lambda w: w["monthly_revenue_at_risk"])

    prep_plan = []
    n_active_weeks = max(1, len(idx.active_week_starts))
    for wd in range(7):
        for hr in trading_hours:
            n = cell_orders.get((wd, hr), 0)
            prep_plan.append({
                "weekday": WEEKDAY_NAMES[wd],
                "hour": hr,
                "orders_expected": _round2(n / n_active_weeks),
            })

    total_revenue = sum(o["total"] for o in idx.delivered if o["total"] is not None)
    n_weeks_span = max(1, len(idx.active_week_starts))
    monthly_total_revenue = total_revenue / n_weeks_span * 4.33 if total_revenue else 0

    # Closure-option candidates.
    #
    # The "never recommend a weekday carrying a peak window" rule makes
    # sense only for the `weekday` scope (shutting the whole day) - a
    # weekday having a dinner rush says nothing about whether a 2-3 hour
    # block on that same weekday, away from the rush, is safe to close.
    # So: `weekly`/`monthly` scopes exclude a candidate block only if it
    # OVERLAPS that weekday's own peak window(s); `weekday` scope excludes
    # nothing at all - closing a whole day always costs something, and the
    # point of the option is to show the owner the price, not to hide it.
    def _fmt_verdict(prefix, rev, share, orders=0):
        # A window can hold orders and still carry no revenue when every one
        # of them was rejected or timed out. Saying "no orders ever recorded"
        # there would be false, so the two cases read differently.
        if rev <= 0 and orders <= 0:
            return f"{prefix} has cost nothing in the available history - no orders ever recorded in this window (0% of revenue)."
        if rev <= 0:
            return f"{prefix} has cost nothing in the available history - the only orders in this window never reached a customer (0% of revenue)."
        return f"{prefix} costs about {_rupees(rev)}, {share * 100:.1f}% of revenue."

    def _reason_no_candidates(scope):
        return {
            "label": "No safe option found", "scope": scope,
            "weekday": None, "hour_start": None, "hour_end": None,
            "orders_lost_per_month": None, "revenue_at_risk_per_month": None,
            "share_of_revenue": None,
            "verdict": f"No {scope} candidates could be ranked from the available history.",
        }

    peak_ranges_by_weekday = defaultdict(list)
    for pw in peak_windows:
        peak_ranges_by_weekday[WEEKDAY_NAMES.index(pw["weekday"])].append((pw["hour_start"], pw["hour_end"]))

    def _overlaps_peak(wd, block_start, block_end):
        return any(block_start < pe and ps < block_end for ps, pe in peak_ranges_by_weekday.get(wd, []))

    # candidate 2-4 hour blocks, within contiguous stretches of trading hours
    hour_runs = contiguous_runs(trading_hours)
    best_block_by_weekday = {}  # wd -> (hour_start, hour_end, orders, revenue)
    for wd in range(7):
        candidates = []
        for run in hour_runs:
            for length in (2, 3, 4):
                for i in range(0, len(run) - length + 1):
                    block = run[i:i + length]
                    bs, be = block[0], block[-1] + 1
                    if _overlaps_peak(wd, bs, be):
                        continue
                    orders_sum = sum(cell_orders.get((wd, h), 0) for h in block)
                    revenue_sum = sum(cell_revenue.get((wd, h), 0.0) for h in block)
                    candidates.append((bs, be, orders_sum, revenue_sum))
        if not candidates:
            continue
        # lowest revenue first; ties broken by fewer orders, then by
        # preferring the longer block (more maintenance time for the same cost)
        candidates.sort(key=lambda c: (c[3], c[2], -(c[1] - c[0])))
        best_block_by_weekday[wd] = candidates[0]

    ranked_blocks = sorted(
        ((wd, *block) for wd, block in best_block_by_weekday.items()),
        key=lambda c: (c[4], c[3]),  # revenue, then orders - ascending, zero-revenue ranks first
    )

    weekly_options = []
    for wd, bs, be, n, rev in ranked_blocks[:5]:
        monthly_rev = _round2(rev / n_weeks_span * 4.33)
        monthly_orders = _round2(n / n_weeks_span * 4.33)
        share = _round2(monthly_rev / monthly_total_revenue) if monthly_total_revenue else 0
        label = f"{WEEKDAY_PLURAL[WEEKDAY_NAMES[wd]]} {bs}:00-{be}:00"
        weekly_options.append({
            "label": label, "scope": "weekly",
            "weekday": WEEKDAY_NAMES[wd], "hour_start": bs, "hour_end": be,
            "orders_lost_per_month": monthly_orders,
            "revenue_at_risk_per_month": monthly_rev,
            "share_of_revenue": share,
            "verdict": _fmt_verdict(f"Closing {label} every week", monthly_rev, share, n),
        })
    if not weekly_options:
        weekly_options = [_reason_no_candidates("weekly")]

    monthly_options = []
    for wd, bs, be, n, rev in ranked_blocks[:5]:
        # closed once a month, not every week: cost is one occurrence, not x4.33
        once_rev = _round2(rev / n_weeks_span)
        once_orders = _round2(n / n_weeks_span)
        share = _round2(once_rev / monthly_total_revenue) if monthly_total_revenue else 0
        label = f"One {WEEKDAY_FULL[WEEKDAY_NAMES[wd]]} {bs}:00-{be}:00 a month"
        monthly_options.append({
            "label": label, "scope": "monthly",
            "weekday": WEEKDAY_NAMES[wd], "hour_start": bs, "hour_end": be,
            "orders_lost_per_month": once_orders,
            "revenue_at_risk_per_month": once_rev,
            "share_of_revenue": share,
            "verdict": _fmt_verdict(f"Closing {label}", once_rev, share, n),
        })
    if not monthly_options:
        monthly_options = [_reason_no_candidates("monthly")]

    # weekday scope: rank all 7 weekdays, excluding nothing - closing a
    # whole day always has a cost, and the option's job is to show it.
    weekday_rev = defaultdict(float)
    weekday_orders_count = defaultdict(int)
    for o in idx.orders:
        wd = o["_dt"].weekday()
        weekday_orders_count[wd] += 1
        if o["order_status"] == DELIVERED and o["total"] is not None:
            weekday_rev[wd] += o["total"]
    weekday_options = []
    for wd in range(7):
        monthly_rev = weekday_rev[wd] / n_weeks_span * 4.33
        share = _round2(monthly_rev / monthly_total_revenue) if monthly_total_revenue else 0
        label = f"Close every {WEEKDAY_FULL[WEEKDAY_NAMES[wd]]}"
        weekday_options.append({
            "label": label, "scope": "weekday",
            "weekday": WEEKDAY_NAMES[wd], "hour_start": trading_hours[0] if trading_hours else 0,
            "hour_end": (trading_hours[-1] + 1) if trading_hours else 0,
            "orders_lost_per_month": _round2(weekday_orders_count[wd] / n_weeks_span * 4.33),
            "revenue_at_risk_per_month": _round2(monthly_rev),
            "share_of_revenue": share,
            "verdict": _fmt_verdict(label, monthly_rev, share, weekday_orders_count[wd]),
        })
    weekday_options.sort(key=lambda w: w["revenue_at_risk_per_month"])
    weekday_options = weekday_options[:5]
    if not weekday_options:
        weekday_options = [_reason_no_candidates("weekday")]

    return {
        "heatmap": heatmap,
        "peak_windows": peak_windows,
        "prep_plan": prep_plan,
        "quiet_windows": quiet_windows,
        "closure_options": weekly_options + weekday_options + monthly_options,
    }


# --------------------------------------------------------------------------
# 7. Quality
# --------------------------------------------------------------------------

def compute_quality(idx):
    """Fulfilment funnel, rating drivers, slow-order penalty, loss reasons.

    Prep time is split into three honest buckets among *rated* orders:
    slow (kpt_duration_min > 25), fast (kpt_duration_min <= 25), and
    unknown (kpt not recorded). Earlier drafts folded "unknown" into
    "fast" to match a headline query that turned out to be loose; keeping
    unknown separate means `avg_rating_fast` only ever describes orders we
    actually timed.
    """
    total = len(idx.orders)
    delivered = idx.delivered
    rated = [o for o in idx.orders if o["rating"] is not None]
    positive = [o for o in rated if o["rating"] >= 4]

    # "stage" is a human label (the UI renders it directly, not a code the
    # UI has to translate) - keep it plain English if it ever changes.
    funnel = [
        {"stage": "Placed", "orders": total, "pct": 100.0},
        {"stage": "Delivered", "orders": len(delivered), "pct": _round2(len(delivered) / total * 100) if total else 0},
        {"stage": "Rated", "orders": len(rated), "pct": _round2(len(rated) / total * 100) if total else 0},
        {"stage": "Rated 4★ or above", "orders": len(positive), "pct": _round2(len(positive) / total * 100) if total else 0},
    ]

    overall_avg = sum(o["rating"] for o in rated) / len(rated) if rated else None

    def driver_row(factor, bucket, subset):
        n = len(subset)
        # n=1 isn't a "driver" - it's one order. A single-order average
        # reads visually next to n=44 as if they carried equal weight, so
        # it's dropped rather than emitted looking like a finding.
        if n < 2:
            return None
        avg = sum(o["rating"] for o in subset) / n
        return {
            "factor": factor, "bucket": bucket, "n": n,
            "avg_rating": _round2(avg),
            "delta": _round2(avg - overall_avg) if overall_avg is not None else None,
        }

    slow = [o for o in rated if o["kpt_duration_min"] is not None and o["kpt_duration_min"] > 25]
    fast = [o for o in rated if o["kpt_duration_min"] is not None and o["kpt_duration_min"] <= 25]
    unknown_kpt = [o for o in rated if o["kpt_duration_min"] is None]
    rating_drivers = [r for r in [
        driver_row("prep_time", "slow (>25min)", slow),
        driver_row("prep_time", "fast (<=25min)", fast),
        driver_row("prep_time", "unknown (kpt not recorded)", unknown_kpt),
        driver_row("discount", "discounted", [o for o in rated if o.get("discount_construct")]),
        driver_row("discount", "full price", [o for o in rated if not o.get("discount_construct")]),
        driver_row("rider_wait", "high (>10min)", [o for o in rated if (o["rider_wait_min"] or 0) > 10]),
        driver_row("rider_wait", "low (<=10min)", [o for o in rated if (o["rider_wait_min"] or 0) <= 10]),
    ] if r is not None]

    slow_avg = sum(o["rating"] for o in slow) / len(slow) if slow else None
    fast_avg = sum(o["rating"] for o in fast) / len(fast) if fast else None
    slow_items = defaultdict(lambda: {"n": 0, "kpts": []})
    for o in slow:
        lines = idx.lines_by_order.get(o["order_id"], {})
        for item_name in lines:
            slow_items[item_name]["n"] += 1
            if o["kpt_duration_min"] is not None:
                slow_items[item_name]["kpts"].append(o["kpt_duration_min"])
    slow_order_items = [
        {"item_name": name, "n": v["n"], "avg_kpt": _round2(sum(v["kpts"]) / len(v["kpts"])) if v["kpts"] else None}
        for name, v in sorted(slow_items.items(), key=lambda kv: -kv[1]["n"])
    ]

    slow_orders = {
        "threshold_min": 25,
        "n": len(slow),
        "avg_rating": _round2(slow_avg) if slow_avg is not None else None,
        "avg_rating_fast": _round2(fast_avg) if fast_avg is not None else None,
        "n_fast": len(fast),  # additive: the pure kpt<=25 bucket, excluding unknown-kpt orders
        "items": slow_order_items,
    }

    lost = [o for o in idx.orders if o["order_status"] != DELIVERED]
    loss_by_reason = defaultdict(lambda: {"n": 0, "value": 0.0})
    for o in lost:
        reason = o.get("cancellation_reason") or o["order_status"]
        loss_by_reason[reason]["n"] += 1
        loss_by_reason[reason]["value"] += o["total"] or 0
    loss_reasons = [
        {"reason": reason, "n": v["n"], "lost_value": _round2(v["value"])}
        for reason, v in sorted(loss_by_reason.items(), key=lambda kv: -kv[1]["value"])
    ]

    weekly = []
    for wk in idx.active_week_starts:
        wk_orders = idx.weeks[wk]
        n = len(wk_orders)
        cancelled = [o for o in wk_orders if o["order_status"] != DELIVERED]
        kpts = [o["kpt_duration_min"] for o in wk_orders if o["kpt_duration_min"] is not None]
        waits = [o["rider_wait_min"] for o in wk_orders if o["rider_wait_min"] is not None]
        complaints = [o for o in wk_orders if o.get("customer_complaint_tag")]
        ratings = [o["rating"] for o in wk_orders if o["rating"] is not None]
        weekly.append({
            "week_start": wk.isoformat(),
            "cancel_rate": _round2(len(cancelled) / n) if n else 0,
            "avg_kpt": _round2(sum(kpts) / len(kpts)) if kpts else None,
            "avg_rider_wait": _round2(sum(waits) / len(waits)) if waits else None,
            "complaints": len(complaints),
            "avg_rating": _round2(sum(ratings) / len(ratings)) if ratings else None,
        })

    return {
        "funnel": funnel,
        "rating_drivers": rating_drivers,
        "slow_orders": slow_orders,
        "loss_reasons": loss_reasons,
        "weekly": weekly,
    }


# --------------------------------------------------------------------------
# 8. Customers
# --------------------------------------------------------------------------

def compute_customers(idx):
    """RFM segmentation, cohort retention, win-back list, weekly new/returning split.

    Recency is measured against the dataset's last order date (not "today"),
    since this is a static historical export. `repeat_rate` overall =
    customers with >=2 orders / all customers (matches the spec's 14%).
    """
    by_customer = defaultdict(list)
    for o in idx.orders:
        if o["customer_id"] is not None:
            by_customer[o["customer_id"]].append(o)
    for cid in by_customer:
        by_customer[cid].sort(key=lambda o: o["_dt"])

    now = idx.last_order_at

    segments = defaultdict(lambda: {"customers": 0, "revenue": 0.0, "orders_sum": 0, "recency_sum": 0})
    for cid, os_ in by_customer.items():
        n_orders = len(os_)
        last_dt = os_[-1]["_dt"]
        recency_days = (now - last_dt).days
        if n_orders >= 3 and recency_days <= 30:
            seg = "champion"
        elif n_orders >= 2 and recency_days <= 60:
            seg = "loyal"
        elif n_orders == 1 and recency_days <= 30:
            seg = "promising"
        elif n_orders >= 2 and 61 <= recency_days <= 120:
            seg = "at_risk"
        elif recency_days > 120:
            seg = "lost"
        else:
            seg = "other"
        revenue = sum(o["total"] or 0 for o in os_ if o["order_status"] == DELIVERED)
        s = segments[seg]
        s["customers"] += 1
        s["revenue"] += revenue
        s["orders_sum"] += n_orders
        s["recency_sum"] += recency_days

    rfm = [
        {
            "segment": seg,
            "customers": v["customers"],
            "revenue": _round2(v["revenue"]),
            "avg_orders": _round2(v["orders_sum"] / v["customers"]),
            "avg_recency_days": _round2(v["recency_sum"] / v["customers"]),
        }
        for seg, v in segments.items()
    ]

    cohorts_map = defaultdict(list)
    for cid, os_ in by_customer.items():
        cohort_month = os_[0]["_dt"].strftime("%Y-%m")
        cohorts_map[cohort_month].append(os_)
    cohorts = []
    for month, cust_orders in sorted(cohorts_map.items()):
        n = len(cust_orders)
        r30 = r60 = r90 = 0
        for os_ in cust_orders:
            first_dt = os_[0]["_dt"]
            for o in os_[1:]:
                gap = (o["_dt"] - first_dt).days
                if gap <= 30:
                    r30 += 1
                if gap <= 60:
                    r60 += 1
                if gap <= 90:
                    r90 += 1
                break  # only the second order (first repeat) counts
        cohorts.append({
            "cohort_month": month, "customers": n,
            "repeat_30": r30, "repeat_60": r60, "repeat_90": r90,
        })

    winback = []
    for cid, os_ in by_customer.items():
        n_orders = len(os_)
        last_dt = os_[-1]["_dt"]
        days_since = (now - last_dt).days
        if n_orders >= 2 and days_since > 45:
            spend = sum(o["total"] or 0 for o in os_ if o["order_status"] == DELIVERED)
            item_counts = Counter()
            for o in os_:
                for item_name, qty in idx.lines_by_order.get(o["order_id"], {}).items():
                    item_counts[item_name] += qty
            favourite = item_counts.most_common(1)[0][0] if item_counts else None
            winback.append({
                "customer_id": cid, "orders": n_orders, "spend": _round2(spend),
                "last_order_at": last_dt.isoformat(), "days_since": days_since,
                "favourite_item": favourite,
            })
    winback.sort(key=lambda w: -w["spend"])

    weekly_split = []
    repeat_rate_trend = []
    first_order_week = {cid: _week_start(os_[0]["_dt"]) for cid, os_ in by_customer.items()}
    for wk in idx.active_week_starts:
        wk_orders = idx.weeks[wk]
        new_cust_ids = {o["customer_id"] for o in wk_orders if first_order_week.get(o["customer_id"]) == wk}
        returning_ids = {o["customer_id"] for o in wk_orders if first_order_week.get(o["customer_id"]) != wk}
        new_rev = sum(o["total"] or 0 for o in wk_orders
                       if o["order_status"] == DELIVERED and first_order_week.get(o["customer_id"]) == wk)
        ret_rev = sum(o["total"] or 0 for o in wk_orders
                       if o["order_status"] == DELIVERED and first_order_week.get(o["customer_id"]) != wk)
        weekly_split.append({
            "week_start": wk.isoformat(),
            "new_customers": len(new_cust_ids),
            "returning_customers": len(returning_ids),
            "new_revenue": _round2(new_rev),
            "returning_revenue": _round2(ret_rev),
        })
        total_active = len(new_cust_ids) + len(returning_ids)
        repeat_rate_trend.append({
            "week_start": wk.isoformat(),
            "repeat_share": _round2(len(returning_ids) / total_active) if total_active else 0,
        })

    return {
        "rfm": rfm, "cohorts": cohorts, "winback": winback,
        "weekly_split": weekly_split, "repeat_rate_trend": repeat_rate_trend,
    }


# --------------------------------------------------------------------------
# 9. Discounts
# --------------------------------------------------------------------------

def compute_discounts(idx):
    """Per discount-construct performance vs the undiscounted baseline.

    `discount_funded` = restaurant-borne discount only (promo/other/brand
    pack, already summed by build.py's `restaurant_discount` field);
    `gold_discount` is platform-funded and excluded from that cost figure -
    that split is the whole point of the field, but the name alone doesn't
    say whose money it is, so the additive `funded_by` field
    ("restaurant"/"platform"/"mixed"/"none") makes it explicit, and every
    `verdict` states the split in words too. `repeat_rate` = share of that
    construct's orders placed by a customer with an earlier order, compared
    in the verdict against the same rate among undiscounted orders (not a
    fixed threshold) - each construct's verdict is built from its own
    numbers, not a shared stub sentence.
    """
    by_customer_first_order = {}
    for o in sorted(idx.orders, key=lambda o: o["_dt"]):
        by_customer_first_order.setdefault(o["customer_id"], o["order_id"])

    def _repeat_rate(os_):
        n = len(os_)
        if not n:
            return 0.0
        repeat = sum(1 for o in os_ if by_customer_first_order.get(o["customer_id"]) != o["order_id"])
        return repeat / n

    baseline = [o for o in idx.delivered if not o.get("discount_construct")]
    baseline_aov = sum(o["total"] or 0 for o in baseline) / len(baseline) if baseline else None
    baseline_repeat_rate = _repeat_rate([o for o in idx.orders if not o.get("discount_construct")])

    by_construct = defaultdict(list)
    for o in idx.orders:
        construct = o.get("discount_construct")
        if construct:
            by_construct[construct].append(o)

    rows = []
    for construct, os_ in by_construct.items():
        delivered = [o for o in os_ if o["order_status"] == DELIVERED]
        n = len(os_)
        aov = sum(o["total"] or 0 for o in delivered) / len(delivered) if delivered else 0
        discount_funded = sum(o.get("restaurant_discount") or 0 for o in delivered)
        gold_funded = sum(o.get("gold_discount") or 0 for o in delivered)
        net_revenue = sum(o["total"] or 0 for o in delivered)
        repeat_rate = _repeat_rate(os_)
        aov_vs_undiscounted = _round2(aov - baseline_aov) if baseline_aov is not None else None
        repeat_vs_baseline = _round2(repeat_rate - baseline_repeat_rate)

        if discount_funded > 0 and gold_funded > 0:
            funded_by = "mixed"
            funding_phrase = f"funded {_rupees(discount_funded)} by the restaurant and {_rupees(gold_funded)} by Zomato Gold"
        elif discount_funded > 0:
            funded_by = "restaurant"
            funding_phrase = f"costs the restaurant {_rupees(discount_funded)} directly"
        elif gold_funded > 0:
            funded_by = "platform"
            funding_phrase = f"funded by Zomato Gold, not the restaurant ({_rupees(gold_funded)})"
        else:
            funded_by = "none"
            funding_phrase = "shows no restaurant- or Gold-funded cost in this data"

        aov_phrase = (f"AOV is {_rupees(abs(aov_vs_undiscounted))} "
                      f"{'above' if aov_vs_undiscounted >= 0 else 'below'} the undiscounted baseline "
                      f"({_rupees(baseline_aov)})") if aov_vs_undiscounted is not None else "AOV has no undiscounted baseline to compare against"
        repeat_phrase = (f"repeat share is {abs(repeat_vs_baseline) * 100:.0f} points "
                         f"{'above' if repeat_vs_baseline >= 0 else 'below'} baseline "
                         f"({repeat_rate * 100:.0f}% vs {baseline_repeat_rate * 100:.0f}%)")
        sample_phrase = f"n={n}"
        if n < 5:
            verdict = f"Too few orders ({sample_phrase}) to read anything into this construct yet - {funding_phrase}."
        elif aov_vs_undiscounted is not None and aov_vs_undiscounted >= 0 and repeat_vs_baseline >= 0:
            verdict = f"Pulling its weight ({sample_phrase}): {aov_phrase} and {repeat_phrase}; {funding_phrase}."
        elif funded_by in ("restaurant", "mixed") and discount_funded > net_revenue * 0.3:
            verdict = f"Expensive ({sample_phrase}): {funding_phrase}, against net revenue of {_rupees(net_revenue)}; {aov_phrase}."
        else:
            verdict = f"Mixed signal ({sample_phrase}): {aov_phrase}, {repeat_phrase}; {funding_phrase}."

        rows.append({
            "construct": construct, "orders": n, "aov": _round2(aov),
            "discount_funded": _round2(discount_funded), "net_revenue": _round2(net_revenue),
            "aov_vs_undiscounted": aov_vs_undiscounted,
            "repeat_rate": _round2(repeat_rate), "verdict": verdict,
            "funded_by": funded_by,
        })

    rows.sort(key=lambda r: -r["orders"])
    return rows


# --------------------------------------------------------------------------
# 10. Dormant items
# --------------------------------------------------------------------------

DORMANT_DAYS_THRESHOLD = 30

# Minimum evidence bar before a dormant item earns a rupee estimate anywhere
# (the dormant table's estimated_lost_revenue AND the revive action) -
# below this, weekly_rate_when_active is too easily a fluke (e.g. 2 units
# sold in a single week) to extrapolate into a confident-looking number.
REVIVE_MIN_UNITS = 5
REVIVE_MIN_ACTIVE_WEEKS = 3


def compute_dormant(idx, prices, menu_rows):
    """Items unsold for >=30 days, with what they used to earn.

    `weekly_rate_when_active` = lifetime units / the item's full observed
    span - first_sold to the *earlier* of (last_sold + 30 days) and the
    dataset's last order date. Dividing by the handful of weeks an item
    happened to sell in (rather than the calendar time it had a chance to
    sell) turns a fluke into a confident-looking rate; this keeps the rate
    honest even for an item that only ever sold in one short burst.
    `estimated_lost_revenue` projects that rate forward across the weeks
    it has been dormant - a cumulative, lifetime-since-dormant figure (not
    a monthly one; see compute_actions for the monthly-capped version used
    in the `revive` action). It carries the exact same minimum-evidence
    gate as the `revive` action (>=5 lifetime units AND >=3 distinct active
    weeks) - below that bar the rate is too easily a fluke to turn into a
    rupee figure anywhere, including this table. Below the gate,
    `estimated_lost_revenue` is null and the additive `reason` field
    explains why in one line; the row stays in the list either way, since
    "we don't know" is itself worth showing.
    """
    price_map = {p["item_name"]: p["unit_price"] for p in prices}
    menu_by_name = {r["item_name"]: r for r in menu_rows}

    rows = []
    for item_name in idx.item_names:
        m = menu_by_name[item_name]
        if m["days_dormant"] < DORMANT_DAYS_THRESHOLD:
            continue
        first_dt = _parse_dt(m["first_sold"])
        last_dt = _parse_dt(m["last_sold"])
        active_weeks = _active_weeks_count(idx, item_name)
        active_span_days = (last_dt - first_dt).days

        span_end = min(last_dt + timedelta(days=30), idx.last_order_at)
        span_weeks = max(1.0, (span_end - first_dt).days / 7.0)
        weekly_rate = m["units"] / span_weeks
        unit_price = price_map.get(item_name) or 0

        eligible = m["units"] >= REVIVE_MIN_UNITS and active_weeks >= REVIVE_MIN_ACTIVE_WEEKS
        if eligible:
            weeks_dormant = m["days_dormant"] / 7.0
            estimated_lost_revenue = _round2(weekly_rate * unit_price * weeks_dormant)
            reason = None
        else:
            estimated_lost_revenue = None
            reason = f"{m['units']} units in {active_span_days} days - too little history to size"

        rows.append({
            "item_name": item_name,
            "units_lifetime": m["units"],
            "last_sold": m["last_sold"],
            "days_dormant": m["days_dormant"],
            "weekly_rate_when_active": _round2(weekly_rate),
            "estimated_lost_revenue": estimated_lost_revenue,
            "reason": reason,
        })

    rows.sort(key=lambda r: -(r["estimated_lost_revenue"] or 0))
    return rows


def _active_weeks_count(idx, item_name):
    """Number of distinct active weeks in which item_name sold >=1 unit."""
    weekly = idx._item_weekly_all.get(item_name, {})
    return sum(1 for w in idx.active_week_starts if weekly.get(w, 0) > 0)


def _best_window_revenue(idx, item_name, unit_price, window=4):
    """Best observed `window`-active-week revenue this item has ever done.

    Used to cap `revive` action impact at what the item has actually
    proven it can do, rather than extrapolating above its own history.
    """
    if unit_price is None:
        return None
    weekly = idx._item_weekly_delivered.get(item_name, {})
    weeks = idx.active_week_starts
    if not weeks:
        return 0.0
    w = min(window, len(weeks))
    best_units = 0
    for i in range(len(weeks) - w + 1):
        units = sum(weekly.get(weeks[j], 0) for j in range(i, i + w))
        best_units = max(best_units, units)
    return best_units * unit_price


# --------------------------------------------------------------------------
# 11. Actions
# --------------------------------------------------------------------------

CONFIDENCE_WEIGHT = {"high": 3, "medium": 2, "low": 1}


def compute_actions(idx, prices, menu_rows, pairs, attach_rows, forecast, demand, quality, customers, discounts, dormant):
    """Ranked, plain-language action list. Capped at 8, quality over quantity."""
    price_map = {p["item_name"]: p["unit_price"] for p in prices}
    menu_by_name = {r["item_name"]: r for r in menu_rows}
    actions = []

    # ops: slow kitchen hurting ratings - almost always the single biggest
    # lever. n is small (often ~6) but the effect size is enormous and
    # acting on it costs nothing, so it still ships - just labelled honestly.
    slow = quality["slow_orders"]
    if slow["n"] >= 3 and slow["avg_rating"] is not None and slow["avg_rating_fast"] is not None:
        gap = slow["avg_rating_fast"] - slow["avg_rating"]
        n_fast = slow.get("n_fast", 0)
        actions.append({
            "id": "ops-slow-kitchen", "kind": "ops", "item_name": None,
            "headline": "Fix prep times over 25 minutes - it is the single biggest rating driver",
            "detail": (f"Orders with prep time over 25 minutes average {slow['avg_rating']}★ "
                       f"across {slow['n']} rated slow orders, versus {slow['avg_rating_fast']}★ "
                       f"across {n_fast} rated orders with prep time 25 minutes or under."),
            "evidence": f"{slow['n']} rated slow orders vs {n_fast} rated fast orders; rating gap {_round2(gap)}★",
            "impact_value": None,
            "impact_period": "monthly",
            "impact_basis": "protects rating, not a direct rupee figure",
            "confidence": "high" if slow["n"] >= 5 else "medium",
            "priority": 0,
            "_qualitative_priority": True,  # huge effect size, costs nothing to act on
        })

    # price_up: plowhorse items, not heavily discount-dependent. Small
    # samples (units<5, or a price resolved from sample_n<5) get a low
    # confidence and the sample sizes stay visible in the evidence string.
    price_sample_n = {p["item_name"]: p.get("sample_n", 0) for p in prices}
    plowhorses = [r for r in menu_rows if r["quadrant"] == "plowhorse" and (r["discount_dependence"] or 0) < 0.3]
    plowhorses.sort(key=lambda r: -r["revenue"])
    for r in plowhorses[:2]:
        price = r["unit_price"]
        rise = max(10, round(price * 0.10 / 10) * 10)
        weeks = len(idx.active_week_starts) or 1
        units_per_month = r["units"] / weeks * 4.33
        impact = units_per_month * rise
        p_n = price_sample_n.get(r["item_name"], 0)
        if r["units"] < 5 or p_n < 5:
            conf = "low"
        elif r["price_confidence"] == "observed" and r["units"] >= 10:
            conf = "high"
        else:
            conf = "medium"
        actions.append({
            "id": f"price-up-{r['item_name']}", "kind": "price_up", "item_name": r["item_name"],
            "headline": f"Raise {r['item_name']} by ~{_rupees(rise)}",
            "detail": (f"High demand ({r['units']} units, price confidence {r['price_confidence']}) at a "
                       f"below-median price of {_rupees(price)}. Low discount dependence "
                       f"({(r['discount_dependence'] or 0) * 100:.0f}% of its orders)."),
            "evidence": f"units={r['units']}, price_confidence={r['price_confidence']} (price sample n={p_n})",
            "impact_value": _round2(impact),
            "impact_period": "monthly",
            "impact_basis": f"{_round2(units_per_month)} units/month x {_rupees(rise)} rise",
            "confidence": conf, "priority": 0,
        })

    # drop: dog items that are not frequent attachments
    dogs = [r for r in menu_rows if r["quadrant"] == "dog" and not r["_is_frequent_attachment"]]
    dogs.sort(key=lambda r: r["units"])
    for r in dogs[:2]:
        actions.append({
            "id": f"drop-{r['item_name']}", "kind": "drop", "item_name": r["item_name"],
            "headline": f"Consider dropping {r['item_name']}",
            "detail": (f"Low demand ({r['units']} units lifetime, n={r['orders']} orders) at a "
                       f"below-median price, and it isn't a frequent combo attachment."),
            "evidence": f"units={r['units']}, orders={r['orders']}, revenue_share="
                        f"{(r['revenue_share'] or 0) * 100:.1f}%",
            "impact_value": _round2(r["revenue"] / max(1, len(idx.active_week_starts)) * 4.33),
            "impact_period": "monthly",
            "impact_basis": "menu-slot cost of carrying a low-mover, not a rupee saving",
            "confidence": "medium" if r["units"] >= 5 else "low", "priority": 0,
        })
    # note frequent-attachment dogs explicitly instead of silently dropping them
    protected_dogs = [r for r in menu_rows if r["quadrant"] == "dog" and r["_is_frequent_attachment"]]
    for r in protected_dogs[:1]:
        actions.append({
            "id": f"keep-{r['item_name']}", "kind": "promo", "item_name": r["item_name"],
            "headline": f"Keep {r['item_name']} despite low standalone demand",
            "detail": f"Low unit sales on its own, but it appears in a combo with n>=3 - dropping it costs the combo.",
            "evidence": f"units={r['units']}; appears in a pair with n>=3",
            "impact_value": None, "impact_period": "monthly",
            "impact_basis": "protects existing combo demand",
            "confidence": "medium", "priority": 0,
        })

    # revive: a dormant item only earns an action - with a rupee figure -
    # once it has cleared a minimum bar of real evidence: >=5 lifetime
    # units AND >=3 distinct active weeks selling. Below that, a short
    # active window (e.g. 3 units sold inside 8 days) makes
    # weekly_rate_when_active annualise a fluke into a confident-looking
    # number; that number would outrank real findings on the strength of
    # noise. Those items stay visible in the `dormant` list (still worth
    # showing) but get no action here. Above the bar, impact is capped at
    # the item's own best observed 4-active-week revenue - never
    # extrapolated above what it has actually done - and confidence stays
    # "low" unless the item cleared 15 lifetime units.
    # compute_dormant already applied this exact gate (single source of
    # truth): estimated_lost_revenue is null iff the item didn't clear it.
    eligible_revive = [
        (r, _active_weeks_count(idx, r["item_name"]))
        for r in dormant if r["estimated_lost_revenue"] is not None
    ]
    eligible_revive.sort(key=lambda t: -t[0]["estimated_lost_revenue"])

    for r, active_weeks in eligible_revive[:2]:
        price = price_map.get(r["item_name"])
        raw_monthly_impact = r["weekly_rate_when_active"] * (price or 0) * 4.33
        cap = _best_window_revenue(idx, r["item_name"], price, window=4)
        capped = cap is not None and raw_monthly_impact > cap
        monthly_impact = _round2(min(raw_monthly_impact, cap)) if cap is not None else _round2(raw_monthly_impact)
        conf = "medium" if r["units_lifetime"] >= 15 else "low"
        cap_note = f", capped at its best observed 4-active-week revenue ({_rupees(cap)})" if capped else ""
        actions.append({
            "id": f"revive-{r['item_name']}", "kind": "revive", "item_name": r["item_name"],
            "headline": f"Revive or retire {r['item_name']}",
            "detail": (f"Dormant {r['days_dormant']} days (last sold {r['last_sold'][:10]}) after "
                       f"selling {r['units_lifetime']} units lifetime across {active_weeks} active weeks, "
                       f"{r['weekly_rate_when_active']} units/week when active{cap_note}."),
            "evidence": f"units_lifetime={r['units_lifetime']}, active_weeks={active_weeks}, days_dormant={r['days_dormant']}",
            "impact_value": monthly_impact,
            "impact_period": "monthly",
            "impact_basis": (f"{r['weekly_rate_when_active']} units/week x {_rupees(price)} x 4.33 weeks/month, "
                              f"if revived, capped at best observed 4-week revenue"),
            "confidence": conf, "priority": 0,
        })

    # dormant items below the revive evidence bar: no rupee claim, but
    # still worth surfacing so the owner knows they exist.
    below_bar = [r for r in dormant if r["estimated_lost_revenue"] is None][:2]
    for r in below_bar:
        active_weeks = _active_weeks_count(idx, r["item_name"])
        actions.append({
            "id": f"dormant-note-{r['item_name']}", "kind": "revive", "item_name": r["item_name"],
            "headline": f"{r['item_name']}: too little history to size a revive",
            "detail": (f"{r['reason']} (below the bar of {REVIVE_MIN_UNITS}+ units, "
                       f"{REVIVE_MIN_ACTIVE_WEEKS}+ active weeks). Still dormant {r['days_dormant']} days; "
                       f"worth a manual look, not a rupee claim."),
            "evidence": f"too few sales to estimate: units_lifetime={r['units_lifetime']}, active_weeks={active_weeks}",
            "impact_value": None,
            "impact_period": "monthly",
            "impact_basis": "too few sales to estimate",
            "confidence": "low", "priority": 0,
        })

    # combo: top pair by n. impact_value is a monthly figure: how often the
    # pair has historically recurred per month, times its combined bill.
    # only pairs that actually co-occur *more* than chance (lift >= 1.2, the
    # same bar suggested_combo_price uses) are candidates for a combo action
    # - a pair that co-occurs less than chance is negative evidence, not a
    # weak positive one, and belongs nowhere near a "create a combo" card
    solid_pairs = [p for p in pairs if p["strength"] in ("solid", "indicative") and (p["lift"] or 0) >= 1.2]
    solid_pairs.sort(key=lambda p: (-(p["lift"] or 0), -p["n"]))
    weeks_span = len(idx.active_week_starts) or 1
    for p in solid_pairs[:2]:
        combo_note = (f"combo price ~{_rupees(p['suggested_combo_price'])}" if p["suggested_combo_price"]
                      else "price unknown for one item, no combo price suggested")
        occurrences_per_month = p["n"] / weeks_span * 4.33
        monthly_impact = _round2(occurrences_per_month * p["combined_value"]) if p["combined_value"] else None
        actions.append({
            "id": f"combo-{p['a']}-{p['b']}", "kind": "combo", "item_name": None,
            "headline": f"Create a combo: {p['a']} + {p['b']}",
            "detail": f"Ordered together {p['n']} times ({p['strength']}); {combo_note}.",
            "evidence": f"n={p['n']}, lift={p['lift']}, strength={p['strength']}",
            "impact_value": monthly_impact,
            "impact_period": "monthly",
            "impact_basis": (f"{_round2(occurrences_per_month)} occurrences/month (n={p['n']} historically) "
                              f"x {_rupees(p['combined_value'])} avg combined bill"),
            "confidence": "medium" if p["strength"] == "solid" else "low", "priority": 0,
        })

    # promo: biggest attach gap. attach.gap_value is lifetime (per the spec
    # formula); scale it to a monthly figure for the action's impact_value.
    if attach_rows:
        gap_row = max(attach_rows, key=lambda r: r["gap_value"])
        if gap_row["gap_value"] > 0:
            monthly_gap = _round2(gap_row["gap_value"] / weeks_span * 4.33)
            actions.append({
                "id": f"attach-{gap_row['main_item']}", "kind": "promo", "item_name": gap_row["main_item"],
                "headline": f"Prompt a side with every {gap_row['main_item']}",
                "detail": (f"Only {gap_row['attach_rate'] * 100:.0f}% of its {gap_row['orders']} orders "
                           f"include a side, below the best-observed attach rate."),
                "evidence": f"orders={gap_row['orders']}, with_side={gap_row['with_side']}",
                "impact_value": monthly_gap,
                "impact_period": "monthly",
                "impact_basis": "attach-rate gap x orders/month x median side price",
                "confidence": "medium" if gap_row["orders"] >= 10 else "low", "priority": 0,
            })

    # winback: highest-spend lapsed customers
    winback = customers["winback"]
    if winback:
        top_spend = sum(w["spend"] for w in winback[:10])
        actions.append({
            "id": "winback-top10", "kind": "winback", "item_name": None,
            "headline": f"Win back the top {min(10, len(winback))} lapsed repeat customers",
            "detail": (f"{len(winback)} customers with 2+ orders have gone quiet for 45+ days, "
                       f"representing {_rupees(top_spend)} in historical spend among the top 10."),
            "evidence": f"n={len(winback)} winback candidates",
            "impact_value": _round2(top_spend * 0.2),
            "impact_period": "one_time",
            "impact_basis": "one-time, not monthly: 20% assumed reactivation on top-10 historical spend",
            "confidence": "low", "priority": 0,
        })

    # ops: cheapest closure window (skip the "no safe option" placeholders,
    # which carry revenue_at_risk_per_month: null)
    priced_closures = [c for c in demand["closure_options"] if c["revenue_at_risk_per_month"] is not None]
    if priced_closures:
        best = min(priced_closures, key=lambda c: c["revenue_at_risk_per_month"])
        actions.append({
            "id": "closure-window", "kind": "ops", "item_name": None,
            "headline": f"Use {best['label']} as a maintenance window",
            "detail": best["verdict"],
            "evidence": f"scope={best['scope']}, based on {len(idx.active_week_starts)} active weeks of history",
            "impact_value": -best["revenue_at_risk_per_month"],
            "impact_period": "monthly",
            "impact_basis": "revenue historically booked in that window, monthly",
            "confidence": "medium" if len(idx.active_week_starts) >= 5 else "low", "priority": 0,
        })

    for a in actions:
        weight = CONFIDENCE_WEIGHT.get(a["confidence"], 1)
        impact = abs(a["impact_value"]) if a["impact_value"] else 0
        if a.pop("_qualitative_priority", False):
            # explicitly-marked non-rupee actions (currently just the
            # prep-time driver) rank on effect size + confidence, not on a
            # fabricated large number
            a["_score"] = weight * 1000
        elif impact:
            a["_score"] = impact * weight
        else:
            # no rupee claim and not qualitatively boosted (e.g. a
            # below-evidence-bar dormant note) - ranks low, never above a
            # real numeric action
            a["_score"] = weight * 0.01

    actions.sort(key=lambda a: -a["_score"])
    actions = actions[:8]
    for i, a in enumerate(actions, start=1):
        a["priority"] = i
        del a["_score"]

    return actions


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def compute_analytics(orders, items, item_costs=None, item_prices_table=None,
                       menu_items_table=None, data_quality_table=None):
    """Build the full `analytics` payload defined in docs/ANALYTICS_SPEC.md.

    `item_costs`, if given, is a dict of item_name -> unit_cost loaded from
    data/item_costs.csv by build.py (the owner's local override). It
    switches the menu matrix's vertical measure to contribution margin (see
    compute_menu).

    `item_prices_table`, `menu_items_table`, `data_quality_table` are the
    fetched rows of `gold.item_prices`, `silver.menu_items` and
    `gold.data_quality` respectively (None if the warehouse predates them -
    build.py degrades to local computation in that case; nothing here
    crashes on their absence).
    """
    idx = Index(orders, items)

    prices, price_source = resolve_prices(idx, item_prices_table)
    idx._prices = prices  # attach_rate needs the price map
    price_map = {p["item_name"]: p["unit_price"] for p in prices}

    category_map = {}
    table_costs = {}
    if menu_items_table:
        for r in menu_items_table:
            name = r["item_name"]
            category_map[name] = r.get("category")
            if r.get("unit_cost") is not None:
                table_costs[name] = r["unit_cost"]
    effective_costs = dict(table_costs)
    if item_costs:
        effective_costs.update(item_costs)  # data/item_costs.csv wins on conflict
    effective_costs = effective_costs or None

    pairs = compute_pairs(idx, price_map)
    attach_rows, attach_excluded = compute_attach(idx, category_map=category_map)
    menu_rows = compute_menu(idx, prices, pairs, attach_rows, item_costs=effective_costs, category_map=category_map)
    forecast = compute_forecast(idx)
    demand = compute_demand(idx)
    quality = compute_quality(idx)
    customers = compute_customers(idx)
    discounts = compute_discounts(idx)
    dormant = compute_dormant(idx, prices, menu_rows)
    actions = compute_actions(
        idx, prices, menu_rows, pairs, attach_rows, forecast, demand, quality, customers, discounts, dormant
    )

    for r in menu_rows:
        r.pop("_is_frequent_attachment", None)
    for o in idx.orders:
        o.pop("_dt", None)

    return {
        "prices": prices,
        "menu": menu_rows,
        "actions": actions,
        "pairs": pairs,
        "attach": attach_rows,
        "forecast": forecast,
        "demand": demand,
        "quality": quality,
        "customers": customers,
        "discounts": discounts,
        "dormant": dormant,
        "data_quality": data_quality_table or [],
        "price_source": price_source,
        "attach_excluded": attach_excluded,
    }
