# Weekly brief - The Oven Vibe

Generated 2026-08-31T19:27:18 from 302 orders (2026-03-01T21:44:00 to 2026-08-30T23:43:00).

_No cost data loaded (`data/item_costs.csv` absent) - the menu matrix and any margin-flavoured numbers below are revenue, not profit. Fill in `data/item_costs.csv` from the `.example` file to upgrade this._

## Headline numbers

- **Next week's forecast** (2026-08-31): 13.3 orders (range 1.92-25.58), ₹3,954 revenue (range ₹572-₹7,605). Method: recency-weighted mean of last 4 same weekdays (0.4/0.3/0.2/0.1), +-1 stdev interval, basis n=8 active weeks.
- **Prep time is the biggest rating driver**: orders over 25 min average 2.17★ across n=6 rated slow orders, vs 4.24★ across n=50 rated orders at or under that threshold (orders with no recorded prep time are shown separately, not folded into either).
- **Repeat rate**: 34 of 238 customers (n=238) have placed more than one order (14.3%).
- **20 customers** (n=20) qualify for win-back (2+ orders, quiet 45+ days).
- **18 menu items** (n=18) have not sold in 30+ days while still on the menu.
- Prices sourced from `gold.item_prices`.

## What changed vs last week

- Week of 2026-08-24: 24 orders, ₹6,732 revenue.
- Week of 2026-08-17: 5 orders, ₹1,713 revenue.
- Change: +19 orders, +₹5,019 revenue.
- Cancel rate: 4.0% this week vs 0.0% prior week.
- Avg rating: 4.83 this week vs 5.0 prior week.
- New vs returning customers this week: 20 new, 4 returning.

## Direct vs Zomato

All-time confirmed orders, by channel:

| Source | Orders | Revenue |
|---|---:|---:|
| zomato | 288 | ₹90,049 |
| direct | 10 | ₹3,617 |

## Data you can and cannot trust

No warnings or failures in the current data-quality checks.

All checks (n=6):

| Check | Status | Value | Detail |
|---|---|---:|---|
| missing_week_gaps | ok | 0 | Weeks with no source CSV: none |
| duplicate_order_ids_bronze | ok | 0 | 0 duplicate Order ID rows in bronze.order_history_raw |
| unparsed_order_placed_at | ok | 0 | 0 bronze rows where Order Placed At failed to parse |
| unparsed_item_quantity | ok | 0 | 0 silver.order_items rows where quantity failed to parse |
| orders_with_no_items | ok | 0 | 0 orders in silver.orders with no matching line items |
| items_with_unknown_price | ok | 0 | 0 items in gold.item_prices with no resolvable price |

Attach-rate list excludes 14 main(s) with fewer than 5 delivered orders - too thin to state a rate: Bestseller Veg Fried Rice (3 orders), Classic Red Sauce Pasta (Penne) (3 orders), Creamy Cheese Maggi (2 orders), Garlic Fried Rice (1 orders), Herb Paneer Delight Pizza (1 orders), Midnight Pizza Box Combo (2 orders), Mixed Treasure Fried Rice (3 orders), Paneer Fried Rice (2 orders), Paneer Tikka Grilled Sandwich [2 slices] (2 orders), Spicy Schezwan Special Fried Rice (2 orders), Tangy Green Chutney Sandwich [2 slices] (2 orders), Ultimate Cheese Delight Pizza (2 orders), Ultimate Cheese Delight Pizza [Regular, 7 inches] (4 orders), Vegie Onion Capsicum Pizza [Regular, 7 inches] (4 orders).

## Ranked actions

### 1. Fix prep times over 25 minutes - it is the single biggest rating driver (ops, confidence: high)

Orders with prep time over 25 minutes average 2.17★ across 6 rated slow orders, versus 4.24★ across 50 rated orders with prep time 25 minutes or under.

- Expected impact: n/a - protects rating, not a direct rupee figure
- Evidence: 6 rated slow orders vs 50 rated fast orders; rating gap 2.07★

### 2. Win back the top 10 lapsed repeat customers (winback, confidence: low)

20 customers with 2+ orders have gone quiet for 45+ days, representing ₹9,083 in historical spend among the top 10.

- Expected impact: ₹1,817 - one-time, not monthly: 20% assumed reactivation on top-10 historical spend
- Evidence: n=20 winback candidates

### 3. Revive or retire Street Style Korean Spicy Veg Maggi (revive, confidence: medium)

Dormant 33 days (last sold 2026-07-28) after selling 15 units lifetime across 9 active weeks, 0.59 units/week when active.

