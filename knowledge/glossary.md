# Glossary

Plain-language meaning of words used in this repo.

| Term | Meaning | Example |
|---|---|---|
| **Smoke test** | A few fast checks that the most important things still work | "Can a customer put a phone in the cart?" |
| **Regression test** | A check that something which worked before still works | Re-running cart tests after a checkout change |
| **E2E (end-to-end) test** | A test that drives the real site in a real browser, like a customer | Home page → product → cart |
| **Unit test** | A test of one small piece of code, without a browser or server | `parse_price("€ 599.00") == 599.00` |
| **Gate** | An automatic check that must pass before a change can move on | PR can't merge while the smoke suite is red |
| **Flaky test** | A test that sometimes passes and sometimes fails without any code change | Fails 1 in 10 runs on WebKit |
| **Quarantine** | A holding place for flaky tests: they still run but don't block | `@pytest.mark.quarantine(reason="JIRA-123")` |
| **Fixture** | Shared setup that pytest gives to a test | A fresh browser with the cookie dialog handled |
| **Marker** | A label on a test used to select which tests run | `pytest -m smoke` |
| **Page object** | A class that knows where to click on one page | `CartPage.remove_line()` |
| **Locator** | Playwright's way to find an element on the page | `get_by_role("button", name="Add to cart")` |
| **Trace** | A replay of a test run: screenshots, clicks, network, console | Opened with `playwright show-trace` |
| **Auto-wait** | Playwright waits until an element is ready before acting | No need for `sleep(3)` |
| **Base URL** | The address of the site under test; changing it switches environment | `https://www.fairphone.com` or an acceptance URL |
| **Acceptance environment** | A copy of the live shop for testing before release | Odoo.sh staging per region |
| **PSP** | Payment service provider; handles card and other payments | Has a test mode on acceptance |
| **Sitemap** | A file listing the site's pages for search engines | `/sitemap.xml` |
| **First-party / third-party** | Code from Fairphone itself / code from other companies loaded on the page | Odoo scripts / analytics, chat widget |
| **uv** | A fast Python package and environment manager | `uv sync` installs everything from `uv.lock` |
