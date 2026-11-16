# Site observations

How the live shop behaves, and what that means for the tests. Seen with Chromium from the Netherlands.

## Language selection
- The EU shop picks its language from the visitor's **location**, not the browser language: from the Netherlands, `/` redirects to `/nl` whatever the browser is set to.
- Opening `/en/` (or `/nl/`) once switches the session: the server sets the cookie `frontend_lang` and later pages stay in that language. Setting the cookie by hand before the first visit does not work.
- The US shop is English only and needs no switch.
- **For tests:** the shared setup opens the language path once before each test (`--language`, default English).

## Pop-ups a test meets
| Pop-up | Where | Answer used by tests | Why |
|---|---|---|---|
| Cookie dialog "Cookies Please!" | First visit, EU and US | **Decline Optional** | Privacy-friendly; fewer third-party scripts |
| "Visiting from the Netherlands? … switch to the local site?" | US shop, visitor outside the US | **Stay on us.fairphone.com** | The test chose the US shop on purpose |
| "Choose your free … Protective Case" | Cart, right after adding a phone (EU and US) | **Continue without adding** | Keep the cart to what the test added |
| "Choose your free … Screen Protector" | Right after the case offer | **Continue without adding** | Same |
| "Accessories for …" with **Go to cart** / **Checkout** | Right after the screen-protector offer | **Go to cart** | Back to the cart without adding |

- The three cart offers are styled pop-ups (`div` with a backdrop), **not** real dialogs: no `role="dialog"`, no `aria-modal`. Screen readers don't announce them as dialogs — an accessibility issue.
- They cover the cart's quantity buttons until they are answered.
- **For tests:** `pages/popups.py` answers each one automatically whenever it shows up.

## Configurator
| | EU | US |
|---|---|---|
| Address | `/configure/the-fairphone-gen-6-1?model=…&operating-system=android` | `/configure/the-fairphone-gen-6?color=…` |
| Choices | **Model** (Gen. 6 / 6+) and **Colour** | **Color** (US spelling) and **Connectivity setup** |
| Add to cart | Enabled straight away | **Disabled** until a connectivity choice is made |
- The product page's buy link reads **BUY NOW** (EU, "KOOP NU" in Dutch) or **configure your phone** (US). Both link to `/configure/`.
- **Choosing a colour is not instant.** After a click, the page asks the server which product matches (`POST /configure/…/availability`) and only then switches the product it will add. Clicking **Add to cart** before that answer adds the **previous** colour. A fast automated click got Horizon Black instead of Forest Green 3 times out of 3; a person clicking 0.5–1.5 s later, even on a slow (400 ms) connection, got the right colour 3 times out of 3. Real customers are unlikely to hit this; a double-click or a very slow connection might.
- **For tests:** wait for the availability answer after choosing a colour, then add to cart.

## Cart
- Quantity buttons **Add one** / **Remove one** call `POST /shop/cart/update_json`. The answer holds the new numbers: `quantity`, `cart_quantity` (items in cart) and `amount` (cart total). Tests compare the screen with these numbers.
- **Remove from cart** asks for confirmation ("Are you sure you want to remove …?" → **cancel** / **remove product**).
- Empty cart: heading-like text **"Your cart is empty"**, a **Home page** link and category links. Header cart icon shows "0".
- EU: Subtotal, Shipping ("Not yet calculated"), VAT, Total. US: Subtotal, Shipping, **Estimated Sales Tax** ("Not yet calculated"), Total.

## Header cart icon
- `<a href="/shop/cart">0</a>`: its only accessible name is the item count. Screen readers announce "0, link" with no word "cart" — an accessibility issue.
- **For tests:** found by its link target (`href` ends with `/shop/cart`), which also works for `/nl/shop/cart`.

## "Go to checkout"
- A plain click on **Go to checkout** is intercepted while a cart offer is still open behind it; once the offers are answered it works. It opens a side panel **"How would you like to complete your order?"** with a **Checkout as guest** link (`/shop/checkout?express=1`) and a login form.
- **Checkout as guest** opens `/shop/address`: heading **Checkout**, section **Address** with First name, Last name, e-mail address, Phone number, Street address, Postal code, City, and a **NEXT STEP** button.
- **For tests:** stop on this page. Never type into it or press NEXT STEP.

## Console messages
- Home page: no errors. Messages come from third-party tools: experiments (Convert), analytics (Clarity, Google Tag Manager, Exponea), consent (DataGrail), an accessibility widget (EqualWeb) and a chat widget.
- Address page: **11 × 404 for country flag images** (`/base/static/img/country_flags/bq.png`, `re.png`, `gp.png` …), requested under `/de/`, `/fr/` and `/nl/` paths while the page is English. Fairphone's own files, so a real (minor) defect.
- US product page: 404 for a navigation thumbnail (`/shop/category/web/image/…fairbuds-2-navigation-thumbnail…`).
- **For tests:** the detection job fails only on Fairphone's own errors; third-party messages are reported.

## EU home page layout
- The hero heading is covered by the hero buttons and the sticky header, so pointer actions on it fail. Not a bug; tests don't hover or click it.

## Bot protection
- No blocking from a local machine. GitHub Actions runners (US data centres): to be seen in the first CI run.

## Possible content issues (recheck before citing)
- Dutch home page shows English text ("Introducing the Fairbuds 2…", "Read more" next to "Lees meer").
- Footer headings with odd capitals: "ProductEN", "FairphonE", "sCHRIJF ME IN".
- Configurator page title says "Configure your The Fairphone Gen. 6+" while configuring the Gen. 6 (also in Dutch).
- Dutch product page heading "De Fairphone (Gen 6)" (no dot) while the menu says "De Fairphone (Gen. 6)".
