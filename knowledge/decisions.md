# Decisions

Short decision records. Newest first. Format: decision — reason — date.

| Date | Decision | Reason |
|---|---|---|
| 2026-11-15 | Python environment managed with **uv** (`pyproject.toml` + `uv.lock`) | Exact versions on every machine and in CI; one command (`uv sync`) to set up |
| 2026-11-15 | **Playwright for both GUI and API checks** | A price shown on screen is compared with the value the page received from Odoo; a mismatch shows whether the screen or the server is wrong |
| 2026-11-15 | **Blocking tests must pass 100%**; flaky tests go to quarantine | A gate that tolerates failures can't separate real bugs from noise; quarantine keeps the gate strict without blocking on known flakiness |
| 2026-11-15 | **Cookie dialog: "Decline Optional"** via a locator handler | Works whenever the dialog appears; declining reduces third-party scripts and console noise; respects privacy |
| 2026-11-15 | **Detection job fails only on first-party problems**; third-party errors are reported only | A red job must mean "we must act"; noise we can't fix teaches people to ignore red |
| 2026-11-15 | **Max 2 workers, Chromium in the PR gate**; other browsers on demand | Production etiquette and a fast gate; cross-browser runs belong on acceptance or on demand |
| 2026-11-15 | **Each change on its own branch + pull request** | Every change is reviewed and the smoke workflow runs on the PR |
