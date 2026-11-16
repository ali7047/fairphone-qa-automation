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
| **Known shop gaps get a test that stays red, in a separate non-blocking job** (`known_issue` marker) | The gap stays visible in every report until it is fixed, while the smoke gate stays trustworthy: red there always means something new broke |
| **Allure report** with steps, screenshots, data and expected-vs-actual per check | A reader can follow and judge a test without opening the code; failures come with trace and video |
| **Typing into checkout only with form posts blocked** | The live shop must never receive a form, even by an accidental Enter key |
| **Blocking tests must pass 100%**; flaky tests go to quarantine | A gate that tolerates failures can't separate real bugs from noise |
| **Trace, screenshot and video kept only for failed tests** | Enough to debug without re-running; passing runs stay fast and small |
| **Detection job fails only on the shop's own problems** | A red job must mean "act now"; third-party noise is reported, not failed |
| **Max 2 workers; Chromium in the PR gate**, other browsers on demand | Production etiquette and a fast gate |
| **Each change on its own branch + pull request** | Every change is reviewed, and the smoke workflow runs on the PR |
