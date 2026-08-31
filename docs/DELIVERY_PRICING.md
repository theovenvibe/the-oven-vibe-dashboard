# Delivery pricing and edge cases — August 2026

One person cooks and delivers. Every delivery therefore costs fuel, wear **and
kitchen downtime**, and the pricing has to hold up in the awkward cases, not
just the average one.

> **Read this before trusting a number here.** Everything computed from the
> warehouse is **Zomato orders only**. Direct WhatsApp and phone orders are not
> logged anywhere, and Zomato's listing closes with the kitchen — so the entire
> late-night and pickup trade is invisible. A late-night recommendation in an
> earlier draft was withdrawn for exactly this reason: the Zomato tail suggested
> ₹232 baskets, while real direct late orders run ₹400–500. Logging direct
> orders is the highest-value data fix available.

## Cost basis

- Petrol ₹109.55/l in Sundargarh (₹101.20 in January — up 8.25%).
- Scooter returns ~10 km/l, which is 4–5× worse than it should be. Verify with a
  full-tank-to-full-tank measurement over 100 km before spending on repairs.
- Wear (tyres, oil, servicing) ₹1.50 per km ridden.
- Owner's time ₹100/hour. Riding ~20 km/h effective, plus 5 minutes at the door.
- **Every delivery is a round trip.** A 4 km drop is 8 km of riding.

| Delivery | Ridden | Fuel + wear | Time | True cost @10 km/l | @40 km/l |
|---|---:|---:|---:|---:|---:|
| 2 km | 4 km | ₹50 | 17 min / ₹28 | **₹78** | ₹45 |
| 4 km | 8 km | ₹100 | 29 min / ₹48 | **₹148** | ₹82 |
| 6 km | 12 km | ₹149 | 41 min / ₹68 | **₹217** | ₹119 |

Menu prices for delivery carry a **+₹20 per item** markup, which on a 1.22-item
basket is about ₹24 of near-pure margin. Contribution per average order is
therefore ~₹71, not ₹47. The markup is invisible; the fee is not. Keep the money
in the markup.

## What the order data says

| Band | Orders | Share | Avg basket | Orders over ₹500 |
|---|---:|---:|---:|---:|
| 0–2 km | 138 | 53% | ₹321 | 16 |
| 2–4 km | 79 | 30% | ₹300 | 5 |
| 4 km+ | 43 | 17% | ₹315 | 3 |

- Median delivery is **1.0 km**. Basket size does **not** rise with distance.
- The two highest-spending customers are at 2.8 km and 4.0 km — the 2–4 km band
  must stay served, but on customer terms, not band terms.
- 21 orders (8%) are under ₹200. Those lose money at any distance.
- After 11pm: 6 orders, ₹232 average. Reopening the kitchen for that loses money.
- Monsoon (Jun–Jul) cuts volume roughly in half and shortens average delivery
  distance to 1.6 km. Rain does not bring bigger baskets.

## Edge-case register

### Geography
1. **Premium customers beyond 2 km** — NTPC Hospital (~4 km), Sriram Nagar
   (~3 km). Highest lifetime spenders. Served, with a minimum order.
2. **Beyond 4 km** — 11 orders were 8–13 km, costing ₹200–320 of riding against
   a ₹99 fee. Route to Zomato, which already delivers every current order at no
   per-trip cost to the kitchen.
3. **Gated campuses** — hospital gates and staff quarters add waiting time that
   no distance band captures. Handled by the campus batch rate below.

### Time
4. **After-hours reopen (23:30–02:00)** — oven relight, gas, and the owner's
   night. Costs ~₹100 above a normal run. Only the oven and fryer run: pasta
   and maggi are off, and any combo containing them goes with them.
4b. **Kitchen closed (02:00–11:30)** — ten and a half hours a day when a price
   checker must say "closed" rather than quote an order nobody can cook. The
   calculator greys out every item and names the opening time.
5. **Peak-hour delivery (19:00–21:00)** — 52 orders land at 7pm alone. Leaving
   the kitchen then does not cost ₹48 of time; it costs the orders not cooked,
   and it makes the rest late. Orders over 25 minutes of prep average **2.17★
   against 4.16★**. This is a routing rule, not a fee.
6. **Quiet hours (12:00–16:00 weekdays)** — kitchen is idle, so the owner's time
   is nearly free. These deliveries should be *cheaper*, to pull demand into the
   dead window.
7. **Pre-scheduled orders** — let the owner batch and plan gas. Reward them.

### Weather
8. **Rain** — slower riding, spoilage risk, personal risk. Monsoon is Jun–Sep.
9. **Extreme heat** — pizza box condensation on long runs; another reason the
   radius stops at 4 km.

### Basket
10. **Small orders** — 8% of orders are under ₹200. A ₹99 fries delivered 2 km
    is a guaranteed loss.
11. **Bulk / party orders** — good money, but oven capacity is finite and one
    person cannot cook six pizzas and deliver at once. Needs lead time.
12. **Threshold gaming** — free delivery must never apply at distances where the
    basket cannot cover the ride.

### Operational risk
13. **Cash on delivery** — refusal and no-change risk rises with basket size,
    distance and lateness.
