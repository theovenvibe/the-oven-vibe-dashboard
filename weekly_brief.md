# Weekly brief - The Oven Vibe

Generated 2026-08-14T22:15:42 from 273 orders (2026-03-01T21:44:00 to 2026-08-07T19:38:00).

_No cost data loaded (`data/item_costs.csv` absent) - the menu matrix and any margin-flavoured numbers below are revenue, not profit. Fill in `data/item_costs.csv` from the `.example` file to upgrade this._

## Headline numbers

- **Next week's forecast** (2026-08-10): 7.9 orders (range 1.85-15.19), ₹2,336 revenue (range ₹548-₹4,491). Method: recency-weighted mean of last 4 same weekdays (0.4/0.3/0.2/0.1), +-1 stdev interval, basis n=8 active weeks.
- **Prep time is the biggest rating driver**: orders over 25 min average 2.17★ across n=6 rated slow orders, vs 4.16★ across n=44 rated orders at or under that threshold (orders with no recorded prep time are shown separately, not folded into either).
- **Repeat rate**: 30 of 215 customers (n=215) have placed more than one order (14.0%).
- **18 customers** (n=18) qualify for win-back (2+ orders, quiet 45+ days).
- **14 menu items** (n=14) have not sold in 30+ days while still on the menu.
- Prices sourced from `gold.item_prices`.

## What changed vs last week

- Week of 2026-08-03: 7 orders, ₹2,311 revenue.
- Week of 2026-07-27: 8 orders, ₹2,027 revenue.
- Change: -1 orders, +₹285 revenue.
- Cancel rate: 0.0% this week vs 0.0% prior week.
- Avg rating: 3.0 this week vs 3.0 prior week.
- New vs returning customers this week: 5 new, 2 returning.

## Data you can and cannot trust

Known issues:

- **WARN** `missing_week_gaps` (value=1): Weeks with no source CSV: 2026-06-08 to 2026-06-14

All checks (n=6):

| Check | Status | Value | Detail |
|---|---|---:|---|
| missing_week_gaps | warn | 1 | Weeks with no source CSV: 2026-06-08 to 2026-06-14 |
| duplicate_order_ids_bronze | ok | 0 | 0 duplicate Order ID rows in bronze.order_history_raw |
| unparsed_order_placed_at | ok | 0 | 0 bronze rows where Order Placed At failed to parse |
| unparsed_item_quantity | ok | 0 | 0 silver.order_items rows where quantity failed to parse |
| orders_with_no_items | ok | 0 | 0 orders in silver.orders with no matching line items |
| items_with_unknown_price | ok | 0 | 0 items in gold.item_prices with no resolvable price |

Attach-rate list excludes 10 main(s) with fewer than 5 delivered orders - too thin to state a rate: Bestseller Veg Fried Rice (3 orders), Classic Red Sauce Pasta (Penne) (2 orders), Creamy Cheese Maggi (2 orders), Garlic Fried Rice (1 orders), Mixed Treasure Fried Rice (3 orders), Paneer Fried Rice (2 orders), Paneer Tikka Grilled Sandwich [2 slices] (2 orders), Spicy Schezwan Special Fried Rice (2 orders), Tangy Green Chutney Sandwich [2 slices] (2 orders), Vegie Onion Capsicum Pizza [Regular, 7 inches] (2 orders).

## Ranked actions

### 1. Fix prep times over 25 minutes - it is the single biggest rating driver (ops, confidence: high)

Orders with prep time over 25 minutes average 2.17★ across 6 rated slow orders, versus 4.16★ across 44 rated orders with prep time 25 minutes or under.

- Expected impact: n/a - protects rating, not a direct rupee figure
- Evidence: 6 rated slow orders vs 44 rated fast orders; rating gap 1.99★

### 2. Win back the top 10 lapsed repeat customers (winback, confidence: low)

18 customers with 2+ orders have gone quiet for 45+ days, representing ₹8,654 in historical spend among the top 10.

- Expected impact: ₹1,731 - one-time, not monthly: 20% assumed reactivation on top-10 historical spend
- Evidence: n=18 winback candidates

### 3. Create a combo: Paneer Tikka Grilled Sandwich [2 slices] + 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] (combo, confidence: low)

Ordered together 2 times (indicative); price unknown for one item, no combo price suggested.

