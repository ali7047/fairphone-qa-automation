# Business context

What the shop is, who changes it, and where it runs. Facts are marked *Observed <date>* or *Assumption:*.

## The shop
- **Platform:** Odoo 16 e-commerce.
- **Storefronts:** www.fairphone.com (EU, several languages and currencies) and a separate US site on the same code base. *Assumption:* the US site URL and its differences (currency USD, sales tax added at checkout) still need to be confirmed.
- **Languages:** at least English and Dutch. *Observed 2026-11-15:* `/` redirected to `/nl` from a Dutch browser; English pages have no language prefix (`/the-fairphone-gen-6`).
- **Products:** smartphones (Fairphone Gen. 6 and Gen. 6+, Android and /e/OS), audio (Fairbuds 2, Fairbuds XL), accessories, spare parts, gift cards.

## Teams and process
- Two Scrum teams, about six developers in total, two-week sprints.
- Jira for tickets, GitHub for code. Developers open pull requests into the production branch.
- Small increments every sprint, plus one or two big launches a year (new phone or audio product) with a traffic peak on launch day.

## Environments
| Environment | What it is | Who uses it |
|---|---|---|
| Production | The live shop | Customers, content editors |
| Acceptance (EU and US) | A copy of the live shop on Odoo.sh | Developers (work in progress), stakeholders (testing), content editors (preparing pages) |

- Payments go through a payment service provider (PSP) with a **test mode** on test environments.
- *Assumption:* acceptance runs payment in test mode and does not send real emails to customers.

## Who changes the shop
Not every change goes through a developer or a deploy:
| Change | Path | Risk |
|---|---|---|
| Code | PR → acceptance → production branch | Covered by tests and gates |
| Content prepared ahead | Content editor on acceptance → publish to live | Reviewed before publishing |
| Content edited live | Content editor (marketing, UX) uses the website editor directly on production | No release, no gate — needs monitoring on live |

This is why the suite also runs checks against the live site, not only before deploys.
