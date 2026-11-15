# Site observations

Things seen on the live site that affect testing. Newest first. Each entry: date, what, impact on tests.

## 2026-11-15 — second check: language pinning and the US shop (Chromium, headless)

**Language is chosen by location, not by browser language**
- With browser languages en-US, en-GB and nl-NL alike, `/` redirected to `/nl` (Dutch) from a Dutch IP. So the browser `locale` setting alone does not give English pages.
- Opening `/en/` once redirects to `/` in English and sets the cookie `frontend_lang=en_US`; after that, `/` stays English for the session.
- Setting the `frontend_lang` cookie by hand before the first visit did **not** work (the site replaced it with `nl_NL`).
- Impact: the shared test setup opens `/en/` first on the EU shop. Every test then runs in English, whatever the runner's location.

**US shop**
- Address: `https://us.fairphone.com` (listed in the EU pages as `hreflang="en-us"`). Separate host, same Odoo look.
- English only (`lang="en-US"`), prices in dollars: "$649.99", "$27.99". Home heading: "Switch to fair. Switch to better."
- Same cookie dialog as the EU shop ("Cookies Please!", same three buttons).

**Home page layout on the EU shop**
- The hero heading is covered by other elements (hero buttons, sticky header), so a pointer action on it times out. Not a bug; tests must not hover or click the heading.

## 2026-11-15 — first read-only walkthrough (Chromium, Windows, Dutch location)

**Language redirect**
- `/` redirected to `/nl`. Requesting `/en/shop` redirected to `/`; `/en/the-fairphone-gen-6` redirected to `/the-fairphone-gen-6`.
- Impact: see the language pinning entry above.

**Cookie dialog**
- Dialog titled "Cookies Please!" (DataGrail) with buttons "Accept All", "Decline Optional", "Customize Settings" and a language selector.
- Impact: one handler clicks "Decline Optional" whenever the dialog appears.

**"Go to checkout" click intercepted**
- A plain click on the button "Go to checkout" in the cart timed out: the wrapper `div.f_button_wrapper` received the click instead of the button.
- Impact: to investigate before writing the checkout journey — the wrapper may be the real click target (a design choice), or this may be a bug for keyboard and assistive-technology users.

**Console**
- Home page: no errors. Messages come from third-party tools: Convert (experiments), Microsoft Clarity, Google Tag Manager, DataGrail, EqualWeb (accessibility widget: "iframe … can escape its sandboxing" warning), a chat widget iframe.
- Odoo logs "Tour Manager is ready." (Odoo's built-in UI test framework is loaded).
- Impact: the detection job separates first-party errors (fail) from third-party noise (report only).

**Bot protection**
- Not blocked from a local machine. Behaviour from GitHub Actions runners (US data centres) still unknown.

**Possible content issues (to recheck before citing)**
- Dutch home page shows English text: hero "Introducing the Fairbuds 2. Your sound. Made better." and "Read more" next to "Lees meer".
- Footer headings with odd capitalisation: "ProductEN", "FairphonE", "sCHRIJF ME IN".
- Configurator page title says "Configure your The Fairphone Gen. 6+" while configuring the Gen. 6.
