# Customer flows

The journeys the suite covers, step by step, with the names a customer sees. Names in other languages: `config/languages.py`.

## 1. Home page and main navigation
1. Open the home page (EU shop: after switching language, see [site-observations.md](site-observations.md)).
2. Cookie dialog appears and is declined.
3. Header menu: **Shop**, **About**, **Fairphone Stories**, **Keep Club**, **Business**, **Support**; cart icon shows the item count ("0").
4. **Shop** opens the groups **Smartphones**, **Audio**, **Accessories**, **Spare parts**.
5. **Smartphones** opens `/smartphones`.

## 2. Product page → variant → cart
1. Open `/the-fairphone-gen-6` (heading "The Fairphone (Gen. 6)").
2. Radio group **Model**: Gen. 6+ (€649) or Gen. 6 (€599, selected).
3. **BUY NOW** → `/configure/the-fairphone-gen-6-1?model=the-fairphone-gen-6&operating-system=android`.
4. Radio group **Colour**: Horizon Black (selected), Forest Green, Cloud White (no longer available). Price "€ 599".
5. Choosing Forest Green adds `&colour=forest-green-android-gen6` to the address.
6. **Add to cart** → `/shop/cart`.

## 3. Cart
- Heading **Cart**, "Your order (1)".
- Line: "The Fairphone (Gen. 6)", "256GB 8GB RAM | Forest Green", "€ 599.00".
- Per line: **Remove one**, quantity field, **Add one**, **Remove from cart**.
- Summary: Subtotal, Shipping ("Not yet calculated"), VAT, Total. Button **Go to checkout**.
- *Assumption:* after removing the last line the cart shows an empty-state message and the cart icon shows "0".

## 4. Guest checkout up to the address step
1. From the cart, **Go to checkout** (a plain click is intercepted; see [site-observations.md](site-observations.md)).
2. *Assumption:* Odoo offers "sign in" or "continue as guest", then the address form.
3. **Stop at the address form.** Never type into it or submit it.

## Other pages
| Page | Path |
|---|---|
| Gen. 6+ | `/the-fairphone-gen-6-plus` |
| Accessories | `/accessories` |
| Spare parts | `/spare-parts` |
| Gift card | `/shop/gift-card-8` |
| Accessory example | `/shop/fairphone-6-protective-case-1892` |
| Return policy | `/legal/return-policy` |
