# CLAUDE.md

Guidance for AI coding assistants working in this repository.
People: start with [README.md](README.md). This file is the short version of the same rules.

## What this repo is
End-to-end and monitoring checks for the Fairphone webshop (Odoo 16, EU and US storefronts),
written in Python with Playwright and pytest, run in GitHub Actions. Dependencies are managed with uv.

## Commands
```bash
uv sync                                          # create .venv and install exact versions from uv.lock
uv run python -m playwright install chromium     # browser for the tests
uv run python -m pytest tests/unit               # helper tests, no browser, seconds
uv run python -m pytest -m smoke                 # critical customer journeys
BASE_URL=https://<acceptance-url> uv run python -m pytest -m smoke   # same suite, other environment
uv run python -m pytest -m detection             # site-health check (max 30 URLs)
```

## Read before you change something
| Task | Read |
|---|---|
| Add or change a test | [knowledge/customer-flows.md](knowledge/customer-flows.md), [knowledge/automation-standards.md](knowledge/automation-standards.md) |
| Prices, VAT, currencies, regions | [knowledge/business-rules.md](knowledge/business-rules.md) |
| Cookie banner, redirects, bot protection | [knowledge/site-observations.md](knowledge/site-observations.md) |
| What the shop is and who changes it | [knowledge/business-context.md](knowledge/business-context.md) |
| Why something is built this way | [knowledge/decisions.md](knowledge/decisions.md) |
| Unknown term | [knowledge/glossary.md](knowledge/glossary.md) |

## Production is a live shop: non-negotiable rules
Full list: [knowledge/production-rules.md](knowledge/production-rules.md).
- Never submit an order, payment, account registration, newsletter, contact form or review.
- At most 2 parallel workers. Scheduled jobs keep their schedule.
- If bot protection blocks a run, record it as a finding. Never bypass it.
- No secrets, credentials or personal data in code, test data or logs.

## Code conventions
- Locators live only in `pages/`. Tests read like customer journeys.
- Selector order: role + visible name → label → stable Odoo attribute. No layout CSS, no XPath.
- No fixed sleeps. Use `expect()` and Playwright's auto-wait.
- A flaky test gets the quarantine marker and a ticket id, not a longer timeout.

## Keep knowledge current
- New fact about the site → `knowledge/site-observations.md`, with the date observed.
- New decision → `knowledge/decisions.md` (decision, reason, date).
- Facts are marked *Observed <date>* or *Assumption:*. Never present an assumption as a fact.
