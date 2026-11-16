# fairphone-qa-automation

End-to-end and monitoring checks for the Fairphone webshop ([www.fairphone.com](https://www.fairphone.com) and [us.fairphone.com](https://us.fairphone.com)), in Python with Playwright and pytest, run in GitHub Actions.

> Work in progress: the customer journeys and the GitHub Actions workflows are being added.

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
