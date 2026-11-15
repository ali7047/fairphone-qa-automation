# Production rules

The suite runs against a live shop with real customers. These rules are not optional.

## Never
- Submit an order or a payment.
- Register an account.
- Submit a newsletter sign-up, contact form or product review.
- Type real personal data anywhere.
- Bypass bot protection (no fake user agents, no CAPTCHA solving, no rotating IPs). A block is a finding to report.
- Commit secrets, credentials or personal data.

## Always
- At most **2 parallel workers** against production.
- Scheduled jobs run at their agreed frequency (detection: weekly). No extra cron jobs "to be safe".
- Use a fresh browser context per test, so tests never share a cart or session.
- Stop the checkout journey at the address step.
- Only listen to API requests the page itself makes; never call order, payment or form endpoints directly.

## When something goes wrong
| Situation | Do |
|---|---|
| Bot protection blocks a run | Stop, record what you saw (status code, page, time, runner), report it |
| A test would need to submit something to pass | Don't. Move that check to acceptance (PSP test mode, test mailbox) |
| A test fails only on production | Check content changes first: editors can change live pages without a deploy |
