"""Build the static dashboard.

Reads the gold/silver layers out of the data-pipeline's DuckDB warehouse and
inlines the result as JSON into `dashboard.html`, so the output is a single
self-contained file with no server and no runtime dependencies.

Usage:
    uv run build.py [--db PATH] [--out PATH]
"""

import argparse
import csv
import json
import shutil
import tempfile
from datetime import date, datetime
from pathlib import Path

import duckdb

import analytics
import weekly_brief

ROOT_DIR = Path(__file__).parent
DEFAULT_DB = ROOT_DIR.parent / "the-oven-vibe-data-pipeline" / "warehouse.duckdb"
TEMPLATE = ROOT_DIR / "template.html"
DEFAULT_OUT = ROOT_DIR / "dashboard.html"
ITEM_COSTS_CSV = ROOT_DIR / "data" / "item_costs.csv"
WEEKLY_BRIEF_OUT = ROOT_DIR / "weekly_brief.md"
PLACEHOLDER = "__DASHBOARD_DATA__"

ORDERS_SQL = """
    SELECT
        order_id,
        order_placed_at,
        order_status,
        total,
        bill_subtotal,
        packaging_charges,
        coalesce(restaurant_discount_promo, 0)
            + coalesce(restaurant_discount_other, 0)
            + coalesce(brand_pack_discount, 0) AS restaurant_discount,
        coalesce(gold_discount, 0) AS gold_discount,
        discount_construct,
        rating,
        review,
        cancellation_reason,
        customer_complaint_tag,
        kpt_duration_min,
        rider_wait_min,
        distance_km,
        customer_id
    FROM silver.orders
    ORDER BY order_placed_at
"""

ITEMS_SQL = """
    SELECT i.order_id, i.quantity, i.item_name
    FROM silver.order_items i
    JOIN silver.orders o USING (order_id)
"""

META_SQL = """
    SELECT
        any_value(restaurant_name) AS restaurant_name,
        any_value(city) AS city,
        any_value(subzone) AS subzone,
        count(*) AS order_count,
        min(order_placed_at) AS first_order_at,
        max(order_placed_at) AS last_order_at
    FROM silver.orders
"""

# Added to the warehouse 13 Aug 2026 - optional at read time, since --db may
# point at an older warehouse. See table_exists()/fetch_if_exists() below.
ITEM_PRICES_SQL = """
    SELECT item_name, unit_price, confidence, sample_n, method
    FROM gold.item_prices
"""

MENU_ITEMS_SQL = """
    SELECT item_name, category, subcategory, is_veg, size, list_price, unit_cost, active
    FROM silver.menu_items
"""

DATA_QUALITY_SQL = """
    SELECT check_name, status, detail, value
    FROM gold.data_quality
"""

# Added to the warehouse 15 Aug 2026 (Phase 8, backend PRD §11 row 8) -
# optional at read time for the same reason as the tables above: an older
# warehouse, or one where pipeline.direct hasn't been run yet, won't have it.
COMBINED_WEEKLY_SALES_SQL = """
    SELECT week_start, source, order_count, confirmed_count, revenue
    FROM gold.combined_weekly_sales
    ORDER BY week_start, source
"""


