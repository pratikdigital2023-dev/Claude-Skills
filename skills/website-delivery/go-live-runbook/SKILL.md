---
name: go-live-runbook
description: A step-by-step runbook for the day of launch — pre-flight checks, DNS cutover, smoke tests, monitoring, and rollback plan. Use the morning of launch and as a template you can hand to an on-call partner.
---

# Go-Live Runbook

The launch day playbook. Follow it. Don't improvise. Most launch disasters
trace back to "we forgot to do X" — this checklist exists to keep that
list at zero.

## When to use

- The morning of launch (every time)
- During staging dress rehearsal (1 week before)
- As a template for any subsequent major release

## T-7 days

- [ ] Code freeze: only critical bug fixes after this point
- [ ] Final design / content review with client; sign-off in writing
- [ ] Full staging environment frozen + accessible to client
- [ ] Lighthouse CI passing on all critical templates
- [ ] Sentry source maps uploading correctly
- [ ] All third-party accounts verified (Stripe live, GA4, Resend domain)
- [ ] Backups: DB snapshot, asset bucket snapshot, current site snapshot
- [ ] Insurance / errors-and-omissions coverage current

## T-3 days

- [ ] Lower DNS TTL on existing records to 300s (5 min)
- [ ] Run final content sync / migration script
- [ ] Verify redirect map covers all old URLs (Screaming Frog list mode)
- [ ] Schedule status page maintenance window (if applicable)
- [ ] Notify client of exact cutover time + who's on call
- [ ] Post-launch monitoring on call rota set
- [ ] Email: "What to expect on launch day" sent to client

## T-1 day

- [ ] Smoke test on staging: every critical user flow
- [ ] Verify email send works on production keys (test against your own inbox)
- [ ] Verify Stripe in **live mode** with a real $1 charge → refund
- [ ] Confirm CMS webhook → revalidation works on production
- [ ] Confirm new site loads at preview URL with prod DB / API
- [ ] Cross-browser smoke test (see `cross-browser-matrix`)
- [ ] Mobile device smoke test (real iOS + Android, not just emulators)
- [ ] Schedule a quick "war room" Zoom for cutover

## T-0 (launch morning)

### 1. Pre-flight (T-60 min)

- [ ] Confirm everyone on the war-room call (PM, dev, client lead)
- [ ] Old site reachable at backup URL (e.g., `old.acme.com`) — rollback path
- [ ] All credentials in front of you (DNS, hosting, CDN, monitoring)
- [ ] Status page incident draft ready (don't publish yet)
- [ ] Coffee

### 2. Final sync (T-30 min)

- [ ] Last incremental content migration run
- [ ] Lock CMS to read-only mode if needed
- [ ] Tag a release in git: `git tag v1.0.0-launch && git push --tags`
- [ ] Snapshot DB
- [ ] Verify production build is current

### 3. Cutover (T-0)

- [ ] Update DNS A/CNAME records to point at new origin
- [ ] Update redirect rules (301 from old paths → new paths)
- [ ] Purge CDN caches (Cloudflare → Caching → Configuration → Purge Everything)
- [ ] Watch DNS propagation: `dig +short acme.com` from multiple regions
- [ ] First curl: `curl -I https://acme.com` → expect 200

### 4. Smoke tests (T+5 to T+30 min)

Have a 20-item checklist tailored to the site. Universal items:
- [ ] Homepage loads + renders correctly
- [ ] Navigation works on all main pages
- [ ] One product / blog / detail page loads with full content
- [ ] Contact form submits successfully + sends notification email
- [ ] Newsletter signup creates contact in ESP
- [ ] Login / signup flow works
- [ ] Checkout flow works (test purchase $1 → refund)
- [ ] 5 random old URLs all 301 to expected new URLs
- [ ] 404 page renders correctly
- [ ] robots.txt + sitemap.xml accessible
- [ ] favicon + OG image render in social previews (run through Twitter
      Card Validator + LinkedIn Post Inspector)

### 5. Monitoring (T+15 to T+60 min)

- [ ] Uptime monitor: green
- [ ] Sentry: no spike in errors
- [ ] Vercel/host logs: nothing alarming
- [ ] Analytics: real-time sessions appearing (GA4 / Plausible)
- [ ] Cloudflare: caching working (high cache hit ratio after 15 min)
- [ ] Server response times under expected baseline

### 6. Submit to search engines (T+60 min)

- [ ] Google Search Console: submit new sitemap
- [ ] Verify domain in GSC (if new)
- [ ] Bing Webmaster Tools: submit sitemap
- [ ] Validate canonical tags on top pages
- [ ] If migrating: file change-of-address in GSC

### 7. Communications (T+90 min)

- [ ] Update status page: "Launch complete" + close incident
- [ ] Email client: "We're live, here's what to monitor"
- [ ] Internal Slack: "🚀 launched"
- [ ] Tweet / LinkedIn post (if client is doing PR)

## Post-launch (T+1 to T+7 days)

- [ ] Daily standup with client for first week
- [ ] Monitor Sentry / uptime / analytics each morning
- [ ] Check Search Console for crawl errors (3 days post-launch)
- [ ] Check Lighthouse CI on production daily
- [ ] Monitor support / contact form for user-reported issues
- [ ] Compare conversion to old site (give it 14 days)

## Rollback plan

If something is critically broken (checkout, payments, login):

### Soft rollback (5–15 min)
- Revert deploy in Vercel/Netlify dashboard ("Promote to production"
  on previous build)
- Verify the bad change is gone

### DNS rollback (1–4 hours due to TTL)
- Repoint DNS at old origin
- Lower TTL further (60s) for next attempt
- Communicate to client

### Database rollback (last resort)
- Restore from snapshot
- Notify users of any data loss
- Post-mortem mandatory

## After-action

Within 24 hours, write a short post-launch note to the client:
- What launched
- What we monitored
- Any issues encountered + how we resolved
- Top metrics so far
- Next 7 days of monitoring

## Anti-patterns

- Launching on a Friday afternoon (no one to fix issues over the weekend)
- Launching during a marketing campaign (no rollback margin)
- No rollback path (old origin already torn down)
- High DNS TTLs at launch (24h+ stuck if you need to rollback)
- No monitoring set up before launch (flying blind)
- One person doing the cutover alone (have a buddy on call)
- Skipping the smoke test "to save time" (always regret this)
- No status page or comms plan (panicked client, panicked users)

## Tools

- **Status pages**: Better Stack, Statuspage, Instatus
- **DNS check**: dnschecker.org, `dig` from multiple regions
- **Smoke tests**: Playwright recorded scripts, BrowserStack
- **Communication**: Slack canvas / Notion runbook with checkboxes

## Tailoring this runbook

Per project, customize:
- Specific URLs to smoke-test
- Specific 3rd-party services to verify
- Specific stakeholders to notify
- Specific revert / rollback commands

Keep the runbook with the project repo (`docs/launch-runbook.md`).
