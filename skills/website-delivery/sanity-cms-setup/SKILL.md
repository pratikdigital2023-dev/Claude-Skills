---
name: sanity-cms-setup
description: Stand up Sanity Studio as the headless CMS for a marketing or content-heavy site — schemas, GROQ queries, image pipeline, draft preview, deploy. Use when the client needs structured content, real-time preview, and a great editor experience.
---

# Sanity CMS Setup

Sanity is the right CMS pick when: editors need real-time collaboration,
content is structurally complex (references, portable text, conditional
fields), and developers want full schema control in code.

## When to use

- Marketing sites with > 5 page templates
- Content-heavy projects (resource libraries, case studies, blogs)
- Multi-tenant or multi-locale content
- Editorial workflows requiring drafts + preview
- Avoid for: pure e-commerce catalogs (use Shopify), small brochure sites
  (use Webflow), or tiny static sites (use MDX in repo)

## Project setup

```bash
npm create sanity@latest -- --project YOUR_PROJECT_ID --dataset production
cd studio
npm install
npm run dev   # studio at http://localhost:3333
```

Two-repo or monorepo? For a $50K project, **monorepo** with `studio/` and
`web/` keeps schemas + frontend in lockstep.

## Schema fundamentals

Every schema lives in `schemas/<name>.ts`. Group by:
- **Documents**: indexable content (Page, Post, Author, Product)
- **Objects**: reusable inline shapes (SeoMeta, CallToAction, Image)
- **Block content**: portable text variants per use case

### Page schema (typical marketing page)
```ts
import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'page',
  title: 'Page',
  type: 'document',
  fields: [
    defineField({name: 'title', type: 'string', validation: r => r.required()}),
    defineField({name: 'slug', type: 'slug',
      options: {source: 'title', maxLength: 96},
      validation: r => r.required()}),
    defineField({name: 'seo', type: 'seoMeta'}),
    defineField({name: 'sections', type: 'array', of: [
      {type: 'heroSection'},
      {type: 'featureGrid'},
      {type: 'logoCloud'},
      {type: 'testimonialSlider'},
      {type: 'faqSection'},
      {type: 'ctaBanner'},
    ]}),
  ],
})
```

Block-based pages let editors compose layouts without touching code.

## Studio structure (UX wins)

In `sanity.config.ts`, define a custom `structure`:
```ts
S.list().title('Content').items([
  S.listItem().title('Pages').schemaType('page')
    .child(S.documentTypeList('page').title('Pages')),
  S.listItem().title('Blog').child(
    S.list().title('Blog').items([
      S.listItem().title('Posts').schemaType('post')
        .child(S.documentTypeList('post').defaultOrdering(
          [{field: 'publishedAt', direction: 'desc'}])),
      S.listItem().title('Authors').schemaType('author')
        .child(S.documentTypeList('author')),
    ])
  ),
  S.divider(),
  S.listItem().title('Site Settings').child(
    S.editor().id('siteSettings').schemaType('siteSettings')
      .documentId('siteSettings')),
])
```

Always make singletons (Site Settings, Homepage) editable from a clear menu
item — never make editors hunt.

## GROQ queries (frontend)

Centralize queries in `lib/queries.ts`:
```ts
export const PAGE_QUERY = `*[_type == "page" && slug.current == $slug][0]{
  _id, title,
  "slug": slug.current,
  seo,
  sections[]{
    _type, _key,
    _type == "heroSection" => { headline, sub, primaryCta, image },
    _type == "featureGrid" => { headline, features[]{title, body, icon} },
    _type == "testimonialSlider" => {
      "items": testimonials[]->{quote, author, role, avatar}
    },
  }
}`
```

Use **projections** (`{ field, ... }`) — never `*` — to keep payloads small.

## Image pipeline

Always use `@sanity/image-url`:
```ts
import imageUrlBuilder from '@sanity/image-url'
const builder = imageUrlBuilder({projectId, dataset})
export const urlFor = (src) => builder.image(src)

// Usage
<img src={urlFor(image).width(1600).quality(80).auto('format').url()}
     loading="lazy" />
```

Sanity's CDN handles WebP/AVIF auto, srcset, and on-the-fly resizing. Don't
download originals.

## Draft preview (Next.js App Router)

1. Create `app/api/preview/route.ts` that sets a cookie + redirects.
2. In Studio, configure `productionUrl` resolver:
```ts
productionUrl: async (prev, {document}) => {
  const slug = document?.slug?.current
  return `${SITE_URL}/api/preview?secret=${SECRET}&slug=${slug}`
}
```
3. Frontend reads the preview cookie + uses Sanity's `previewDrafts`
   perspective for unpublished content.

## Deploy

- **Studio**: `sanity deploy` → `<project>.sanity.studio` (free) or your
  own subdomain (`cms.client.com`) via Vercel.
- **Webhooks**: configure on `sanity.io/manage` to ping
  `/api/revalidate` in Next on every publish (ISR).
- **Roles**: Editor / Viewer / Admin. Use Custom Access Controls for
  multi-tenant setups.

## Migration from existing CMS

Use `sanity dataset import` with NDJSON. For each old record:
1. Map fields to new schema
2. Transform body content to portable text (use `@sanity/block-tools`)
3. Upload assets first, reference by `_id`
4. Keep old IDs in a `_migration` field for traceability

## Anti-patterns

- One mega "page" schema with conditional fields for every template
- Storing site config as a regular document instead of a singleton
- Inline `*` GROQ queries (downloads everything)
- Bypassing `urlFor` and serving Sanity originals
- No webhook → stale cache after publish
- Editors with `Admin` role by default (use Editor)

## Pricing notes (for proposals)

- Free tier: 10K docs, 500K API CDN req/mo — fine for MVP
- Growth: $99/mo, fits most $50K builds
- Add seats per editor; build cost includes initial 5 editor accounts
