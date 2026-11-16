# CLAUDE.md

Instructions for AI coding assistants in this repository. People: start with [README.md](README.md).

## Before changing anything, read
| Task | Read |
|---|---|
| Add or change a test | [knowledge/automation-standards.md](knowledge/automation-standards.md), [knowledge/customer-flows.md](knowledge/customer-flows.md) |
| Prices, VAT, currencies | [knowledge/business-rules.md](knowledge/business-rules.md) |
| Language, cookie dialog, site quirks | [knowledge/site-observations.md](knowledge/site-observations.md) |
| The shop, teams and environments | [knowledge/business-context.md](knowledge/business-context.md) |
| Why something is built this way | [knowledge/decisions.md](knowledge/decisions.md) |
| Testing against the live shop | [knowledge/production-rules.md](knowledge/production-rules.md) — mandatory |

## Commands
See [README.md](README.md). Always run Python tools as `uv run python -m <tool>`.

## Keep knowledge current
- A new fact about the site goes in `knowledge/site-observations.md`; a new decision in `knowledge/decisions.md`.
- Mark anything not confirmed as *Assumption:*. Keep each fact in one file and link to it from others.
