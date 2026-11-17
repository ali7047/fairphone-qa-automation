# fairphone-qa-automation

End-to-end and monitoring checks for the Fairphone webshop — [www.fairphone.com](https://www.fairphone.com) (EU) and
[us.fairphone.com](https://us.fairphone.com) — in Python with Playwright and pytest, run in GitHub Actions.

| | |
|---|---|
| **Smoke suite** (pre-deploy gate candidate) | 4 customer journeys on the live shop, on every pull request and by hand |
| **Detection job** | weekly site-health check of 30 sampled pages, on Mondays and by hand |
| **Reports** | one Allure report per run, published at [ali7047.github.io/fairphone-qa-automation](https://ali7047.github.io/fairphone-qa-automation/) |
| **Example runs** | Smoke [#5 ✅](https://github.com/ali7047/fairphone-qa-automation/actions/runs/44047248782) · [#4 ❌ (flaky click, explained below)](https://github.com/ali7047/fairphone-qa-automation/actions/runs/44044990875) · Detection [#1 ✅](https://github.com/ali7047/fairphone-qa-automation/actions/runs/44052095967) |

Contents: [Run locally](#run-locally) · [Workflows](#workflows) · [What is tested](#what-is-tested) · [Decisions](#decisions-and-why) ·
[Findings on the live shop](#findings-on-the-live-shop) · [Limitations](#known-limitations) · [Another day](#with-another-day) ·
[What I left out](#what-i-left-out-and-why) · [AI assistance](#ai-assistance) · [Layout](#project-layout)

The **90-day QA strategy (Part 1)** is delivered as a separate document with the submission email.
Parts 2 and 4 are in [docs/](docs/).

---

## Run locally

Needs [uv](https://docs.astral.sh/uv/) — it installs the right Python by itself.

```bash
uv sync                                          # install exact versions from uv.lock
uv run python -m playwright install chromium     # download the test browser (once)

uv run python -m pytest tests/unit               # config, rules and helpers: no browser, about a second
uv run python -m pytest -m smoke                 # the 4 journeys on the live EU shop, in English
uv run python -m pytest -m smoke --language nl   # same journeys in Dutch
uv run python -m pytest -m smoke --headed        # watch the browser
uv run python -m pytest -m known_issue           # checks that fail until a known shop gap is fixed
uv run python -m pytest -m detection -n 2        # site health: this week's 30 pages
uv run python -m pytest -m detection --pages /stories,/nl/returns   # site health of chosen pages

npx allure-commandline@2 serve allure-results    # open the report (needs Node.js and Java)
```

| Option | Environment variable | Default | Use |
|---|---|---|---|
| `--base-url` | `BASE_URL` | the region's live shop | **point the same suite at acceptance** |
| `--region` | `REGION` | `eu` | `eu` or `us` |
| `--language` | `SHOP_LANGUAGE` | `en` | `en`, `nl` (EU) |
| `--max-pages` | `MAX_PAGES` | `30` | detection, capped at 30 |
| `--pages` | `PAGES` | a sample of the sitemap | detection: check given pages |
| `--sample-seed` | `SAMPLE_SEED` | this ISO week | detection: which sample |

Before pushing: `uv run python -m ruff check . && uv run python -m ruff format --check . && uv run python -m pytest tests/unit`

---

## Workflows

Both have a **Run workflow** button (Actions → workflow → Run workflow).

### Smoke tests — every pull request, and by hand

```
Lint ─────┐
          ├──> Smoke journeys (gate) ──┐
Unit ─────┘                            ├──> Allure report (link on its box)
          └──> Known issues ───────────┘
```

| Job | What it does | Can turn the run red? |
|---|---|---|
| Lint | `ruff check` (likely bugs, unused code, import order) + `ruff format --check` | Yes |
| Unit tests | 69 tests of config, test data, detection rules and helpers; no browser | Yes |
| Smoke journeys | the 4 journeys, 2 workers, 1 retry; starts only after Lint **and** Unit pass | Yes — **the gate** |
| Known issues | checks for known shop gaps; they fail on purpose, the job stays green with a warning | No |
| Allure report | builds and publishes the report | No |

Manual options: shop, language, address (e.g. acceptance), browser, known issues on/off. Typical run: about 3 minutes.

### Detection (weekly) — Mondays 06:00 UTC, and by hand

```
Lint ─────┐
          ├──> Detection (≤30 pages) ──> Allure report (link on its box)
Unit ─────┘
```

Manual options: shop, number of pages, **specific pages** (e.g. a page a content editor just published), sample seed. Typical run: about 5 minutes.

### Reports and evidence

One click from: the **link on the Allure report box** in the run graph, **View deployment** on the pull request, or
**📊 Open the Allure report** at the top of the run summary (followed by a results table).
Each run keeps its own address (`/smoke/<run>/`, `/detection/<run>/`); `/smoke/latest/` and `/detection/latest/` open the newest;
the [index page](https://ali7047.github.io/fairphone-qa-automation/) lists all runs; the last 20 per workflow are kept.

Each test in the report shows its **Data / Steps / Expected** description, every step with a screenshot, the test data,
the shop's server answers, and **expected vs actual** for each check. A failed test also gets its **screenshot, video and
Playwright trace** (open at [trace.playwright.dev](https://trace.playwright.dev)). The same files are attached to the run as artifacts.

---

## What is tested

### Smoke suite (`tests/smoke/`)

| # | Journey | Checks |
|---|---|---|
| 1 | Home page and Shop menu | status < 400, page in the chosen language, cookie dialog gone, menu text in that language, empty cart, prices in the shop's currency; Shop menu → Smartphones opens with its heading |
| 2 | Phone → colour → cart | configurator price = cart line price = cart total; the chosen colour is on the line; quantity 1; header count 1 |
| 3 | Quantity, then remove | after **Add one**: quantity 2 and total = 2 × unit price, **both on screen (GUI) and in the shop's server answer (API)**; after **Remove**: server says 0 items, "Your cart is empty", header 0 |
| 4 | Guest checkout | **Go to checkout → Checkout as guest** reaches `/shop/address` with empty fields; **stops there** |

Prices are read from the page while the test runs (never typed into a test) and compared as numbers (`utils/money.py`).
The same journeys run in English and Dutch (`--language nl`); visible texts per language live in `config/languages.py`.

### Known issue (`tests/known_issues/`)

Typing **"37"** as *Street address + house number* (a house number without a street) and leaving the field shows **no warning**.
The test expects a warning, so it fails until the shop adds one. Every form post is blocked in the browser before typing,
and the report proves nothing was sent. It also checks iDEAL is offered as a payment method; choosing iDEAL is only possible
after submitting the address, so that belongs on acceptance.

### Detection job (`tests/detection/`)

| Step | How |
|---|---|
| Which pages | up to **30** from `sitemap.xml` (1,672 addresses), spread over sections (shop, stories, legal, …), always the home page; skips what **robots.txt** disallows and action addresses (login, "add …") |
| Which week | the ISO week seeds the sample: a re-run checks the same pages, next week others |
| What is recorded | every answer **≥ 400** (the page and everything it loads) and every **JavaScript error** (uncaught crashes and `console.error`) |

**Fails the job** — Fairphone must act: a broken page (≥ 400 or no answer); a crash in **Fairphone's own** script (owner read
from the error's stack trace); a missing Fairphone script or stylesheet; a Fairphone server error (5xx); bot protection answering instead of the shop.

**Report only** — shown, never red: third-party errors (analytics, chat, consent, reCAPTCHA, reviews), missing images, console messages.

**Why:** red must mean "act now". The first runs had about 60–90 messages per run, none of them something Fairphone could
or needed to fix that day; failing on them would teach everyone to ignore red. Rules: `utils/site_health.py`, unit-tested in `tests/unit/test_site_health_rules.py`.

### Next webshop-specific checks for the detection job

1. **Price consistency (first).** For each sampled product page, compare the price shown on the page with the price the cart
   returns for that product. *Why this one:* content editors change product pages directly on the live site, outside any release;
   a page that still shows an old or campaign price misleads customers. That is a money and legal risk (EU price-indication rules),
   and nothing in a deploy pipeline would catch it. The cart's server answer already gives the real price (journey 3 uses it).
2. **Content completeness.** Every product page shows a price, a VAT note and delivery info, and NL/DE/FR pages are really in their
   language. *Why:* the Dutch home page already shows English text ("Read more" next to "Lees meer"); with editors publishing
   live, a half-translated or incomplete page is the most likely kind of change to slip through.

---

## Decisions and why

Full list: [knowledge/decisions.md](knowledge/decisions.md). The main ones:

| Decision | Why |
|---|---|
| **Python + uv** | required stack; Odoo is Python, so the shop's developers can read and extend the tests; `uv.lock` gives the same versions everywhere |
| **Tests in their own repository** | they test the running shop from outside, any environment by address, including changes that never go through code (live content edits). Unit and integration tests belong in the shop's own repository |
| **Selectors**: role + visible name → label → stable attribute (`href`, `aria-label`); never styling classes, XPath or position | survive redesigns; read like what a customer sees. Visible names per language in `config/languages.py`. Example: the cart icon's only name is its count, so it is found by its link target (`a[href$="/shop/cart"]`) |
| **No fixed sleeps** | Playwright waits for elements; checks use `expect()`, which retries. One deliberate exception: the detection job waits 3 s after a page loads, because there is no event for "third-party scripts have finished" and it only observes |
| **Cookie dialog** | a locator handler declines it whenever it appears ("Decline Optional" in the EU, "Accept Essentials Only" from the US); the same for the "Visiting from …?" prompt. Declining loads fewer third-party scripts |
| **Flaky tests**: 1 retry in CI; a pass on retry is still visible in the report; repeat offenders get `@pytest.mark.quarantine` with a ticket and run outside the gate | a gate that tolerates failures can't separate bugs from noise; a retry hides nothing because it is reported |
| **Known gaps**: a test that fails until fixed, in a job that stays green with a warning | the gap stays visible in every report; the run's colour only shows new problems |
| **Lint and unit tests first**, browser jobs only after both pass | cheap checks fail in a minute; no browser traffic on the live shop when the code is broken |
| **Structure**: page objects in `pages/` (locators + actions), test data in `test_data/`, expectations in tests, shared setup in `tests/conftest.py` | a developer adds a journey by following [knowledge/automation-standards.md](knowledge/automation-standards.md) |
| **Unit tests for the helpers** (price reader, sample picker, detection rules) | browser tests rely on them; a wrong helper would report shop bugs that don't exist or hide real ones; 69 tests in about a second |

### Production etiquette

Never submits an order, payment, account, newsletter, contact form or review. Journey 4 stops at the address form; the one test
that types into it blocks every form post first. At most **2 parallel workers**; detection runs **weekly** only; robots.txt respected.
If bot protection blocks a run, the job reports it as a finding and does not try to get around it. Full rules: [knowledge/production-rules.md](knowledge/production-rules.md).

---

## Findings on the live shop

Details: [knowledge/site-observations.md](knowledge/site-observations.md).

| Finding | Where | Suggested severity |
|---|---|---|
| Address step accepts **"37"** as street + house number without a warning | checkout, EU | Medium — undeliverable address, manual fix by customer service |
| A fast **Add to cart** right after choosing a colour adds the **previous** colour (the page switches product only after a server answer) | configurator | Medium — rare for people (double-click, slow connection), wrong product shipped |
| Live Keep Club page loads a script from **`sandbox-franz.fairphone.com/…/branch/release-test/…`** | `/fr/keep-club-fairphone` | High risk to raise — a test build serving customers can change without a release |
| 11 country-flag images answer **404** on the address page (requested under `/de/`, `/fr/`, `/nl/` while the page is English) | checkout | Minor |
| Cart offers (free case, screen protector, accessories) are **not real dialogs** to screen readers; the cart icon's only name is its count ("0, link") | cart, header | Minor — accessibility |
| Dutch home page shows English text; footer headings "ProductEN", "FairphonE"; configurator title says "Gen. 6+" on the Gen. 6 | content | Minor |

**Bot protection:** not blocked, locally or from GitHub's US runners. What CI did reveal is **location**: GitHub's runners get a US
cookie dialog and a "Visiting from the US?" prompt that a local run in the Netherlands never sees, and faking a US location locally
does not bring them up (the shop decides from the IP address). In Fairphone's real setup I would ask for the test runners to be
allowlisted (a known IP range or a signed header) so bot protection never blocks the gate, and run CI from an EU region for the EU shop.

---

## Known limitations

- **US shop**: the suite supports `--region us`, but the US journeys are not stable yet (slow page loads from the Netherlands, a different
  configurator with a carrier choice). The pipelines run the EU shop.
- **German and French** texts are not in `config/languages.py` yet; only English and Dutch are checked.
- **Retries**: one flaky case was seen in CI (a pop-up appearing at the moment of a click, run #4) and fixed; one retry is still allowed.
- **Detection** waits a fixed 3 s after load to catch late third-party errors; slower scripts can be missed.
- **Nothing after the address step** is tested (shipping, payment, iDEAL, confirmation emails): that needs acceptance with the payment provider in test mode.
- **Reports** are public (GitHub Pages of a public repository). They contain no personal data, but a company setup would keep them private.
- **Git history on `main`**: pull requests #2 and #3 were squash-merged, so `main` shows one commit per pull request; each of those
  commits lists its step-by-step commits in its message, and the closed pull requests
  ([#1](https://github.com/ali7047/fairphone-qa-automation/pull/1), [#2](https://github.com/ali7047/fairphone-qa-automation/pull/2), [#3](https://github.com/ali7047/fairphone-qa-automation/pull/3))
  keep the individual commits (22 in total).

## With another day

1. Run the suite against **acceptance**: guest checkout through payment in test mode (iDEAL), and the **order confirmation email**
   per country (VAT shown) with a test mailbox — the kind of bug that only shows after the address step.
2. Add the **price-consistency** check to detection (above).
3. Make the **US** journeys stable and add German and French texts.
4. **Cross-browser** run on WebKit (Safari) and a mobile viewport, nightly rather than in the PR gate.
5. Quarantine marker wired into the pipeline (separate non-blocking job, ticket id required), and a **flaky-rate** figure in the summary.
6. Send the weekly detection summary to the team channel.

## What I left out, and why

- **Visual comparison of pages**: content editors change pages every week; screenshot diffs would mostly report intended changes.
- **Performance and load tests**: they need an agreed target and must never run against the live shop; they belong before a big launch, on acceptance.
- **A test management tool**: tests, reports and decisions live in the repository and the Allure report for now.
- **More journeys**: four solid, explained journeys in two languages are worth more than many shallow ones.

---

## AI assistance

The strategy, decisions, severity rules and go/no-go approach are mine. I used **Claude Code** (an AI coding assistant) to explore
the live site, write and refactor code and tests, and draft documents from my points. I reviewed every change and can explain each line.

| AI did | I did |
|---|---|
| Explored the site (pages, pop-ups, element names, the cart's server answers) | Decided what to test, the order of work and what to leave out |
| Wrote the first version of code, tests and workflows | Reviewed every change; asked for rewrites (plain language, no repetition, data/steps/expected in every test, API vs GUI) |
| Investigated failures (traces, CI reports) and proposed fixes | Chose the rules: 100% blocking pass rate, quarantine, what fails detection, known issues green, NEW/UPD/FIX commits |
| Drafted documents from my notes | Wrote the strategy, severity rules and the go/no-go approach; edited the drafts |

**What was new to me:** I work with Python and pytest; **Playwright for Python** was the new part — its locators and auto-waiting,
locator handlers for pop-ups, tracing, and reading the browser's network traffic for the API checks. Also new: Allure reports
published to GitHub Pages, uv, and ruff.

**Time:** about 8 hours.

---

## Project layout

```
config/               which shop, language and address; visible texts per language
pages/                page objects: where to click (locators + actions), pop-up handling
test_data/            what the journeys buy and where they go, per shop and language
utils/                price reading, sitemap sampling, site-health rules, report evidence
tests/unit/           tests for config, test data, rules and helpers (no browser)
tests/smoke/          the 4 customer journeys
tests/known_issues/   checks that fail until a known shop gap is fixed
tests/detection/      the weekly site-health check
.github/workflows/    smoke.yml, detection.yml, allure-report.yml (shared report job)
.github/scripts/      report publishing (GitHub Pages) and the run summary
knowledge/            how the shop works, rules, standards and decisions
docs/                 Part 2 (refinement) and Part 4 (go/no-go)
```
