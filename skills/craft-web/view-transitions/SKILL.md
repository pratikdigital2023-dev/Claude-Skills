---
name: view-transitions
description: Use the View Transitions API for native page-to-page and DOM-state morphing animations across same-document SPAs and cross-document MPAs. Covers Astro, Next.js App Router, and vanilla integration with safe progressive-enhancement fallbacks.
---

# View Transitions API

The View Transitions API turns a hard page swap into a morphed transition
— shared elements move between pages, the rest cross-fades. It's how
sites like Astro docs and many 2024+ sites get app-like navigation feel
without an SPA framework.

## When to use

- MPA (Astro, plain HTML, Rails) — get SPA-like transitions for free
- SPA where you want shared-element morphing on route change
- DOM-state changes (filtering a list, expanding a card) where you want morph-not-cut

## Browser support (as of 2026)

- Same-document: Chrome 111+, Edge 111+, Safari 18+, Firefox (behind flag/in progress)
- Cross-document: Chrome 126+, Safari 18.2+, Firefox in development
- **Always treat as progressive enhancement** — fall back to hard nav

## Two flavors

1. **Same-document** (`document.startViewTransition`) — SPA route changes, DOM morphs
2. **Cross-document** (`@view-transition { navigation: auto }`) — MPA navigation between full HTML docs

## Same-document usage

```js
function navigate(url) {
  if (!document.startViewTransition) {
    location.href = url
    return
  }
  document.startViewTransition(async () => {
    // your DOM update logic
    await loadAndRender(url)
  })
}
```

For React, wrap state updates:
```js
import { flushSync } from 'react-dom'

function toggle() {
  if (!document.startViewTransition) { setOpen(o => !o); return }
  document.startViewTransition(() => {
    flushSync(() => setOpen(o => !o))
  })
}
```

## Cross-document (MPA)

Drop in your CSS:
```css
@view-transition {
  navigation: auto;
}
```

Browser automatically applies a cross-fade between page navigations on
same-origin links. No JS required.

## Naming elements for shared transitions

Mark elements with `view-transition-name`:
```css
.product-card[data-id="42"] {
  view-transition-name: product-42;
}
.product-detail-hero {
  view-transition-name: product-42;
}
```

The browser sees the same name on both pages and morphs between them.
Names must be **unique per page** at any given moment.

Dynamic names:
```js
el.style.viewTransitionName = `product-${id}`
```

## Customizing the animation

The browser creates pseudo-elements you can target:
```css
::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: 400ms;
  animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}

::view-transition-old(product-42) {
  animation: fade-out 0.3s both;
}
::view-transition-new(product-42) {
  animation: fade-in 0.3s both;
}
```

`root` targets everything not otherwise named. Specific names override.

## Astro

Astro has first-class support:
```astro
---
import { ViewTransitions } from 'astro:transitions'
---
<head>
  <ViewTransitions />
</head>
```

Mark shared elements:
```astro
<img src={img} transition:name={`hero-${slug}`} />
```

Persist elements (e.g., audio player) across nav:
```astro
<audio transition:persist>...</audio>
```

## Next.js App Router

Next supports View Transitions via the experimental `next/navigation`
hooks; for now use a custom wrapper:

```tsx
'use client'
import { useRouter } from 'next/navigation'
import { useTransition } from 'react'

export function useViewTransitionRouter() {
  const router = useRouter()
  return (href: string) => {
    if (!document.startViewTransition) { router.push(href); return }
    document.startViewTransition(() => router.push(href))
  }
}
```

Cross-document mode + `next export` static output works without JS.

## React + state morphing

Animate list reorders, filter changes, modal open:
```tsx
function FilterToggle() {
  const [filter, setFilter] = useState('all')
  const update = (v: string) => {
    if (!document.startViewTransition) { setFilter(v); return }
    document.startViewTransition(() => flushSync(() => setFilter(v)))
  }
  return <Tabs onChange={update} value={filter} />
}
```

Apply `view-transition-name` to each card so they morph positions instead
of fading in place.

## Performance

- Default 250ms ease — feels snappy
- Avoid >500ms — looks slow
- Don't apply names to 100s of elements (pixel snapshot for each is expensive)
- Test on low-end Android — V T snapshots can stutter

## Reduced motion

```css
@media (prefers-reduced-motion: reduce) {
  ::view-transition-old(*),
  ::view-transition-new(*) {
    animation: none !important;
  }
}
```

## Accessibility

- Focus management: ensure focus moves to expected element after navigation
- Screen reader announcements: a transition is visual only; ensure aria-live regions still update
- Keyboard nav unaffected, but verify

## Common pitfalls

- Two elements sharing a `view-transition-name` on the same page → animation ignored
- Conditional names using `display: none` — element must be in DOM at transition start
- Iframes inside transitioned regions can flicker
- Forgetting to fall back when API absent (always check)
- Naming `body` or huge containers (entire page becomes one snapshot — slow + jittery)
- Animating `width/height` instead of letting transition compute — disable defaults, use transforms

## Debugging

- Chrome DevTools → Animations panel pauses + scrubs view transitions
- `document.startViewTransition` returns a `ViewTransition` object with `ready`, `finished`, `updateCallbackDone` promises
- Set `animation-duration: 5s` on `::view-transition-group(*)` to slow-mo

## Reference sites

- docs.astro.build (page-to-page)
- chrome.com/docs/blog
- many 2024+ portfolio sites (search "view transitions awwwards")

## Pricing notes (for proposals)

- Cross-document MPA setup: 2–4 hrs
- Same-document SPA wrapper + named shared elements: 8–16 hrs
- Custom-tuned page transitions across a 20-page site: 24–48 hrs

## Anti-patterns

- Treating it as a required feature (always progressive enhancement)
- Long durations (>500ms) — feels broken
- Too many shared names (chaos, slow)
- No reduced-motion override
- Using it where a simple CSS transition would work
- Relying on it for content morph (it's visual only — DOM still swaps)
