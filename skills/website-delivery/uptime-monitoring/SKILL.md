---
name: uptime-monitoring
description: Monitor production uptime with synthetic checks, status page, and on-call alerting. Covers Better Stack, UptimeRobot, Pingdom, Checkly, and custom Cloudflare Workers monitors. Use after launch (and ideally pre-launch on staging).
---

# Uptime Monitoring

Sentry tells you about errors users hit; uptime monitoring tells you when
no users *can* hit anything. Both are needed. The first hour of an outage
is when you most need 30 seconds of automated detection.

## When to use

- Always — the first thing to set up after launch
- Pre-launch: monitor staging to catch flaky deploys
- Adding 3rd party services (Stripe, GTM, fonts) that can outage independently

## Decision: which provider

| Provider | When |
|---|---|
| **Better Stack** | Best modern UX, status page included, free tier |
| **UptimeRobot** | Simplest, generous free, no status page bells |
| **Pingdom** | Enterprise, more $$$ |
| **Checkly** | Synthetic browser tests + uptime, dev-friendly |
| **Cloudflare Health Checks** | If already on Cloudflare, $5/mo, simple |

For a $50K project: **Better Stack** (or UptimeRobot if budget-tight).

## What to monitor

Pick the right targets:

| Target | Type | Frequency |
|---|---|---|
| Homepage HTTP 200 | HTTP | 1 min |
| Critical pages (/pricing, /signup, /checkout) | HTTP | 1 min |
| API health endpoint (`/api/health`) | HTTP | 30 sec |
| Login flow | Synthetic browser | 5 min |
| Checkout flow (test mode) | Synthetic browser | 15 min |
| DNS resolution | DNS | 5 min |
| SSL certificate expiry | SSL | daily |
| 3rd party deps (Stripe, GTM, CDN) | HTTP | 5 min |

## Health endpoint

Build a lightweight `/api/health`:
```ts
// app/api/health/route.ts
export async function GET() {
  const checks = await Promise.allSettled([
    checkDb(),
    checkCache(),
    checkExternalApi(),  // optional
  ])
  const status = checks.every(c => c.status === 'fulfilled') ? 'ok' : 'degraded'
  return Response.json({
    status,
    timestamp: new Date().toISOString(),
    version: process.env.VERCEL_GIT_COMMIT_SHA?.slice(0, 7),
    checks: {
      db: checks[0].status,
      cache: checks[1].status,
      external: checks[2].status,
    },
  }, { status: status === 'ok' ? 200 : 503 })
}
```

Rules:
- Cheap (≤ 200ms) — should not stress the system
- No auth required (monitor needs to hit it)
- Returns 200 only when all critical deps are alive
- Returns 503 (not 500) on degradation — clearer signal

## Synthetic browser tests

For critical flows, run real Playwright/Chromium tests every N minutes:

```ts
// In Checkly or self-hosted
import { test, expect } from '@playwright/test'

test('checkout flow', async ({ page }) => {
  await page.goto('https://acme.com/products/sku-123')
  await page.click('button:has-text("Add to cart")')
  await page.click('a:has-text("Checkout")')
  await page.fill('input[name="email"]', 'monitor@acme.com')
  await page.click('button:has-text("Continue")')
  await expect(page).toHaveURL(/checkout\.stripe\.com/)
})
```

Run from multiple regions (US East, EU West, Asia) to catch regional issues.

## Status page

Public status page builds trust + saves support tickets during incidents.

Best Stack and Statuspage.io let you:
- Show component status (web, API, payments, email)
- Post incident updates
- Subscribe via email/SMS/RSS

URL: `status.acme.com` (subdomain).

For B2B SaaS: status page is **table stakes**. For brochure sites: optional.

## Alerting

Match severity to channel:

| Severity | Trigger | Channel | SLA |
|---|---|---|---|
| **Critical** | Homepage down 2+ checks | Phone call + SMS + Slack | 15 min response |
| **High** | API errors > 5% / 5 min | SMS + Slack | 1 hour |
| **Medium** | Slow response p95 > 3s | Slack | Next biz day |
| **Low** | SSL expires in 14 days | Email | Plan |

Page only when human action is required. Don't page on transient blips
(use a 2-of-3 check rule).

## On-call rotation

For solo agencies: just you. For teams: rotation via PagerDuty / Better
Stack on-call.
- Primary on-call (8h shift)
- Secondary fallback
- Schedule covers nights + weekends if SLA requires

## Incident response runbook

When a critical alert fires:
1. Acknowledge within 5 min (stops escalation)
2. Open status page incident (template: "investigating")
3. Open dedicated Slack thread or war room
4. Run through runbook (see below)
5. Update status page every 15 min, even with "still investigating"
6. Post-mortem within 5 business days

### Runbook template (per service)

```
SERVICE: Web frontend

If down (5xx or no response):
- Check Vercel deployment status: https://vercel.com/acme/dashboard
- Check Cloudflare status: https://www.cloudflarestatus.com
- Check origin: curl -I https://origin.acme.com
- Roll back: vercel rollback in Vercel dashboard
- Cache nuke: Cloudflare → Caching → Purge Everything (last resort)

Escalation: contact lead@acme.com after 30 min if not resolved
```

## SSL monitoring

Cert expiry is preventable but still happens. Monitor:
- `*.acme.com` certificate
- Email if < 14 days to expiry
- Page if < 3 days

Most modern hosts (Vercel, Cloudflare, Netlify) auto-renew Let's Encrypt
certs. Still monitor — auto-renew can fail.

## Domain monitoring

Set calendar reminders 60 + 30 + 14 + 7 days before domain expiry. Domain
hijacking via expiry is a catastrophic, easily preventable mistake.

## Geo-distributed checks

Monitor from at least:
- US East (Virginia)
- US West (Oregon)
- EU (Frankfurt or London)
- Asia (Singapore or Tokyo)

If a check fails in only one region, it's likely an ISP / regional CDN
issue, not your site.

## Logs + correlation

When uptime alert fires, you want to see logs in one click. Send Vercel /
Cloudflare logs to:
- **Better Stack Logs** (if using their uptime)
- **Datadog** (if enterprise)
- **Axiom** (developer-friendly, generous free tier)

## Pre-launch checklist

- [ ] HTTP monitor on homepage (1-min interval)
- [ ] HTTP monitor on each critical page
- [ ] `/api/health` endpoint live + monitored
- [ ] Synthetic browser test on signup/checkout
- [ ] SSL expiry monitor active
- [ ] Domain expiry calendar reminder set
- [ ] Status page live (if applicable)
- [ ] Alerts route to correct channel by severity
- [ ] On-call rotation defined (even if solo)
- [ ] Runbook written for top 3 incident types

## Anti-patterns

- Monitoring only the homepage (specific routes break independently)
- One alert channel for all severities (alarm fatigue)
- 1-of-1 check rule (alerts on every transient blip)
- Health endpoint that requires auth (monitor can't hit it)
- Health endpoint that's expensive (DDoS yourself)
- No status page for B2B SaaS (loses customer trust during incidents)
- Forgotten domain renewal (worst-case scenario)

## Pricing notes (for proposals)

- Better Stack: free tier (10 monitors, 3-min interval); $25/mo for 1-min + status page
- UptimeRobot: free for 50 monitors at 5-min; $7+/mo for 1-min
- Checkly: free tier; $80+/mo for browser checks at scale
- Cloudflare Health Checks: $5/mo

For a $50K project: $25/mo for Better Stack covers everything.