def jsonable(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def fetch(con, sql):
    cur = con.execute(sql)
    columns = [d[0] for d in cur.description]
    return [
        {col: jsonable(val) for col, val in zip(columns, row)}
        for row in cur.fetchall()
    ]


def connect(db_path):
    """Open the warehouse read-only, falling back to a copy if it is locked.

    DuckDB takes a process-level lock, so an editor or notebook holding the
    warehouse open would otherwise block a build.
    """
    try:
        return duckdb.connect(str(db_path), read_only=True), None
    except duckdb.IOException:
        tmp_dir = tempfile.mkdtemp(prefix="oven-vibe-")
        tmp_db = Path(tmp_dir) / db_path.name
        shutil.copy2(db_path, tmp_db)
        return duckdb.connect(str(tmp_db), read_only=True), tmp_dir


def table_exists(con, schema, table):
    row = con.execute(
        "SELECT count(*) FROM information_schema.tables WHERE table_schema = ? AND table_name = ?",
        [schema, table],
    ).fetchone()
    return bool(row and row[0] > 0)


def fetch_if_exists(con, schema, table, sql):
    """Fetch `sql` if schema.table exists in this warehouse, else None.

    Lets build.py run against an older warehouse that predates
    gold.item_prices / silver.menu_items / gold.data_quality without
    crashing - analytics.py already treats None as "fall back to local
    computation" for all three.
    """
    if not table_exists(con, schema, table):
        return None
    return fetch(con, sql)


def load_item_costs(path):
    """Load data/item_costs.csv (columns: item_name,unit_cost) if it exists.

    Blank/unparseable costs are skipped rather than treated as zero, so a
    partially-filled file still upgrades the items that ARE filled in.
    Returns None (not {}) when the file is absent, so callers can tell
    "no cost data" apart from "cost data with nothing usable in it".
    """
    if not path.exists():
        return None
    costs = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            item_name = (row.get("item_name") or "").strip()
            raw_cost = (row.get("unit_cost") or "").strip()
            if not item_name or not raw_cost:
                continue
            try:
                costs[item_name] = float(raw_cost)
            except ValueError:
                continue
    return costs


def enrich_orders(orders, items):
    """Add is_first_order and items_count to each order dict, in place.

    is_first_order: this is the earliest order (by order_placed_at) placed
    by this customer_id. items_count: distinct line-item count on the order
    (not total quantity).
    """
    items_count_by_order = {}
    for it in items:
        items_count_by_order[it["order_id"]] = items_count_by_order.get(it["order_id"], 0) + 1

    first_order_id_by_customer = {}
    for o in sorted(orders, key=lambda o: o["order_placed_at"]):
        first_order_id_by_customer.setdefault(o["customer_id"], o["order_id"])

    for o in orders:
        o["items_count"] = items_count_by_order.get(o["order_id"], 0)
        o["is_first_order"] = first_order_id_by_customer.get(o["customer_id"]) == o["order_id"]
    return orders


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    if not args.db.exists():
        raise SystemExit(f"warehouse not found: {args.db}\nRun the data pipeline first.")

    con, tmp_dir = connect(args.db)
    try:
        meta = fetch(con, META_SQL)[0]
        orders = fetch(con, ORDERS_SQL)
        items = fetch(con, ITEMS_SQL)
        item_prices_table = fetch_if_exists(con, "gold", "item_prices", ITEM_PRICES_SQL)
        menu_items_table = fetch_if_exists(con, "silver", "menu_items", MENU_ITEMS_SQL)
        data_quality_table = fetch_if_exists(con, "gold", "data_quality", DATA_QUALITY_SQL)
        combined_weekly_sales_table = fetch_if_exists(
            con, "gold", "combined_weekly_sales", COMBINED_WEEKLY_SALES_SQL
        )
    finally:
        con.close()
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    enrich_orders(orders, items)

    item_costs = load_item_costs(ITEM_COSTS_CSV)

    analytics_payload = analytics.compute_analytics(
        orders, items, item_costs=item_costs,
        item_prices_table=item_prices_table,
        menu_items_table=menu_items_table,
        data_quality_table=data_quality_table,
        combined_weekly_sales_table=combined_weekly_sales_table,
    )

    # has_cost_data reflects whichever cost source actually resolved a
    # margin for at least one item - CSV, silver.menu_items.unit_cost, or
    # both - not just whether the CSV file happens to exist.
    meta["has_cost_data"] = any(r.get("unit_margin") is not None for r in analytics_payload["menu"])

    payload = {
        "meta": meta,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "orders": orders,
        "items": items,
        "analytics": analytics_payload,
    }

    template = TEMPLATE.read_text()
    if PLACEHOLDER not in template:
        raise SystemExit(f"{TEMPLATE.name} is missing the {PLACEHOLDER} placeholder")

    # </script> inside embedded JSON would close the host script tag early.
    data = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    args.out.write_text(template.replace(PLACEHOLDER, data))

    weekly_brief.write_brief(WEEKLY_BRIEF_OUT, meta, orders, analytics_payload)

    size_kb = args.out.stat().st_size / 1024
    print(f"{args.out.name}: {size_kb:.0f} KB")
    print(f"  {len(payload['orders'])} orders, {len(payload['items'])} line items")
    print(f"  {payload['meta']['first_order_at']} -> {payload['meta']['last_order_at']}")
    print(f"  has_cost_data={meta['has_cost_data']}")
    print(f"  price_source={analytics_payload['price_source']}"
          f" (gold.item_prices {'found' if item_prices_table is not None else 'absent'})")
    print(f"  silver.menu_items {'found' if menu_items_table is not None else 'absent'}"
          f", gold.data_quality {'found' if data_quality_table is not None else 'absent'}"
          f" ({len(analytics_payload['data_quality'])} checks)")
    print(f"  gold.combined_weekly_sales {'found' if combined_weekly_sales_table is not None else 'absent'}"
          f" (direct_vs_zomato {'present' if analytics_payload['direct_vs_zomato'] else 'absent'})")
    print(f"  {WEEKLY_BRIEF_OUT.name} written")


if __name__ == "__main__":
    main()
