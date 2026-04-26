---
name: color-management-p3-hdr
description: Use modern color spaces (Display-P3 wide gamut, color-mix, OKLCH, HDR) on the web — when to use them, how to fall back gracefully, asset pipeline considerations, and brand-safe color tokens. Use when the brand demands the colors that sRGB literally cannot display.
---

# Color Management (Display-P3, OKLCH, HDR)

sRGB has been the web's color floor since 1996. Modern displays (every
Mac, iPhone, iPad, most premium Android, modern Windows laptops) show
**Display-P3** — about 25% more color than sRGB, especially in saturated
reds, greens, oranges. CSS Color 4 (Chrome 111+, Safari 15+, Firefox 113+)
finally lets us use it.

## Why this matters

A pure red Apple-tier brand on sRGB looks "fine"; on P3 it punches.
Without color management, the same hex code displays differently on
different screens. With it, you specify the color you want and the
browser handles the gamut.

## When to use

- Brand has saturated, vivid colors (especially reds, oranges, magentas, greens)
- Photography is shot/edited in Display-P3 or wider
- Hero treatments where color is the point
- The site renders on new MacBooks / iPhones (most of your audience)

## When NOT to use as required

- Brand uses muted / desaturated colors only — sRGB is fine
- Audience is dominantly Windows + older displays
- You can't audit on hardware that supports it

## Color spaces — quick reference

| Space | Gamut | Use |
|---|---|---|
| **sRGB** | small | legacy fallback, most assets |
| **Display-P3** | ~25% wider | modern displays, brand color |
| **Rec. 2020 / BT.2020** | very wide | HDR video, future |
| **OKLCH / OKLab** | perceptual | color math, palettes, gradients |
| **CIELAB / LCH** | perceptual (older) | similar role to OKLCH |

OKLCH is for *math* (computing palettes, gradients, contrast). P3 is for
*output* (telling the browser to use a wider gamut).

## CSS Color 4 syntax

```css
/* Display-P3 with sRGB fallback */
:root {
  --brand-red: #ff0033;                    /* sRGB fallback */
  --brand-red: color(display-p3 1 0 0.2);  /* P3 — overrides if supported */
}

/* OKLCH (perceptual) */
.btn { background: oklch(70% 0.2 25); }    /* L=70%, chroma=0.2, hue=25 */

/* Lab */
.alt { color: lab(70% 50 30); }

/* color-mix for hover/focus tints */
.btn:hover { background: color-mix(in oklch, var(--brand-red), black 10%); }
```

The cascading fallback pattern (line 1 then line 2) is the easiest way to
ship P3 without breaking older browsers.

## Display-P3 detection

```css
@media (color-gamut: p3) {
  :root { --brand: color(display-p3 1 0 0.2); }
}
```

Most modern setups don't need this — the cascading fallback above is enough.

## Gradients

Default gradients interpolate in sRGB → muddy middle ground (the famous
"gray middle" of red→blue). Specify the color space:

```css
.gradient {
  background: linear-gradient(in oklch, red, blue);
}
```

`in oklch` or `in oklab` give perceptually smooth gradients. `in srgb`
(default) gives the muddy classic look. Test side by side — the
difference is dramatic.

## color-mix() (the most useful new function)

Compute hover/focus/disabled states without preprocessor:
```css
:root { --brand: oklch(60% 0.2 250); }

.btn { background: var(--brand); }
.btn:hover    { background: color-mix(in oklch, var(--brand), white 10%); }
.btn:active   { background: color-mix(in oklch, var(--brand), black 10%); }
.btn:disabled { background: color-mix(in oklch, var(--brand), gray 50%); }
```

No more `lighten()` SCSS functions. CSS does it natively + perceptually.

## Building a token system

