# Decisions

Why the suite is built the way it is. One line per decision; git history shows when.

| Decision | Reason |
|---|---|
| **Python with uv** (`pyproject.toml` + `uv.lock`) | Odoo is Python, so the shop's developers can read and extend the tests; uv installs exact versions everywhere with one command |
| **Tests live in their own repository** | The live shop is tested from outside, like a customer; see "Where tests live" in [automation-standards.md](automation-standards.md) |
| **Region profiles (EU, US) and a language option** | Same tests for both shops, every language and any acceptance copy; currency and tax rules stay with the region |
| **Switch the shop language before each test** | The shop picks its language by location; a fixed language keeps text-based locators valid on any machine |
| **Cookie dialog declined automatically** | Works whenever the dialog appears; declining loads fewer third-party scripts; privacy-friendly |
| **Playwright for both GUI and API checks** | A price on screen is compared with the value the page received from the server; a mismatch shows which side is wrong |
| **Helpers have their own unit tests** | Browser tests rely on them; a wrong helper would report shop bugs that don't exist, or hide real ones |
| **Known shop gaps get a test that fails until fixed; its job stays green with a warning** | The gap stays visible in every report, while the run's colour only shows new problems |
| **Allure report** with steps, screenshots, data and expected-vs-actual per check | A reader can follow and judge a test without opening the code; failures come with trace and video |
| **Typing into checkout only with form posts blocked** | The live shop must never receive a form, even by an accidental Enter key |
| **Allure report published to GitHub Pages, one address per run**, link on the run page | One click from the run to the report; earlier runs' links keep working; no download or local tools needed |
| **Lint and unit tests first, in parallel; browser tests only after both pass** | Cheap checks fail in about a minute; no browser traffic on the live shop when the code itself is broken |
| **Blocking tests must pass 100%**; flaky tests go to quarantine | A gate that tolerates failures can't separate real bugs from noise |
| **Trace, screenshot and video kept only for failed tests** | Enough to debug without re-running; passing runs stay fast and small |
| **Detection fails only on what Fairphone must act on**: broken page, own script crash, missing own script/style, own 5xx. Third-party errors, missing images and console messages are reported only | A red job must mean "act now"; the first runs had about 60–90 messages each, none actionable — failing on them would teach people to ignore red |
| **Whose script crashed is read from the error's stack trace** | Uncaught errors carry no source; the stack shows the script address. Without it, a Yotpo widget crash was blamed on the shop |
| **Detection samples ≤30 pages, spread over site sections, seeded by ISO week** | Light on the live shop; every section gets checked over time; a re-run checks the same pages |
| **Detection respects robots.txt and skips action addresses** (login, "add …") | A monitoring job must not visit what crawlers are asked to skip, nor trigger actions |
| **Detection on Mondays 06:00 UTC, no retries** | Low traffic, before the week's releases; a page that fails once is worth seeing |
| **Max 2 workers; Chromium in the PR gate**, other browsers on demand | Production etiquette and a fast gate |
| **Each change on its own branch + pull request** | Every change is reviewed, and the smoke workflow runs on the PR |
