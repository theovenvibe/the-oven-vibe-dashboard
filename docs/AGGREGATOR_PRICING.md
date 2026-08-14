# Aggregator pricing — Zomato and Swiggy

One price list for both platforms, reverse-calculated from what actually reaches
the bank. Derived from a real settlement statement, not an estimate.

## The settlement, reconciled

Payout cycle 06–12 Jul 2026, 11 orders, 8 delivered. Every line ties out against
the warehouse to the paisa:

```
A  customer paid ₹2,795 + 5% GST ₹139.75            = ₹2,934.75  ✓
C  commission ₹755.09 (27.0%) + penalties ₹239.78   = ₹994.87    ✓
D  GST remitted ₹139.75 + 18% GST on commission ₹135.92 = ₹275.68 ✓
                                             net payout = ₹1,664.21 ✓
```

**Commission is 27.0%**, plus 18% GST on that commission — not the 40% assumed
earlier. That week carried no advertising spend and no restaurant-funded
discount.

| | Realisation | Markup needed |
|---|---:|---:|
| As billed (no ads, no own discount) | **68.1%** | **1.47×** |
| Including that week's rejection penalties | 59.5% | 1.68× |
| If a 20% restaurant-funded discount runs | 54.5% | 1.83× |
| Plus ads at ₹500/week over 8 orders | 36.6% | 2.73× |

## Rejections cost more than any pricing decision

Three of eleven orders were rejected or timed out that week, costing **₹239.78 in
penalties — 8.6% of the week's order value.** That is larger than several points
of commission, and it is entirely self-inflicted.

At 27% commission the platform is workable. At 27% plus a 27% rejection rate it
is not. Fixing rejections is worth more than every price change in this document.

## The price list — one list, both platforms

Priced so it never has to change again: it carries the commission, a **20%
discount allowance** and a **10% ads allowance** simultaneously, and still clears
the local floor. Every rung is at least **2.04×** local, which is the point where
those three costs together stop eating the margin.

| Markup | Survives 20% discount | + 10% ads | Customer still ≥ local price until |
|---:|---:|---:|---:|
| 1.47× (bare floor) | no | no | 32% off |
| 1.84× | yes | no | 46% off |
| **2.2× (chosen)** | **yes** | **yes** | **55% off** |

At 2.2× the headroom is: **27% discount** alone, or **20% discount plus 15% ads**
together, before payout drops under the local price.

### The ladder

Steps shrink as the customer climbs, so the first trade-up is the only real
decision and every rung after it feels like small change:

| Pizza | Local | **Aggregator** | Step |
|---|---:|---:|---:|
| Zesty Onion Feast | 129 | **289** | entry |
| Ultimate Cheese Delight | 159 | **349** | +60 |
| Golden Corn Classic | 169 | **379** | +30 |
| Crunchy Capsicum | 189 | **419** | +40 |
| Herb Paneer Delight | 209 | **459** | +40 |
| Vegie Onion Capsicum | 219 | **479** | +20 |
| Paneer Makhni Royale | 229 | **519** | +40 |

Paneer Makhni at ₹519 is the anchor: it exists to make ₹459 read as mid-range.

| Rest of the menu | Local | **Aggregator** |
|---|---:|---:|
| Tangy Green Chutney Sandwich | 89 | **199** |
| Fiery Cheese Chilli Sandwich | 129 | **289** |
| Street Style Korean Maggi | 159 | **349** |
| Paneer Tikka Sandwich | 169 | **379** |
| Classic Red Sauce Pasta | 189 | **419** |
| Creamy Alfredo Pasta | 209 | **459** |
| Cheesy Garlic Bread Toast | 129 | **289** |
| Classic French Fries [Small] | 59 | **129** ¹ |
| Classic French Fries [Large] | 99 | **219** |
| Spicy Peri Peri Fries [Small] | 79 | **179** ¹ |
| Spicy Peri Peri Fries [Large] | 129 | **299** |
| Garlic Butter / Sweet Corn | 25 | **59** |
| Cheese Dip / Peri Peri Dip | 29 | **69** |
| Extra Cheese | 39 | **89** |
| Extra Paneer | 59 | **139** |
| Midnight Pizza Box Combo | 179 | **399** ¹ |
| Fiesta Pizza Combo | 339 | **709** |

¹ **Proposed, not yet live on Zomato.** These three did not exist when the list
was first set: the fries were one SKU, and the Midnight combo was added later.
All three sit at 2.2×. Confirm before entering them.

### What the ladder does to a cart

Starting from one Herb Paneer at ₹459:

| Action | Cart | You keep extra |
|---|---:|---:|
| add a dip | ₹528 | +₹34 |
| add fries | ₹678 | +₹107 |
| add fries and a dip | ₹747 | +₹141 |
| switch to the Fiesta combo | ₹709 | +₹123 |

Combos beat their own parts by **9–13%**, so the upsell reads as a saving rather
than a spend. Add-ons sit at 13–30% of a pizza — small enough to say yes to
without thinking, which is exactly where cart growth comes from.

**The missing rung was a cheap side**, and it now exists: fries were split into
Small and Large in August, putting a **₹129** side on the platform under the
₹219 one. Low enough to be an impulse, high enough to clear the floor.

Whether it actually builds carts is unproven. The order history says discounts
do not lift basket size at all (1.24 items per order against 1.21) — see
`../../marketing/findings/2026-08-14-discount-behaviour.md`. A cheap rung is a
better bet than a discount for the same purpose, but treat it as a hypothesis
until post-relaunch orders can test it.

## Edge cases

1. **Never run a restaurant-funded discount at these prices.** It multiplies
   straight into the realisation: a flat 20% takes 68.1% down to 54.5%. Five of
   six discount constructs in the order history were already platform-funded (₹0
   to the kitchen) — keep it that way, and prefer capped offers ("20% off up to
   ₹100") over flat percentages, which have no ceiling.
2. **Advertising is the fastest way to lose the margin.** ₹500 a week over 8
   orders is ₹62 per order — worse than the commission on a ₹300 order. The
   statement shows ₹0 spent, which is the right number until volume justifies it.
3. **Swiggy parity is priced defensively.** Identical prices on both platforms
   means the worse platform sets the floor. Pull one Swiggy settlement and
   re-check; if its commission exceeds ~34%, the Swiggy list has to rise on its
   own or those items come off Swiggy.
4. **Packaging is charged at ₹10 and is commissionable** — it appears inside the
   order value the 27% is taken from, so it is not a clean pass-through.
5. **Rejection penalties scale with order value** (₹63, ₹45 and ₹132 on three
   orders). The most expensive order to reject is the biggest one, which is
   exactly the one most likely to arrive when the kitchen is busy.
6. **GST input credit changes the answer.** The ₹135.92 of GST on commission is
   recoverable if registered normally, and a dead cost under the composition
   scheme. Worth confirming, as it is roughly 5 points of realisation.
7. **The price gap is now a selling point.** ₹209 on the website against ₹359 on
   Zomato is the platform's cost, not greed — say so, and let the calculator make
   the direct channel the obvious choice.

## Correction to the dashboard

`revenue` counts what customers paid, not what reached the bank. ₹81,604 of
delivered Zomato revenue is about **₹55,600** at 68.1% realisation, or **₹48,500**
after typical rejection penalties. The dashboard should carry a payout figure
beside the revenue one; until it does, mentally multiply by two-thirds.
