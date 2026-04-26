---
name: gsap-scroll-choreography
description: Build scroll-driven animation sequences with GSAP and ScrollTrigger — pinned sections, horizontal scroll, scrubbed timelines, parallax, reveal stacks. The de-facto stack for high-end agency motion. Use when CSS scroll-timeline isn't sufficient or browser support matters.
---

# GSAP + ScrollTrigger

GSAP is the industry standard for high-end web motion. It's not free (paid
license required for some plugins on commercial sites), but for $50K-tier
projects the license cost is negligible vs. the time saved.

## When to use

- Scroll-driven hero choreography (text reveals, image reveals, sequences)
- Pinned sections that animate as user scrolls through them
- Horizontal scroll within a vertical site
- Scrubbed video / image-sequence playback tied to scroll
- Stagger reveals across grids
- Anywhere CSS animations + IntersectionObserver get unwieldy

## When NOT to use

- Simple "fade in on view" — use IntersectionObserver + CSS
- Native scroll-driven animations are sufficient (Chrome 115+, but not Safari yet for many features)
- Project budget can't carry the GSAP Business license fee

## License (don't skip this)

- Free for non-commercial / personal sites
- **Club GSAP / Business** required for commercial sites that use:
  - SplitText
  - MorphSVG
  - DrawSVG
  - ScrollSmoother (paid plugin)
  - Inertia, Physics2D, etc.
- ScrollTrigger itself is free for any use as of 2024+ (verify current terms)

Budget license cost into the proposal.

## Stack

```bash
npm i gsap
```

Register plugins explicitly:
```js
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
gsap.registerPlugin(ScrollTrigger)
```

In React, use `@gsap/react` for the `useGSAP` hook (handles cleanup):
```bash
npm i @gsap/react
```

## Core patterns

### 1. Reveal on scroll
```js
gsap.from('.reveal', {
  y: 60, opacity: 0, duration: 1, ease: 'power3.out',
  stagger: 0.1,
  scrollTrigger: { trigger: '.reveal', start: 'top 80%' }
})
```

### 2. Pinned section with progress
```js
gsap.timeline({
  scrollTrigger: {
    trigger: '#chapter-1',
    start: 'top top',
    end: '+=2000',
    pin: true,
    scrub: 1,
  }
})
.to('.bg', { scale: 1.5 })
.to('.headline', { yPercent: -100 }, 0)
.from('.next', { opacity: 0 }, 0.5)
```

### 3. Horizontal scroll inside vertical page
```js
const panels = gsap.utils.toArray('.panel')
gsap.to(panels, {
  xPercent: -100 * (panels.length - 1),
  ease: 'none',
  scrollTrigger: {
    trigger: '.horizontal-wrap',
    pin: true,
    scrub: 1,
    end: () => '+=' + document.querySelector('.horizontal-wrap').offsetWidth,
  }
})
```

### 4. Image-sequence scrub (Apple-style)
```js
const frames = 240
const img = document.querySelector('canvas')
const ctx = img.getContext('2d')
const images = []
for (let i = 0; i < frames; i++) {
  const im = new Image()
  im.src = `/seq/${String(i).padStart(4,'0')}.webp`
  images.push(im)
}
const obj = { frame: 0 }
gsap.to(obj, {
  frame: frames - 1,
  snap: 'frame',
  ease: 'none',
  scrollTrigger: { trigger: '#seq', start: 'top top', end: '+=4000', scrub: 0.5, pin: true },
  onUpdate: () => ctx.drawImage(images[obj.frame], 0, 0),
})
```

### 5. Parallax layers
```js
gsap.utils.toArray('[data-speed]').forEach(el => {
  gsap.to(el, {
    yPercent: -100 * el.dataset.speed,
    ease: 'none',
    scrollTrigger: { trigger: el, scrub: true, start: 'top bottom', end: 'bottom top' }
  })
})
```

## React integration

```tsx
import { useRef } from 'react'
import { useGSAP } from '@gsap/react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
gsap.registerPlugin(ScrollTrigger)

export function Hero() {
  const ref = useRef<HTMLDivElement>(null)
  useGSAP(() => {
    gsap.from('.line', { y: 80, opacity: 0, stagger: 0.05,
      scrollTrigger: { trigger: '.line', start: 'top 80%' }})
  }, { scope: ref })
  return <div ref={ref}>...</div>
}
```

`useGSAP` auto-disposes timelines + ScrollTriggers on unmount. Always
scope to a ref to avoid global pollution.

## Refresh + responsive

```js
ScrollTrigger.config({ ignoreMobileResize: true })

// recalc on resize but not on iOS URL bar bounce
let resizeTimer
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => ScrollTrigger.refresh(), 200)
})
```

Use `gsap.matchMedia` to swap timelines per breakpoint:
```js
const mm = gsap.matchMedia()
mm.add('(min-width: 768px)', () => {
  gsap.to('.x', { xPercent: -100, scrollTrigger: { ... } })
})
mm.add('(max-width: 767px)', () => {
  gsap.to('.x', { yPercent: -100, scrollTrigger: { ... } })
})
```

## Performance

- Use `will-change: transform` only on actively-animating elements, then remove
- Animate `transform` and `opacity` only — never `top/left/width/height`
- `scrub: 1` (smoothing) feels better than `scrub: true` (raw)
- Disable triggers far above the fold with `scrollTrigger.refresh()` after content loads
- Use `markers: true` in dev to debug, never ship

## Reduced motion

```js
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
if (reduced) {
  ScrollTrigger.getAll().forEach(t => t.kill())
  // optionally set final state
  gsap.set('.reveal', { opacity: 1, y: 0 })
}
```

Test by enabling "Reduce motion" in OS settings + DevTools rendering panel.

## Common pitfalls

- Forgetting `ScrollTrigger.refresh()` after async content loads — triggers misaligned
- Not killing timelines on route change in SPAs — leaks + double-fires
- Animating layout properties (causes jank — use transform)
- Pinned sections without setting min-height on parent (collapse)
- `start: 'top top'` when there's a sticky header (offset needed)
- Stacking 20 pins (each is a fixed-position element)
- Using ScrollTrigger before content has loaded fonts (positions shift)

## Smooth scroll combo

GSAP has ScrollSmoother (paid). Free alternative: Lenis (see
`smooth-scroll-lenis` skill) — works with ScrollTrigger via:
```js
lenis.on('scroll', ScrollTrigger.update)
gsap.ticker.add((time) => lenis.raf(time * 1000))
gsap.ticker.lagSmoothing(0)
```

## Debugging

- `markers: true` shows trigger zones
- `ScrollTrigger.getAll()` lists all instances
- `ScrollTrigger.refresh(true)` forces full recalc
- GSDevTools (paid plugin) for timeline scrubbing in dev

## Reference sites to study

- apple.com (any product page)
- linear.app
- stripe.com
- monks.com
- studio sites: Active Theory, Resn, Locomotive

## Pricing notes (for proposals)

- Simple scroll reveals across site: 8–16 hrs
- Pinned hero with timeline: 16–32 hrs
- Image-sequence scrub: 24–48 hrs (frames + tuning)
- Full agency-tier scroll narrative (pinned chapters + parallax + 3D): 80–160 hrs

## Anti-patterns

- ScrollTrigger on every section "to add motion" — feels seasick
- Pinning longer than 200vh (loses context)
- Scrub speed mismatched between sibling animations
- Ignoring reduced-motion
- Shipping markers + console.log in production
- Mixing GSAP with CSS scroll-snap (they fight)
- No matchMedia variants (mobile gets desktop choreography)
