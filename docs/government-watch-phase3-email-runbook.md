# Government Watch 2.0: live email release checks

## Two different email systems

- The GitHub Actions Watch sender reads `WATCH_SMTP_HOST`, `WATCH_SMTP_PORT`, `WATCH_SMTP_USER`, `WATCH_SMTP_PASSWORD`, and `WATCH_SMTP_FROM`. Its successfully received one-time diagnostic proved only this sender.
- Supabase Auth separately sends new-account confirmations and password-recovery links. GitHub Secrets do **not** configure Supabase Auth. The project Auth SMTP settings must be configured independently. Never expose provider credentials in HTML, JavaScript, issues, public logs, or this document.

## Configure Supabase Auth SMTP (project owner action)

1. Open [Katoptron Supabase dashboard](https://supabase.com/dashboard/project/bpvkapswslmgfazbzpsv) and locate **Authentication > SMTP Settings**.
2. Enable custom SMTP with a provider-approved sending address. For an initial Gmail beta: host `smtp.gmail.com`, port `587`, user and From set to the authorized sending Gmail account, password set to a **Google app password**, and sender name `Katoptron`. A dedicated app password separate from GitHub's Watch credential is preferable. A production-scale service with verified sender domain and SPF/DKIM/DMARC is recommended instead of consumer Gmail.
3. Keep **Confirm email** turned ON in **Authentication > Providers > Email**. Do **not** enable automatic confirmation simply to get around delivery problems.
4. Configure the Site URL and Redirect URL allowlist so `https://ayeemecee0.github.io/Katoptron/government-watch.html` is permitted. Verify against the project's actual configuration.
5. Keep signup-email rate limits, password-reset limits and CAPTCHA appropriate for an externally available site. Do not put service-role keys or app passwords in website assets.

## Test new signup and password reset

1. Use a genuinely new address not already registered in this project's Auth table. Previously submitted repeat signups return generic success to prevent account enumeration. They do not prove a new confirmation email was sent.
2. On the [Government Watch page](https://ayeemecee0.github.io/Katoptron/government-watch.html), create the new account. The on-page result is intentionally generic when Supabase reports success.
3. Find the confirmation message in the actual recipient mailbox, click the link, return to the Watch page, sign in, and confirm the page displays `Email confirmed.`.
4. On a separate existing account, use **Forgot password**. Verify the actual recovery email arrives, open the link on the same site and use **Save new password**. Sign in with the new password.
5. Inspect **Supabase > Authentication > Logs** for failed SMTP handoffs, rate limits and other errors. Redact addresses/tokens in any shared logs.

## Test a real newly observed source event

1. Sign in as a confirmed account, select a followed locality, select the appropriate evidence categories, and opt in. This explicit consent must predate the *observation* time of the event.
2. Wait for a **genuine new** government-sourced change, previously unseen `event_key`, with a source URL, date, and correct locality/category. Do not manufacture evidence, backdate an `observed_at` timestamp or publish synthetic public data just to pass the test.
3. Allow the daily Watch sender to run (or manually trigger it with **Send test email** turned **OFF**). Verify a delivered source-cited digest, one protected delivery receipt, no duplicate delivery on rerun, and no emails after unsubscribe.
4. In the absence of a real new event or an active subscriber, record the production-trigger check as **NOT YET VERIFIED**, not failed and not passed.

## Verified isolated regression (no production mail/data writes)

`node scripts/test_watch_auth_ui.cjs` tests real confirmation wording, category controls, signup ambiguity, recovery and locality selection.

`python -m unittest discover -s scripts -p 'test_government_watch_alerts.py' -v` exercises a source-pinned signed original government document through eligibility, sender composition, receipt de-duplication and unsubscribe, using protected data and mail stubs, **not** a fabricated production government event.
