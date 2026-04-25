---
name: cross-browser-matrix
description: Define and execute a cross-browser / cross-device test matrix using BrowserStack, Sauce Labs, or local Playwright. Covers which browser/OS/viewport combinations to support, how to test efficiently, and what to do when something only breaks in one environment.
---

# Cross-Browser Test Matrix

You can't test on every browser × OS × device. Pick a defensible matrix
based on your actual users (analytics), then automate what you can and
manually test what you can't.

## When to use

- Pre-launch QA phase
- After a major redesign or framework upgrade
- After a bug report from a specific browser
- When supporting an enterprise client with locked-down IT

## Step 1: pick the matrix

Pull from analytics:
- GA4 → Tech → Browser → top 5 by sessions
- GA4 → Tech → Operating System → top 4
- GA4 → Tech → Screen Resolution → top 5

For most US/EU consumer sites in 2025+, the matrix looks like:

### Browsers (latest + 1 prior)
- Chrome
- Safari
- Firefox
- Edge

### OS
- macOS (latest + 1 prior)
- Windows 11 (and 10 if traffic warrants)
- iOS (latest + 1 prior)
- Android (latest + 1 prior)

### Viewports
- Desktop: 1440×900 (most common), 1920×1080, 1280×800
- Tablet: 768×1024 (iPad)
- Mobile: 390×844 (iPhone 14/15), 360×800 (Android typical)

## Recommended primary matrix (the 12 you actually run)

| # | Browser | OS | Viewport |
|---|---|---|---|
| 1 | Chrome (latest) | macOS | 1440×900 |
| 2 | Chrome (latest) | Windows 11 | 1920×1080 |
| 3 | Safari (latest) | macOS | 1440×900 |
| 4 | Safari Mobile (latest) | iOS 17 | iPhone 14 |
| 5 | Safari Mobile (prev) | iOS 16 | iPhone 13 |
| 6 | Chrome Mobile | Android 14 | Pixel 7 |
| 7 | Chrome Mobile | Android 13 | Samsung Galaxy S22 |
| 8 | Firefox (latest) | Windows 11 | 1920×1080 |
| 9 | Edge (latest) | Windows 11 | 1920×1080 |
| 10 | Chrome (latest) | Windows 11 | 1280×800 |
| 11 | Safari Tablet | iPadOS 17 | iPad Pro |
| 12 | Chrome (prev) | macOS | 1440×900 |

Adjust based on your traffic. If 30% of your users are on Edge (B2B
enterprise), bump it up.

## Step 2: distinguish automated vs manual

| Test | Method |
|---|---|
| Layout / responsive at common viewports | Visual regression (Chromatic, Percy) |
| Critical user flows (signup, checkout) | Playwright across browsers |
| Component states (hover, focus, active) | Storybook + Chromatic |
| Form submission edge cases | Playwright |
| Real touch interactions | Manual on real device |
| iOS-specific quirks (safe area, scroll bounce) | Manual on real iPhone |
| Print stylesheet | Manual |
| Print to PDF | Manual |
| Screen reader | Manual (NVDA, JAWS, VoiceOver) |

Rule: **automate the boring stuff, manually test the weird stuff.**

## Step 3: run automated tests

### Playwright (multi-browser)
```ts
// playwright.config.ts
export default {
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'webkit',   use: { ...devices['Desktop Safari'] } },
    { name: 'firefox',  use: { ...devices['Desktop Firefox'] } },
    { name: 'mobile-safari', use: { ...devices['iPhone 14'] } },
    { name: 'mobile-chrome', use: { ...devices['Pixel 7'] } },
  ],
  reporter: 'html',
}
```

Run: `npx playwright test --project=mobile-safari`

### BrowserStack / Sauce Labs (real devices)

Use when:
- You don't have a Mac (need Safari)
- You don't have an iPhone (need real iOS)
- Bug reproduces only on a specific device
- Compliance requires evidence of real-device testing

Setup:
1. BrowserStack account ($30+/mo)
2. Pipe Playwright tests via their grid
3. Or use **BrowserStack Live** for manual screenshare-style testing

