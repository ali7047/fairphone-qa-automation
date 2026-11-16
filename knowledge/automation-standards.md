# Automation standards

How tests in this repo are written. A new contributor should be able to add a test by following this page.

## Where tests live
| Test level | Lives in | Owner | Runs |
|---|---|---|---|
| Unit and integration (Odoo `TransactionCase`, `HttpCase`, JS tours) | The shop's own repository, next to the code | Developers | On every PR, in seconds/minutes |
| End-to-end and live monitoring | **This repository** | QA, with developers contributing | On PRs, after deploys, on a schedule |

End-to-end tests treat the shop as a black box (a customer's view), test **any** environment by address, and also catch changes that never go through the code repository (content edited live). Their own repository keeps their dependencies and schedule out of the shop's build.

## Tools
| Tool | Why |
|---|---|
| Python 3.12 + uv | Same language as Odoo; uv pins exact versions in `uv.lock` |
| pytest | Fixtures for shared setup, markers to select suites |
| Playwright for Python | Real browsers, auto-waiting, traces, and API requests in the same test |
| pytest-playwright | Browser fixtures and `--base-url` |
| pytest-xdist | Parallel runs, capped at 2 workers |
| pytest-rerunfailures | One retry in CI to detect flaky tests |
| allure-pytest | Report with every step, screenshot, data and server answer; trace and video for failed tests |
| ruff | Lint (likely bugs, unused code, import order) and formatting, one tool; rules in `pyproject.toml` |

## Structure
```
config/settings.py   which shop, language and address (options and environment variables)
config/languages.py  visible texts per language, used by page objects
pages/               one class per page; locators and actions only
utils/               helpers without a browser (price parsing, sitemap sampling)
tests/unit/          tests for config and helpers: no browser, no network
tests/smoke/         critical customer journeys on the real shop
tests/detection/     site-health checks on the real shop
```

## Every browser test states data, steps and expected result
```python
def test_cart_total_matches_configurator_price(page, settings):
    """
    Data:     what goes in, and where it comes from
    Steps:    what the test does on the shop
    Expected: what must be true at the end
    """
    ...
    assert actual == expected, f"Expected {expected}, actual {actual}"
```
- Give every `assert` and `expect` a message that says expected vs actual.
- Read values such as prices **from the page while the test runs**; never type a price into a test.

## Locators (in this order)
1. Role + visible name: `get_by_role("button", name=self.text("add_to_cart"))`
2. Label or placeholder: `get_by_label(...)`
3. A stable attribute: `href`, `name=`, `data-*`, form `action`
4. Never: styling classes, XPath, position (`nth()`) without a comment saying why

Visible names come from `config/languages.py`, so the same test runs in every language.

**Finding a locator:** right-click → Inspect (text and attributes); DevTools → Accessibility tab (role and name); or let Playwright suggest one:
```bash
uv run python -m playwright codegen https://www.fairphone.com/en/
```

## Waiting
- No `time.sleep()` or `wait_for_timeout()`.
- Check with `expect(locator).to_have_text(...)`: it retries until it passes or times out.
- Wrap actions that load a page in `expect_navigation()` / `expect_response()` when the next step depends on it.

## Adding a test
1. Describe the journey in [customer-flows.md](customer-flows.md).
2. Add or extend a page object in `pages/`; add new visible texts to `config/languages.py` for every language.
3. Write the test in `tests/<suite>/test_<journey>.py` with a marker (`@pytest.mark.smoke`) and the Data/Steps/Expected docstring.
4. Compare money with `utils.money.parse_price()`, never as text.
5. Run it 3 times locally, in English and Dutch, before opening a PR.
6. Run lint and formatting: `uv run python -m ruff check . && uv run python -m ruff format --check .` (the pipeline runs the same).

## Naming
- Files: `test_<journey>.py`. Tests: `test_<what_the_customer_does>`.
- Page objects: `<Name>Page` in `pages/<name>_page.py`.

## Flaky tests
- CI retries a failed test once. "Passed on retry" is reported as flaky, not as green.
- Flaky twice in a week → `@pytest.mark.quarantine(reason="JIRA-123")`; quarantined tests run in a separate, non-blocking job.
- Quarantine is temporary: fix or delete within two sprints.

## Commits and branches
- One branch per change, opened as a pull request. Commit messages: `NEW: <summary>`, body says *why*.