```css
:root {
  /* Brand source */
  --brand-h: 250;
  --brand-c: 0.2;
  --brand-l: 60%;

  /* Computed palette */
  --brand-50:  oklch(95% calc(var(--brand-c) * 0.2) var(--brand-h));
  --brand-100: oklch(90% calc(var(--brand-c) * 0.4) var(--brand-h));
  --brand-500: oklch(var(--brand-l) var(--brand-c) var(--brand-h));
  --brand-900: oklch(20% calc(var(--brand-c) * 0.5) var(--brand-h));

  /* P3 brand */
  --brand-vivid: color(display-p3 0.2 0.3 1);
}
```

Adjust hue once → entire palette shifts perceptually correctly.

## Image assets

- Photography exported as Display-P3 JPEG (Photoshop: Save As → Color Profile: Display P3)
- WebP supports color profiles — preserve them
- AVIF supports wider gamuts natively
- Don't strip color profiles in image optimization (some optimizers do — verify)

Check an image's profile:
```bash
exiftool image.jpg | grep -i profile
identify -verbose image.jpg | grep -i colorspace
```

## HDR (still emerging)

HDR on the web is real but limited:
- HDR images: AVIF + JPEG XL with HDR metadata
- HDR video: VP9 / AV1 with proper metadata, `<video>` tag
- HDR canvas: Chrome 130+ via `colorSpace: 'rec2100-hlg'` on canvas
- CSS HDR: experimental as of 2026

For now, treat HDR as a hero-only enhancement on Safari/Chrome with
graceful fallback.

## Contrast + accessibility

Wider gamut doesn't change contrast ratios — WCAG AA (4.5:1 body, 3:1
large) still applies. Use APCA (the proposed WCAG 3 contrast formula)
for more accurate perception:

```js
import { APCAcontrast, sRGBtoY, displayP3toY } from 'apca-w3'
```

Tools: Stark, contrast.tools, APCA online checker.

## Color picker tooling

- **Apple Digital Color Meter** — sample any pixel
- **Sip** (Mac) — picker that knows about P3
- **Figma** — supports P3 since 2024
- **OKLCH.com** — visual OKLCH picker
- **Polypane** — preview gamut differences

Avoid generic eyedroppers that show only sRGB.

## Verify on real hardware

Color management is invisible until you compare:
- Open same page on a 2018 ThinkPad (sRGB) and a 2023 MacBook (P3)
- Check hero color — does it pop on Mac without breaking on PC?
- Photography — does skin tone hold up?
- Print → browser comparison if applicable

## Common pitfalls

- Specifying P3 without sRGB fallback → broken on older browsers
- Using `oklch()` in a hex/HSL workflow without conversion (math is different)
- Stripping color profiles during image optimization
- Designing in Figma sRGB then expecting P3 punch in browser
- Not testing on Windows/PC (P3 is mac-centric)
- Mixing `color-mix(in srgb, ...)` with OKLCH design tokens (interpolation mismatch)
- Trusting the browser DevTools color picker — many show sRGB only

## Tooling integration

- **Tailwind v4** — supports OKLCH + P3 native
- **Open Props** — color tokens in modern spaces
- **Radix Colors** — has P3 versions
- **CSS preprocessors** — generally pass through CSS Color 4 syntax untouched

## Reference sites

- apple.com (vivid product hero colors in P3)
- linear.app (OKLCH design system)
- many AAA gaming sites
- editorial sites with photography (NYT, The Verge feature articles)

## Pricing notes (for proposals)

- Audit + token migration to OKLCH/P3: 8–16 hrs
- Photography pipeline (P3 export + verify): 2–4 hrs per asset batch
- Design+dev parity verification across hardware: 4–8 hrs

## Anti-patterns

- P3 colors with no sRGB fallback (broken in older browsers)
- Mixing color spaces in gradients (`linear-gradient(red, oklch(...))` — undefined)
- Photography stripped of profile (loses gamut on export)
- Not auditing on actual hardware
- "P3 makes it pop" without measuring — many brands look identical
- Using OKLCH math then outputting hex (round-trip loses precision)
- Forgetting Windows / Android still dominate global traffic