- Expected impact: ₹508 - 0.59 units/week x ₹199 x 4.33 weeks/month, if revived, capped at best observed 4-week revenue
- Evidence: units_lifetime=15, active_weeks=9, days_dormant=33

### 4. Revive or retire Fiery Cheese Chilli Sandwich [2 slices] (revive, confidence: low)

Dormant 49 days (last sold 2026-07-12) after selling 13 units lifetime across 8 active weeks, 0.62 units/week when active.

- Expected impact: ₹454 - 0.62 units/week x ₹169 x 4.33 weeks/month, if revived, capped at best observed 4-week revenue
- Evidence: units_lifetime=13, active_weeks=8, days_dormant=49

### 5. Create a combo: ⭐ Ultimate Cheese Delight Pizza [Regular, 7 inches] + 🔥 Most Ordered Classic French Fries (combo, confidence: low)

Ordered together 3 times (indicative); combo price ~₹280.

- Expected impact: ₹183 - 0.52 occurrences/month (n=3 historically) x ₹352 avg combined bill
- Evidence: n=3, lift=2.04, strength=indicative

### 6. Prompt a side with every Paneer Makhni Royale Pizza [Regular, 7 inches] (promo, confidence: medium)

Only 4% of its 45 orders include a side, below the best-observed attach rate.

- Expected impact: ₹84 - attach-rate gap x orders/month x median side price
- Evidence: orders=45, with_side=2

### 7. Raise Street Style Korean Spicy Veg Maggi by ~₹20 (price_up, confidence: high)

High demand (15 units, price confidence observed) at a below-median price of ₹199. Low discount dependence (23% of its orders).

- Expected impact: ₹52 - 2.6 units/month x ₹20 rise
- Evidence: units=15, price_confidence=observed (price sample n=8)

### 8. Raise Fiery Cheese Chilli Sandwich [2 slices] by ~₹20 (price_up, confidence: high)

High demand (13 units, price confidence observed) at a below-median price of ₹169. Low discount dependence (25% of its orders).

- Expected impact: ₹45 - 2.25 units/month x ₹20 rise
- Evidence: units=13, price_confidence=observed (price sample n=6)

## Appendix: menu

| Item | Units | Revenue | Price | Confidence | Quadrant | Trend |
|---|---:|---:|---:|---|---|---:|
| 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] | 83 | ₹23,120 | ₹289 | observed | star | -14% |
| Paneer Makhni Royale Pizza [Regular, 7 inches] | 46 | ₹14,214 | ₹309 | observed | star | -17% |
| Golden Corn Classic Pizza [Regular, 7 inches] | 51 | ₹11,221 | ₹229 | observed | star | +0% |
| ⭐ Ultimate Cheese Delight Pizza [Regular, 7 inches] | 37 | ₹6,897 | ₹209 | observed | plowhorse | -91% |
| 🌙 Midnight Pizza Box Combo (7” Pizza + Small Fries) | 14 | ₹3,497 | ₹269 | observed | star | -40% |
| Fiesta Pizza Combo | 7 | ₹3,493 | ₹499 | observed | star | n/a |
| Herb Paneer Delight Pizza [Regular, 7 inches] | 7 | ₹2,723 | ₹389 | observed | star | n/a |
| Street Style Korean Spicy Veg Maggi | 15 | ₹2,587 | ₹199 | observed | plowhorse | n/a |
| Fiery Cheese Chilli Sandwich [2 slices] | 13 | ₹2,028 | ₹169 | observed | plowhorse | n/a |
| Creamy Alfredo Pasta (Fusilli) | 8 | ₹1,752 | ₹219 | observed | plowhorse | n/a |
| Crunchy Capsicum Pizza [Regular, 7 inches] | 7 | ₹1,743 | ₹249 | observed | star | n/a |
| Zesty Onion Feast Pizza [Regular, 7 inches] | 9 | ₹1,512 | ₹189 | observed | plowhorse | n/a |
| Midnight Pizza Box Combo | 2 | ₹1,334 | ₹667 | observed | puzzle | n/a |
| Spicy Peri Peri French Fries | 12 | ₹1,309 | ₹119 | derived | plowhorse | n/a |
| Ultimate Cheese Delight Pizza [Regular, 7 inches] | 4 | ₹1,196 | ₹299 | observed | star | n/a |
| 🔥 Most Ordered Classic French Fries | 12 | ₹1,188 | ₹99 | observed | plowhorse | n/a |
| Vegie Onion Capsicum Pizza [Regular, 7 inches] | 5 | ₹1,156 | ₹289 | observed | star | n/a |
| Mixed Treasure Fried Rice | 3 | ₹897 | ₹299 | observed | puzzle | n/a |
| Ultimate Cheese Delight Pizza | 2 | ₹598 | ₹299 | observed | puzzle | n/a |
| Bestseller Veg Fried Rice | 3 | ₹567 | ₹189 | observed | dog | n/a |
| Spicy Schezwan Special Fried Rice | 2 | ₹556 | ₹278 | observed | puzzle | n/a |
| Paneer Fried Rice | 2 | ₹538 | ₹269 | observed | puzzle | n/a |
| Classic Red Sauce Pasta (Penne) | 3 | ₹537 | ₹179 | observed | dog | n/a |
| Chilli Garlic Potato Pops | 3 | ₹474 | ₹158 | derived | dog | n/a |
| Paneer Tikka Grilled Sandwich [2 slices] | 5 | ₹458 | ₹229 | derived | star | n/a |
| Creamy Cheese Maggi | 2 | ₹438 | ₹219 | observed | dog | n/a |
| Herb Paneer Delight Pizza | 1 | ₹389 | ₹389 | derived | puzzle | n/a |
| Sandwich Meal Box Combo | 1 | ₹389 | ₹389 | observed | puzzle | n/a |

