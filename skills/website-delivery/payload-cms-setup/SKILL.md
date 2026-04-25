---
name: payload-cms-setup
description: Stand up Payload CMS as a self-hosted, code-first headless CMS with TypeScript collections, blocks, access control, and draft preview. Use when the client wants to own their data, needs custom auth/access logic, or wants the CMS bundled with the Next.js app.
---

# Payload CMS Setup

Payload is the right pick when: the client insists on self-hosting (own
the database), the project needs sophisticated access control, or you want
CMS + frontend in a single Next.js deploy.

## When to use

- Self-hosting requirement (regulated industries, EU data residency)
- Multi-tenant SaaS with row-level access control
- Need to bundle CMS into a Next.js monolith
- Heavy custom logic (hooks, computed fields, integrations)
- Avoid for: clients who want a fully managed service (use Sanity / Contentful)

## Project setup (Payload 3 + Next.js)

```bash
npx create-payload-app@latest my-site
# Choose: "Next.js" template, PostgreSQL, TypeScript
cd my-site
cp .env.example .env  # set DATABASE_URI, PAYLOAD_SECRET
npm run dev
# Frontend: localhost:3000, Admin: localhost:3000/admin
```

## Collection (= content type)

```ts
// src/collections/Pages.ts
import type { CollectionConfig } from 'payload'

export const Pages: CollectionConfig = {
  slug: 'pages',
  admin: { useAsTitle: 'title', defaultColumns: ['title','slug','_status'] },
  versions: { drafts: { autosave: { interval: 2000 } } },
  access: {
    read: ({ req }) => req.user ? true : { _status: { equals: 'published' } },
    create: ({ req }) => Boolean(req.user),
  },
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'slug', type: 'text', required: true, unique: true,
      hooks: { beforeValidate: [({ value, data }) =>
        value || slugify(data?.title) ] }},
    { name: 'seo', type: 'group', fields: [
      { name: 'title', type: 'text' },
      { name: 'description', type: 'textarea' },
      { name: 'ogImage', type: 'upload', relationTo: 'media' },
    ]},
    { name: 'layout', type: 'blocks', blocks: [
      Hero, FeatureGrid, LogoCloud, Testimonials, CTA, FAQ,
    ]},
  ],
}
```

## Blocks (composable page sections)

```ts
// src/blocks/Hero.ts
export const Hero = {
  slug: 'hero',
  fields: [
    { name: 'eyebrow', type: 'text' },
    { name: 'headline', type: 'text', required: true },
    { name: 'sub', type: 'textarea' },
    { name: 'primaryCTA', type: 'group', fields: [
      { name: 'label', type: 'text' },
      { name: 'href', type: 'text' },
    ]},
    { name: 'image', type: 'upload', relationTo: 'media' },
  ],
}
```

The frontend renders the `layout` array by `block.blockType`:
```tsx
{page.layout.map(block => {
  switch (block.blockType) {
    case 'hero': return <Hero key={block.id} {...block} />
    case 'featureGrid': return <FeatureGrid key={block.id} {...block} />
  }
})}
```

## Access control (Payload's killer feature)

```ts
access: {
  read: () => true,
  create: ({ req }) => req.user?.role === 'editor',
  update: ({ req, doc }) => {
    if (req.user?.role === 'admin') return true
    return { 'tenant.id': { equals: req.user?.tenant } }
  },
  delete: ({ req }) => req.user?.role === 'admin',
}
```

Use this for: multi-tenant content, draft visibility, role-based publish.

## Globals (singletons)

```ts
// src/globals/SiteSettings.ts
export const SiteSettings: GlobalConfig = {
  slug: 'site-settings',
  fields: [
    { name: 'siteName', type: 'text' },
    { name: 'logo', type: 'upload', relationTo: 'media' },
    { name: 'mainNav', type: 'array', fields: [
      { name: 'label', type: 'text' },
      { name: 'href', type: 'text' },
    ]},
    { name: 'footer', type: 'group', fields: [
      { name: 'columns', type: 'array', fields: [...] },
    ]},
  ],
}
```

## Media + uploads

```ts
// src/collections/Media.ts
export const Media: CollectionConfig = {
  slug: 'media',
  upload: {
    staticDir: 'media',
    imageSizes: [
      { name: 'thumbnail', width: 400, height: 300, crop: 'center' },
      { name: 'card', width: 768 },
      { name: 'hero', width: 1600 },
    ],
    adminThumbnail: 'thumbnail',
    mimeTypes: ['image/*'],
  },
  fields: [{ name: 'alt', type: 'text', required: true }],
}
```

For production, swap local storage for **S3 / R2 / Vercel Blob** via
`@payloadcms/storage-s3`.

## Draft preview (Next.js)

1. Mark collections with `versions: { drafts: true }`.
2. Server component fetches drafts conditionally:
```tsx
const payload = await getPayload({ config })
const isPreview = (await draftMode()).isEnabled
const { docs } = await payload.find({
  collection: 'pages',
  where: { slug: { equals: params.slug } },
  draft: isPreview,
})
```
3. Editor clicks "Preview" in admin → hits `/api/preview` → enables draft
   mode → redirects to the page.

## Hosting

- **Vercel + Neon/Supabase Postgres**: easiest, ~$25/mo for small builds
- **Railway / Fly.io**: if you want Payload + DB co-located
- **AWS / Hetzner / DO**: full control, more ops overhead

For a $50K project, Vercel + managed Postgres is the right default.

## Database choice

| DB | Why |
|---|---|
| **Postgres** | Default. Better relational querying, supports row-level access. |
| **MongoDB** | Original Payload backend. Use only if existing infra demands it. |
| **SQLite** | Dev-only / tiny sites. |

## Anti-patterns

- One giant `Pages` collection with 30 conditional fields
- No access control (everyone can edit everything)
- Storing media on the local filesystem in production
- Skipping `unique: true` on slug fields (ships with duplicate URLs)
- Bundling Payload admin in the public frontend bundle (use route groups)
- No backup strategy for the Postgres DB

## Pricing notes (for proposals)

- Payload itself: free + open source
- Cloud (managed): from $35/mo
- Self-hosted: factor in DB ($25–50/mo) + storage + maintenance time
