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

### When a test fails

A screenshot, a video and a Playwright trace are saved in `test-results/<test-name>/`. The trace replays every step, click and network call:

```bash
uv run python -m playwright show-trace test-results/<test-name>/trace.zip
```

## Project layout

```
config/       which shop, language and address; visible texts per language
pages/        page objects: where to click, kept out of the tests
utils/        helpers, e.g. reading "€ 599.00" or "$649.99" as a number
tests/unit/   tests for config and helpers (no browser)
tests/smoke/  customer journeys on the real shop
knowledge/    how the shop works and how tests are written here
```
