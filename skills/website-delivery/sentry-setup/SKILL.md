---
name: sentry-setup
description: Wire Sentry into a frontend + backend stack for error tracking, performance tracing, source maps, release tracking, and PII-safe session replay. Use on any production site to catch what users see (and don't report).
---

# Sentry Setup

Sentry catches the bugs users hit but never report. Without it, your error
floor is "tickets in inbox" — usually a small fraction of actual issues.
With it: every error, with stack trace, browser, OS, and reproduction trail.

## When to use

- Every production deployment (always)
- After a launch where users report issues you can't reproduce
- When you need release health metrics (% of sessions with errors)
- Migrating from another error tracker (Bugsnag, Rollbar, LogRocket)

## Decision: which tier

| Tier | When |
|---|---|
| Free | < 5K errors/mo, single user — POC only |
| Team ($26/mo) | Most $50K projects, up to ~50K events |
| Business ($80/mo) | Multi-project, performance + replay quotas |

## Setup (Next.js — App Router)

```bash
npx @sentry/wizard@latest -i nextjs
```

The wizard creates:
- `sentry.client.config.ts` (browser)
- `sentry.server.config.ts` (Node runtime)
- `sentry.edge.config.ts` (Edge runtime)
- Updates `next.config.js` with `withSentryConfig`
- Adds source map upload step

### Client config
```ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_VERCEL_ENV,  // production / preview / development
  release: process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA,
  tracesSampleRate: 0.1,            // 10% of transactions for tracing
  replaysSessionSampleRate: 0.1,    // 10% of sessions for replay
  replaysOnErrorSampleRate: 1.0,    // 100% of sessions with errors
  integrations: [
    Sentry.replayIntegration({
      maskAllText: true,
      blockAllMedia: true,
      mask: ['.sensitive', '[data-private]'],
    }),
  ],
  beforeSend(event) {
    // Strip PII from error messages
    if (event.user) {
      delete event.user.ip_address
      delete event.user.email
    }
    return event
  },
  ignoreErrors: [
    'ResizeObserver loop limit exceeded',
    'Non-Error promise rejection captured',
    /chrome-extension/,
    /Script error\.?/,
  ],
})
```

### Server config (similar, no replay)
```ts
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.VERCEL_ENV,
  release: process.env.VERCEL_GIT_COMMIT_SHA,
  tracesSampleRate: 0.1,
  beforeSend(event) {
    // strip secrets, headers, body if needed
    return event
  },
})
```

## Releases + source maps

The wizard sets up `@sentry/webpack-plugin` to upload source maps on build.
Verify:
- Source maps are NOT served to users (deleted from `.next/static/...` in prod)
- Sentry receives them (check Project → Releases → Files)
- Errors show readable stack traces (TypeScript file + line, not minified)

For Vercel: source maps are uploaded via the Sentry Vercel integration
(install in Sentry → Settings → Integrations → Vercel).

## Error grouping

Sentry auto-groups errors. To improve:
- **`fingerprint`** in `Sentry.captureException` to merge similar errors
- Use `Sentry.setContext`, `setTag`, `setUser` for filtering
- Custom error classes preserve `.name` for grouping

```ts
try { doThing() } catch (e) {
  Sentry.captureException(e, {
    tags: { feature: 'checkout' },
    extra: { orderId: id, userId: user.id },
  })
}
```

## User context (PII-aware)

```ts
Sentry.setUser({ id: user.id })  // never email/name in prod
```

For B2B, send Org ID as a tag for cross-customer triage:
```ts
Sentry.setTag('org_id', user.orgId)
```

## Performance / tracing

Sentry traces requests across the stack: client → server → DB. Out of the
box in Next.js, you get:
- Page load + navigation transactions
- API route transactions
- Database queries (with Prisma instrumentation)
- External API calls

Tune `tracesSampleRate`:
- 0.01–0.1 for high-traffic prod
- 1.0 for staging / low-traffic prod

Custom traces:
```ts
await Sentry.startSpan({ name: 'checkout.fulfill', op: 'biz' }, async () => {
  await fulfillOrder(...)
})
```

## Session replay

Records DOM mutations + console + network during user session. Replays
errors with exact reproduction.

**Privacy is critical**:
- `maskAllText: true` (default after recent versions)
- `blockAllMedia: true` (don't capture user-uploaded images)
- Mark sensitive components: `<div data-private>...</div>`
- Mask credit card / password inputs (`type=password` is auto)
- Disable replay for unauthenticated users if you don't need it

For sites handling health / financial data: **disable replay or get DPA
sign-off**.

## Alerts

Set up in Sentry → Alerts:
- **High-severity issues** → Slack #engineering immediately
- **Spike detection** — error rate doubles → page on-call
- **Performance regression** — p95 LCP > 3s → PR comment
- **Release health** — < 95% crash-free sessions → block promotion

## Release health

Tag every deploy with the commit SHA. Sentry tracks:
- Sessions on each release
- Crash-free session rate
- Time to detect new errors

Combined with Vercel, "what release introduced this?" becomes one click.

## Privacy + compliance

- Sentry is a data processor under GDPR — sign their DPA
- US data residency: choose `https://sentry.io` (US) vs. `de.sentry.io` (EU)
- Strip PII via `beforeSend`
- Document Sentry as a processor in your privacy policy
- For GDPR: don't capture `req.body` on auth routes

## Environment hygiene

- **Different DSNs** per environment — never send dev errors to prod
- **Filter local dev**: don't init in dev unless debugging
- **Sample rates by env**: 1.0 in staging, 0.1 in prod

## Pre-launch checklist

- [ ] DSNs configured per environment
- [ ] Source maps uploading (errors show readable traces)
- [ ] PII stripped in `beforeSend`
- [ ] Replay configured with masking
- [ ] User context set (ID only)
- [ ] Release tag set to commit SHA
- [ ] Slack / email alerts configured
- [ ] Privacy policy lists Sentry as a processor
- [ ] Common noise filtered (`ignoreErrors`)
- [ ] Performance budget alert configured

## Anti-patterns

- One DSN across all environments (prod alerts polluted with dev noise)
- Capturing user emails / passwords / payment in `extra` (PII leak)
- 100% sample rate in prod (eats quota in days)
- Source maps publicly served (exposes original code)
- `console.error` calls Sentry-wrapped without context (low signal)
- Ignoring all errors as "noise" without grouping/filtering
- No release tagging (can't correlate errors with deploys)

## Pricing notes (for proposals)

- Team: $26/mo, includes 50K errors + 100K transactions + 500 replays
- Business: $80/mo, larger quotas + advanced features
- Self-hosted Sentry: free but 4–8 hours of setup + ongoing maintenance

For a $50K project: budget Team plan ($26/mo) for the first 6 months;
upgrade if quota hit.
