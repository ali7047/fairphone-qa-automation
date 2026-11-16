# Business context

What the shop is, who changes it, and where it runs. *Assumption:* marks what is not confirmed yet.

## The shop
- **Platform:** Odoo 16 e-commerce.
- **Storefronts:**
  | Shop | Address | Languages | Currency |
  |---|---|---|---|
  | EU | https://www.fairphone.com | English, Dutch, German, French | EUR (more per country, see [business-rules.md](business-rules.md)) |
  | US | https://us.fairphone.com | English | USD |
- Both run on the same code base. How the shop picks its language: [site-observations.md](site-observations.md).
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
- *Assumption:* acceptance runs payments in test mode and does not send real emails to customers.

## Who changes the shop
Not every change goes through a developer or a deploy:
| Change | Path | Safety net |
|---|---|---|
| Code | PR → acceptance → production branch | Tests and gates |
| Content prepared ahead | Content editor on acceptance → publish to live | Review before publishing |
| Content edited live | Content editor (marketing, UX) uses the website editor on production | None — needs checks on the live site |

This is why the suite also runs against the live site, not only before deploys.
