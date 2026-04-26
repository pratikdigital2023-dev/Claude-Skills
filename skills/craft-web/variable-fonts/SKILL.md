---
name: variable-fonts
description: Ship variable fonts correctly — subsetting, font-display strategy, font-feature-settings, animated weight/width axes, FOIT/FOUT control, and self-hosting vs Google Fonts trade-offs. Use to get pixel-precise type at 60 fps without jank.
---

# Variable Fonts

Type is half of brand. A $50K site lives or dies by typography. Variable
fonts let you animate weight, width, and optical size as smoothly as
opacity, and they often weigh less than 2–3 static weights combined.

## When to use

- Brand uses 3+ weights / styles → variable file beats multiple statics
- Headlines need subtle weight animation on hover / scroll
- Optical sizes matter (fine type vs display)
- You want one HTTP request instead of six

## When NOT to use

- Single weight / style — ship a static woff2
- Browser support matters for IE11 (it doesn't, in 2026)
- Designer's font isn't available as variable

## Sourcing

- **Foundries**: most quality variable fonts cost money. Budget license fees.
- **Google Fonts**: many free variables (Inter, DM Sans, Manrope, Recursive)
- **Fontshare**: free for commercial use (Cabinet Grotesk, Satoshi)
- **GitHub**: many open-source variables (e.g., Inter, Roboto Flex)

Verify license per project — webfont vs app vs ad-impression terms differ.

## Self-host or CDN?

**Self-host** is the default for $50K-tier:
- Faster (no DNS lookup, no extra TLS handshake)
- Privacy (no Google Fonts cookie/IP exposure — required in EU after 2022 ruling)
- Full control over `font-display`
- Subsetting to exactly what you need

Use Google Fonts CDN only for prototypes.

## Subsetting (essential)

A full variable font with all axes + Latin + Cyrillic + symbols can be
500 KB+. Subset to your actual character set:

```bash
npx fonttools subset Inter.ttf \
  --output-file=Inter-subset.woff2 \
  --flavor=woff2 \
  --layout-features=kern,liga,calt,ss01,ss02 \
  --unicodes='U+0000-00FF,U+2000-206F,U+2070-209F'
```

Tools:
- `glyphhanger` — auto-detects what your site uses
- `pyftsubset` (fonttools) — manual control
- `wakamai-fondue` — inspect what's in a font

Target sizes:
- Latin only, single axis: 25–60 KB woff2
- Latin + Latin Ext + Cyrillic, two axes: 80–150 KB
- Anything over 200 KB → subset more aggressively

## @font-face (variable)

```css
@font-face {
  font-family: 'Inter';
  src: url('/fonts/Inter-Variable.woff2') format('woff2-variations');
  font-weight: 100 900;          /* range, not single value */
  font-stretch: 75% 125%;        /* if width axis */
  font-style: normal;
  font-display: swap;
}
```

`font-display`:
- `swap` — show fallback immediately, swap when font loads. **Default for body**.
- `optional` — use font only if cached. Best for performance, may not load on first visit.
- `block` — wait up to 3s for font (FOIT). Acceptable for branded display headlines.
- `fallback` — middle ground.

## Loading strategy

Preload critical fonts:
```html
<link rel="preload" href="/fonts/Inter-Variable.woff2" as="font" type="font/woff2" crossorigin>
```

Only preload fonts used above the fold. Each preload competes for
bandwidth.

For Next.js / Vite, use `next/font/local` or `unplugin-fonts` — they
automatically inline + preload + size-adjust.

## Size-adjust (avoid CLS)

When swapping from system font to webfont, line lengths shift → CLS.
Match metrics with `size-adjust`:

```css
@font-face {
  font-family: 'Inter-fallback';
  src: local('Arial');
  ascent-override: 90%;
  descent-override: 22%;
  line-gap-override: 0%;
  size-adjust: 107%;
}

body {
  font-family: 'Inter', 'Inter-fallback', system-ui, sans-serif;
}
```

Tools to compute these: `fontpie`, Capsize, `next/font` does it automatically.

## Using axes

Standard registered axes: `wght`, `wdth`, `slnt`, `ital`, `opsz`.
Custom axes are foundry-specific (e.g., Recursive's `MONO`, `CASL`).

```css
.headline {
  font-family: 'Inter';
  font-weight: 750;            /* anywhere in 100–900 */
  font-variation-settings: 'opsz' 32, 'wght' 750;
}
```

Note: `font-weight` and `font-variation-settings: 'wght'` can fight each
other. Use one consistently — most teams pick `font-weight` for normal
flow + `font-variation-settings` only when animating.

## Animating axes

```css
.btn {
  font-variation-settings: 'wght' 400;
  transition: font-variation-settings 0.3s ease;
}
.btn:hover {
  font-variation-settings: 'wght' 700;
}
```

Apple-style scroll-driven weight animation:
```js
gsap.to('.headline', {
  fontVariationSettings: '"wght" 900',
  scrollTrigger: { trigger: '.headline', scrub: 1, start: 'top 80%' }
})
```

Use sparingly — it's striking the first time, gimmicky the third.

## OpenType features

Most variable fonts ship with stylistic alternates. Enable per element:

```css
.numbers { font-feature-settings: 'tnum' 1, 'lnum' 1; }     /* tabular numerals */
.headline { font-feature-settings: 'ss01' 1; }              /* alt 'a' or whatever */
.body { font-feature-settings: 'kern' 1, 'liga' 1, 'calt' 1; }
```

Enable selectively per use case. Tabular numerals on data tables prevent
column wobble.

## Optical sizes

Fonts with `opsz` axis switch glyph design between display and text. Wire to size:

```css
.body { font-size: 16px; font-variation-settings: 'opsz' 16; }
.h1 { font-size: 96px; font-variation-settings: 'opsz' 96; }
```

Or use the `font-optical-sizing: auto` property (Chrome/Safari) — browser does it for you.

## Performance budget

- Total font CSS+files: < 150 KB initial load
- Max 2 font families
- Variable file replaces 3+ static weights
- Always woff2 (woff fallback only if you must support pre-2018 browsers)

## CLS / FOUT measurement

Lighthouse → "Avoid layout shifts from late-loading fonts". Metric:
shift caused by fallback swap. Target: 0 with size-adjust.

Test in throttled 3G + Slow CPU in DevTools.

## Common pitfalls

- Using full Google Fonts CDN with all axes (300 KB+ on first load)
- No subsetting → shipping Cyrillic to a US-only site
- `font-display: block` on body (3s blank text)
- Preloading 5 fonts (only preload above-fold critical ones)
- Mixing `font-weight: 700` with `font-variation-settings: 'wght' 700` (fights)
- Forgetting `crossorigin` on preload link (font won't actually be used)
- Self-hosting without `font-display` set (default is `block`)

## Tools

- `glyphhanger` — subset by site usage
- `wakamai-fondue` — font inspector
- `Variable Fonts` site (v-fonts.com) — browse + test
- `Font Style Matcher` — for fallback metrics
- `Capsize` (Seek) — leading + spacing math
- `next/font` / `astro:assets/fonts` — bundlers handle most of this

## Reference sites with great type

- vercel.com (Geist Variable)
- linear.app (Inter Variable)
- monospace.app
- nytimes.com (Imperial)
- typography labs: tomorrow.bg, anewall.com

## Pricing notes (for proposals)

- Type system + variable font integration: 6–12 hrs
- Custom subsetting + preload tuning: 4–8 hrs
- Fallback metric matching (zero-CLS): 2–4 hrs
- Foundry license fees: $200–2,000+ depending on traffic + family

## Anti-patterns

- Two non-variable weights when a variable file would be smaller
- Animating `font-variation-settings` on every element (jank)
- No fallback chain (system font sans-serif at minimum)
- Using `@import` in CSS for fonts (blocks render)
- Hosting on third-party CDN with no SLA
- Forgetting woff2 (only woff/ttf shipped — 30% larger)
- Loading italic + roman as separate variable files when an `ital` axis exists
