---
name: redirect-map-builder
description: Audit an existing site's URLs and produce a complete redirect map (old → new) for migration — 301s, 410s, regex rules, and the actual redirect file format for Vercel / Cloudflare / nginx / Netlify. Use whenever URLs change in a migration.
---

# Redirect Map Builder

A migration that doesn't preserve URL value loses 30–80% of organic search
traffic in the first 3 months. The redirect map is the single most
important artifact for protecting SEO during a relaunch.

## When to use

- Replatforming (CMS or framework change)
- Restructuring URL taxonomy on an existing site
- Consolidating multiple sites
- Domain change (acquisition, rebrand)

## Inputs

- Source URLs: every URL on the old site
- Target URLs: the new site's sitemap
- Decisions: which old URLs become which new URLs
- Categories: migrate, redirect-to-parent, retire (410)

## Step 1: extract every old URL

Best to most fallible:
1. **Server access logs** — actual URLs users hit (last 90 days)
2. **CMS export** — DB dump of every published URL
3. **Sitemap.xml** — what the site claims it has
4. **Crawl** — Screaming Frog or Sitebulb

Combine all three. The union is your **complete URL inventory**.

```bash
# Crawl with Screaming Frog (CLI)
screamingfrogseospider --crawl https://acme.com --headless \
  --export-tabs "Internal:All" --output-folder ./crawl

# Or via curl + sitemap
curl -s https://acme.com/sitemap.xml | xmllint --xpath '//*[local-name()="loc"]/text()' - > old-urls.txt
```

Add log-based URLs:
```bash
awk '{print $7}' access.log | sort -u > log-urls.txt
cat old-urls.txt log-urls.txt | sort -u > all-old-urls.txt
```

## Step 2: classify each URL

Spreadsheet columns:
| Old URL | Action | New URL | Status code | Notes |
|---|---|---|---|---|
| /about-us | redirect | /about | 301 | rename |
| /services/seo-audit | redirect | /services/seo | 301 | consolidate |
| /old-promo-2022 | gone | — | 410 | dead campaign |
| /admin | gone | — | 410 | should never have been public |
| /blog/2022/01/post-slug | redirect | /resources/blog/post-slug | 301 | restructure |
| /products/abc?utm=x | n/a | n/a | n/a | strip query, redirect to canonical |

### Decision rules
- **Migrate**: still relevant, has traffic / backlinks → 301
- **Consolidate**: similar content elsewhere → 301 to canonical
- **Retire**: no traffic, no backlinks, no value → 410
- **Block**: was never meant to be public → 410 + remove from sitemap

## Step 3: prioritize

Sort by traffic + backlinks. Get the top 50 perfect; eyeball the next 500;
catch-all the long tail.

```bash
# Match URLs with GA4 / Search Console export to add traffic column
# csvkit: csvjoin --left -c url all-old-urls.csv ga4-export.csv > prioritized.csv
```

## Step 4: build the redirect file

### Vercel / Next.js (`next.config.js`)
```js
module.exports = {
  async redirects() {
    return [
      // Specific renames
      { source: '/about-us', destination: '/about', permanent: true },
      { source: '/services/seo-audit', destination: '/services/seo', permanent: true },

      // Pattern: /blog/YYYY/MM/slug → /resources/blog/slug
      {
        source: '/blog/:year(\\d{4})/:month(\\d{2})/:slug',
        destination: '/resources/blog/:slug',
        permanent: true,
      },

      // Wildcard category move
      { source: '/articles/:slug*', destination: '/resources/articles/:slug*', permanent: true },
    ]
  },
}
```

For 410s in Next: respond from a route handler:
```ts
// app/old-promo-2022/page.tsx
export default function Gone() { return <div>Page no longer available</div> }
export const metadata = { robots: { index: false } }
// Set status: use middleware or `notFound()` won't return 410. For 410:
export const dynamic = 'force-dynamic'
// In middleware.ts, return new Response(null, { status: 410 }) for matching paths
```

### Cloudflare (Bulk Redirects)
1. Cloudflare → Rules → Redirect Rules → Bulk Redirects
2. Create a list (CSV: source, target, status code)
3. Apply to your zone

```csv
URL,Target URL,Status code,Preserve query string,Preserve path
https://acme.com/about-us,https://acme.com/about,301,false,false
https://acme.com/services/seo-audit,https://acme.com/services/seo,301,false,false
```

