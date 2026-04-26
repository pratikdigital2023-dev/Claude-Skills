---
name: smooth-scroll-lenis
description: Add buttery smooth-scroll to a site using Lenis (the open-source replacement for Locomotive Scroll), integrate cleanly with GSAP ScrollTrigger and React, and avoid the accessibility pitfalls of hijacking native scroll.
---

# Smooth Scroll (Lenis)

Smooth scroll is half the difference between "site" and "experience".
Done badly, it breaks accessibility, anchor links, and momentum. Done
well, it feels weightless.

## When to use

- Site has scroll-driven motion (parallax, scrub, pinned sections) — smoothing dampens jitter
- Brand calls for premium feel
- You're going to sync it with GSAP ScrollTrigger

## When NOT to use

- Content-heavy site (blog, docs, ecommerce) — users want native speed
- Mobile-first audience — smooth scroll on touch can feel laggy
- You can't commit to thorough QA across browsers + devices

## Why Lenis

- Tiny (~3 KB)
- No DOM hijacking — patches `window` scroll, anchor links + DevTools "scroll into view" still work
- First-class GSAP integration
- Maintained (Studio Freight)

Alternatives:
- ScrollSmoother (GSAP, paid, well-tuned)
- Locomotive Scroll (older, hijacks scroll — more issues)
- Native CSS `scroll-behavior: smooth` (anchor links only)

## Install

```bash
npm i lenis
```

## Vanilla setup

```js
import Lenis from 'lenis'

const lenis = new Lenis({
  duration: 1.2,                 // 1.0–1.5 feels natural
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  smoothWheel: true,
  smoothTouch: false,            // KEEP FALSE — touch should feel native
  wheelMultiplier: 1,
  touchMultiplier: 2,
})

function raf(time) {
  lenis.raf(time)
  requestAnimationFrame(raf)
}
requestAnimationFrame(raf)
```

## React (Next.js / Vite)

```tsx
'use client'
import { useEffect } from 'react'
import Lenis from 'lenis'

export function SmoothScrollProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const lenis = new Lenis({ smoothTouch: false })
    let raf: number
    const update = (t: number) => { lenis.raf(t); raf = requestAnimationFrame(update) }
    raf = requestAnimationFrame(update)
    return () => { cancelAnimationFrame(raf); lenis.destroy() }
  }, [])
  return <>{children}</>
}
```

Wrap once at the app root. Don't instantiate per route.

## GSAP ScrollTrigger integration

The single most important pattern when using both:

```js
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
gsap.registerPlugin(ScrollTrigger)

const lenis = new Lenis({ smoothTouch: false })
lenis.on('scroll', ScrollTrigger.update)
gsap.ticker.add((time) => { lenis.raf(time * 1000) })
gsap.ticker.lagSmoothing(0)
```

Without this, ScrollTrigger fires off-time and pinned sections judder.

## Anchor links

Lenis exposes `scrollTo`:
```js
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', (e) => {
    e.preventDefault()
    const target = a.getAttribute('href')
    lenis.scrollTo(target, { offset: -80, duration: 1.5 })
  })
})
```

Pass `immediate: true` to skip animation (useful on initial page load with hash).

## Stop / start (for modals, drawers)

```js
// when modal opens
lenis.stop()
// when modal closes
lenis.start()
```

Lenis adds `data-lenis-prevent` you can attach to scrollable areas inside
modals so they scroll natively.

## Accessibility

**Critical**: smooth scroll often breaks for users who rely on:
- Keyboard scroll (Page Down, Space, arrow keys) — Lenis handles by default but verify
- Screen readers — ensure focus-driven scroll still lands correctly
- `prefers-reduced-motion` — disable smoothing entirely

```js
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches
const lenis = new Lenis({
  duration: reduced ? 0 : 1.2,
  smoothWheel: !reduced,
})
```

Always test:
- Tab key navigation (focus should scroll element into view)
- DevTools "Scroll into view" right-click
- Hash links in fresh tab
- Browser back/forward scroll restoration

## Pinned sections + scroll restoration

Browsers try to restore scroll on back-nav. Smooth scroll can fight this.
Use:
```js
if ('scrollRestoration' in history) history.scrollRestoration = 'manual'
```
…and persist position yourself if needed. For most sites, `'auto'` is fine
once Lenis is initialized.

## Mobile rules

- **smoothTouch: false** — period. iOS already has elastic momentum scroll. Smoothing it causes lag.
- Don't smooth-scroll on `<textarea>` or scrollable inner elements
- Test with one-finger swipe + flick on iOS Safari

## Performance

- Lenis itself is cheap. The cost is what you animate WITH it.
- Use `will-change: transform` selectively on parallax layers, remove after
- `passive: true` on wheel listeners (Lenis handles)
- Profile in DevTools Performance tab — look for long frames during scroll

## Common pitfalls

- Smoothing touch (turn it off)
- Forgetting GSAP ticker integration → ScrollTrigger fires at wrong times
- Initializing twice (HMR + StrictMode) — wrap with effect cleanup
- Anchor links jump instantly because click handler not attached
- `position: fixed` elements look fine but `position: sticky` may misbehave with some setups (test thoroughly)
- Iframe scroll fights with Lenis — exclude with `data-lenis-prevent`
- Not killing on unmount → leaked event listeners

## Debugging

- `lenis.scroll` — current scroll position
- `lenis.velocity` — current velocity
- `lenis.on('scroll', console.log)` to inspect events
- Toggle `smoothWheel: false` to bisect issues

## Reference sites

- studiofreight.com (creators)
- 14islands.com
- active.theory
- many awwwards.com SOTD entries

## Pricing notes (for proposals)

- Lenis setup + GSAP integration: 4–8 hrs
- Anchor links + accessibility QA: 2–4 hrs
- Performance tuning across breakpoints: 4–8 hrs
- Total: ~half a day to a day for a clean integration

## Anti-patterns

- Smooth scroll on a docs site
- `smoothTouch: true` on mobile
- No `prefers-reduced-motion` opt-out
- Different smoothing per route
- Smoothing inside an already-scrollable container (fights itself)
- Shipping without keyboard QA
- Not stopping Lenis when a modal opens (background scrolls underneath)
