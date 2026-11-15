# Business rules

Rules the tests check or must respect. Everything here was seen on the live shop, except lines marked *Assumption:*.

## Prices and VAT
- **EU prices include VAT.** Dutch cart: Subtotal €599.00, VAT €103.96, Total €599.00 (599.00 / 1.21 × 0.21 = 103.96, so 21% VAT is inside the price).
- **One price, many places:** the price on the product page, in the configurator, on the cart line and as cart total must be the same amount.
- *Assumption:* VAT follows the delivery country (e.g. NL 21%, DE 19%).
- *Assumption:* US prices exclude tax; sales tax is added at checkout per state.

## Currencies and formats
| Shop | Currency | Formats |
|---|---|---|
| EU | EUR | "€599", "€ 599", "€ 599.00", "€27.95" |
| US | USD | "$649.99", "$27.99" |
| *Assumption:* UK / CH | GBP / CHF | "£…", "CHF …" |

Tests compare prices as numbers, never as text (`utils/money.py`).

## Shipping and returns
- "Delivery: 2-5 days (from €3.95)". The cart shows shipping as "Not yet calculated" until an address is known.
- "14 day easy returns": 14-day right of withdrawal with free return shipping.

## Warranty
- Gen. 6: "five-year warranty", software support until 2033.

## Gift cards and promo codes
- Gift cards are sold as a product (`/shop/gift-card-8`). The cart has **one shared field**, "Use a gift card or promo code".
- *Assumption:* fixed values €25 / €50 / €100, sent by email with a code, valid one year; the remaining balance stays on the card.

## Availability
- A variant can be "No longer available" (Cloud White Gen. 6). Tests choose a variant that is in stock.