- Expected impact: ₹199 - 0.38 occurrences/month (n=2 historically) x ₹528 avg combined bill
- Evidence: n=2, lift=2.25, strength=indicative

### 4. Raise Street Style Korean Spicy Veg Maggi by ~₹20 (price_up, confidence: high)

High demand (15 units, price confidence observed) at a below-median price of ₹199. Low discount dependence (23% of its orders).

- Expected impact: ₹56 - 2.82 units/month x ₹20 rise
- Evidence: units=15, price_confidence=observed (price sample n=8)

### 5. Raise Fiery Cheese Chilli Sandwich [2 slices] by ~₹20 (price_up, confidence: high)

High demand (13 units, price confidence observed) at a below-median price of ₹169. Low discount dependence (25% of its orders).

- Expected impact: ₹49 - 2.45 units/month x ₹20 rise
- Evidence: units=13, price_confidence=observed (price sample n=6)

### 6. Create a combo: Crunchy Capsicum Pizza [Regular, 7 inches] + Spicy Peri Peri French Fries (combo, confidence: low)

Ordered together 2 times (indicative); price unknown for one item, no combo price suggested.

- Expected impact: ₹142 - 0.38 occurrences/month (n=2 historically) x ₹378 avg combined bill
- Evidence: n=2, lift=6.5, strength=indicative

### 7. Prompt a side with every Paneer Makhni Royale Pizza [Regular, 7 inches] (promo, confidence: medium)

Only 5% of its 40 orders include a side, below the best-observed attach rate.

- Expected impact: ₹68 - attach-rate gap x orders/month x median side price
- Evidence: orders=40, with_side=2

### 8. Consider dropping Garlic Fried Rice (drop, confidence: low)

Low demand (1 units lifetime, n=1 orders) at a below-median price, and it isn't a frequent combo attachment.

- Expected impact: ₹39 - menu-slot cost of carrying a low-mover, not a rupee saving
- Evidence: units=1, orders=1, revenue_share=0.0%

## Appendix: menu

| Item | Units | Revenue | Price | Confidence | Quadrant | Trend |
|---|---:|---:|---:|---|---|---:|
| 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] | 83 | ₹23,120 | ₹289 | observed | star | +0% |
| Paneer Makhni Royale Pizza [Regular, 7 inches] | 41 | ₹12,669 | ₹309 | observed | star | -86% |
| Golden Corn Classic Pizza [Regular, 7 inches] | 46 | ₹10,076 | ₹229 | observed | star | +0% |
| ⭐ Ultimate Cheese Delight Pizza [Regular, 7 inches] | 37 | ₹6,897 | ₹209 | observed | plowhorse | +0% |
| 🌙 Midnight Pizza Box Combo (7” Pizza + Small Fries) | 14 | ₹3,497 | ₹269 | observed | star | +25% |
| Fiesta Pizza Combo | 6 | ₹2,994 | ₹499 | observed | star | n/a |
| Street Style Korean Spicy Veg Maggi | 15 | ₹2,587 | ₹199 | observed | plowhorse | n/a |
| Fiery Cheese Chilli Sandwich [2 slices] | 13 | ₹2,028 | ₹169 | observed | plowhorse | n/a |
| Creamy Alfredo Pasta (Fusilli) | 8 | ₹1,752 | ₹219 | observed | star | n/a |
| Crunchy Capsicum Pizza [Regular, 7 inches] | 7 | ₹1,743 | ₹249 | observed | star | n/a |
| Zesty Onion Feast Pizza [Regular, 7 inches] | 9 | ₹1,512 | ₹189 | observed | plowhorse | n/a |
| Spicy Peri Peri French Fries | 12 | ₹1,309 | ₹119 | derived | plowhorse | n/a |
| 🔥 Most Ordered Classic French Fries | 12 | ₹1,188 | ₹99 | observed | plowhorse | n/a |
| Mixed Treasure Fried Rice | 3 | ₹897 | ₹299 | observed | star | n/a |
| Vegie Onion Capsicum Pizza [Regular, 7 inches] | 3 | ₹578 | ₹289 | observed | star | n/a |
| Bestseller Veg Fried Rice | 3 | ₹567 | ₹189 | observed | plowhorse | n/a |
| Spicy Schezwan Special Fried Rice | 2 | ₹556 | ₹278 | observed | puzzle | n/a |
| Paneer Fried Rice | 2 | ₹538 | ₹269 | observed | puzzle | n/a |
| Chilli Garlic Potato Pops | 3 | ₹474 | ₹158 | derived | plowhorse | n/a |
| Paneer Tikka Grilled Sandwich [2 slices] | 3 | ₹458 | ₹229 | derived | star | n/a |
| Creamy Cheese Maggi | 2 | ₹438 | ₹219 | observed | puzzle | n/a |
| Sandwich Meal Box Combo | 1 | ₹389 | ₹389 | observed | puzzle | n/a |
| Pasta Treat Combo | 1 | ₹377 | ₹377 | derived | puzzle | n/a |
| Classic Red Sauce Pasta (Penne) | 2 | ₹358 | ₹179 | observed | dog | n/a |
| Tangy Masala Corn | 2 | ₹258 | ₹129 | observed | dog | n/a |
| Tangy Green Chutney Sandwich [2 slices] | 2 | ₹238 | ₹119 | observed | dog | n/a |
| Garlic Fried Rice | 1 | ₹209 | ₹209 | observed | dog | n/a |
| Cheesy Corn Mix | 1 | ₹179 | ₹179 | observed | dog | n/a |

