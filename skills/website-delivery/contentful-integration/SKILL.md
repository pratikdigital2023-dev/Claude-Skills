---
name: contentful-integration
description: Integrate Contentful as the headless CMS — content models, locales, environments, GraphQL queries, webhooks, and ISR-safe revalidation. Use when the client already runs on Contentful, has a marketing team that prefers it, or needs enterprise governance.
---

# Contentful Integration

Contentful is the right pick when: the client is already invested in
Contentful licensing, marketing/editorial teams prefer it (familiar UX),
or the project needs robust localization + environment workflows.

## When to use

- Existing Contentful subscription
- Multi-locale, multi-region content
- Multiple environments (dev, staging, prod) with content promotion
- Enterprise governance (roles, audit log, SSO)
- Avoid for: small projects (cost), code-first developer preference (use Payload/Sanity)

## Project setup

1. Create a space in Contentful → grab `SPACE_ID`, `CDA_TOKEN`, `CPA_TOKEN`,
   `CMA_TOKEN`.
2. Create environments: `master` (prod), `staging`, `dev`.
3. Install CLI for migrations: `npm i -g contentful-cli`.

```bash
contentful login
contentful space use --space-id SPACE_ID
contentful space environment list
```

## Content modeling

Define models as code via migrations (NOT in the UI for production):
```js
// migrations/0001-create-page.js
module.exports = function(migration) {
  const page = migration.createContentType('page')
    .name('Page')
    .displayField('title')
  page.createField('title').type('Symbol').required(true)
  page.createField('slug').type('Symbol').required(true).validations([
    {regexp: {pattern: '^[a-z0-9-/]+$'}},
    {unique: true},
  ])
  page.createField('seo').type('Link').linkType('Entry').validations([
    {linkContentType: ['seoMeta']},
  ])
  page.createField('sections').type('Array').items({
    type: 'Link', linkType: 'Entry',
    validations: [{linkContentType: ['hero','featureGrid','faqSection']}],
  })
}
```

Run with: `contentful space migration ./migrations/0001-create-page.js`

Always check migrations into git — UI-only changes are unreproducible.

## GraphQL queries

```graphql
query Page($slug: String!) {
  pageCollection(where: { slug: $slug }, limit: 1) {
    items {
      sys { id }
      title
      slug
      seo { title description ogImage { url width height } }
      sectionsCollection(limit: 20) {
        items {
          __typename
          ... on Hero { headline sub primaryCtaLabel primaryCtaHref
            image { url width height description } }
          ... on FeatureGrid { headline featuresCollection { items {
            title body iconName }}}
        }
      }
    }
  }
}
```

Use the **GraphQL Content API** (`graphql.contentful.com`) over REST when
queries get nested — fewer round trips, no overfetching.

## Frontend data layer

```ts
// lib/contentful.ts
const ENDPOINT = `https://graphql.contentful.com/content/v1/spaces/${SPACE_ID}/environments/${ENV}`

export async function gql<T>(query: string, vars: object, preview = false): Promise<T> {
  const token = preview ? CPA_TOKEN : CDA_TOKEN
  const res = await fetch(ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ query, variables: vars }),
    next: { revalidate: 60, tags: ['contentful'] },
  })
  const json = await res.json()
  if (json.errors) throw new Error(JSON.stringify(json.errors))
  return json.data
}
```

## Locales

Set up locales in Settings → Locales. Default `en-US`, then add `de-DE`, etc.
Mark fields as **localized** in the model. Frontend passes `locale` to
GraphQL.

For URL strategy:
- **Subdirectory**: `/de/about` (most common, Next.js i18n routing)
- **Subdomain**: `de.site.com` (separate Vercel projects)
- **ccTLD**: `site.de` (highest SEO value, most ops cost)

## Environments + content promotion

Workflow:
1. Editorial works in `staging` environment
2. Devs work against `dev` environment
3. Promote to `master` via the Merge app or `contentful-cli`:
   `contentful space environment merge --se staging --te master`

Aliases (paid tier) let you swap an environment under `master` with zero
downtime. Worth it for high-traffic sites.

## Webhooks for revalidation

Configure on Settings → Webhooks → New webhook:
- URL: `https://yoursite.com/api/revalidate?secret=XYZ`
- Triggers: `Entry.publish`, `Entry.unpublish`, `Asset.publish`
- Filter by content type if needed

```ts
// app/api/revalidate/route.ts
import { revalidateTag } from 'next/cache'
export async function POST(req: Request) {
  const url = new URL(req.url)
  if (url.searchParams.get('secret') !== process.env.REVALIDATE_SECRET) {
    return new Response('unauthorized', { status: 401 })
  }
  revalidateTag('contentful')
  return Response.json({ revalidated: true })
}
```

## Preview mode

Use the **Preview API** + Next's `draftMode()`:
1. In Contentful, set the Preview URL on the entry: `https://yoursite.com/api/preview?secret=XYZ&slug={entry.fields.slug}`
2. Route enables `draftMode` and redirects.
3. Server component checks `draftMode().isEnabled` to decide which token to use.

## Roles & governance

For a $50K build, set up roles up front:
- **Admin**: agency lead
- **Editor**: client marketing team (publish own content)
- **Translator**: locale-specific
- **Developer**: model + migrations only

## Anti-patterns

- Editing models in the UI for production (unreproducible)
- Hardcoding the master environment (always pass `ENV` as env var)
- Not setting up the webhook → stale ISR cache
- Using Delivery API with PREVIEW token (or vice versa)
- Inlining the asset URL without `?w=` resize params (ships originals)
- Localizing fields you don't actually translate (clutter)
- Single environment for both dev + content team

## Pricing notes (for proposals)

- Free tier: 25K records, 2 locales — okay for very small builds
- Basic: $300/mo — minimum for serious projects
- Premium / Enterprise: custom — usually only when client already has it

If client doesn't have a Contentful contract, default to Sanity or Payload
(both cheaper at this tier).
