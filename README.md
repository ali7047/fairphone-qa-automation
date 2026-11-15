# fairphone-qa-automation

End-to-end and monitoring checks for the Fairphone webshop ([www.fairphone.com](https://www.fairphone.com) and [us.fairphone.com](https://us.fairphone.com)), written in Python with Playwright and pytest, and run in GitHub Actions.

> Work in progress: the customer-journey tests and the GitHub Actions workflows are being added.

## Run locally

Needs [uv](https://docs.astral.sh/uv/) (it installs the right Python by itself).

```bash
uv sync                                          # install exact versions from uv.lock into .venv
uv run python -m playwright install chromium     # download the test browser (once)

uv run python -m pytest tests/unit               # helper tests: no browser, under a second
uv run python -m pytest -m smoke                 # browser tests against the live EU shop
uv run python -m pytest -m smoke --region us     # same tests against the US shop
uv run python -m pytest -m smoke --headed        # watch the browser while it runs
```

### Where the tests run

| Option | Environment variable | Default | Example |
|---|---|---|---|
| `--region` | `REGION` | `eu` | `--region us` |
| `--base-url` | `BASE_URL` | the region's live shop | `--base-url https://<acceptance-url>` |

The region decides currency, language and tax rules; the base URL decides which copy of the shop is tested. Pointing the suite at an acceptance environment is one option: `--base-url`.

### When a test fails

A screenshot, a video and a Playwright trace are saved in `test-results/<test-name>/`. Open the trace to replay every step, click and network call:

```bash
uv run python -m playwright show-trace test-results/<test-name>/trace.zip
```

## Project layout

```
config/settings.py   region profiles (EU, US) and how the address under test is chosen
pages/               page objects: where to click, kept out of the tests
utils/money.py       turns "€ 599.00", "$649.99", "1.234,56 €" into comparable numbers
tests/conftest.py    shared setup: fresh browser per test, English pinned, cookie dialog declined
tests/unit/          tests for the helpers
tests/smoke/         critical customer journeys
knowledge/           what the suite is built on: shop context, journeys, rules, decisions
```
