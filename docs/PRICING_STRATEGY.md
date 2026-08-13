# Pricing strategy — local menu, August 2026

Written from `analytics.menu` (units, quadrant, revenue share) and
`analytics.attach` in the dashboard, plus two owner-supplied facts: cost
inflation is running near 45%, and the proposed price list returns about 10%
net profit.

## The problem with a flat rise

The ₹20 taken two months ago was flat, so it landed unevenly: +25% on a ₹79
side, +7% on a ₹279 combo. Add-ons got nothing at all. A flat rupee rise always
overcharges the cheap end (where customers are most price-aware) and
undercharges the expensive end (where they are least).

## The ladder

Every item sits in one of six tiers. The tier decides the move, and the tier
comes from demand data, not from taste.

| Tier | Rule | Why | Volume |
|---|---|---|---|
| **A — Anchor** | hold | The prices customers check before deciding the menu is expensive: the cheapest pizza, Classic Fries, the entry sandwich. These set price perception for everything else. | 7% |
| **B — Bestseller** | +1 step (₹10) | Herb Paneer, Golden Corn, Paneer Makhni, Ultimate Cheese are 65% of all units. They are chosen for taste, not price, but the concentration means any mistake here is the whole business — so one small step only. | 65% |
| **C — Mid-tail** | +1 rung (₹10–20) | Real demand, no price-anchor role. Absorbs a normal rise. | 18% |
| **D — Impulse** | +2 rungs (₹20) | Sides, dips, extras. Bought inside a bigger bill where a ₹20 move is invisible, and they were never raised. | 6% |
| **E — Dead weight** | +2 rungs or delist | 14 items have not sold in 100+ days. A rise on an item nobody orders costs nothing; if it still does not sell, delist it and cut the prep/stock load. | 4% |
| **F — Combo** | ~10% off parts | See below. | — |

## Combo pricing

A combo prices at **about 10% off the sum of its parts**, rounded to a ₹9
ending, and must sit **at least ₹40 above its own main item's solo price**.

15–17% is a promotion, not a standing price. The first pass here held combo
prices flat while components rose, which pushed the savings to 16–17% by
accident — generous enough that the combo cannibalises the à-la-carte sale it
was meant to grow. Shipped prices:

| Combo | Parts | Price | Saves | Above its main |
|---|---:|---:|---:|---:|
| Fiesta Pizza | 378 | 339 | ₹39 (10%) | +130 |
| Pasta Treat | 348 | 309 | ₹39 (11%) | +100 |
| Sandwich Meal Box | 308 | 279 | ₹29 (9%) | +110 |

Parts assume the Coke at ₹40; it is not a priced SKU in `menu.json`.

**A "one item + drink" bundle cannot work.** Its only lever is the drink, so the
discount caps at the drink's value — around 12% — and the combo lands within
₹10 of the item sold alone. Both rice meal boxes had that shape and both sold
zero units in five months. A combo needs a main plus a side.

## What it produces

- Blended uplift over the proposed list: **+6.0%**, unit-weighted.
- Net margin: **10% → 15.1%**. Profit per ₹100 of sales rises from ₹10 to ₹15 —
  about 50% more profit rupees on the same volume.
- Felt change on a typical order: **₹10–30 on one item**. The entry price of
  each category does not move at all.

Full inflation recovery is not attempted. Cost is up ~45%; this plan takes
about 22% over the old list in total. Chasing the rest through menu price in
one move would cost volume — the remainder has to come from attach rate,
portion control and supplier terms.

## Guardrails

1. **Never move an anchor.** Zesty Onion Feast Pizza ₹129, Classic French Fries
   ₹99, Tangy Green Chutney Sandwich ₹89. If these rise, the whole menu reads as
   expensive regardless of what else is true.
2. **Keep every combo cheaper than its parts by ₹30 or more.** After this
   revision Fiesta is the one at risk — hold it at ₹319 while its components
   rise, or it stops being a combo.
3. **One step at a time.** Take the proposed list now; take the optimise column
   6–8 weeks later, only if the dashboard shows units holding.
4. **Watch, in this order:** units on the four bestsellers, then average order
   value, then repeat rate. Rate is the last to move and the first that matters —
   losing a repeat customer costs more than the rise earns.

## Menu cut — August 2026

The gas price rise and shortage forced the wok station out, which the demand data
supports independently: the five fried-rice SKUs together sold 11 units in five
months, on the most fuel-hungry station in the kitchen.

Dropped from `menu.json` (11 SKUs): all five fried rice items, both rice
meal-box combos, Creamy Cheese Maggi (2 units — Korean Spicy Maggi at 15 units
stays), Tangy Masala Corn and Cheesy Corn Mix (3 units combined, no basket
role), Motu Burger (never ordered, never on the printed menu).

Kept deliberately: Classic Red Sauce Pasta (owner's call), Tangy Green Chutney
Sandwich (₹89 price anchor), Vegie Onion Capsicum Pizza (same oven line, so the
marginal cost of carrying it is near zero), Chilli Garlic Potato Pops (shares
the fryer with fries).

Any new SKU must be oven, griddle or fryer — no wok, no long boil — until gas
economics change. A shorter menu also shortens prep, and prep time is the
biggest rating driver in this data (2.17★ over 25 minutes vs 4.16★ under).

## The non-price lever

Attach rate on pizzas is 10%, and the best-observed rate on a main with real
volume is 12%. Every attached side is a high-margin add with no menu-price
change at all. Moving attach from 10% to 25% is worth more than another ₹10 on
the bestsellers, and no customer experiences it as a price rise.

## Review loop

Re-run `uv run build.py` weekly and read the Menu tab. The quadrant an item sits
in is the tier signal: a plowhorse (high demand, low price) is the next
candidate for a rise; a puzzle (low demand, high price) needs promotion or
repositioning before any further increase; a dog with no basket role is a
delisting, not a pricing problem.
