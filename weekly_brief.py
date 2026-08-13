"""Write weekly_brief.md - the same analysis as prose, for an AI agent to read.

Pure Python, stdlib only. Called from build.py after analytics.py has
produced the `analytics` payload. Structure (per docs/ANALYTICS_SPEC.md):
headline numbers, what changed since last week, the ranked actions with
evidence and expected impact, then appendix tables (menu, pairs, forecast,
win-back). Plain markdown, no HTML, every number carries its sample size.
"""

from datetime import datetime


def _fmt_money(x):
    if x is None:
        return "n/a"
    return f"₹{x:,.0f}"


def _fmt_pct(x):
    if x is None:
        return "n/a"
    return f"{x * 100:.1f}%"


def _week_over_week(basis_weeks):
    """Compare the two most recent active weeks in the forecast basis."""
    if len(basis_weeks) < 2:
        return None
    this_wk, prev_wk = basis_weeks[-1], basis_weeks[-2]
    order_delta = this_wk["orders"] - prev_wk["orders"]
    rev_delta = (this_wk["revenue"] or 0) - (prev_wk["revenue"] or 0)
    return {
        "this_week": this_wk, "prev_week": prev_wk,
        "order_delta": order_delta, "rev_delta": rev_delta,
    }


def _headline_section(meta, orders, analytics_payload):
    lines = ["# Weekly brief - The Oven Vibe", ""]
    lines.append(f"Generated {datetime.now().isoformat(timespec='seconds')} "
                 f"from {meta['order_count']} orders "
                 f"({meta['first_order_at']} to {meta['last_order_at']}).")
    if not meta.get("has_cost_data"):
        lines.append("")
        lines.append("_No cost data loaded (`data/item_costs.csv` absent) - the menu matrix and "
                     "any margin-flavoured numbers below are revenue, not profit. Fill in "
                     "`data/item_costs.csv` from the `.example` file to upgrade this._")
    lines.append("")
    lines.append("## Headline numbers")
    lines.append("")

    forecast = analytics_payload["forecast"]
    quality = analytics_payload["quality"]
    customers = analytics_payload["customers"]

    n_basis = len(forecast["basis_weeks"])
    lines.append(f"- **Next week's forecast** ({forecast['week_start']}): "
                 f"{forecast['orders_expected']} orders (range {forecast['orders_low']}-"
                 f"{forecast['orders_high']}), {_fmt_money(forecast['revenue_expected'])} revenue "
                 f"(range {_fmt_money(forecast['revenue_low'])}-{_fmt_money(forecast['revenue_high'])}). "
                 f"Method: {forecast['method']}, basis n={n_basis} active weeks.")

    slow = quality["slow_orders"]
    if slow["n"]:
        lines.append(f"- **Prep time is the biggest rating driver**: orders over "
                     f"{slow['threshold_min']} min average {slow['avg_rating']}★ "
                     f"across n={slow['n']} rated slow orders, vs {slow['avg_rating_fast']}★ "
                     f"across n={slow.get('n_fast', 'n/a')} rated orders at or under that threshold "
                     f"(orders with no recorded prep time are shown separately, not folded into either).")

    orders_by_customer = {}
    for o in orders:
        cid = o.get("customer_id")
        if cid is not None:
            orders_by_customer[cid] = orders_by_customer.get(cid, 0) + 1
    total_customers = len(orders_by_customer)
    repeat_customers = sum(1 for n in orders_by_customer.values() if n > 1)
    if total_customers:
        lines.append(f"- **Repeat rate**: {repeat_customers} of {total_customers} customers "
                     f"(n={total_customers}) have placed more than one order "
                     f"({_fmt_pct(repeat_customers / total_customers)}).")

    winback = customers["winback"]
    if winback:
        lines.append(f"- **{len(winback)} customers** (n={len(winback)}) qualify for win-back "
                     f"(2+ orders, quiet 45+ days).")

    dormant = analytics_payload["dormant"]
    if dormant:
        lines.append(f"- **{len(dormant)} menu items** (n={len(dormant)}) have not sold in 30+ days "
                     f"while still on the menu.")

    price_source = analytics_payload.get("price_source")
    if price_source:
        lines.append(f"- Prices sourced from `{price_source}`.")

    return lines


