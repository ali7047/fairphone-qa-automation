# fairphone-qa-automation

End-to-end tests and a weekly site-health check for the Fairphone webshop ([www.fairphone.com](https://www.fairphone.com)),
built with Playwright for Python and pytest and run in GitHub Actions. For the shop's developers and QA: it runs the critical
customer journeys on every pull request and shows what broke, with screenshots and traces.

Reports: [ali7047.github.io/fairphone-qa-automation](https://ali7047.github.io/fairphone-qa-automation/) ·
Example runs: [Smoke #5](https://github.com/ali7047/fairphone-qa-automation/actions/runs/44047248782) ·
[Detection #1](https://github.com/ali7047/fairphone-qa-automation/actions/runs/44052095967)

## Prerequisites

* Python 3.11 or higher (uv installs it if missing)
* [uv](https://docs.astral.sh/uv/) for dependencies
* Node.js and Java 17, only to open the Allure report locally

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ali7047/fairphone-qa-automation.git
   ```
2. Go to the project directory:
   ```bash
   cd fairphone-qa-automation
   ```
3. Install the dependencies and the test browser:
   ```bash
   uv sync
   uv run python -m playwright install chromium
   ```

## Usage

```bash
uv run python -m pytest tests/unit                         # helpers and rules, no browser (~1 s)
uv run python -m pytest -m smoke                           # 4 customer journeys on the live EU shop
uv run python -m pytest -m smoke --language nl --headed    # in Dutch, with the browser visible
uv run python -m pytest -m smoke --base-url https://<acceptance-url>   # same suite on acceptance
uv run python -m pytest -m detection -n 2                  # site health of this week's 30 pages
uv run python -m pytest -m known_issue                     # checks that fail until a known shop gap is fixed
npx allure-commandline@2 serve allure-results              # open the report
```

A failed test leaves its screenshot, video and Playwright trace in `test-results/` and in the Allure report.

## What is tested

| Suite | What it checks | When |
|---|---|---|
| **Smoke** (the gate) | 1. Home page and Shop menu · 2. Phone + colour → cart at the configurator price · 3. Quantity +1 (screen and server answer agree), then remove → empty cart · 4. Guest checkout up to the address form, nothing submitted | Every pull request, by hand |
| **Known issues** | "37" as street + house number is accepted without a warning. Fails until fixed; never turns the run red | With smoke |
| **Detection** | Up to 30 sitemap pages (robots.txt respected, new sample each week); records HTTP answers ≥ 400 and JavaScript errors | Mondays 06:00 UTC, by hand |

**Detection fails** only for what Fairphone must act on: a broken page, a crash in its own scripts, a missing own script or style,
a 5xx from its server. Third-party errors, missing images and console messages are **reported only**: red must mean "act now".

**Next check to add: price consistency.** Compare each product page's price with the price the cart returns. Content editors change
pages live, outside any release; a stale price misleads customers and is a legal risk that no deploy pipeline catches.
After that: content completeness (price, VAT note and delivery info present; page really in its language).

## Workflows

`smoke.yml` (every pull request) and `detection.yml` (weekly): lint and unit tests run in parallel; browser tests start only when
both pass; an Allure report is published to GitHub Pages and linked on the report job's box and on the pull request.
Both have a **Run workflow** button with options (shop, language, address, browser / pages). Smoke takes ~3 min, detection ~5 min.

## Decisions

* **Selectors**: role + visible name → label → stable attribute; never styling classes or XPath. Visible texts per language live in `config/languages.py`.
* **No fixed sleeps**: Playwright waits by itself and `expect()` retries. One exception: detection waits 3 s after load to catch late third-party errors.
* **Cookie banner** and **"Visiting from …?" prompt**: answered by locator handlers whenever they appear, with the privacy-friendly option.
* **Flaky tests**: 1 retry in CI, still visible in the report; repeat offenders go to quarantine with a ticket, outside the gate.
* **Live-shop etiquette**: nothing is ever submitted; at most 2 workers; detection weekly only; bot protection is reported, never bypassed.
* **Structure**: page objects in `pages/`, test data in `test_data/`, shared setup in `tests/conftest.py`.

More: [knowledge/decisions.md](knowledge/decisions.md) · live-shop findings: [knowledge/site-observations.md](knowledge/site-observations.md)

## Limitations and next steps

* **Bot protection**: no block, locally or from GitHub's US runners. Those runners do get a US cookie dialog and a "Visiting from the US?"
  prompt that a run from the Netherlands never sees. In Fairphone's setup: allowlist the test runners and run EU checks from an EU region.
* **Not tested**: anything after the address step (payment, iDEAL, emails), which needs acceptance with payment in test mode.
  The US journeys are not stable yet; German and French texts are not added.
* **Left out on purpose**: visual comparison (content changes weekly), performance tests (need a target, never on live), more journeys (four solid ones first).
* **With another day**: checkout and order emails on acceptance; the price-consistency check; WebKit and mobile nightly; quarantine wired into CI.

## AI assistance

Claude Code (an AI coding assistant) was used to explore the site, write and refactor code and tests, and draft documents;
every change was reviewed.

## Contributing

Open a pull request; lint, unit tests and smoke must pass. How to add a test: [knowledge/automation-standards.md](knowledge/automation-standards.md).
Commit messages start with `NEW:`, `UPD:` or `FIX:`.
