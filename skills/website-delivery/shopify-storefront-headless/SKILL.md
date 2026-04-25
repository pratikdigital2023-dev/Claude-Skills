---
name: shopify-storefront-headless
description: Build a headless Shopify storefront — Storefront API, cart, checkout (Shopify-hosted or custom), product variants, metafields, and webhooks. Use when the client runs (or wants to run) on Shopify but needs a custom storefront beyond what Liquid themes allow.
---

# Headless Shopify Storefront

Headless Shopify is the right pick when: the client wants Shopify's
back-office (orders, fulfillment, customers) but a fully custom storefront
in Next.js / Remix / Astro. Otherwise use a Liquid theme.

## When to use

- Client already on Shopify Plus or upgrading from Liquid
- Brand wants design freedom Liquid can't provide
- Need to share product data with a marketing site or app
- Mixing commerce with content-heavy CMS pages
- Avoid for: stores under $500K/yr revenue (Liquid theme is fine + cheaper)

## Architecture

```
[ Shopify Admin (DB, orders, payments) ]
                 │
        ┌────────┴────────┐
   Storefront API     Admin API
        │                  │
[ Custom Next.js storefront ]   [ Backoffice integrations ]
```

Storefront API: read products + write cart, **public** (with API token).
Admin API: orders, customers, inventory — **server-side only**.

## Setup

1. Shopify Admin → Apps → Develop apps → Create app
2. Configure Storefront API access (read products, read collections,
   write checkouts)
3. Install required plugin: **Hydrogen / Storefront API** access
4. Generate Storefront access token + Admin API token
5. Frontend env: `SHOPIFY_STORE_DOMAIN`, `SHOPIFY_STOREFRONT_TOKEN`

## Recommended frameworks

- **Hydrogen** (Shopify's Remix-based meta-framework) — best DX with
  Shopify, opinionated, deploy on Oxygen
- **Next.js + @shopify/hydrogen-react** — most flexible, deploy anywhere
- **Astro + Shopify Storefront** — best for content-heavy sites

For a $50K project pairing commerce + marketing site, **Next.js** is the
default.

## GraphQL query: product list

```graphql
query Products($first: Int!) {
  products(first: $first, sortKey: BEST_SELLING) {
    edges { node {
      id handle title descriptionHtml
      featuredImage { url altText width height }
      priceRange { minVariantPrice { amount currencyCode } }
      variants(first: 20) { edges { node {
        id title price { amount currencyCode } availableForSale
      }}}
    }}
  }
}
```

## Cart with the Cart API

Shopify's modern Cart API (replacing Checkout API):
```ts
// Create cart
const { cartCreate } = await sf(`mutation { cartCreate { cart { id checkoutUrl } } }`)

// Add line
await sf(`mutation Add($cartId: ID!, $lines: [CartLineInput!]!) {
  cartLinesAdd(cartId: $cartId, lines: $lines) { cart { id } }
}`, { cartId, lines: [{ merchandiseId: variantId, quantity: 1 }] })

// Get cart
const { cart } = await sf(`query Cart($id: ID!) {
  cart(id: $id) {
    checkoutUrl totalQuantity
    cost { totalAmount { amount currencyCode } }
    lines(first: 50) { edges { node {
      id quantity merchandise { ... on ProductVariant {
        id title price { amount } product { handle title featuredImage { url } }
      }}
    }}}
  }
}`, { id: cartId })
```

Persist `cartId` in a cookie. On checkout, redirect to `cart.checkoutUrl`
(Shopify-hosted, secure, mobile-optimized).

## Custom checkout (Shopify Plus only)

For brands with Plus, use the **Checkout Extensibility** API to:
- Add custom fields
- Inject loyalty/gift logic
- Custom payment methods

Otherwise, **always use Shopify-hosted checkout** — building your own is
illegal in many jurisdictions for card processing without massive PCI scope.

## Product variants + metafields

Variants: size/color/etc. Each has its own SKU + price.
Metafields: extra structured data (e.g., "shoe_width", "ingredients").

Define metafields in Settings → Custom data → Products. Query them:
```graphql
metafield(namespace: "custom", key: "ingredients") { value }
```

## Inventory + availability

```graphql
variants(first: 50) {
  edges { node {
    availableForSale
    quantityAvailable  # only on Plus + scoped tokens
  }}
}
```

Use `availableForSale` for "Out of stock" buttons. `quantityAvailable`
shows actual stock count (be careful — competitive intel).

## Webhooks (Admin API)

Subscribe via Admin → Settings → Notifications → Webhooks. Useful events:
- `orders/create` — sync to your DB / fulfillment
- `products/update` — invalidate ISR cache
- `inventory_levels/update` — refresh stock display

```ts
// Verify webhook
import crypto from 'crypto'
const hmac = req.headers.get('x-shopify-hmac-sha256')!
const body = await req.text()
const computed = crypto.createHmac('sha256', SHOPIFY_WEBHOOK_SECRET)
  .update(body, 'utf8').digest('base64')
if (computed !== hmac) return new Response('invalid', { status: 401 })
```

## Localization

- Markets in Shopify: per-country pricing, currencies, languages
- Storefront API accepts `@inContext(country: US, language: EN)` directive
- Frontend: pass user's locale + country in query context

## SEO essentials

- Server-render product/collection pages (not CSR-only)
- Use Shopify's structured data fields (price, availability) → JSON-LD on page
- Canonical URL = `/products/<handle>` (avoid query params)
- Build a `sitemap.xml` from Storefront API (don't rely on Shopify's default)

## Hosting + caching

- Vercel + Next.js ISR with `revalidate: 60` on product pages
- Webhook on `products/update` → `revalidatePath('/products/[handle]')`
- Shopify Oxygen if you go Hydrogen-only

## Anti-patterns

- Building your own card form (PCI nightmare — use hosted checkout)
- Storing Shopify tokens in client-side code
- No webhook for product updates → stale prices
- Hardcoding Shopify variant IDs (use handles + lookup)
- Skipping inventory check before "Add to cart" (sells out-of-stock items)
- Using deprecated Checkout API instead of Cart API

## Pricing notes (for proposals)

- Shopify Basic: $39/mo (fine for headless if traffic < 100K/mo)
- Shopify: $105/mo
- Advanced: $399/mo
- Plus: $2,300+/mo (required for Checkout Extensibility, custom apps)

Headless build adds ~80–200 hours vs. a Liquid theme. Be honest about
ongoing maintenance cost.
