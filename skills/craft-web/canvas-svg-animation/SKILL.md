---
name: canvas-svg-animation
description: Build performant 2D motion with Canvas, SVG, Lottie, and Rive — when to choose each, accessibility patterns, and integration with React. Use for icons-in-motion, illustration animation, data viz, and bespoke 2D effects that don't justify WebGL.
---

# Canvas / SVG / Lottie / Rive

For 2D motion below the WebGL threshold. Picking the right tool here
determines whether your motion runs at 60 fps on a 3-year-old phone.

## Decision matrix

| Need | Use | Why |
|---|---|---|
| Icon micro-animation | **SVG + CSS/JS** | Crisp, accessible, tiny |
| Illustrated character animation | **Lottie** or **Rive** | Designer-driven |
| Interactive data viz | **D3 + SVG** (small) or **Canvas** (>1k points) | DOM cost |
| Particle effect (10k+) | **Canvas 2D** or **WebGL** | DOM dies |
| Branded loader | **Lottie** | Designer ships JSON |
| Logo morph | **SVG + GSAP MorphSVG** | Single tool |
| Game-like UI feedback | **Rive** | State machines + interactivity |
| Scroll-driven path drawing | **SVG + GSAP DrawSVG** | One tool, accessible |

## SVG animation

The default for icons + simple shapes — accessible by nature, infinitely scalable.

### CSS-only
```css
@keyframes draw {
  from { stroke-dashoffset: 200; }
  to { stroke-dashoffset: 0; }
}
.path { stroke-dasharray: 200; animation: draw 1s ease forwards; }
```

### GSAP + DrawSVG (paid)
```js
gsap.from('.path', { drawSVG: 0, duration: 1.5, ease: 'power2.inOut' })
```

### GSAP MorphSVG (paid) — shape-to-shape morphing
```js
gsap.to('#circle', { morphSVG: '#square', duration: 1 })
```

### SMIL (built-in SVG animation)
Works but limited; ignore it — use CSS or GSAP.

## Canvas 2D

Use when you have more elements than the DOM can handle (~500+ moving
nodes), or when you need pixel-level effects.

### Setup with HiDPI
```js
const dpr = window.devicePixelRatio || 1
canvas.width = canvas.clientWidth * dpr
canvas.height = canvas.clientHeight * dpr
ctx.scale(dpr, dpr)
```

### Animation loop
```js
let raf
function tick(t) {
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  // draw...
  raf = requestAnimationFrame(tick)
}
raf = requestAnimationFrame(tick)
// cleanup: cancelAnimationFrame(raf)
```

### Particles (~5k+)
```js
const particles = Array.from({ length: 5000 }, () => ({
  x: Math.random() * w, y: Math.random() * h,
  vx: (Math.random() - 0.5) * 2, vy: (Math.random() - 0.5) * 2,
}))

function tick() {
  ctx.fillStyle = 'rgba(0,0,0,0.05)'  // motion trail
  ctx.fillRect(0, 0, w, h)
  ctx.fillStyle = 'white'
  for (const p of particles) {
    p.x += p.vx; p.y += p.vy
    if (p.x < 0 || p.x > w) p.vx *= -1
    if (p.y < 0 || p.y > h) p.vy *= -1
    ctx.fillRect(p.x, p.y, 1, 1)
  }
  requestAnimationFrame(tick)
}
```

Past ~50k particles, switch to WebGL (instanced points).

### OffscreenCanvas + Worker
Heavy canvas work blocks the main thread. Move to a worker:
```js
const offscreen = canvas.transferControlToOffscreen()
worker.postMessage({ canvas: offscreen }, [offscreen])
// in worker: render off-thread
```

## Lottie

Designer exports After Effects animation → JSON; web plays it.

### When it's right
- Branded loaders, success states
- Illustrated explainers
- Onboarding animations
- Anything an animator already built in AE

### Stack
- **lottie-web** (original) — heaviest, most features
- **@lottiefiles/dotlottie-web** — newer dotLottie format, smaller
- **lottie-react** — React wrapper

```tsx
import { DotLottieReact } from '@lottiefiles/dotlottie-react'
<DotLottieReact src="/anim/loader.lottie" loop autoplay />
```