## Appendix: pairs

| A | B | n | strength | lift | combo price |
|---|---|---:|---|---:|---:|
| Crunchy Capsicum Pizza [Regular, 7 inches] | Spicy Peri Peri French Fries | 2 | indicative | 7.19 | n/a |
| ⭐ Ultimate Cheese Delight Pizza [Regular, 7 inches] | 🔥 Most Ordered Classic French Fries | 3 | indicative | 2.04 | ₹280 |
| Paneer Tikka Grilled Sandwich [2 slices] | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] | 2 | indicative | 1.86 | n/a |
| Golden Corn Classic Pizza [Regular, 7 inches] | Spicy Peri Peri French Fries | 3 | indicative | 1.48 | ₹310 |
| Spicy Peri Peri French Fries | ⭐ Ultimate Cheese Delight Pizza [Regular, 7 inches] | 2 | indicative | 1.36 | n/a |
| 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] | 🔥 Most Ordered Classic French Fries | 4 | indicative | 1.24 | ₹350 |
| Paneer Makhni Royale Pizza [Regular, 7 inches] | 🔥 Most Ordered Classic French Fries | 2 | indicative | 1.12 | n/a |
| Fiery Cheese Chilli Sandwich [2 slices] | Paneer Makhni Royale Pizza [Regular, 7 inches] | 2 | indicative | 1.12 | n/a |
| Creamy Alfredo Pasta (Fusilli) | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] | 2 | indicative | 1.07 | n/a |
| Spicy Peri Peri French Fries | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] | 3 | indicative (less often than chance) | 0.93 | n/a |
| Street Style Korean Spicy Veg Maggi | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] | 2 | indicative (less often than chance) | 0.57 | n/a |
| Golden Corn Classic Pizza [Regular, 7 inches] | ⭐ Ultimate Cheese Delight Pizza [Regular, 7 inches] | 2 | indicative (less often than chance) | 0.32 | n/a |
| Golden Corn Classic Pizza [Regular, 7 inches] | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] | 3 | indicative (less often than chance) | 0.22 | n/a |
| Paneer Makhni Royale Pizza [Regular, 7 inches] | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] | 2 | indicative (less often than chance) | 0.17 | n/a |

## Appendix: forecast by weekday

| Weekday | Orders expected | Range | Revenue expected |
|---|---:|---:|---:|
| Mon | 1.7 | 0.0-3.59 | ₹505 |
| Tue | 2.6 | 0.38-4.82 | ₹773 |
| Wed | 1.8 | 0.54-3.06 | ₹535 |
| Thu | 1.0 | 0.0-2.41 | ₹297 |
| Fri | 1.4 | 0.4-2.4 | ₹416 |
| Sat | 3.6 | 0.6-6.6 | ₹1,070 |
| Sun | 1.2 | 0.0-2.7 | ₹357 |

Basis weeks (n=8):

| Week | Orders | Revenue |
|---|---:|---:|
| 2026-06-29 | 9 | ₹2,641 |
| 2026-07-06 | 11 | ₹2,795 |
| 2026-07-13 | 9 | ₹2,563 |
| 2026-07-20 | 9 | ₹2,560 |
| 2026-07-27 | 8 | ₹2,027 |
| 2026-08-03 | 7 | ₹2,311 |
| 2026-08-17 | 5 | ₹1,713 |
| 2026-08-24 | 24 | ₹6,732 |

## Appendix: win-back list (n=20)

