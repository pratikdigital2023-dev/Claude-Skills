---
name: edge-caching-strategy
description: Design the cache layer for a modern site — CDN cache rules, ISR / SSG / SSR / RSC trade-offs, cache tags + on-demand revalidation, stale-while-revalidate, and per-route cache TTLs. Use when planning architecture for any traffic > a few hundred visits/day.
---

# Edge Caching Strategy

The right cache strategy makes a $50K site feel instant for users and
cheap to run. The wrong one serves stale prices to checkout, or hits the
origin on every request and bills you 1000x more than necessary.

## When to use

- New site architecture decisions
- Site has dynamic + static content (most do)
- Origin compute or DB cost is climbing
- Pages are slow despite small payloads (cache misses)

## Mental model

Three caches, in order:
1. **Browser cache** — the user's machine
2. **Edge / CDN cache** — Cloudflare / Vercel Edge / Fastly POPs
3. **Origin cache** — your app's in-memory or Redis

Each layer reduces requests to the next. Optimize from the user out.

## Per-route strategy

Pick one of these for every route. Don't blanket-apply.

| Strategy | Use for | Cache TTL | Revalidation |
|---|---|---|---|
| **Static (SSG)** | Marketing pages, blog | At build time | On rebuild |
| **ISR** | CMS-driven pages | 60–600s + on-demand | Webhook on publish |
| **Stale-while-revalidate** | Personalized but cacheable | 60s + revalidate background | Async |
| **SSR (no cache)** | Per-user dashboards | none | n/a |
| **RSC streaming** | Mixed static + dynamic | hybrid | per segment |
| **Static asset (immutable)** | JS/CSS/fonts/images | 1 year + content hash | content hash change |
| **Edge function** | Geo / A/B / rewrite | 0 (compute), but result is cached | varies |

## Next.js App Router specifics

Each route by default:
- **Server components**: cached unless they fetch with `no-store`
- **`fetch()` calls**: cached by default (`{ next: { revalidate: 60 } }`)
- **Dynamic functions** (`cookies()`, `headers()`): opt route into dynamic

Force a cache strategy:
```ts
// app/products/[slug]/page.tsx
export const revalidate = 300  // ISR every 5 min
// OR
export const dynamic = 'force-dynamic'  // never cache
// OR
export const dynamic = 'force-static'   // SSG, fail at build if dynamic
```

## On-demand revalidation (ISR + tags)

This is the killer feature. Tag fetches:
```ts
const data = await fetch(`${CMS}/api/page/${slug}`, {
  next: { tags: ['page', `page:${slug}`], revalidate: 600 },
})
```

Webhook from CMS triggers revalidation:
```ts
// app/api/revalidate/route.ts
import { revalidateTag, revalidatePath } from 'next/cache'

export async function POST(req: Request) {
  const { slug, type } = await req.json()
  if (type === 'page') {
    revalidateTag(`page:${slug}`)
    revalidatePath(`/${slug}`)
  } else if (type === 'global') {
    revalidateTag('page')  // nuke all pages
  }
  return Response.json({ ok: true })
}
```

## Cache headers

Set explicit headers for static assets:
```ts
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/_next/static/:path*',
        headers: [{ key: 'Cache-Control', value: 'public, max-age=31536000, immutable' }],
      },
      {
        source: '/api/:path*',
        headers: [{ key: 'Cache-Control', value: 'no-store' }],
      },
    ]
  },
}
```

For HTML pages, Vercel + Next handles this. On Cloudflare Pages or
self-hosted, set `s-maxage` (CDN) and `max-age` (browser):
```
Cache-Control: public, s-maxage=3600, max-age=0, stale-while-revalidate=60
```

- `s-maxage`: CDN caches 1 hour
- `max-age=0`: browser revalidates on each visit
- `stale-while-revalidate=60`: serve stale up to 60s while refetching

## Cloudflare cache rules

If using Cloudflare, configure cache rules in the dashboard:
- **Cache static assets aggressively**: `*.{js,css,woff2,jpg,webp,avif,svg}`
  → Edge TTL 1 month, browser 1 day
- **Cache HTML conditionally**: based on query string + cookie absence
- **Bypass cache for**: `/api/*`, `/checkout/*`, anything with `Cookie` containing session

## Vary headers

If the response differs per condition, declare it:
```
Vary: Accept-Encoding, Accept-Language, Cookie
```

Without Vary, the CDN can serve gzip to a non-supporting client, or
English to a German user, or one user's session to another.

## Personalization without breaking cache

Patterns:
- **Edge personalization**: rewrite at the edge based on geo/cookie, but
  serve cached HTML for each variant (e.g., A/B branches as 2 cache keys)
- **Client-side personalization**: render shell, hydrate user data via API
- **Streaming RSC**: cache static segments, stream dynamic ones
- **ESI / fragment caching**: assemble cached fragments per request (Fastly)

## Cache invalidation patterns

The hard part of caching. Approaches:
- **Tag-based** (Next ISR, Cloudflare Cache Tags) — best
- **URL-based** (`revalidatePath`) — simple but blunt
- **Soft purge / SWR** — serve stale while fetching fresh
- **Hard purge** — only on disasters; warms slowly

Always test that publishing in CMS invalidates the right pages. This is
the #1 thing that breaks silently.

## Cost optimization

Edge caching dramatically reduces:
- Origin compute (most pages never hit your function)
- Database queries (cached responses include their data)
- Bandwidth (compressed at edge)
- Image transforms (CDN caches them)

For a marketing site at 100K visits/mo:
- Without caching: $100–500/mo origin
- With ISR + 60s revalidate: $5–20/mo origin

## Per-environment

- **Production**: aggressive caching, on-demand revalidation
- **Staging**: short TTLs (10s) so devs see changes fast
- **Preview** (Vercel): no cache by default, fine for review

Use env vars to flip TTLs per env.

## Pre-launch checklist

- [ ] Every route has an explicit caching decision documented
- [ ] Static assets sent with `Cache-Control: immutable`
- [ ] HTML pages have appropriate `s-maxage` + `stale-while-revalidate`
- [ ] CMS webhook → `/api/revalidate` works end to end
- [ ] Cache hit rate > 80% on top 10 pages (test with `curl -I`)
- [ ] Vary headers correct for personalized responses
- [ ] Checkout/auth routes explicitly NOT cached
- [ ] Query params don't fragment cache (canonical or strip irrelevant)
- [ ] Origin can survive 10x normal traffic (cache failure scenario)

## Anti-patterns

- One blanket `Cache-Control` for the whole site (everything stale or never cached)
- Caching authenticated responses (security disaster — leaks user data)
- Setting `s-maxage` on the same response with `Set-Cookie` (Cloudflare won't cache)
- Forgetting Vary on `Accept-Encoding` (mixed gzip/identity served)
- ISR with no on-demand revalidation (60s+ stale after publish)
- Hammering origin on every cache miss (use SWR or a backing cache)
- Long browser cache on HTML (users see stale page after deploy)

## Pricing notes (for proposals)

CDN caching is mostly free with modern hosts:
- **Vercel**: included; pay for bandwidth + function invocations
- **Cloudflare**: free for most use cases; $25/mo Pro for advanced rules
- **Fastly**: $50+/mo, most powerful but expensive

For $50K projects: stick with Vercel default + Cloudflare in front for DNS
+ WAF.