### Optimizing Lottie
- Convert to dotLottie (`.lottie`) — gzipped JSON, often 50% smaller
- Avoid raster images inside Lottie (bloats file)
- Avoid complex effects (drop shadows, blur — slow)
- Cap to 30 fps where possible (most animation doesn't need 60)
- Use `LottieFiles Optimizer` online tool

### Pitfalls
- 5 MB Lottie file (compress + simplify)
- Lottie playing on every card while scrolled out of view (pause off-screen)
- Different render modes (canvas vs SVG vs HTML) — test each, pick smallest stutter
- Unsupported AE features render incorrectly — preview before signing off

## Rive

The next-gen tool — combines Lottie-style animation with state machines
and runtime interactivity.

### When it's right
- Interactive characters (button hovers, mascot reacts to cursor)
- Game-like UI (toggle that morphs, character that reacts to input)
- Animations with multiple states/inputs (loading → success → error)

### Stack
- Designer authors in **Rive editor** (free)
- Ships `.riv` file (very small — 5–50 KB typically)
- Web plays via **@rive-app/canvas** or **@rive-app/react-canvas**

```tsx
import { useRive } from '@rive-app/react-canvas'

function Toggle() {
  const { RiveComponent, rive } = useRive({
    src: '/anim/toggle.riv',
    stateMachines: 'State Machine 1',
    autoplay: true,
  })
  return <RiveComponent style={{ width: 200, height: 200 }} />
}
```

### Why pick Rive over Lottie
- Smaller files
- True interactivity (no JS gymnastics)
- Better runtime perf
- Designer + dev share a single source

### Tradeoff
- Smaller ecosystem than Lottie
- Designers may not know it (training)
- Some teams have AE pipelines already

## Accessibility

All four mediums are visual. Always:
- Provide `<title>` + `<desc>` in SVG
- `role="img"` + `aria-label` on container
- Respect `prefers-reduced-motion` (pause / show static frame)
- Don't rely on motion alone to convey state (also change color/text)
- For Lottie/Rive, provide a static fallback image inside `<noscript>`

```tsx
const reduced = useReducedMotion()
return reduced ? <img src="/anim/static.png" alt="" /> : <RiveComponent />
```

## Performance

- Pause off-screen with IntersectionObserver
- Cap pixel ratio on Canvas (clamp to 2)
- Use `will-change` sparingly
- Profile in DevTools — long frames during animation = problem
- Lottie SVG renderer is heavier than canvas renderer; test both

```js
const io = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) lottie.play(); else lottie.pause()
  })
})
io.observe(animContainer)
```

## React patterns

```tsx
// Lazy-load animation libs (keep main bundle lean)
const Lottie = lazy(() => import('@lottiefiles/dotlottie-react').then(m => ({ default: m.DotLottieReact })))

<Suspense fallback={<img src="/poster.png" alt="" />}>
  <Lottie src="/anim/x.lottie" autoplay />
</Suspense>
```

## File-size budgets

- SVG icon animation: < 5 KB
- Lottie / dotLottie: < 100 KB ideal, 250 KB max
- Rive: < 50 KB typical
- Canvas asset (sprite sheet for 2D animation): depends, < 500 KB

## Common pitfalls

- Using SVG for 5000 elements (DOM dies — use canvas)
- Using Canvas for static icons (loses accessibility — use SVG)
- 2 MB Lottie hero animation (compress, simplify, convert to dotLottie)
- Animation playing forever when off-screen (battery, GPU)
- No reduced-motion fallback
- SVG without `<title>` (screen reader silent)
- Rive file with ALL state machines included when only one is used (split files)

## Tools

- **Lottie**: After Effects + Bodymovin, LottieFiles online editor
- **Rive**: native Rive editor (Mac/Win/Web)
- **SVG**: Figma → export, SVGOMG to optimize, IcoMoon
- **Canvas**: pixi.js for richer 2D, p5.js for sketches, plain canvas for control
- **Inspect**: SVGO, dotLottie viewer, Rive runtime inspector

## Reference sites

- airbnb.com (early Lottie pioneers)
- duolingo.com (mascot animations — Rive territory)
- linear.app (subtle SVG path motion)
- studio sites: build.lt, locomotive.ca

## Pricing notes (for proposals)

- SVG icon set with hover/click motion: 6–12 hrs
- Lottie integration of designer-supplied JSON: 2–4 hrs/animation
- Rive interactive character + state machine: 16–40 hrs (designer + dev)
- Custom Canvas effect (particle field, etc.): 16–32 hrs

## Anti-patterns

- Lottie for everything (some things are 1 SVG path)
- 60 fps all-the-time animations (drain battery, no human notices vs 30)
- No off-screen pause
- Canvas with no DPR scaling (blurry on retina)
- SVG inline-rendered when 50 instances exist (use `<use>` + sprite)
- Different motion language per page (no system)
- Decorative animation that distracts from primary CTA
