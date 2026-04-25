---
name: webflow-export-and-migrate
description: Migrate a site off Webflow to a code-based stack (Next.js / Astro), or extract Webflow's CMS content + design tokens into a portable format. Use when the client has outgrown Webflow's pricing/features but loves the design.
---

# Webflow Export & Migrate

Webflow is great until: pricing scales (Site Plans + CMS items), the team
needs custom backend logic, or the marketing team wants Git-based workflows.
This skill covers extracting both the **design** and the **content**.

## When to use

- Client wants to move off Webflow due to cost or limits
- Migrating Webflow CMS content into Sanity / Contentful / Payload
- Reproducing a Webflow design in code while keeping CMS in Webflow
- Avoid this if: client is happy with Webflow and the site fits its limits

## Two extraction paths

### Path A: HTML/CSS export (design only)
- Webflow Settings → Export Code → ZIP
- Get static HTML, CSS, JS, and assets for static pages
- **Doesn't include CMS-driven pages** (those need API extraction)
- Useful as a reference, not as a deployable artifact

### Path B: CMS export via Data API
For collections (CMS items), use the Webflow Data API:
```bash
curl -X GET https://api.webflow.com/v2/collections/{COLLECTION_ID}/items \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "accept: application/json"
```

Returns JSON with all fields. Iterate through every collection, paginate
(100 items / page max), save to disk.

## Migration script template (Node)

```ts
// scripts/migrate-webflow.ts
import { writeFile, mkdir } from 'fs/promises'
import { WebflowClient } from 'webflow-api'

const wf = new WebflowClient({ accessToken: process.env.WEBFLOW_TOKEN })
const SITE_ID = process.env.WEBFLOW_SITE_ID

async function exportAll() {
  await mkdir('./webflow-export', { recursive: true })
  const collections = await wf.collections.list({ siteId: SITE_ID })

  for (const c of collections.collections) {
    const items: any[] = []
    let offset = 0
    while (true) {
      const page = await wf.collections.items.listItems(c.id, { offset, limit: 100 })
      items.push(...page.items)
      if (page.items.length < 100) break
      offset += 100
    }
    await writeFile(`./webflow-export/${c.slug}.json`, JSON.stringify(items, null, 2))
    console.log(`✓ ${c.displayName}: ${items.length} items`)
  }

  const assets = await wf.assets.list(SITE_ID)
  await writeFile('./webflow-export/_assets.json', JSON.stringify(assets, null, 2))
}
exportAll().catch(console.error)
```

## Asset migration

Webflow hosts assets on `uploads-ssl.webflow.com`. To migrate:
1. Download every asset URL from `_assets.json`
2. Upload to your new asset host (Sanity CDN, Cloudinary, S3+CloudFront)
3. Build a URL-rewrite map: `oldUrl → newUrl`
4. Apply the map to every CMS field that contains an asset URL

## Design token extraction

Webflow doesn't export tokens directly. Approach:
1. Open published site in browser DevTools
2. Inspect computed styles on representative elements
3. Document into a tokens file:
```json
{
  "color": { "brand": "#1a1a1a", ... },
  "spacing": { "1": "0.25rem", ... },
  "fontSize": { "h1": "3.5rem", ... }
}
```
4. Feed into `figma-to-code-handoff` or `tailwind.config.ts`

For complex sites, **rebuild from the Figma source of truth** (if available)
rather than reverse-engineering CSS — faster and cleaner.

## Frontend rebuild strategy

For each Webflow page:
| Page type | Strategy |
|---|---|
| Static marketing | Rebuild as React/Astro components |
| CMS-driven (blog, case studies) | Migrate to new CMS, build templates |
| Forms | Replace Webflow Forms with React Hook Form + your ESP/CRM webhook |
| E-commerce | Migrate to Shopify or Stripe (Webflow Ecom is limited) |
| Memberships | Replace Webflow Memberships with Clerk / Auth.js + DB |

## Redirect map (critical)

Webflow's default URLs follow `/{collection-slug}/{item-slug}`. If you change
either in the new system, build a 301 map for every URL.

Use Webflow's sitemap.xml as the source:
```bash
curl https://yoursite.webflow.io/sitemap.xml > old-sitemap.xml
# parse → CSV → diff against new sitemap → generate redirect rules
```

Hand off to `redirect-map-builder` for the redirect file format.

## SEO preservation checklist

- [ ] Every old URL has a 301 to the new equivalent
- [ ] Meta titles + descriptions migrate field-by-field
- [ ] Canonical tags point to new URLs
- [ ] OG images migrate (don't 404)
- [ ] Schema/JSON-LD reproduced on new templates
- [ ] `robots.txt` + `sitemap.xml` regenerated
- [ ] Submit new sitemap to Search Console immediately after launch

## Webflow-specific gotchas

- **Embed code blocks**: Webflow lets editors paste raw HTML. These need
  manual review before migration — they often contain inline styles.
- **Interactions / animations**: not portable. Rebuild in Framer Motion or
  CSS (see `motion-design-patterns`).
- **Symbols**: convert to React components 1:1.
- **Conditional visibility**: rebuild as conditional rendering on server.
- **Localized sites**: Webflow's Localization is a separate plan — export
  per locale and merge.

## Cutover plan

1. Build full new site on staging (own subdomain or Vercel preview)
2. Migrate CMS content (run script weekly until launch to catch new edits)
3. Run final content sync the morning of launch
4. Update DNS to point at new host (see `dns-ssl-cdn-setup`)
5. Cancel Webflow Site Plan only after 30+ days of monitoring
   (you may need to roll back)

## Anti-patterns

- Exporting HTML and treating it as production code
- Migrating without a redirect map (instant SEO disaster)
- Forgetting form integrations (Webflow Forms → your CRM)
- Skipping interactions, then "we'll add them back later" (never happens)
- Cancelling Webflow on day 1 of launch (no rollback path)

## Pricing notes (for proposals)

Webflow → headless migration is typically 60–120 hours for a 30-page site.
Quote the **content migration script** as a separate line item — it's
reusable infrastructure.