Cloudflare supports up to 5M redirects per account on Pro+ plans.

### Netlify (`_redirects` file)
```
/about-us              /about              301
/services/seo-audit    /services/seo       301
/blog/:year/:month/:slug   /resources/blog/:slug   301
/articles/*            /resources/articles/:splat   301
/old-promo-2022        -                   410
```

### nginx
```
rewrite ^/about-us$           /about              permanent;
rewrite ^/services/seo-audit$ /services/seo       permanent;
rewrite ^/blog/(\d{4})/(\d{2})/(.+)$ /resources/blog/$3 permanent;
location = /old-promo-2022 { return 410; }
```

### Apache (`.htaccess`)
```
Redirect 301 /about-us /about
Redirect 301 /services/seo-audit /services/seo
RedirectMatch 301 ^/blog/\d{4}/\d{2}/(.+)$ /resources/blog/$1
RedirectMatch 410 ^/old-promo-2022$
```

## Step 5: avoid redirect chains

A redirect chain (A→B→C) loses SEO value at each hop and slows users.

Bad:
```
/about-us → /company → /about
```

Good:
```
/about-us → /about
/company  → /about
```

Audit by feeding the redirect map into itself: every source URL's
destination must NOT also be a source URL.

## Step 6: handle query strings + trailing slashes

Decisions to make once and apply consistently:
- Trailing slash policy: `/about` or `/about/` (pick one, redirect the other)
- Query strings on legacy URLs: strip irrelevant ones (utm_*, fbclid, etc.) ?
- Capitalized URLs: `/About-Us` → 301 to lowercase

Vercel / Next has `trailingSlash` config to enforce one variant globally.

## Step 7: test

Before launch, hit every redirect:
```bash
# Read CSV, curl each, check status + final destination
while IFS=, read -r src dst expected; do
  actual_status=$(curl -s -o /dev/null -w "%{http_code}" -I "https://acme.com$src")
  actual_final=$(curl -s -o /dev/null -w "%{redirect_url}" -L "https://acme.com$src")
  echo "$src -> $actual_final ($actual_status, expected $expected)"
done < redirects.csv > test-results.txt
```

Or use **httpstatus.io** (web tool) — paste up to 100 URLs, see status codes.

## Step 8: monitor post-launch

Daily for first 2 weeks:
- Search Console → Crawl Errors → look for 4xx / 5xx
- Check most-trafficked old URLs are still hitting expected new URLs
- Watch organic traffic — small dip (5–15%) is normal short-term, anything
  bigger means redirects are wrong

## Common gotchas

- **Server vs. proxy redirects** — if Cloudflare AND your origin both have
  redirect rules, the first one fires (often unexpectedly)
- **Case sensitivity** — `/About` vs `/about`; nginx is case-sensitive by default
- **Trailing slash mismatch** — single redirect rule may not match both
- **Protocol** — make sure `http` → `https` happens before redirect logic
- **Subdomain redirects** — `www` → apex (or vice versa) needs its own rule
- **Encoded characters** — `/résumé` vs `/r%C3%A9sum%C3%A9`

## Pre-launch checklist

- [ ] Every URL on old site categorized (migrate / consolidate / retire)
- [ ] Top 100 URLs by traffic perfectly mapped
- [ ] Redirect file generated for the target host
- [ ] No redirect chains (every source → final destination, one hop)
- [ ] Tested 100% of redirects (script above)
- [ ] 410s actually return 410 (not 404 or soft 404)
- [ ] Trailing slash + case + protocol normalized
- [ ] `sitemap.xml` regenerated with only new URLs
- [ ] Search Console change-of-address filed (if domain changing)

## Anti-patterns

- Catch-all `/*` → `/` (kills all old URLs into one page; SEO disaster)
- Skipping 410s ("just let them 404") — soft 404s are penalized
- 302 (temporary) instead of 301 (permanent) — SEO equity not transferred
- Loops (A → B → A)
- Rule order ambiguity (broad rule shadowing specific rule above it)
- No regression test post-launch
- Forgetting `www` and protocol variants

## Tools

- **Crawl**: Screaming Frog, Sitebulb, Ahrefs Site Audit
- **Bulk test**: httpstatus.io, custom curl script
- **Backlink discovery**: Ahrefs / SEMrush — find URLs with external links
  you must preserve
- **GSC**: Coverage report → flags missing redirects after launch