_STATUS_ICON = {"ok": "OK", "warn": "WARN", "fail": "FAIL"}


def _data_quality_section(analytics_payload):
    """Data you can and cannot trust, from gold.data_quality (if present)."""
    checks = analytics_payload.get("data_quality") or []
    lines = ["", "## Data you can and cannot trust", ""]
    if not checks:
        lines.append("No `gold.data_quality` checks available from this warehouse - "
                     "treat every number here as unaudited for gaps/duplicates.")
        return lines

    warn_or_fail = [c for c in checks if c["status"] in ("warn", "fail")]
    if warn_or_fail:
        lines.append("Known issues:")
        lines.append("")
        for c in warn_or_fail:
            icon = _STATUS_ICON.get(c["status"], c["status"].upper())
            lines.append(f"- **{icon}** `{c['check_name']}` (value={c['value']}): {c['detail']}")
        lines.append("")
    else:
        lines.append("No warnings or failures in the current data-quality checks.")
        lines.append("")

    lines.append(f"All checks (n={len(checks)}):")
    lines.append("")
    lines.append("| Check | Status | Value | Detail |")
    lines.append("|---|---|---:|---|")
    for c in checks:
        lines.append(f"| {c['check_name']} | {c['status']} | {c['value']} | {c['detail']} |")

    excluded = analytics_payload.get("attach_excluded") or []
    if excluded:
        names = ", ".join(f"{e['main_item']} ({e['orders']} orders)" for e in excluded)
        lines.append("")
        lines.append(f"Attach-rate list excludes {len(excluded)} main(s) with fewer than 5 delivered "
                     f"orders - too thin to state a rate: {names}.")

    return lines


def _changed_section(analytics_payload):
    lines = ["", "## What changed vs last week", ""]
    wow = _week_over_week(analytics_payload["forecast"]["basis_weeks"])
    if wow is None:
        lines.append("Not enough active-week history yet to compare week over week.")
        return lines

    this_wk, prev_wk = wow["this_week"], wow["prev_week"]
    order_sign = "+" if wow["order_delta"] >= 0 else ""
    rev_sign = "+" if wow["rev_delta"] >= 0 else ""
    lines.append(f"- Week of {this_wk['week_start']}: {this_wk['orders']} orders, "
                 f"{_fmt_money(this_wk['revenue'])} revenue.")
    lines.append(f"- Week of {prev_wk['week_start']}: {prev_wk['orders']} orders, "
                 f"{_fmt_money(prev_wk['revenue'])} revenue.")
    lines.append(f"- Change: {order_sign}{wow['order_delta']} orders, "
                 f"{rev_sign}{_fmt_money(wow['rev_delta'])} revenue.")

    weekly_q = analytics_payload["quality"]["weekly"]
    if len(weekly_q) >= 2:
        this_q, prev_q = weekly_q[-1], weekly_q[-2]
        lines.append(f"- Cancel rate: {_fmt_pct(this_q['cancel_rate'])} this week vs "
                     f"{_fmt_pct(prev_q['cancel_rate'])} prior week.")
        if this_q["avg_rating"] is not None or prev_q["avg_rating"] is not None:
            lines.append(f"- Avg rating: {this_q['avg_rating']} this week vs {prev_q['avg_rating']} prior week.")

    split = analytics_payload["customers"]["weekly_split"]
    if len(split) >= 1:
        cur = split[-1]
        lines.append(f"- New vs returning customers this week: {cur['new_customers']} new, "
                     f"{cur['returning_customers']} returning.")

    return lines


