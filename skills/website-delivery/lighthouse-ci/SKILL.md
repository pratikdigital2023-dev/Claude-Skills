---
name: lighthouse-ci
description: Add Lighthouse CI to a website's pipeline to enforce performance, accessibility, SEO, and best-practice budgets on every PR. Use to lock Core Web Vitals before launch and prevent regressions afterward.
---

# Lighthouse CI

If you don't gate performance in CI, it regresses. Every release adds a
script, an image, a font — and LCP creeps from 1.8s to 4.2s without anyone
noticing until traffic drops.

## When to use

- Pre-launch (always, even if simple)
- After a performance audit identified specific regressions
- When Core Web Vitals are a contractual SLA
- Sites where SEO ranking depends on speed (everyone)

## What it gates

| Category | Default thresholds |
|---|---|
| Performance | ≥ 0.90 |
| Accessibility | ≥ 0.95 |
| Best Practices | ≥ 0.95 |
| SEO | ≥ 1.00 |
| LCP | ≤ 2500ms |
| CLS | ≤ 0.10 |
| INP | ≤ 200ms |
| TBT | ≤ 200ms |

## Setup (Vercel + Next.js + GitHub Actions)

```bash
npm install -D @lhci/cli
```

`lighthouserc.cjs`:
```js
module.exports = {
  ci: {
    collect: {
      url: [
        'https://acme-preview.vercel.app/',
        'https://acme-preview.vercel.app/pricing',
        'https://acme-preview.vercel.app/products',
        'https://acme-preview.vercel.app/blog/sample',
      ],
      numberOfRuns: 3,
      settings: {
        preset: 'desktop',  // run separately for mobile
        throttlingMethod: 'simulate',
      },
    },
    assert: {
      preset: 'lighthouse:recommended',
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'categories:best-practices': ['error', { minScore: 0.95 }],
        'categories:seo': ['error', { minScore: 1.0 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'interaction-to-next-paint': ['warn', { maxNumericValue: 200 }],
        'total-blocking-time': ['error', { maxNumericValue: 200 }],
        // Page-weight budgets
        'resource-summary:script:size': ['warn', { maxNumericValue: 250000 }],
        'resource-summary:image:size': ['warn', { maxNumericValue: 500000 }],
        'resource-summary:total:size': ['warn', { maxNumericValue: 1500000 }],
        // Disable noisy ones if needed
        'unused-javascript': 'off',
        'uses-text-compression': ['warn', {}],
      },
    },
    upload: {
      target: 'temporary-public-storage',
      // For self-hosted server: target: 'lhci', serverBaseUrl: 'https://lhci.acme.com', token: process.env.LHCI_TOKEN
    },
  },
}
```

## GitHub Actions workflow

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI
on:
  pull_request:
  push:
    branches: [main]

jobs:
  lhci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - name: Wait for Vercel preview
        uses: patrickedqvist/wait-for-vercel-preview@v1.3.1
        id: preview
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          max_timeout: 180
      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli@0.13.x
          PREVIEW_URL="${{ steps.preview.outputs.url }}" lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
```

Modify URLs to use the preview URL dynamically (env interpolation in the
LHCI config).

## Run modes

- **Desktop only** — fast, enforces minimums; run on every PR
- **Mobile** — slower, more representative; run nightly + on main
- **Real device** — only via WebPageTest / paid tools, not LHCI

## Performance budgets per page type

Don't enforce one budget across all pages. Set per-template:
| Template | Performance | LCP target |
|---|---|---|
| Marketing home | 0.95 | 2000ms |
| Product detail | 0.90 | 2500ms |
| Blog post | 0.95 | 2200ms |
| Search results | 0.85 | 3000ms |
| Checkout | 0.90 | 2500ms (also INP < 200ms hard) |

Multiple `lighthouserc` configs or array of pages with per-page assertions.

## Common LCP fixes

| Symptom | Fix |
|---|---|
| Hero image > 2s | `priority` on `next/image`, AVIF, correct `sizes`, preload font |
| Big JS bundle blocks paint | Code-split, lazy-load non-critical, defer 3rd-party |
| Web fonts FOIT | `font-display: swap`, preload, self-host |
| TTFB > 800ms | ISR / SSG instead of SSR, edge runtime, faster origin |
| 3rd party tracking | Load post-LCP, defer GTM, use Partytown |

## Common CLS fixes

- Reserve space for images: `width` + `height` always set
- Reserve space for ads: container with min-height
- Reserve space for late-loading content (hero text revealed by JS)
- Avoid auto-injected banners that push content down (cookie banners
  should be sticky overlays)
- Web fonts: use `size-adjust` to match fallback metrics, or self-host

## Common INP fixes

- Break up long tasks: `setTimeout(() => {}, 0)` or `scheduler.yield()`
- Remove unused JS (especially heavy 3rd-party SDKs)
- Move heavy work to web workers
- Defer non-critical event handlers
- Hydration: use React Server Components / Astro islands to skip client JS

## Reporting

LHCI uploads each run's report. Two destinations:
- `temporary-public-storage` — free, expires in days, fine for PR comments
- Self-hosted LHCI server — historical trend, costs ~$10/mo (Render/Fly)

Add a status check + a PR comment with score deltas. The LHCI GitHub App
(Lighthouse CI) does this automatically.

## Manual checks LHCI doesn't catch

- **Real-world LCP** — test on a 4G phone, not lab
- **Bundle analysis** — `@next/bundle-analyzer` to spot fat dependencies
- **Third-party perf** — check `https://www.webpagetest.org/` for waterfall
- **CrUX** — monitor real-user data via Chrome User Experience Report

## Anti-patterns

- Setting all assertions to `warn` (CI never fails → regressions ship)
- Running on production URL (slow + flaky; use preview URL)
- One run per page (high variance; always `numberOfRuns: 3`)
- Ignoring INP because "it's new" (it replaced FID in March 2024)
- Gaming Lighthouse with synthetic accessibility (axe + manual still needed)
- Disabling all SEO checks because client doesn't care (until they do)

## Pricing notes (for proposals)

- LHCI itself: free
- Hosting an LHCI server: ~$10/mo
- Time to set up: 4–8 hours
- Time to remediate to pass thresholds: highly variable (10–60 hours)

For a $50K project, **always include LHCI** in the build cost. Won't ship
on time without it.