14. **Cancellation after cooking** — 13 orders were lost in five months, ₹1.4K of
    it to Zomato cancellations.
15. **Single-person capacity** — one "kitchen is full" rejection already in the
    data. Cooking and riding cannot overlap.
16. **Gas cylinder exhaustion mid-service** — the reason the wok station is gone.
17. **Customer unreachable at the door** — dead time with no revenue.

### Customer equity
18. **Regulars must not be surged.** 24 customers have ordered more than once and
    repeat rate is only 14%. Surging the few people who come back is the most
    expensive rupee on this page.
19. **Zomato price parity** — customers who see both channels must not feel
    cheated. Zomato already prices ~1.5× the local menu, so direct stays cheaper
    even after the delivery markup.
20. **Surge stacking** — late night plus rain plus distance must never compound
    into an absurd number. Hard cap.

## The pricing

### Base

| Distance | Fee | Minimum order | Free delivery above |
|---|---:|---:|---:|
| 0–2 km | ₹29 | ₹199 | ₹499 |
| 2–4 km | ₹69 | ₹399 | ₹699 |
| Beyond 4 km | — | — | order via Zomato |

### Situational

| Case | Charge | Rule |
|---|---:|---|
| After-hours kitchen (23:30–02:00) | +₹49 | Every late order, **pickup included** — the oven is fired either way. Minimum ₹399, prepaid, **no pasta or maggi** |
| After-hours delivery (23:30–02:00) | +₹30 | On top of the normal distance fee. Free delivery is switched off in this window |
| Pickup during the late window | discount withdrawn | The ₹30 pickup discount does not apply — collecting saves the ride, not the reopen |
| Rain | +₹29 | Only while declared on the site; never applied retroactively. **Waived on a prepaid order — except late night**, where prepaying is the condition of firing the oven rather than a waiver, so the charge still applies |
| Pre-order | — | An explicit mode with **3 hours** of prep notice. Every rule is judged at the chosen slot: a pre-order for 11:45pm is priced as late night |
| Quiet hours (12:00–16:00, Mon–Fri) | **₹19** | Free above ₹349 |
| Pre-ordered 3+ hours ahead | **−₹10** | Lets the kitchen batch |
| Campus batch (NTPC, Sriram Nagar) | **₹39 flat** | 2+ orders, same campus, within a 20-minute window |
| Pickup | **−₹30** | Cheapest possible outcome for the kitchen |
| Bulk (4+ pizzas) | free delivery, 10% off | 60 minutes' notice, prepaid |

**Hard caps and protections**

- Total delivery charge never exceeds **₹149**, and that ceiling covers the base
  fee *and* every surcharge. An earlier ₹99 cap applied to the base fee only,
  which made a late-night 0–2 km run (₹29 + ₹79 = ₹108) contradict the promise
  printed beside it. The worst realistic stack — 2–4 km plus late night plus
  rain, ₹177 — now lands on the cap, and the breakdown shows the capping line
  rather than silently adjusting.
- Customers with 3+ orders: all situational fees waived, free delivery above
  ₹399. **Not offered publicly yet** — direct orders are not logged anywhere, so
  a self-declared claim could not be verified, and the site must not advertise a
  benefit that cannot be administered. Applied by hand when the kitchen quotes;
  re-expose it once repeat customers are actually tracked.
- Cash on delivery capped at ₹500. Prepaid required for after-hours, bulk, and
  anything beyond 2 km.

### Does every row earn?

Contribution = 15% of basket + ₹24 markup.

| Scenario | Fee | Contribution | In | Cost | Result |
|---|---:|---:|---:|---:|---:|
| 0–2 km, ₹314 basket | ₹29 | ₹71 | ₹100 | ₹78 | **+₹22** |
| 0–2 km, ₹499 (free delivery) | ₹0 | ₹99 | ₹99 | ₹78 | **+₹21** |
| 2–4 km, ₹399 minimum | ₹69 | ₹84 | ₹153 | ₹148 | **+₹5** |
| 2–4 km, NTPC regular at ₹413 | ₹69 | ₹86 | ₹155 | ₹148 | **+₹7** |
| After hours delivery, ₹400 | ₹108 | ₹84 | ₹192 | ₹178 | **+₹14** |
| After hours pickup, ₹400 | ₹49 | ₹84 | ₹133 | ₹100 | **+₹33** |
| After hours delivery, ₹500 | ₹108 | ₹105 | ₹213 | ₹178 | **+₹35** |
| After hours pickup, ₹500 | ₹49 | ₹105 | ₹154 | ₹100 | **+₹54** |
| Quiet hours, ₹314 basket | ₹19 | ₹71 | ₹90 | ₹25 | **+₹65** |
| Pickup, ₹314 basket | −₹30 | ₹71 | ₹41 | ₹0 | **+₹41** |

Nothing loses money. The 2–4 km rows are thin — **₹5–7** — and that is entirely
the mileage. At 40 km/l the same rows earn **+₹71 and +₹73**. Until the scooter
is serviced, batch those runs or let Zomato take them.

## Review

Re-check when petrol moves more than ₹5/l, when the scooter's mileage changes,
or when the share of orders beyond 2 km exceeds 40%. The Demand tab's quiet
windows tell you which hours to keep the quiet-hour rate on.
