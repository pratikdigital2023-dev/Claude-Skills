---
name: motion-design-patterns
description: Apply tasteful, performant motion to a marketing website using Framer Motion, GSAP, or CSS — entrance animations, scroll-linked effects, hover micro-interactions, and page transitions. Respects prefers-reduced-motion. Use when building or polishing the visual layer.
---

# Motion Design Patterns

Good motion makes a site feel premium. Bad motion makes it feel slow,
janky, or motion-sickness-inducing. This skill encodes the patterns that
work and the rules that keep them performant + accessible.

## When to use

- Adding entrance animations to hero / feature blocks
- Building scroll-linked effects (parallax, sticky sections, reveals)
- Polishing hover and click micro-interactions
- Page-transition animation between routes
- Loading / state animations

## Library choice

| Library | Best for | Bundle | Notes |
|---|---|---|---|
| CSS `@keyframes` + `transition` | Hovers, simple reveals | 0 | Always start here |
| Framer Motion | React-heavy sites, declarative | ~30KB | Pairs with Next.js cleanly |
| GSAP | Complex timelines, scroll, SVG | ~30–60KB | License needed for some plugins |
| Lottie | Designer-authored animations | ~30KB + JSON | Heavy if abused |
| CSS scroll-driven animations | Modern scroll effects | 0 | Limited browser support |

Default: **CSS for simple, Framer Motion for React UI, GSAP only if the
project genuinely needs timelines or paid plugins.**

## Core principles

1. **Motion is communication, not decoration.** Every animation answers
   "where did this come from?" or "what changed?"
2. **Duration**: 150–300ms for UI; 600–1200ms for hero/storytelling.
3. **Easing**: `cubic-bezier(0.16, 1, 0.3, 1)` (out-expo) for entrances;
   `ease-out` for exits; never linear.
4. **Stagger**: 50–100ms between sibling elements; never more than 600ms total.
5. **Don't animate `top/left`** — animate `transform` (GPU-accelerated).
6. **Honor `prefers-reduced-motion`** — always.

## CSS reduced-motion baseline

Put this at the top of any motion-heavy site:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## Pattern: entrance reveal on scroll

**Framer Motion**:
```tsx
import { motion } from "framer-motion";

const reveal = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } }
};

<motion.div initial="hidden" whileInView="visible"
  viewport={{ once: true, margin: "0px 0px -100px 0px" }}
  variants={reveal}>
  ...
</motion.div>
```

Rules:
- `once: true` — never re-trigger (annoying)
- Trigger ~100px before in-view (smooth, not jarring)
- Stagger via `staggerChildren: 0.08` on the parent

## Pattern: scroll progress / sticky parallax

```tsx
import { motion, useScroll, useTransform } from "framer-motion";

const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
const y = useTransform(scrollYProgress, [0, 1], ["0%", "-30%"]);
return <motion.img style={{ y }} src="..." />;
```

Limit parallax depth: max 30% relative travel. More than that = motion sickness.

## Pattern: hover micro-interactions

```css
.card {
  transition: transform 200ms cubic-bezier(0.16, 1, 0.3, 1),
              box-shadow 200ms ease;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.08);
}
```

- Lift: 2–4px max
- Color shifts: 100–150ms
- Touch devices ignore `:hover` — don't make functionality depend on it

## Pattern: page transitions (Next.js App Router)

Use `framer-motion`'s `AnimatePresence` with `key={pathname}`. Keep page
transitions under 300ms in + 200ms out. Anything longer feels broken.

```tsx
"use client";
import { AnimatePresence, motion } from "framer-motion";
import { usePathname } from "next/navigation";

export function PageTransition({ children }) {
  const pathname = usePathname();
  return (
    <AnimatePresence mode="wait">
      <motion.div key={pathname}
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
        transition={{ duration: 0.2 }}>
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
```

## Pattern: button / icon press

```css
.btn { transition: transform 100ms ease; }
.btn:active { transform: scale(0.97); }
```

Subtle. Communicates "yes, you pressed it" without being cute.

## Pattern: number counter / metrics reveal

Use `framer-motion`'s `useMotionValue` + `useTransform`, animate from 0 to
target over 1.5–2s when in view. Round to int. Don't use this for prices
or anything precise — it can read as fake.

## Performance checklist

- [ ] Every animated element uses `transform` and/or `opacity` only
- [ ] No animation runs continuously off-screen (use `whileInView`)
- [ ] Heavy GSAP scroll triggers use `ScrollTrigger.batch` for siblings
- [ ] No layout thrashing (avoid `width`/`height` animation)
- [ ] Lottie files < 50KB; static SVG preferred when possible
- [ ] `will-change` only on actively animated elements (remove after)
- [ ] FPS check on a mid-tier mobile device (target 60fps)

## Accessibility checklist

- [ ] `prefers-reduced-motion` disables non-essential motion
- [ ] No flashing > 3 Hz (seizure risk)
- [ ] Focus rings are not animated
- [ ] Auto-playing carousels have pause control
- [ ] Animated content has a static fallback (e.g., for screen readers)

## Anti-patterns

- 4-second hero reveals (users hit the back button)
- Parallax with > 30% travel (motion sickness)
- Animating `top` / `left` (causes layout, kills FPS)
- "Surprise" animations on click that delay the actual action
- Lottie files used for UI states (use CSS / Framer)
- Different easing on every element (looks chaotic)
- No reduced-motion fallback
