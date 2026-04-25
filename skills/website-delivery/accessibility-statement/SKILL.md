---
name: accessibility-statement
description: Publish a WCAG 2.2 AA conformance statement that documents the site's accessibility status, known issues, testing methods, and feedback channel. Use before launch to satisfy ADA, EAA (June 2025), Section 508, and AODA requirements.
---

# Accessibility Statement

A required document under the European Accessibility Act (effective June
28, 2025), AODA (Ontario), Section 508 (US federal), and increasingly
expected for ADA Title III compliance. Also serves as a public commitment
to your users.

## When to use

- Pre-launch (always)
- After significant redesign
- After accessibility audit + remediation
- When a customer / regulator asks for one

## Standard to target

| Standard | When to target |
|---|---|
| **WCAG 2.2 AA** | Default for new sites in 2025+ |
| **WCAG 2.1 AA** | Acceptable but lagging |
| **WCAG 2.2 AAA** | Aspirational; some success criteria are subjective or cost-prohibitive |
| **EN 301 549** | EU public sector + EAA (essentially WCAG 2.1 AA + extras) |
| **Section 508** | US federal (refers to WCAG 2.0 AA + extras) |

For a $50K commercial project: **WCAG 2.2 AA** is the right target.

## Required content

Every accessibility statement should include:

### 1. Conformance level
> "This site aims to conform to WCAG 2.2 Level AA."

State whether you fully conform, partially conform, or don't conform yet.
Honesty is a legal defense; misrepresentation is a liability.

### 2. Scope
- Which URLs are covered (e.g., "all pages on www.acme.com except legacy
  blog posts at /old-blog/*")
- Which technologies (HTML, JS, PDFs, video)
- Date of statement + last review date

### 3. Testing methods
- Automated tools used (axe DevTools, Lighthouse, WAVE, Pa11y)
- Manual testing (keyboard navigation, screen reader testing — name
  which: NVDA, JAWS, VoiceOver, TalkBack)
- User testing with people with disabilities (if conducted)
- Date of last audit + name of auditor (internal or external firm)

### 4. Known issues
List specific known accessibility barriers honestly:
- Component / page affected
- WCAG criterion failed
- Workaround if any
- Planned remediation date

Example:
```
- /products/legacy-printer-2010
  Failure: 1.4.3 Contrast (Minimum) — header text contrast 3.2:1
  Workaround: high-contrast mode toggle available
  Planned fix: page being deprecated Q3 2025
```

### 5. Feedback mechanism
- Email address (e.g., accessibility@acme.com)
- Phone (if available)
- Form link
- Postal address
- **Response SLA** — commit to a timeframe (typical: 5 business days)

### 6. Enforcement contact (region-dependent)
- **EU**: link to user's national supervisory authority
- **US Federal**: Department of Justice / agency contact
- **Ontario (AODA)**: Ministry contact

### 7. Alternatives
If something can't be made accessible, offer an alternative:
- Phone-in ordering for a checkout flow that has issues
- Accessible PDF version of an inaccessible interactive document
- Chat / human assistance

## Example statement template

```markdown
# Accessibility Statement for Acme

Last updated: April 25, 2025

## Our commitment
Acme is committed to ensuring digital accessibility for people with
disabilities. We are continually improving the user experience for everyone
and applying the relevant accessibility standards.

## Conformance status
The Web Content Accessibility Guidelines (WCAG) define requirements for
designers and developers to improve accessibility for people with
disabilities. They define three levels of conformance: Level A, Level AA,
and Level AAA.

This website is **partially conformant** with WCAG 2.2 Level AA.
Partially conformant means that some parts of the content do not fully
conform to the accessibility standard.

## Scope
This statement applies to www.acme.com, including all pages under the
primary domain. PDF documents under /resources/ are being remediated and
will reach conformance by Q3 2025.

## Testing approach
- Automated: axe DevTools (latest), Lighthouse 11
- Manual: keyboard-only navigation, NVDA + Firefox, VoiceOver + Safari
- User testing: scheduled annually with a third-party panel of users with
  disabilities
- Last full audit: March 1, 2025 by [Auditor Name / Firm]

## Known issues
- PDF documents predating January 2024 may not have a proper reading order.
  HTML alternatives are available; contact us for any specific document.
- Video content lacks audio descriptions. Captions are available on all
  videos. Audio descriptions will be added by Q4 2025.

## Feedback
We welcome your feedback on the accessibility of Acme. Contact us:
- Email: accessibility@acme.com
- Phone: +1 555 555 5555
- Form: https://acme.com/accessibility-feedback

We aim to respond to feedback within 5 business days.

## Enforcement
[Region-specific authority contact details]
```

## Where to publish

- Footer link: "Accessibility" or "Accessibility Statement"
- Direct URL: `/accessibility` (canonical)
- Linked from contact page
- Linked from your sitemap

## Audit frequency

- Annual full audit minimum (third-party preferred)
- Continuous automated testing in CI (axe-core via Pa11y)
- Re-audit after significant redesign

## Related work (be honest in the statement about these)

To support an accessibility statement, the site itself needs:

### Technical baseline
- Semantic HTML (use `<button>` not `<div onClick>`)
- Logical heading order (one `h1`, no skipped levels)
- Alt text on every meaningful image; `alt=""` on decorative
- Keyboard navigable (every interactive element reachable + visible focus)
- Focus rings not removed (or replaced with custom equivalents)
- Color contrast 4.5:1 (3:1 for large text + UI components)
- ARIA only when semantic HTML can't do the job
- Skip-to-content link
- Language attribute (`<html lang="en">`)
- Form fields with associated `<label>`s
- Error messages associated with fields (`aria-describedby`)
- Captions on video, transcripts on audio
- No autoplay video with sound

### Process
- Component library passes axe in Storybook
- Lighthouse CI gates accessibility score
- Manual keyboard test on every release
- Screen reader smoke test on each major release

## Pre-launch checklist

- [ ] Statement live at `/accessibility`
- [ ] Footer link present on every page
- [ ] Conformance level stated honestly (with caveats)
- [ ] Known issues listed with remediation dates
- [ ] Feedback email monitored
- [ ] SLA stated and team committed to it
- [ ] Enforcement authority listed for relevant jurisdictions
- [ ] Last reviewed date is current

## Anti-patterns

- "We are fully WCAG 2.2 AA compliant" with no audit basis (legal liability)
- No known-issues section ("there must be some — disclose them")
- Generic / templated statement that doesn't reference your site
- Feedback email goes to an unmonitored alias
- "We are working on accessibility" with no timeline (regulators want dates)
- No statement at all (mandatory in EU under EAA)
- Hidden in legal/utility footer cluster — make it findable

## Tools / auditors

- **Self-audit tooling**: axe DevTools, Lighthouse, WAVE, Pa11y CI
- **Audit firms**: Deque, Level Access, TPGi, Knowbility (US); AbilityNet
  (UK); Accessible Web (multi-region)
- **User testing panels**: Fable, Applause, Knowbility

## Pricing notes (for proposals)

- Self-authored statement: 2–4 hours of work (free)
- Third-party WCAG audit: $4K–25K depending on scope
- Annual recurring audit: $3K–10K
- Remediation: variable — budget 10–20% of build cost for retrofits
