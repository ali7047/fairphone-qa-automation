# fairphone-qa-automation

End-to-end and monitoring checks for the Fairphone webshop ([www.fairphone.com](https://www.fairphone.com) and [us.fairphone.com](https://us.fairphone.com)), in Python with Playwright and pytest, run in GitHub Actions.

> Work in progress. The US shop journeys are not stable yet; the pipelines run the EU shop.

## Run locally

Needs [uv](https://docs.astral.sh/uv/); it installs the right Python by itself.

```bash
uv sync                                          # install exact versions from uv.lock
uv run python -m playwright install chromium     # download the test browser (once)

uv run python -m pytest tests/unit               # config, rules and helpers: no browser, about a second
uv run python -m pytest -m smoke                 # the 4 journeys on the live EU shop, in English
uv run python -m pytest -m smoke --language nl   # same journeys in Dutch
uv run python -m pytest -m smoke --headed        # watch the browser
uv run python -m pytest -m known_issue           # checks that fail today because of a known shop gap
uv run python -m pytest -m detection -n 2        # site health: this week's 30 pages
uv run python -m pytest -m detection --pages /stories,/nl/returns   # site health of chosen pages
```

### Choosing what to test

| Option | Environment variable | Default | Values |
|---|---|---|---|
| `--region` | `REGION` | `eu` | `eu`, `us` |
| `--language` | `SHOP_LANGUAGE` | `en` | `en`, `nl` on `eu`; `en` on `us` |
| `--base-url` | `BASE_URL` | the region's live shop | any address, e.g. an acceptance copy |
| `--max-pages` | `MAX_PAGES` | `30` | detection: at most 30 |
| `--pages` | `PAGES` | a sample of the sitemap | detection: comma-separated pages |
| `--sample-seed` | `SAMPLE_SEED` | this ISO week (e.g. `2026-W47`) | detection: which sample |

## GitHub Actions

Two workflows, both with a **Run workflow** button (Actions → choose the workflow → Run workflow).

### Smoke tests — on every pull request, and by hand

```
Lint ─────┐
          ├──> Smoke journeys (gate) ──┐
Unit ─────┘                            ├──> Allure report (link on its box)
          └──> Known issues ───────────┘
```

| Job | What it does | Can make the run red? |
|---|---|---|
| Lint | `ruff check` (likely bugs, unused code, import order) and `ruff format --check` | Yes |
| Unit tests | Config, test data, detection rules and helpers, no browser | Yes |
| Smoke journeys | The 4 customer journeys, 2 workers, 1 retry. Starts only after Lint **and** Unit pass | Yes — this is the gate |
| Known issues | Checks for known shop gaps. They fail on purpose; the job stays green with a warning, the failure shows in the report | No |
| Allure report | One report from both browser jobs, published as a web page | No |

Manual options: shop, language, address (e.g. an acceptance copy), browser, and whether to run known issues.

### Detection (weekly) — every Monday 06:00 UTC, and by hand

```
Lint ─────┐
          ├──> Detection (≤30 pages) ──> Allure report (link on its box)
Unit ─────┘
```

- Picks at most **30 public pages** from the sitemap, spread over the sections of the site (shop, stories, legal, …), always including the home page. Pages that robots.txt asks crawlers to skip, and addresses that are actions rather than pages (login, "add …"), are left out.
- Same week = same pages, so a re-run checks exactly the same pages; next week checks others.
- Records, for every page: answers of **400 and above** (the page and everything it loads) and **JavaScript errors** (crashes and console errors).
- **Fails the job** only for problems Fairphone must act on: a broken page, a crash in the shop's own scripts, a missing shop script or style, a shop server error (5xx). Everything else — third-party tools, missing images, console messages — is listed in the report but does not fail the job. Why: [knowledge/decisions.md](knowledge/decisions.md); rules: `utils/site_health.py`.
- Manual options: shop, number of pages, **specific pages** (e.g. a page a content editor just published), sample seed.

### Opening a report

One click from any of these:
- the **Allure report** box in the run graph: the link under the job name;
- the pull request: **View deployment**;
- the top of the run's summary page: **📊 Open the Allure report**, followed by a results table.

Each run keeps its own address, e.g. `https://ali7047.github.io/fairphone-qa-automation/smoke/<run>/` or `/detection/<run>/`.
`/smoke/latest/` and `/detection/latest/` open the newest; [the index page](https://ali7047.github.io/fairphone-qa-automation/) lists all runs; the last 20 per workflow are kept.
How: the shared report job (`.github/workflows/allure-report.yml`) pushes the report to the `gh-pages` branch (one fresh commit each time, so old reports don't pile up in git history) and GitHub Pages serves it. It turns Pages on by itself on its first run.

### Before pushing

```bash
uv run python -m ruff check . && uv run python -m ruff format --check .   # lint
uv run python -m ruff format .                                             # fix formatting
uv run python -m pytest tests/unit                                         # unit tests
```

## Test report (Allure)

Every run writes results to `allure-results/`. To open them locally (needs Node.js and Java):

```bash
npx allure-commandline@2 serve allure-results
```

Each test shows its Data / Steps / Expected description, every step with a screenshot,
the test data, the shop's server answers, and "expected vs actual" for each check.
A failed test also gets its screenshot, video and Playwright trace, which replays every step:

```bash
uv run python -m playwright show-trace test-results/<test-name>/trace.zip
```

## Project layout

```
config/          which shop, language and address; visible texts per language
pages/           page objects: where to click, kept out of the tests
test_data/       what the journeys buy and where they go, per shop and language
utils/           price reading, sitemap sampling, site-health rules, report evidence
tests/unit/      tests for config, test data, rules and helpers (no browser)
tests/smoke/     the 4 customer journeys on the real shop
tests/known_issues/  checks that fail until a known shop gap is fixed
tests/detection/ the site-health check of sampled pages
.github/         workflows, shared report job, report publishing scripts
knowledge/       how the shop works and how tests are written here
```
