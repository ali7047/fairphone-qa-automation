# Site observations

How the live shop behaves, and what that means for the tests. Seen with Chromium from the Netherlands.

## Language selection
- The EU shop picks its language from the visitor's **location**, not the browser language: from the Netherlands, `/` redirects to `/nl` whatever the browser is set to.
- Opening `/en/` (or `/nl/`) once switches the session: the server sets the cookie `frontend_lang` and later pages stay in that language. Setting the cookie by hand before the first visit does not work.
- The US shop is English only and needs no switch.
- **For tests:** the shared setup opens the language path once before each test (`--language`, default English).

## Cookie dialog
- Dialog "Cookies Please!" on the first visit, same on EU and US, with **Accept All**, **Decline Optional**, **Customize Settings**. It covers buttons such as **Add to cart** until it is answered.
- **For tests:** declined automatically by `CookieDialog` in `pages/base_page.py`.

## Header cart icon
- `<a href="/shop/cart">0</a>`: its only accessible name is the item count. Screen readers announce "0, link" with no word "cart" — an accessibility issue.
- **For tests:** found by its link target (`href` ends with `/shop/cart`), which also works for `/nl/shop/cart`.

## "Go to checkout" click intercepted
- A plain click on **Go to checkout** in the cart times out: the wrapper element around the button receives the click.
- **For tests:** to investigate in the checkout journey — the wrapper may be the intended target, or this is a keyboard/assistive-technology bug.

## EU home page layout
- The hero heading is covered by the hero buttons and the sticky header, so pointer actions on it fail. Not a bug; tests don't hover or click it.

## Console messages
- Home page: no errors. Messages come from third-party tools: experiments (Convert), analytics (Clarity, Google Tag Manager), consent (DataGrail), an accessibility widget (EqualWeb, warns about an iframe sandbox) and a chat widget.
- Odoo logs "Tour Manager is ready." (Odoo's own UI test framework is loaded).
- **For tests:** the detection job fails only on Fairphone's own errors; third-party messages are reported.

## Bot protection
- No blocking from a local machine. GitHub Actions runners (US data centres): to be seen in the first CI run.

## Possible content issues (recheck before citing)
- Dutch home page shows English text ("Introducing the Fairbuds 2…", "Read more" next to "Lees meer").
- Footer headings with odd capitals: "ProductEN", "FairphonE", "sCHRIJF ME IN".
- Configurator page title says "Configure your The Fairphone Gen. 6+" while configuring the Gen. 6.