| Customer | Orders | Spend | Last order | Days since | Favourite item |
|---|---:|---:|---|---:|---|
| cae781c91c564d21265740dfeca7d4e91c9729ec03c02c976237a907d775c0c8 | 4 | ₹1,292 | 2026-06-20 | 71 | Paneer Makhni Royale Pizza [Regular, 7 inches] |
| 5082fc72b4b94031860bfa45660dc4ff568f57eb650e1b1f0adc18dcbad093a3 | 4 | ₹1,274 | 2026-05-13 | 109 | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] |
| d908b23c029ece8581bb8d24a8e880fb861d6634864f3a83005f84f011105dbc | 2 | ₹1,085 | 2026-04-17 | 135 | Fiesta Pizza Combo |
| 54fd77bc508143b4bd8c664f1342be738f462a35e992c76d8cac083cec2c2c9e | 2 | ₹976 | 2026-06-23 | 68 | Street Style Korean Spicy Veg Maggi |
| f0ac8d4fca436d571c3a35cac34fed56b12af83756d2c64423718d278997e131 | 2 | ₹943 | 2026-05-02 | 120 | Paneer Makhni Royale Pizza [Regular, 7 inches] |
| 5b76856af5addc8554e6b7ab7c227d4ac327c0ff3372cd959c34cc77f09c9b4f | 3 | ₹776 | 2026-06-26 | 65 | ⭐ Ultimate Cheese Delight Pizza [Regular, 7 inches] |
| fc87c3117c3f6e3ca67906476b93fb861c793e438e32ad745efb121b2cce6103 | 3 | ₹708 | 2026-05-05 | 117 | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] |
| 6157284ea51247f37b49b269315453bdf4d1ff2aaeaa5377f38d537ff835e034 | 2 | ₹688 | 2026-04-29 | 123 | ⭐ Ultimate Cheese Delight Pizza [Regular, 7 inches] |
| b5c63073bf3e99ead1a322b602cd8385b70c6c6e54e1f8873fa5c97eb68f4e48 | 2 | ₹683 | 2026-04-03 | 149 | Spicy Peri Peri French Fries |
| 309440d626f0564225868b93619400be189ad5aa61751fd651987f7d190a01d2 | 2 | ₹657 | 2026-03-16 | 167 | Creamy Alfredo Pasta (Fusilli) |
| 60a6a552e871be218f95ce2eed03ecd43a5b4dca23f7212640128fe9aa1f59f9 | 2 | ₹607 | 2026-03-04 | 179 | Paneer Makhni Royale Pizza [Regular, 7 inches] |
| 3e34d5ff9c00a7ace2e12503a2992ba7447b40c18c5e449aa301b4eb6aeaa0e4 | 2 | ₹598 | 2026-04-11 | 141 | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] |
| d938385876aa1fbbe2b82f7d42a32bb0003acb629caaa23f86ef7a2df2723c82 | 2 | ₹576 | 2026-04-22 | 130 | Paneer Makhni Royale Pizza [Regular, 7 inches] |
| 909210241d485c870828d2340927546857a7323dfdf18336a62bc9a28ce14a3c | 2 | ₹576 | 2026-06-26 | 65 | Golden Corn Classic Pizza [Regular, 7 inches] |
| 36c7acff75ff8698506472b6ef2b81b26b3296e65333d22be0f62a51f420d990 | 2 | ₹538 | 2026-05-16 | 106 | ⭐ Ultimate Cheese Delight Pizza [Regular, 7 inches] |
| 0472394d359ace87f27d19bdd24c480870d8474dcde257a9e9edaddde6cf5696 | 2 | ₹478 | 2026-04-18 | 134 | Golden Corn Classic Pizza [Regular, 7 inches] |
| 8635ba65059c6cebd4aa0c8dd61c67639d8bf7e049445bc03612b5b8a477747f | 2 | ₹428 | 2026-04-04 | 148 | Golden Corn Classic Pizza [Regular, 7 inches] |
| 295a65085bf780338cac8a396051d0e24d096ef91d632c7b30c0cbbb4871d967 | 2 | ₹418 | 2026-04-11 | 141 | Street Style Korean Spicy Veg Maggi |
| efe6e903260f23f00e75ff99cf17c975e7d4cbd253ef128e612dbe5fb5dfaaf0 | 2 | ₹407 | 2026-05-02 | 120 | Paneer Makhni Royale Pizza [Regular, 7 inches] |
| 610778b78f3718c3100f2253092f550ec75f0f3c8c09df2ced9ec8ab63615aab | 2 | ₹229 | 2026-03-18 | 165 | Creamy Cheese Maggi |