def _actions_section(analytics_payload):
    lines = ["", "## Ranked actions", ""]
    actions = analytics_payload["actions"]
    if not actions:
        lines.append("No actions surfaced from the current data.")
        return lines
    for a in actions:
        impact = _fmt_money(a["impact_value"]) if a["impact_value"] is not None else "n/a"
        lines.append(f"### {a['priority']}. {a['headline']} ({a['kind']}, confidence: {a['confidence']})")
        lines.append("")
        lines.append(a["detail"])
        lines.append("")
        lines.append(f"- Expected impact: {impact} - {a['impact_basis']}")
        lines.append(f"- Evidence: {a['evidence']}")
        lines.append("")
    return lines


def _appendix_menu(analytics_payload):
    lines = ["## Appendix: menu", "", "| Item | Units | Revenue | Price | Confidence | Quadrant | Trend |",
             "|---|---:|---:|---:|---|---|---:|"]
    for m in sorted(analytics_payload["menu"], key=lambda r: -(r["revenue"] or 0))[:28]:
        price = _fmt_money(m['unit_price']) if m["unit_price"] is not None else "unknown"
        trend = f"{m['trend_pct']:+.0f}%" if m["trend_pct"] is not None else "n/a"
        lines.append(f"| {m['item_name']} | {m['units']} | {_fmt_money(m['revenue'])} | {price} | "
                     f"{m['price_confidence']} | {m['quadrant'] or 'n/a'} | {trend} |")
    return lines


def _appendix_pairs(analytics_payload):
    lines = ["", "## Appendix: pairs", "", "| A | B | n | strength | lift | combo price |",
             "|---|---|---:|---|---:|---:|"]
    for p in analytics_payload["pairs"][:20]:
        lift = f"{p['lift']:.2f}" if p["lift"] is not None else "n/a"
        combo = _fmt_money(p['suggested_combo_price']) if p["suggested_combo_price"] else "n/a"
        reads_as = f" ({p['reads_as']})" if p.get("reads_as") else ""
        lines.append(f"| {p['a']} | {p['b']} | {p['n']} | {p['strength']}{reads_as} | {lift} | {combo} |")
    return lines


def _appendix_forecast(analytics_payload):
    forecast = analytics_payload["forecast"]
    lines = ["", "## Appendix: forecast by weekday", "", "| Weekday | Orders expected | Range | Revenue expected |",
             "|---|---:|---:|---:|"]
    for w in forecast["by_weekday"]:
        lines.append(f"| {w['weekday']} | {w['orders_expected']} | {w['orders_low']}-{w['orders_high']} | "
                     f"{_fmt_money(w['revenue_expected'])} |")
    lines.append("")
    lines.append("Basis weeks (n=" + str(len(forecast["basis_weeks"])) + "):")
    lines.append("")
    lines.append("| Week | Orders | Revenue |")
    lines.append("|---|---:|---:|")
    for w in forecast["basis_weeks"]:
        lines.append(f"| {w['week_start']} | {w['orders']} | {_fmt_money(w['revenue'])} |")
    return lines


def _appendix_winback(analytics_payload):
    winback = analytics_payload["customers"]["winback"]
    lines = ["", f"## Appendix: win-back list (n={len(winback)})", "",
             "| Customer | Orders | Spend | Last order | Days since | Favourite item |",
             "|---|---:|---:|---|---:|---|"]
    for w in winback[:25]:
        lines.append(f"| {w['customer_id']} | {w['orders']} | {_fmt_money(w['spend'])} | "
                     f"{w['last_order_at'][:10]} | {w['days_since']} | {w['favourite_item'] or 'n/a'} |")
    return lines


def build_brief_text(meta, orders, analytics_payload):
    lines = []
    lines += _headline_section(meta, orders, analytics_payload)
    lines += _changed_section(analytics_payload)
    lines += _data_quality_section(analytics_payload)
    lines += _actions_section(analytics_payload)
    lines += _appendix_menu(analytics_payload)
    lines += _appendix_pairs(analytics_payload)
    lines += _appendix_forecast(analytics_payload)
    lines += _appendix_winback(analytics_payload)
    return "\n".join(lines) + "\n"


def write_brief(path, meta, orders, analytics_payload):
    path.write_text(build_brief_text(meta, orders, analytics_payload))
