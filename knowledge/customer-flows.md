# Customer flows

The journeys the suite covers, step by step. Screen names are the visible English text. *Observed 2026-11-15* unless marked otherwise.

## 1. Home page and main navigation
1. Open `/` (English: no language prefix).
2. Cookie dialog "Cookies Please!" appears → "Decline Optional".
3. Header menu: **Shop**, **About**, **Fairphone Stories**, **Keep Club**, **Business**, **Support**; cart icon shows the item count ("0").
4. The Shop menu opens groups: **Smartphones**, **Audio**, **Accessories**, **Spare parts**.
5. Clicking **Smartphones** opens `/smartphones`.

## 2. Product page → variant → cart
1. Open `/the-fairphone-gen-6` (heading "The Fairphone (Gen. 6)").
2. Radio group **Model**: "The Fairphone (Gen. 6+)" €649 / "The Fairphone (Gen. 6)" €599 (checked).
3. Link **BUY NOW** → `/configure/the-fairphone-gen-6-1?model=the-fairphone-gen-6&operating-system=android`.
4. Configurator: radio group **Colour** — "Horizon Black" (default), "Forest Green", "Cloud White" (*no longer available*). Price shown: "€ 599".
5. Choosing "Forest Green" adds `&colour=forest-green-android-gen6` to the URL.
6. Button **Add to cart** → redirects to `/shop/cart`.

## 3. Cart
- Heading **Cart**, "Your order (1)".
- Line: "The Fairphone (Gen. 6)", "256GB 8GB RAM | Forest Green", "€ 599.00".
- Controls per line: **Remove one**, quantity field, **Add one**, **Remove from cart**.
- Summary: Subtotal "€ 599.00", Shipping "Not yet calculated", VAT "€ 103.96", Total "€ 599.00".
- Button **Go to checkout**. Field label "Use a gift card or promo code".
- Accepted payment logos: iDEAL, Visa, Mastercard, American Express, PayPal, Klarna, Apple Pay.
- *Assumption:* after **Remove from cart** on the last line, the cart shows an empty-state message and the cart icon returns to "0" (to verify).

## 4. Guest checkout up to the address step
1. From the cart, **Go to checkout**.
2. *Assumption:* Odoo shows a choice between signing in and continuing as a guest, then the address form (to verify).
3. **Stop at the address form.** Never type into it or submit it.
- *Observed 2026-11-15:* a plain click on **Go to checkout** was intercepted by the button's wrapper element. See [site-observations.md](site-observations.md).

## Other URLs seen
| Page | URL |
|---|---|
| Gen 6+ | `/the-fairphone-gen-6-plus` |
| Accessories | `/accessories` |
| Spare parts | `/spare-parts` |
| Gift card product | `/shop/gift-card-8` |
| Accessory example | `/shop/fairphone-6-protective-case-1892` |
| Return policy | `/legal/return-policy` |
