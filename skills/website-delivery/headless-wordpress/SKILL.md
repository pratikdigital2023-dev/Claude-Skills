---
name: headless-wordpress
description: Run WordPress as a headless CMS feeding a modern frontend (Next.js / Astro) via WPGraphQL or REST. Covers ACF integration, preview, ISR, plugins to install/avoid, and hosting. Use when the client insists on WP, has existing WP content, or needs the WP plugin ecosystem.
---

# Headless WordPress

WordPress headless is the right pick when: the client has 10+ years of
content in WP, their team is trained on the WP editor, or the project
needs WooCommerce / specific WP plugins. Otherwise, prefer a modern CMS.

## When to use

- Existing WP install with significant content
- Client team is wedded to the WP editor (don't fight this)
- Need a specific WP-only plugin (WooCommerce, MemberPress, LearnDash)
- Avoid for: greenfield builds with no WP history (use Sanity / Payload)

## Architecture

```
[ WordPress (admin + DB) ] ──GraphQL/REST──> [ Next.js / Astro frontend ]
                                              │
                                              └──> [ CDN cache ]
```

WP runs on a basic LAMP host or a managed service (WP Engine, Kinsta).
Frontend runs on Vercel/Netlify and consumes the WP API. Editors keep
working in WP — they don't need to learn anything new.

## WordPress side: required plugins

Install these:
- **WPGraphQL** — exposes a GraphQL endpoint at `/graphql`
- **WPGraphQL for ACF** — exposes Advanced Custom Fields
- **Advanced Custom Fields PRO** — custom field UI for editors
- **WPGraphQL Smart Cache** — query-level cache invalidation
- **Yoast SEO** + **WPGraphQL Yoast SEO** — SEO meta in API
- **Headless WordPress** plugin (Faust/Atlas-style) — for preview

**Avoid / disable**:
- Page builders that bypass the editor (Divi, Elementor body builder)
- Caching plugins that conflict with API responses (WP Rocket page cache)
- Comment systems that inject HTML into post content

## Content modeling with ACF

Define field groups for each post type:
```
Field Group: Page Sections
Location: Post Type == page
Fields:
  - sections (Flexible Content)
    Layouts: hero, feature_grid, testimonial, cta_banner
    Hero:
      - eyebrow (Text)
      - headline (Text, required)
      - sub (Textarea)
      - primary_cta (Group: label + href)
      - image (Image)
```

ACF Flexible Content gives editors the same "block" experience as Sanity
or Payload. WPGraphQL exposes it cleanly.

## Frontend GraphQL query

```graphql
query Page($slug: ID!) {
  page(id: $slug, idType: URI) {
    title slug seo { title metaDesc }
    pageSections {
      sections {
        ... on Page_Pagesections_Sections_Hero {
          fieldGroupName
          eyebrow headline sub
          primaryCta { label href }
          image { sourceUrl(size: LARGE) altText mediaDetails { width height } }
        }
        ... on Page_Pagesections_Sections_FeatureGrid { ... }
      }
    }
  }
}
```

## Frontend fetcher

```ts
// lib/wp.ts
export async function wp<T>(query: string, vars: object = {}, preview = false) {
  const res = await fetch(`${WP_URL}/graphql`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(preview ? { Authorization: `Bearer ${WP_PREVIEW_TOKEN}` } : {}),
    },
    body: JSON.stringify({ query, variables: vars }),
    next: { revalidate: 300, tags: ['wp'] },
  })
  const json = await res.json()
  if (json.errors) throw new Error(JSON.stringify(json.errors))
  return json.data as T
}
```

## Preview workflow

1. Add `Headless WordPress` plugin (or build a small auth plugin)
2. WP admin's "Preview" button hits: `https://yoursite.com/api/preview?secret=X&id={post.id}`
3. Next route enables draft mode + fetches the post in draft state via GraphQL.

## Image handling

- Disable WP's auto-resize image sizes you don't use (saves disk)
- Serve images via WP's media URL OR proxy them through a CDN (Cloudflare,
  ImageKit) for AVIF/WebP transforms
- Frontend uses `next/image` with the WP origin in `images.remotePatterns`

## Revalidation on publish

Add a small WP hook in `functions.php`:
```php
add_action('save_post', function($post_id) {
  if (wp_is_post_revision($post_id)) return;
  wp_remote_post(SITE_URL . '/api/revalidate', [
    'body' => json_encode([
      'secret' => REVALIDATE_SECRET,
      'slug' => get_post($post_id)->post_name,
    ]),
    'headers' => ['Content-Type' => 'application/json'],
  ]);
});
```

## Hosting choices

| Tier | WP host | Frontend | Total monthly |
|---|---|---|---|
| Budget | DreamHost / SiteGround | Vercel hobby | ~$20 |
| Standard | WP Engine starter | Vercel Pro | ~$50–100 |
| Enterprise | Kinsta / Pantheon | Vercel Enterprise | $500+ |

For a $50K project, **WP Engine + Vercel Pro** is the safe default.

## Security baseline

- Hide `/wp-admin` from public — IP allowlist or Cloudflare Access
- 2FA for all admins (Wordfence Login Security or similar)
- Disable XML-RPC unless explicitly needed
- Auto-update plugins, but pin major versions
- Daily DB + uploads backup (host-managed or UpdraftPlus)
- WAF in front (Cloudflare or Wordfence)

## Migration from monolithic WP

1. Audit current theme — identify which parts are dynamic vs. static
2. Map every URL on the old site → new URL (use `redirect-map-builder`)
3. Disable theme rendering on the public side: redirect `/` → frontend
4. Keep `/wp-admin`, `/wp-json`, `/graphql` accessible
5. Verify all old shortlinks, embeds, RSS feeds redirect correctly

## Anti-patterns

- Letting editors install random plugins (sandbox a staging env)
- Using a page builder (Divi/Elementor) that bypasses the API
- No rate limiting on GraphQL endpoint (DoS risk)
- Committing `wp-content/uploads/` to git (use S3 offload)
- Forgetting to disable WP's default theme front-end after going headless
- Relying on WP's built-in user accounts for the frontend (use NextAuth /
  Clerk, treat WP users as editors only)

## Pricing notes (for proposals)

Headless WP **costs more than monolithic WP** to build (two stacks) but
delivers much better Core Web Vitals + dev experience. Be honest with
clients: budget +30–50% on build vs. a vanilla WP redesign.
