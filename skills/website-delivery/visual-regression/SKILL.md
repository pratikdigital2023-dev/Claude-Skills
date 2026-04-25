---
name: visual-regression
description: Set up automated visual regression testing using Chromatic (Storybook), Percy, or Playwright snapshots. Catches unintended visual changes on every PR. Use to prevent CSS regressions in component libraries and on critical pages.
---

# Visual Regression Testing

A 1px shift in a navbar might be intentional or might be a bug. Visual
regression tests catch the difference automatically and force a human to
approve or fix.

## When to use

- Component libraries / design systems (must-have)
- Marketing sites with frequent edits
- After a CSS / Tailwind upgrade
- After a designer hands off a token change

## Decision: which tool

| Tool | Best for | Cost |
|---|---|---|
| **Chromatic** | Component-level (Storybook) | Free 5K snaps/mo, then $149+/mo |
| **Percy** | Page-level + Cypress / Playwright | Free 5K, $200+/mo |
| **Playwright snapshots** | In-repo, free, full control | Free, more maintenance |
| **Lost Pixel** | Open-source alternative to Percy | Free (self-host) |
| **BackstopJS** | OG OSS option, declining | Free |

For most $50K projects: **Chromatic** if you have Storybook (component
library), **Playwright snapshots** otherwise.

## Pattern A: Storybook + Chromatic

If you maintain a component library:
1. Build every component as a Storybook story
2. Story exports represent every visual variant + state
3. Chromatic snaps each story on every PR
4. Diff against last approved baseline
5. PR check passes only when changes are reviewed and accepted

```ts
// Button.stories.tsx
export default { component: Button }
export const Primary = { args: { variant: 'primary', children: 'Click me' } }
export const Loading = { args: { variant: 'primary', loading: true, children: 'Loading' } }
export const Disabled = { args: { variant: 'primary', disabled: true, children: 'Disabled' } }
export const FullWidth = { args: { variant: 'primary', fullWidth: true, children: 'Full' } }
```

Each export = a snapshot. Coverage = product of (variant × state × size).

```yaml
# .github/workflows/chromatic.yml
- uses: chromaui/action@v11
  with:
    projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
    onlyChanged: true
    exitZeroOnChanges: false  # fail PR until reviewed
```

## Pattern B: Playwright snapshots

For page-level tests without a Storybook:
```ts
// tests/visual.spec.ts
import { test, expect } from '@playwright/test'

const viewports = [
  { name: 'desktop', size: { width: 1440, height: 900 } },
  { name: 'tablet', size: { width: 768, height: 1024 } },
  { name: 'mobile', size: { width: 390, height: 844 } },
]

for (const vp of viewports) {
  test(`homepage ${vp.name}`, async ({ page }) => {
    await page.setViewportSize(vp.size)
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    await page.evaluate(() => document.fonts.ready)
    await expect(page).toHaveScreenshot(`home-${vp.name}.png`, {
      fullPage: true,
      maxDiffPixelRatio: 0.01,
      animations: 'disabled',
    })
  })
}
```

Snapshots commit to `tests/__screenshots__/` directory. Diff results are
shown in the Playwright HTML report.

## Stable snapshot recipes

### Disable animations
```css
/* tests/_visual.css — inject in test pages */
*, *::before, *::after {
  animation: none !important;
  transition: none !important;
}
```

In Playwright config:
```ts
use: { animations: 'disabled' }
```

### Wait for fonts
```ts
await page.evaluate(() => document.fonts.ready)
```

### Wait for images
```ts
await page.waitForLoadState('networkidle')
// Or wait for specific images
await page.waitForFunction(() =>
  Array.from(document.images).every(img => img.complete && img.naturalHeight > 0)
)
```

### Mask dynamic content
```ts
await expect(page).toHaveScreenshot({
  mask: [
    page.locator('[data-testid="timestamp"]'),
    page.locator('.live-counter'),
    page.locator('iframe'),  // 3rd party widgets
  ],
})
```

### Stable random data
- Set fixed seeds for any RNG
- Mock `Date.now()` if used in render
- Pin demo data in fixtures

## Coverage strategy

Don't try to snapshot everything. Snapshot:
1. **Every component variant** in your design system
2. **Every page template** (home, product, blog, contact, 404)
3. **Critical states** (loading, error, empty, success)
4. **Each viewport** (desktop, tablet, mobile)

Skip:
- One-off marketing pages with unique content (high false-positive rate)
- Components with too much randomness (carousels with random order)
- Iframe-heavy pages (3rd party content varies)

## CI integration

Block PR merges on visual regression failure:
```yaml
- name: Run visual tests
  run: npx playwright test tests/visual.spec.ts
- name: Upload snapshots on failure
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: visual-diff
    path: test-results/
```

For Chromatic, the GitHub status check appears on every PR with a link to
the diff UI for review.

## Reviewing diffs

Each diff gets one of three actions:
- **Accept**: change is intentional → new baseline
- **Reject**: change is a bug → revert / fix
- **Review later**: defer (don't merge until decided)

Bake into PR checklist: "Visual regression diffs reviewed and accepted/fixed."

## Updating baselines

When you intentionally change visuals:
```bash
# Playwright
npx playwright test --update-snapshots

# Chromatic
# Click "Accept all" in the build UI
```

**Never auto-accept in CI.** That defeats the entire purpose.

## Tackling flake

Visual tests can be flaky. Sources + fixes:

| Source | Fix |
|---|---|
| Font rendering (sub-pixel) | `maxDiffPixelRatio: 0.01` (allow tiny diffs) |
| Animation in flight | `animations: 'disabled'` |
| Timestamps / live data | mask the locator |
| Loading skeletons | wait for `networkidle` + actual content |
| 3rd party widgets | mask or stub |
| Different OS (CI vs local) | run baselines from CI Linux Docker |

If you can't kill flake, raise `maxDiffPixelRatio` slightly — but never above
0.05 (you'll miss real bugs).

## Pre-launch checklist

- [ ] Tool chosen + integrated in CI
- [ ] Every component / page template snapshotted
- [ ] Snapshots taken on Linux (CI environment) for reproducibility
- [ ] Animations + dynamic content stabilized
- [ ] PR check fails on unreviewed changes
- [ ] Process for accepting baseline changes is documented
- [ ] Baseline images committed to repo (or stored in tool)

## Anti-patterns

- Auto-accepting all changes in CI (defeats the purpose)
- Snapshotting unstable pages (gives up after 5 false positives)
- Local-only baselines (different OS = different rendering)
- One mega-snapshot per page (hard to spot which component changed)
- Snapshotting full-page on infinite scroll (massive images, useless diff)
- Ignoring repeated false positives (real bugs hide in the noise)
- Visual tests without a real "what changed" review process

## Pricing notes (for proposals)

- Chromatic: free 5K snapshots/mo (most $50K projects fit)
- Percy: free 5K snapshots/mo
- Playwright: free
- Self-hosted Lost Pixel: free + ~$10/mo infra

For most builds: Playwright snapshots locally + Chromatic for design
system components.
