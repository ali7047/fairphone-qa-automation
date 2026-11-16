# fairphone-qa-automation

End-to-end and monitoring checks for the Fairphone webshop ([www.fairphone.com](https://www.fairphone.com) and [us.fairphone.com](https://us.fairphone.com)), in Python with Playwright and pytest, run in GitHub Actions.

> Work in progress: the weekly detection job is being added. The US shop journeys are not stable yet.

## Run locally

Needs [uv](https://docs.astral.sh/uv/); it installs the right Python by itself.

```bash
uv sync                                          # install exact versions from uv.lock
uv run python -m playwright install chromium     # download the test browser (once)

uv run python -m pytest tests/unit               # config and helper tests: no browser, under a second
uv run python -m pytest -m smoke                 # journeys on the live EU shop, in English
uv run python -m pytest -m smoke --language nl   # same journeys in Dutch
uv run python -m pytest -m smoke --region us     # same journeys on the US shop
uv run python -m pytest -m smoke --headed        # watch the browser
uv run python -m pytest -m known_issue           # checks that fail today because of a known shop gap
```

## GitHub Actions

`Smoke tests` runs on every pull request and on demand (Actions → Smoke tests → Run workflow, with shop, language, address and browser to choose).

```
Lint ─────┐
          ├──> Smoke journeys (gate) ──┐
Unit ─────┘                            ├──> Allure report
          └──> Known issues (may fail) ┘
```

| Job | What it does | Blocks a PR? |
|---|---|---|
| Lint | `ruff check` (likely bugs, unused code, import order) and `ruff format --check` | Yes |
| Unit tests | Config, test data and helpers, no browser | Yes |
| Smoke journeys | The 4 customer journeys, 2 workers, 1 retry. Starts only after Lint **and** Unit pass | Yes |
| Known issues | Checks for known shop gaps; red until the shop is fixed | No |
| Allure report | One report from both browser jobs, published as a web page; link and results table on the run page | No |

**Opening the report** — one click from any of these:
- the **Allure report** box in the run graph: the link under the job name;
- the pull request: **View deployment** next to *allure-report*;
- the top of the run's summary page: **📊 Open the Allure report**.
Each run keeps its own address (`https://ali7047.github.io/fairphone-qa-automation/smoke/<run number>/`), the newest is always at
[`/smoke/latest/`](https://ali7047.github.io/fairphone-qa-automation/smoke/latest/), and
[the index page](https://ali7047.github.io/fairphone-qa-automation/) lists every published run. The last 20 runs are kept.
The report is also attached to the run as the **allure-report** artifact (kept 14 days), and **playwright-artifacts-*** holds traces and videos of failed tests.

How it is published: the report job pushes the report to the `gh-pages` branch (one fresh commit each time, so old reports don't pile up in git history) and GitHub Pages serves that branch as a website. The job turns Pages on by itself on its first run.

Before pushing, run the same checks locally:

```bash
uv run python -m ruff check . && uv run python -m ruff format --check .   # lint
uv run python -m ruff format .                                             # fix formatting
uv run python -m pytest tests/unit                                         # unit tests
```

### Choosing what to test

| Option | Environment variable | Default | Values |
|---|---|---|---|
| `--region` | `REGION` | `eu` | `eu`, `us` |
| `--language` | `SHOP_LANGUAGE` | `en` | `en`, `nl` on `eu`; `en` on `us` |
| `--base-url` | `BASE_URL` | the region's live shop | any address, e.g. an acceptance copy |

### Test report (Allure)

Every run writes results to `allure-results/`. To open them as a report (needs Node.js and Java):

```bash
npx allure-commandline@2 serve allure-results
```

Each test shows its Data / Steps / Expected description, every step with a screenshot,
the test data, the shop's server answers, and "expected vs actual" for each check.

### When a test fails

The report also gets the screenshot, video and Playwright trace of the failed test
(saved in `test-results/<test-name>/` too). The trace replays every step, click and network call:

```bash
uv run python -m playwright show-trace test-results/<test-name>/trace.zip
```

## Project layout

```
config/       which shop, language and address; visible texts per language
pages/        page objects: where to click, kept out of the tests
test_data/    what the journeys buy and where they go, per shop and language
utils/        helpers: reading "€ 599.00" or "$649.99" as a number; report evidence
tests/unit/   tests for config, test data and helpers (no browser)
tests/smoke/  the 4 customer journeys on the real shop
knowledge/    how the shop works and how tests are written here
```
