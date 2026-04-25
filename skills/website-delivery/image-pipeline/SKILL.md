---
name: image-pipeline
description: Set up an end-to-end image pipeline — modern formats (AVIF/WebP), responsive srcset, lazy loading, blur placeholders, and CDN transforms via next/image, Cloudinary, or ImageKit. Use to hit Core Web Vitals and reduce bandwidth on any image-heavy site.
---

# Image Pipeline

Images are usually the largest payload on a marketing site and the biggest
lever for LCP. A correct pipeline saves 60–90% of image bytes vs. naive
serving.

## When to use

- Any new build (always — never raw `<img src="huge.jpg" />`)
- Audit of an existing site failing Core Web Vitals
- Migration from a host that didn't optimize images
- Building an image-heavy editorial / portfolio site

## Decision: which transform layer?

| Option | When |
|---|---|
| **next/image** | Next.js sites, static-friendly, free |
| **Cloudinary** | Multi-stack, sophisticated transforms, $$ |
| **ImageKit** | Cheaper Cloudinary alternative, good DX |
| **Sanity / Contentful CDN** | Already using one of those CMSes |
| **Cloudflare Images** | Single-purpose, $5/mo + per-image |

For a $50K Next.js project: **next/image** + your CMS's CDN. Add Cloudinary
only if you need video transforms or AI background removal.

## Format strategy

Serve in this order, fall back gracefully:
1. **AVIF** — best compression, modern browsers (~95% support)
2. **WebP** — broad support, slightly larger than AVIF
3. **JPEG / PNG** — fallback

`next/image` handles this automatically when you set
`images.formats: ['image/avif', 'image/webp']` in `next.config.js`.

## Responsive serving

Always serve different sizes per viewport. Naive `<img>` sends the same
2400px hero to a phone. With `next/image`:
```tsx
<Image
  src={hero}
  alt="Product hero"
  width={1600} height={900}
  sizes="(min-width: 1024px) 1200px, (min-width: 640px) 80vw, 100vw"
  priority   // for LCP image only
/>
```

Rules:
- **`priority`** only on the LCP image (hero, above-fold). Lazy everything else.
- **`sizes`** is required for responsive images — describes display size at each
  breakpoint, *not* image dimensions.
- **`width` and `height`** are required to prevent CLS — must match the source
  aspect ratio.

## Lazy loading

`next/image` lazy-loads by default. Native `<img>`: add `loading="lazy"`.
Never lazy-load above-the-fold images (kills LCP).

## Blur placeholder

Better than blank space while images load:
```tsx
<Image src={hero} placeholder="blur" blurDataURL={blurUrl} ... />
```

Generate blur data URLs at build time:
- **Next + static imports**: automatic
- **Next + remote images**: use `plaiceholder` package
- **Sanity**: `urlFor(img).blur(50).width(20).url()` → tiny placeholder

## Aspect-ratio CSS to prevent CLS

Even with `width`/`height`, set CSS aspect ratio for grid layouts:
```css
.image-wrap { aspect-ratio: 16 / 9; overflow: hidden; }
.image-wrap > img { width: 100%; height: 100%; object-fit: cover; }
```

## Cloudinary / ImageKit URLs

If you go this route, build URLs with transforms in the path:
```ts
// Cloudinary
const url = `https://res.cloudinary.com/${cloud}/image/upload/f_auto,q_auto,w_1600/${publicId}`

// ImageKit
const url = `https://ik.imagekit.io/${id}/${path}?tr=f-auto,q-auto,w-1600`
```

Always include:
- `f_auto` (or `f-auto`) → format negotiation
- `q_auto` → quality auto-tune
- `w_<n>` → max width

## SVG handling

- **Logos / icons**: SVG only, optimize with SVGO, inline when possible
- **Decorative icons**: use a sprite sheet or inline `<svg>` so you can
  control color via CSS
- **Never gzip SVG via CDN twice** (some hosts double-compress)
- **Don't use SVG for photos** (you can't, just listing this so you don't try)

## Video posters

For `<video>` tags, always set a `poster` (extracted first frame as a still
image). Prevents black flash before play.

## Image budgets

Set hard limits:
| Image type | Max bytes |
|---|---|
| Hero (above fold) | 200 KB |
| In-page editorial | 100 KB |
| Thumbnail | 30 KB |
| Logo | 15 KB |
| Decorative SVG | 5 KB |

Add a CI check (Lighthouse CI or custom script) that fails on over-budget
images.

## CMS / editor guidance

Editors are the #1 source of bloated images. Provide:
- A **max upload size** in the CMS (e.g., 5 MB)
- **Required alt text** field
- **Recommended dimensions** in field help text
- **Auto-resize on upload** (Sanity, Cloudinary, Payload all support)

Don't let editors upload 10 MB iPhone photos.

## Accessibility

- **Alt text**: required on every meaningful image; empty (`alt=""`) for
  decorative images so screen readers skip them
- **Don't put critical info in images** (text in images can't be read /
  translated / searched)
- **Contrast**: text overlaid on images must meet 4.5:1; add a gradient or
  scrim if not

## Pre-launch audit

```bash
# WebPageTest or PageSpeed Insights — check LCP image
# Look for:
# - LCP image is preloaded
# - LCP image is the right size for the viewport
# - LCP image is in AVIF or WebP
# - No off-screen images load above the fold
```

## Anti-patterns

- `<img src="huge.jpg" style="width: 200px" />` (downloads full size)
- Lazy-loading the hero image (kills LCP)
- No width/height (causes CLS)
- Same image at every breakpoint
- Letting editors upload originals with no resize
- SVG for photos (impossible)
- Inline base64 images > 1 KB (kills HTML parse + caching)
- Using `priority` on every image (defeats the purpose)

## Pricing notes (for proposals)

- next/image + Vercel: bundled with Vercel pricing, free tier covers most
  small builds
- Cloudinary: free up to 25 credits (~25K transforms), then $89+/mo
- ImageKit: free up to 20 GB bandwidth, $49+/mo
- Sanity image CDN: included