## Appendix: pairs

| A | B | n | strength | lift | combo price |
|---|---|---:|---|---:|---:|
| Crunchy Capsicum Pizza [Regular, 7 inches] | Spicy Peri Peri French Fries | 2 | indicative | 6.50 | n/a |
| Paneer Tikka Grilled Sandwich [2 slices] | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] | 2 | indicative | 2.25 | n/a |
| ⭐ Ultimate Cheese Delight Pizza [Regular, 7 inches] | 🔥 Most Ordered Classic French Fries | 3 | indicative | 1.84 | ₹280 |
| Golden Corn Classic Pizza [Regular, 7 inches] | Spicy Peri Peri French Fries | 3 | indicative | 1.48 | ₹310 |
| Spicy Peri Peri French Fries | ⭐ Ultimate Cheese Delight Pizza [Regular, 7 inches] | 2 | indicative | 1.23 | n/a |
| Paneer Makhni Royale Pizza [Regular, 7 inches] | 🔥 Most Ordered Classic French Fries | 2 | indicative | 1.14 | n/a |
| Fiery Cheese Chilli Sandwich [2 slices] | Paneer Makhni Royale Pizza [Regular, 7 inches] | 2 | indicative | 1.14 | n/a |
| 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] | 🔥 Most Ordered Classic French Fries | 4 | indicative | 1.12 | n/a |
| Creamy Alfredo Pasta (Fusilli) | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] | 2 | indicative (less often than chance) | 0.96 | n/a |
| Spicy Peri Peri French Fries | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] | 3 | indicative (less often than chance) | 0.84 | n/a |
| Street Style Korean Spicy Veg Maggi | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] | 2 | indicative (less often than chance) | 0.52 | n/a |
| Golden Corn Classic Pizza [Regular, 7 inches] | ⭐ Ultimate Cheese Delight Pizza [Regular, 7 inches] | 2 | indicative (less often than chance) | 0.32 | n/a |
| Golden Corn Classic Pizza [Regular, 7 inches] | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] | 3 | indicative (less often than chance) | 0.22 | n/a |
| Paneer Makhni Royale Pizza [Regular, 7 inches] | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] | 2 | indicative (less often than chance) | 0.17 | n/a |

## Appendix: forecast by weekday

| Weekday | Orders expected | Range | Revenue expected |
|---|---:|---:|---:|
| Mon | 0.6 | 0.1-1.1 | ₹177 |
| Tue | 1.4 | 0.11-2.69 | ₹414 |
| Wed | 1.9 | 1.4-2.4 | ₹562 |
| Thu | 1.5 | 0.0-3.23 | ₹444 |
| Fri | 1.4 | 0.25-2.55 | ₹414 |
| Sat | 0.6 | 0.0-1.75 | ₹177 |
| Sun | 0.5 | 0.0-1.46 | ₹148 |

Basis weeks (n=8):

| Week | Orders | Revenue |
|---|---:|---:|
| 2026-06-15 | 3 | ₹945 |
| 2026-06-22 | 12 | ₹3,446 |
| 2026-06-29 | 9 | ₹2,641 |
| 2026-07-06 | 11 | ₹2,795 |
| 2026-07-13 | 9 | ₹2,563 |
| 2026-07-20 | 9 | ₹2,560 |
| 2026-07-27 | 8 | ₹2,027 |
| 2026-08-03 | 7 | ₹2,311 |

