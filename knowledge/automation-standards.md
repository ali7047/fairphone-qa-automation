# Automation standards

How tests in this repo are written. A new contributor should be able to add a test by following this page.

## Tools
| Tool | Why |
|---|---|
| Python 3.12 + uv | One language with the shop (Odoo is Python); uv pins exact versions in `uv.lock` |
| pytest | Fixtures for shared setup, markers to select suites |
| Playwright for Python | Real browsers, auto-waiting, traces, and API requests in the same test |
| pytest-playwright | Browser fixtures and `--base-url` |
| pytest-xdist | Parallel runs, capped at 2 workers |
| pytest-rerunfailures | One retry in CI to detect flaky tests |
| pytest-html | Self-contained HTML report |

## Structure
```
config/      where to test: base URL, region, locale (from environment variables)
pages/       one class per page; locators and actions live only here
utils/       helpers without a browser (money parsing, sitemap sampling)
tests/unit/       tests for the helpers
tests/smoke/      critical customer journeys
tests/detection/  site-health checks
```

## Selectors (in this order)
1. Role + accessible name: `page.get_by_role("button", name="Add to cart")`
2. Label or placeholder: `page.get_by_label("Email")`
3. Stable Odoo attributes: `name=`, `data-*`, form `action`
4. Never: layout CSS classes, XPath, `nth()` without a reason in a comment

## Waiting
- No `time.sleep()` or `wait_for_timeout()`.
- Assert with `expect(locator).to_have_text(...)` — it retries until the timeout.
- Wrap navigation-causing actions in `expect_navigation()` / `expect_response()` when the next step depends on it.

## Adding a test
1. Describe the journey in [customer-flows.md](customer-flows.md).
2. Add or extend a page object in `pages/` (locators + actions, no assertions about business rules).
3. Write the test in `tests/<suite>/test_<journey>.py`; give it a marker (`@pytest.mark.smoke`).
4. Compare money with `utils.money.parse_price()`, never as strings.
5. Run it 3 times locally before opening a PR.

## Naming
- Files: `test_<journey>.py`. Tests: `test_<what_the_customer_does>`.
- Page objects: `<Name>Page` in `pages/<name>_page.py`.

## Flaky tests
- CI retries a failed test once. "Passed on retry" is reported as flaky, not as green.
- Flaky twice in a week → mark `@pytest.mark.quarantine(reason="JIRA-123")`. Quarantined tests run in a separate, non-blocking job.
- Quarantine is temporary: fix or delete within two sprints.

## Commits and branches
- One branch per change, opened as a pull request. Commit messages say *why*, not only *what*.