```ts
// Via BrowserStack SDK
use: {
  // ...
  connectOptions: { wsEndpoint: `wss://cdp.browserstack.com/playwright?...` },
}
```

## Step 4: fix browser-specific bugs

### Common Safari issues
- `gap` in flexbox (older Safari versions)
- `100vh` includes the browser chrome (use `100dvh` or `100svh`)
- `position: sticky` inside `overflow: auto` may not work
- Date inputs styled differently
- Some CSS animations clip at edges
- iOS scroll bounce overscroll (use `overscroll-behavior: none`)
- `:has()` selector landed in 15.4 — feature-detect

### Common Firefox issues
- `scroll-behavior: smooth` works but feels different
- Form autofill colors override `:autofill` selector
- `text-wrap: balance` not yet (as of late 2024)
- `backdrop-filter` on some older versions

### Common Chrome on Android issues
- Safe areas / notches handled differently
- Pull-to-refresh interferes with sticky elements
- Soft keyboard pushes viewport (use Visual Viewport API)

### Common Edge issues
- Mostly Chrome at this point — parity is high
- Edge-specific bugs are rare; usually IE polyfills mistakenly enabled

## Step 5: feature-detect, don't user-agent-sniff

```js
// GOOD
if (CSS.supports('selector(:has(*))')) { ... }
if ('IntersectionObserver' in window) { ... }

// BAD
if (navigator.userAgent.includes('Safari')) { ... }
```

For CSS:
```css
@supports (text-wrap: balance) {
  h1 { text-wrap: balance; }
}
@supports not (text-wrap: balance) {
  h1 { /* fallback */ }
}
```

## Step 6: progressive enhancement strategy

For sites that must support older browsers:
- **HTML works without JS** (forms POST, links navigate)
- **CSS Grid + Flexbox**: with fallbacks for ancient browsers (rare in 2025)
- **Modern features**: behind `@supports`
- **Polyfills**: only for actively used target browsers, lazy-loaded

Browser support targets in `package.json`:
```json
"browserslist": [
  ">0.5%",
  "not dead",
  "not op_mini all",
  "last 2 versions"
]
```

## Step 7: visual regression tests

Catches layout bugs you wouldn't notice manually. Tools:
- **Chromatic** (Storybook integration, $$)
- **Percy** (BrowserStack)
- **Playwright snapshots** (free, in your repo)

```ts
test('homepage layout', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveScreenshot('homepage-desktop.png', { maxDiffPixelRatio: 0.01 })
})
```

Run on: Chromium desktop, Webkit mobile, at minimum.

## Step 8: manual smoke test on real devices

For each release, manually exercise on at least:
- 1 real iPhone (latest iOS)
- 1 real Android (latest)
- 1 desktop browser the team doesn't use daily

20-minute checklist:
- Navigate every primary section
- Tap every CTA
- Submit one form
- Open one video
- Use the mobile menu
- Check landscape orientation
- Background and resume the app
- Resize the browser window

## Pre-launch checklist

- [ ] Matrix defined + signed off based on analytics
- [ ] Playwright tests passing on top 3 browser projects
- [ ] Visual regression baseline captured
- [ ] BrowserStack / Sauce Labs runs clean on real devices
- [ ] Manual test on real iPhone + Android done
- [ ] Known browser-specific bugs documented + acceptable
- [ ] Feature-detect (not UA-sniff) audit done
- [ ] `browserslist` in package.json reflects actual support targets

## Anti-patterns

- Testing only on Chrome on a Mac (your team's bubble)
- Testing only at one viewport
- User-agent sniffing instead of feature detection
- "We support modern browsers" with no defined matrix
- No real-device testing (emulators miss touch + Safari quirks)
- Treating a Chrome-only bug as Chrome's fault, not your code's
- Visual regression baselines auto-updated without review (silent breaks)

## Pricing notes (for proposals)

- Playwright: free, runs locally and CI
- BrowserStack: $30+/mo per parallel session
- Chromatic: free up to 5K snapshots/mo, $149+/mo otherwise
- LambdaTest: ~$15/mo (cheapest cloud grid option)

For a $50K project: budget $50/mo for cross-browser tooling for the first
year.
