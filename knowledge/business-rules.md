# Business rules

Rules that tests must respect. *Observed <date>* = seen on the live site. *Assumption:* = still to confirm with the business.

## Prices and VAT
- **EU prices include VAT.** *Observed 2026-11-15 (NL cart):* Subtotal €599.00, VAT €103.96, Total €599.00. 599.00 / 1.21 × 0.21 = 103.96 → 21% Dutch VAT included.
- The price on the product page, in the configurator, in the cart line and in the cart total must be the same number ("one price, many places").
- *Assumption:* VAT depends on the delivery country (e.g. NL 21%, DE 19%). The cart shows the VAT for the current country.
- *Assumption:* US prices are shown without tax; sales tax is added at checkout based on the state.

## Currencies and number formats
| Region | Currency | Format seen or expected |
|---|---|---|
| EU (euro countries) | EUR | "€599", "€ 599.00", "€27.95" (*Observed 2026-11-15*) |
| UK | GBP | *Assumption:* "£…" |
| Switzerland | CHF | *Assumption:* "CHF …" |
| US | USD | "$649.99", "$27.99" (*Observed 2026-11-15*) |

Tests compare prices as numbers (`Decimal`), never as text, so "€599" and "€ 599.00" count as equal.

## Shipping and returns
- *Observed 2026-11-15:* "Delivery: 2-5 days (from €3.95)". Cart shows shipping as "Not yet calculated" before an address is known.
- *Observed 2026-11-15:* "14 day easy returns" / "Enjoy a 14-day right of withdrawal with free return shipping."

## Warranty
- *Observed 2026-11-15:* "Industry-leading five-year warranty*", "Software support till 2033" (Gen. 6).

## Gift cards and promo codes
- *Observed 2026-11-15:* gift cards are sold as a product (`/shop/gift-card-8`). The cart has **one shared field**, "Use a gift card or promo code".
- *Assumption:* fixed values €25 / €50 / €100, sent by email with a code, valid one year; remaining balance stays on the card.

## Product availability
- *Observed 2026-11-15:* a variant can be marked "No longer available" (Cloud White). Tests must choose a variant that is in stock.