## Appendix: win-back list (n=18)

| Customer | Orders | Spend | Last order | Days since | Favourite item |
|---|---:|---:|---|---:|---|
| cae781c91c564d21265740dfeca7d4e91c9729ec03c02c976237a907d775c0c8 | 4 | ₹1,292 | 2026-06-20 | 47 | Paneer Makhni Royale Pizza [Regular, 7 inches] |
| 5082fc72b4b94031860bfa45660dc4ff568f57eb650e1b1f0adc18dcbad093a3 | 4 | ₹1,274 | 2026-05-13 | 86 | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] |
| d908b23c029ece8581bb8d24a8e880fb861d6634864f3a83005f84f011105dbc | 2 | ₹1,085 | 2026-04-17 | 111 | Fiesta Pizza Combo |
| f0ac8d4fca436d571c3a35cac34fed56b12af83756d2c64423718d278997e131 | 2 | ₹943 | 2026-05-02 | 96 | Paneer Makhni Royale Pizza [Regular, 7 inches] |
| 70773b8a81799e3078a423e2757a650c5f45688207e9aeaa073c851110adb625 | 2 | ₹716 | 2026-04-29 | 100 | Golden Corn Classic Pizza [Regular, 7 inches] |
| fc87c3117c3f6e3ca67906476b93fb861c793e438e32ad745efb121b2cce6103 | 3 | ₹708 | 2026-05-05 | 94 | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] |
| 6157284ea51247f37b49b269315453bdf4d1ff2aaeaa5377f38d537ff835e034 | 2 | ₹688 | 2026-04-29 | 99 | ⭐ Ultimate Cheese Delight Pizza [Regular, 7 inches] |
| b5c63073bf3e99ead1a322b602cd8385b70c6c6e54e1f8873fa5c97eb68f4e48 | 2 | ₹683 | 2026-04-03 | 126 | Spicy Peri Peri French Fries |
| 309440d626f0564225868b93619400be189ad5aa61751fd651987f7d190a01d2 | 2 | ₹657 | 2026-03-16 | 143 | Creamy Alfredo Pasta (Fusilli) |
| 60a6a552e871be218f95ce2eed03ecd43a5b4dca23f7212640128fe9aa1f59f9 | 2 | ₹607 | 2026-03-04 | 156 | Paneer Makhni Royale Pizza [Regular, 7 inches] |
| 3e34d5ff9c00a7ace2e12503a2992ba7447b40c18c5e449aa301b4eb6aeaa0e4 | 2 | ₹598 | 2026-04-11 | 117 | 🔥 Herb Paneer Delight Pizza [Regular, 7 inches] |
| d938385876aa1fbbe2b82f7d42a32bb0003acb629caaa23f86ef7a2df2723c82 | 2 | ₹576 | 2026-04-22 | 107 | Paneer Makhni Royale Pizza [Regular, 7 inches] |
| 36c7acff75ff8698506472b6ef2b81b26b3296e65333d22be0f62a51f420d990 | 2 | ₹538 | 2026-05-16 | 83 | ⭐ Ultimate Cheese Delight Pizza [Regular, 7 inches] |
| 0472394d359ace87f27d19bdd24c480870d8474dcde257a9e9edaddde6cf5696 | 2 | ₹478 | 2026-04-18 | 111 | Golden Corn Classic Pizza [Regular, 7 inches] |
| 8635ba65059c6cebd4aa0c8dd61c67639d8bf7e049445bc03612b5b8a477747f | 2 | ₹428 | 2026-04-04 | 124 | Golden Corn Classic Pizza [Regular, 7 inches] |
| 295a65085bf780338cac8a396051d0e24d096ef91d632c7b30c0cbbb4871d967 | 2 | ₹418 | 2026-04-11 | 118 | Street Style Korean Spicy Veg Maggi |
| efe6e903260f23f00e75ff99cf17c975e7d4cbd253ef128e612dbe5fb5dfaaf0 | 2 | ₹407 | 2026-05-02 | 97 | Paneer Makhni Royale Pizza [Regular, 7 inches] |
| 610778b78f3718c3100f2253092f550ec75f0f3c8c09df2ced9ec8ab63615aab | 2 | ₹229 | 2026-03-18 | 141 | Creamy Cheese Maggi |
