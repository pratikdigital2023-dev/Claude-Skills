---
name: cookie-consent
description: Implement a compliant cookie consent banner with GTM Consent Mode v2, granular categories, geo-targeted display, and event-driven script blocking. Covers Cookiebot, Osano, and self-hosted alternatives. Use on any site that targets EU/UK/CH/Brazil users or runs ads in California.
---

# Cookie Consent

Most sites get this wrong: a "Got it" button on page load doesn't satisfy
GDPR, ePrivacy, or California's CPRA. Done correctly, consent unblocks
analytics + ads while keeping you out of regulator scope.

## When to use

- Any site with EU/UK/Switzerland/Brazil traffic
- California sites running ad networks or selling data
- Sites loading any third-party scripts (GA4, Meta Pixel, Hotjar, etc.)
- Replacing a non-compliant "this site uses cookies" banner

## Decision: vendor or self-host

| Option | Strength | Weakness |
|---|---|---|
| **Cookiebot** | Most mature, geo-targeted, scanner | $11–$50/mo per site |
| **Osano** | Strong UX, free tier (5K visits) | Smaller scanner DB |
| **OneTrust** | Enterprise-grade, IAB TCF integrated | Heavy, expensive |
| **Iubenda** | Includes legal docs, multi-language | Cluttered admin |
| **Self-hosted (Klaro / cookieconsent.js)** | No vendor cost, full control | You own legal compliance + updates |

For a $50K project: **Cookiebot** unless client specifies otherwise. Use a
self-hosted lib only if budget is tight and the client accepts ownership.

## Required categories (GDPR / CPRA)

| Category | Default | Examples |
|---|---|---|
| **Strictly necessary** | Always on (no consent needed) | Session, CSRF, language pref |
| **Functional** | Off until opt-in | Live chat, embedded video remember-me |
| **Analytics** | Off until opt-in | GA4, Hotjar, Plausible (most), Sentry session replay |
| **Marketing / advertising** | Off until opt-in | Meta Pixel, Google Ads, LinkedIn Insight |

Each category requires:
- A description in plain language
- A list of the specific cookies / scripts in that category
- A toggle to opt in / out
- A "Save preferences" button (not just "Accept all")

## Banner UX rules (regulator-tested)

- **"Reject all" must be as prominent as "Accept all"** — same size, position,
  weight (CNIL, ICO, EDPB all enforce this)
- **No pre-ticked boxes** for non-essential
- **Granular controls accessible without scrolling**
- **Persistent settings access** (a footer link or floating cog icon)
- **Re-prompt every 12 months** (or sooner if you add new cookies)

## Google Consent Mode v2 (mandatory for Google Ads in EEA)

Without Consent Mode v2, your Google Ads remarketing in EEA stopped working
in March 2024. Required signals:

```js
gtag('consent', 'default', {
  'ad_storage': 'denied',
  'ad_user_data': 'denied',          // v2
  'ad_personalization': 'denied',    // v2
  'analytics_storage': 'denied',
  'functionality_storage': 'denied',
  'personalization_storage': 'denied',
  'security_storage': 'granted',
  wait_for_update: 500,
})
```

Then on consent change:
```js
gtag('consent', 'update', {
  'ad_storage': consent.marketing ? 'granted' : 'denied',
  'analytics_storage': consent.analytics ? 'granted' : 'denied',
  // ...etc
})
```

Cookiebot and Osano emit this automatically. If self-hosting, do it manually.

## Script blocking pattern

Don't load tracking scripts until consent is given. With GTM:
- Set GA4, Meta, etc. tags to fire on **custom event** triggers
- The consent banner pushes `consent_given` events to dataLayer
- Tags fire only when the matching event arrives

Without GTM:
```tsx
// app/components/Analytics.tsx
'use client'
import { useConsent } from '@/lib/consent'
import Script from 'next/script'

export function Analytics() {
  const { analytics } = useConsent()
  if (!analytics) return null
  return (
    <Script src="https://www.googletagmanager.com/gtag/js?id=G-XXX" strategy="afterInteractive" />
  )
}
```

## Geo-targeted display

Best practice: show the banner to **all users**, but pre-select different
defaults by region. EU/UK/CH: opt-in (everything off). US: opt-out
(analytics on by default, toggle to disable).

If you must geo-gate the banner entirely:
- IP geolocation via Cloudflare's `CF-IPCountry` header or Vercel's
  `request.geo.country` (Edge runtime)
- Cache the result for the session

## Server-side rendering

Render a minimal placeholder server-side, hydrate the real banner client-side
based on stored consent. Avoid layout shift — reserve space.

## Storing consent

- **Cookie**: `consent={"analytics":1,"marketing":0,"ts":1234567890}` —
  set Secure, HttpOnly only if you don't need JS access (most banners need
  JS access; use SameSite=Lax)
- **localStorage**: only if you don't need server-side awareness
- **Server record**: required if you need an audit trail (GDPR Art 7.1)

## Audit trail (GDPR requirement)

You must be able to prove someone consented. Log:
- Timestamp
- IP (hashed) or session ID
- Consent string (which categories accepted)
- Banner version shown
- User-agent

Cookiebot / Osano store this for you. Self-hosted: write to your DB.

## Cookie scanner

A scanner crawls your site and identifies cookies/scripts in use. Run
weekly. Cookiebot, Osano include scanners. Manual fallback: open DevTools
→ Application → Cookies on each page type.

Maintain a **cookie register** doc with one row per cookie:
| Cookie | Purpose | Provider | Type | Duration | Category |
|---|---|---|---|---|---|

## Privacy / cookie policy

The banner must link to a Cookie Policy that lists every cookie. This
should auto-generate from your scanner. See `privacy-policy-and-tos-generator`.

## Pre-launch checklist

- [ ] Banner shows on first visit with no scripts pre-loaded
- [ ] "Reject all" is as prominent as "Accept all"
- [ ] Granular toggles work; settings save
- [ ] Re-opening preferences is possible from footer
- [ ] Consent Mode v2 signals fire correctly (test in GTM debug)
- [ ] No tracking scripts load before consent
- [ ] Cookie policy lists every cookie in use
- [ ] Audit trail / consent log is being recorded
- [ ] Tested on EU IP (if geo-gating) — VPN check
- [ ] Re-prompt rule set (12 months default)

## Anti-patterns

- "Accept" is large and green; "Reject" is a tiny grey link (illegal in EU)
- Pre-ticked checkboxes for analytics/marketing
- Loading GA4 / Meta Pixel before consent fires (most common violation)
- "By using this site you agree" implied consent (not consent under GDPR)
- No way to change preferences after the first click
- Cookie wall ("accept or leave the site") — illegal in most EU member states
- Granular settings hidden behind 3 clicks

## Pricing notes (for proposals)

- Cookiebot: free for < 100 subpages; $11+/mo otherwise
- Osano: free for < 5K visits/mo
- OneTrust: $7K+/yr (only if client demands)
- Self-hosted: 0 license, 4–8 hours of dev to wire correctly
