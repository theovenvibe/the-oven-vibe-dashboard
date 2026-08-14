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

## The price list

Set from the penalty-inclusive rate (1.68×), which leaves headroom rather than
pricing at the exact floor. **The same prices go on Swiggy**, whose rate is not
yet known — this buffer absorbs a commission up to about 34% before the floor is
breached, so parity is safe until a Swiggy statement says otherwise.

| Item | Local | Now | **Set to** | Then pays |
|---|---:|---:|---:|---:|
| Zesty Onion Feast Pizza | 129 | 189 | **219** | 149 |
| Ultimate Cheese Delight Pizza | 159 | 209 | **269** | 183 |
| Golden Corn Classic Pizza | 169 | 229 | **289** | 197 |
| Crunchy Capsicum Pizza | 189 | 249 | **319** | 217 |
| Herb Paneer Delight Pizza | 209 | 289 | **359** | 244 |
| Paneer Makhni Royale Pizza | 229 | 309 | **389** | 265 |
| Mushroom Supreme Pizza | 229 | 299 | **389** | 265 |
| Vegie Onion Capsicum Pizza | 219 | 289 | **369** | 251 |
| Creamy Alfredo Pasta | 209 | 219 | **359** | 244 |
| Classic Red Sauce Pasta | 189 | 199 | **319** | 217 |
| Street Style Korean Maggi | 159 | 199 | **269** | 183 |
| Tangy Green Chutney Sandwich | 89 | 119 | **159** | 108 |
| Fiery Cheese Chilli Sandwich | 129 | 169 | **219** | 149 |
| Paneer Tikka Sandwich | 169 | 229 | **289** | 197 |
| Classic French Fries | 99 | 99 | **169** | 115 |
| Spicy Peri Peri Fries | 129 | 119 | **219** | 149 |
| Cheesy Garlic Bread Toast | 129 | 129 | **219** | 149 |
| Crunchy Peri Makhana | 129 | 149 | **219** | 149 |
| Fiesta Pizza Combo | 319 | 499 | **539** | 367 |
| Pasta Treat Combo | 299 | 339 | **509** | 347 |
| Sandwich Meal Box Combo | 269 | 389 | **459** | 313 |
| Cheese Dip / Peri Peri Dip | 29 | 29 | **49** | 33 |
| Garlic Butter / Sweet Corn | 25 | 29 | **49** | 33 |
| Extra Cheese | 39 | 39 | **69** | 47 |
| Extra Paneer | 59 | 49 | **109** | 74 |

**26 of 27 items currently pay less than the local kitchen price.** Only the
Fiesta Combo clears it. The sides and add-ons are worst: they were listed at
local prices, so a ₹99 portion of fries returns ₹67, and extra paneer at ₹49
returns ₹33 against a ₹59 local price.

Average change is about **+₹78** per item. The same week at these prices would
have paid roughly **₹2,034 instead of ₹1,664** — and that is before fixing a
single rejection.

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
