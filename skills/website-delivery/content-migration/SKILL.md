---
name: content-migration
description: Move content from an old site (any CMS or static HTML) into a new CMS — scrape, clean, transform, upload, and verify. Includes URL → URL mapping, asset rehost, and link rewriting. Use during a replatform when client has > 20 pages of existing content.
---

# Content Migration

The unsexy work that determines whether launch goes smoothly or becomes a
two-week debugging nightmare. Plan for migration to take 15–30% of the
total project budget on content-heavy sites.

## When to use

- Replatforming an existing site
- Consolidating multiple sites into one
- Rehosting assets (Webflow → Cloudinary, WP → S3)
- Significant URL restructure even within the same CMS

## Inputs

- Source: old site URL, CMS access (admin login or API token), or raw export
- Target: new CMS schemas + API token
- A spreadsheet of every URL on the old site (use Screaming Frog)
- Final sitemap of the new site
- Locked redirect map (old URL → new URL)

## Process

### 1. Audit the source

Crawl with Screaming Frog → CSV with: URL, title, H1, meta desc, status,
inlinks, outlinks, content type, word count.

Categorize:
- **Migrate as-is** — well-performing, evergreen content
- **Migrate + rewrite** — outdated tone, broken links, thin content
- **Consolidate** — multiple posts on the same topic (combine, redirect)
- **Retire** — low traffic, off-strategy (301 to closest topic)

### 2. Build the URL map

Spreadsheet columns:
| Old URL | Action | New URL | New template | Notes |
|---|---|---|---|---|
| /about-us | migrate | /about | page | rename |
| /blog/old-post-1 | migrate | /resources/blog/post-slug | post | rewrite intro |
| /services/seo | retire | /services | page | 301 to parent |
| /test-page | drop | (gone) | — | 410 |

Every row → either a 301, a 410, or a "migrate" action. **No URL is left
unaccounted for.**

### 3. Extract content

Pick the cheapest reliable method:

| Source | Best extraction |
|---|---|
| WordPress | WP REST API (`/wp-json/wp/v2/posts?per_page=100&page=N`) |
| Webflow | Webflow Data API (see `webflow-export-and-migrate`) |
| Contentful / Sanity | Native export |
| Static HTML | Cheerio / BeautifulSoup scrape |
| Squarespace / Wix | RSS feed + manual scrape (no APIs) |

Save raw content as JSON or NDJSON, **don't transform yet**. You'll iterate.

### 4. Transform

Per record, transform old fields → new schema fields. Example:
```ts
function transformPost(old) {
  return {
    _type: 'post',
    title: old.title.rendered,
    slug: { current: old.slug },
    publishedAt: old.date,
    excerpt: stripHtml(old.excerpt.rendered),
    body: htmlToPortableText(old.content.rendered),  // critical step
    author: { _ref: authorMap[old.author] },
    seo: {
      title: old.yoast_head_json?.title,
      description: old.yoast_head_json?.description,
      ogImage: old.yoast_head_json?.og_image?.[0]?.url,
    },
  }
}
```

**HTML body → block content / portable text** is the hardest step. Tools:
- Sanity: `@sanity/block-tools` + `JSDOM`
- Payload / generic Slate: custom HTML→Slate transform
- Markdown-based CMS: `turndown` (HTML → MD)

### 5. Asset migration

For every image / video / PDF in the old content:
1. Download from old URL
2. Upload to new asset host
3. Build a map: `oldAssetUrl → newAssetUrl`
4. Rewrite all references in transformed content

Script template:
```ts
async function migrateAsset(url: string) {
  const res = await fetch(url)
  const buf = await res.arrayBuffer()
  const { _id, url: newUrl } = await sanity.assets.upload('image', Buffer.from(buf), {
    filename: path.basename(url),
  })
  assetMap.set(url, { _id, newUrl })
  return _id
}
```

### 6. Link rewriting

For every internal link in body content:
- Look up old URL in URL map → replace with new URL
- If old URL is in retired list → drop the link or redirect-rewrite
- Make external links open in new tab (consistent UX)

### 7. Upload to new CMS

Batch upload via the target CMS's import API. Always:
- Validate against schema first (reject invalid records, log them)
- Use idempotent IDs (so re-running doesn't duplicate)
- Run on a staging dataset, not production
- Sanity check counts: `imported === expected`

### 8. Verify

- Random spot-check 20 migrated pages: do they render correctly?
- Run Screaming Frog on the new site: every page returns 200, links don't 404
- Diff sitemap: every old URL → has redirect or migrated equivalent
- Check images aren't broken (oversights in asset map)

## Re-running the migration

Migrations always need 2–5 runs:
- Run 1: discover edge cases
- Run 2: handle them
- Run 3: handle the next batch
- Run N: production cutover

Make scripts **idempotent and incremental**:
- Use `_id` based on a hash of source URL (re-runs update, don't duplicate)
- Add `--since=2025-01-01` flag to only fetch new/updated source records
- Log all failures to a CSV for human review

## Cutover day plan

1. Final incremental sync (4–6 AM, low traffic)
2. Verify counts match
3. Lock the old CMS (read-only)
4. Cut DNS to new site (see `go-live-runbook`)
5. Apply redirect rules
6. Smoke-test top 20 pages + checkout
7. Submit new sitemap to Search Console

## Common gotchas

- **Smart quotes / em dashes**: HTML entities mishandled in transformation
- **Inline styles in body**: WordPress / Wix inject `<span style="...">`
  — strip during HTML→portable text conversion
- **Embedded iframes** (YouTube, etc.): preserve, but switch to your block
  type if you have one
- **Shortcodes** (WordPress `[gallery]`, etc.): expand server-side before
  migration or build custom blocks
- **Authors that don't exist**: pre-create author records in target CMS,
  build a map
- **Multi-language**: extract per-locale, link translations explicitly

## Anti-patterns

- "We'll migrate manually" for > 20 pages (always scope-creeps)
- Migrating without a redirect map (catastrophic SEO loss)
- Not migrating assets (you'll be hot-linking from a domain you no longer own)
- One mega-script with no error log (fails silently on edge cases)
- Migrating directly to production (no rollback)
- Skipping the diff/spot-check step
- Cutting over before search engines have re-indexed (do post-launch audit)

## Tools

- **Crawl**: Screaming Frog (free under 500 URLs), Sitebulb
- **HTML extraction**: Cheerio (Node), BeautifulSoup (Python)
- **HTML → Markdown**: Turndown
- **Bulk asset transfer**: rclone, AWS DataSync, custom script

## Pricing notes (for proposals)

Quote migration as a **separate, fixed-fee line item**:
- 0–50 pages: $3K–6K
- 50–500 pages: $8K–20K
- 500+ pages: hourly + buffer
- Add 20–30% if asset rehost is required
