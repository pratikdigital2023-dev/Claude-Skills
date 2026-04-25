---
name: figma-to-code-handoff
description: Convert approved Figma designs into a clean dev handoff — design tokens (color, typography, spacing, radii, shadows) exported for code, component naming conventions, and a per-component spec sheet. Use after design approval, before frontend build.
---

# Figma → Code Handoff

Most "design vs. dev mismatch" pain comes from sloppy handoff: tokens that
don't map to CSS variables, components named differently in Figma vs. code,
inconsistent spacing scales. This skill makes the handoff machine-readable.

## When to use

- Visual design is approved, build is about to start
- Adopting a new design system mid-project
- Migrating from Sketch / XD / Adobe to Figma
- Designer and developer are different people / agencies

## Pre-handoff checklist (designer)

Before passing to dev, the Figma file must have:
- [ ] All colors as **variables** (Figma Variables, not styles for new files)
- [ ] All text styles defined and applied consistently
- [ ] All spacing using a defined scale (4 or 8 px base)
- [ ] All effects (shadows) as styles
- [ ] All radii using a defined scale
- [ ] Components published in a library (not detached instances)
- [ ] Pages organized: `🟢 Production / 🟡 In Progress / 🔴 Archive`
- [ ] Cover page with: file purpose, contact, last updated

## Token export

Use **Figma Variables → JSON** via Tokens Studio plugin or Figma's REST API.

Token categories (W3C Design Tokens spec):
```json
{
  "color": {
    "primary": { "50": "#...", "500": "#...", "900": "#..." },
    "neutral": { "0": "#fff", "950": "#0a0a0a" },
    "semantic": {
      "background": { "value": "{color.neutral.0}" },
      "foreground": { "value": "{color.neutral.950}" },
      "border": { "value": "{color.neutral.200}" }
    }
  },
  "spacing": { "1": "4px", "2": "8px", "3": "12px", "4": "16px" },
  "radius": { "sm": "4px", "md": "8px", "lg": "16px", "full": "9999px" },
  "fontFamily": { "sans": "Inter, ...", "mono": "JetBrains Mono, ..." },
  "fontSize": { "xs": "12px", "sm": "14px", "base": "16px", "lg": "18px" },
  "lineHeight": { "tight": 1.1, "normal": 1.5, "relaxed": 1.7 },
  "shadow": { "sm": "0 1px 2px ...", "md": "0 4px 12px ..." }
}
```

Tools to convert tokens.json → CSS / Tailwind / Style Dictionary output:
- Style Dictionary (Amazon)
- Tokens Studio (formerly Figma Tokens)
- shadcn/ui token generator

## Naming convention (must match across Figma + code)

| Figma layer | Code component | CSS class |
|---|---|---|
| `Button/Primary` | `<Button variant="primary" />` | `.btn--primary` |
| `Card/Default` | `<Card />` | `.card` |
| `Hero/With Media` | `<Hero variant="with-media" />` | `.hero--with-media` |

Pick one of: BEM, Tailwind, CSS Modules, kebab-case CSS — and use it
**everywhere**. Inconsistency here causes hours of debugging.

## Per-component spec sheet

For each component, document:
```
Component: Button
Variants: primary | secondary | ghost | destructive
Sizes: sm (32px) | md (40px) | lg (48px)
States: default | hover | active | focus | disabled | loading
Props: label, onClick, icon (left/right), iconOnly, fullWidth
A11y: native <button>, focus-visible ring 2px primary at 2px offset,
      aria-busy when loading, min 44×44 hit target
Animations: 150ms ease background, 200ms ease transform on press
Forbidden: never nest a button inside a link or vice versa
```

## Spacing & layout discipline

- **Base scale**: 4px (or 8px for marketing sites)
- **Section padding**: t/b 64–128 desktop, 40–80 mobile
- **Container max-width**: typically 1200–1280px (avoid `100%` for prose)
- **Grid**: 12-col desktop, 4-col mobile (most common)
- **Gutters**: 24px desktop, 16px mobile

If a designer hands you `padding: 23px`, push back. Off-scale values are bugs.

## Image / asset handoff

- Export raster from Figma at 1× and 2× (retina); skip 3× unless device-targeted
- All marketing images → AVIF + WebP fallback, JPEG fallback for compatibility
- All icons → SVG, optimized via SVGO, no inline styles
- All images get a defined aspect ratio in code (prevents CLS)
- Naming: `hero-product-screen.webp` not `Group 47 copy.png`

## Accessibility annotations (designer responsibility)

Designer must specify:
- [ ] Heading order on every page (no decorative `<h2>`s)
- [ ] Color contrast ≥ 4.5:1 for body text, 3:1 for large text and UI
- [ ] Focus state for every interactive element
- [ ] Reduced-motion alternative for any animation > 200ms
- [ ] Logical reading order (especially for grid layouts)

## Handoff meeting agenda (45 min)

1. Walk through cover page + file structure (5 min)
2. Token export — show CSS / TS variables (5 min)
3. Component library — variants, props, states (15 min)
4. Page-by-page flow, focusing on edge cases (15 min)
5. Open questions + ownership for follow-up (5 min)

Always record + follow up with a written summary including:
- Decisions made
- Open questions with owners
- Linked spec docs
- Source-of-truth: "if Figma and code disagree, [Figma | code] wins"

## Anti-patterns

- "The Figma file *is* the spec" with no written notes
- One designer per page (inconsistency creeps in)
- Components built without published variants (devs improvise)
- Tokens defined per-page instead of globally
- "Make it look like the design" with no token map
- Designer changes Figma after handoff without notifying dev
- Multiple sources of truth (Figma + Storybook + Notion all stale)

## Tools

- **Tokens**: Tokens Studio, Style Dictionary
- **Inspect**: Figma Inspect panel, Dev Mode
- **Component docs**: Storybook (with Figma plugin to embed designs)
- **Diff over time**: Figma branching, Eraser
