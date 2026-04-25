---
name: wireframe-spec
description: Produce annotated low-fidelity wireframes that lock content priority and component decisions before visual design. Use after sitemap and journeys are approved, before high-fidelity design. Catches structural issues when they're cheap to fix.
---

# Wireframe Spec

Wireframes are not "ugly mockups." They're a contract about what each page
contains, in what order, with what hierarchy — independent of how it looks.
Locking wireframes before high-fidelity design saves 2–5x rework.

## When to use

- After sitemap and journey maps are approved
- Before any visual/brand design
- For any new page template or significantly redesigned page

## Fidelity choice

| Lo-fi (sketch / boxes) | Mid-fi (FigJam / Whimsical) | Hi-fi wireframe (Figma) |
|---|---|---|
| Speed: hours | Speed: days | Speed: 1–2 wk |
| Use for: brainstorming | Use for: stakeholder review | Use for: dev handoff |

For a $50K project, **mid-fi is usually right.** Skip lo-fi unless the team
needs creative exploration; skip hi-fi wireframes if you go straight to
design comps.

## What every wireframe includes

For each page template (not every page — templates):
1. **Page name + URL pattern**
2. **Primary user goal** (one sentence)
3. **Primary CTA** (one)
4. **Content blocks in priority order** — top to bottom
5. **Per-block notes**:
   - Block name (e.g. "hero", "social-proof", "pricing-table")
   - Purpose (why is this here)
   - Content type (headline, body copy, image, video, form, list)
   - Required fields (CMS implication)
   - Component reference (use existing or new?)
   - Behavior (sticky? collapsible? lazy-loaded?)

## Block library

Standardize on a finite set of blocks. A typical site needs ~15:
- Hero (with eyebrow, headline, sub, primary CTA, secondary CTA, media)
- Logo cloud
- Feature grid (2/3/4 column)
- Feature row (alternating image-text)
- Stats / metrics
- Testimonial (single, slider, grid)
- Comparison table
- FAQ (accordion)
- CTA banner
- Newsletter / lead form
- Pricing table
- Team grid
- Timeline / process
- Blog / resource grid
- Footer

If a designer proposes a 16th block, push back hard. Custom blocks blow up
both design and CMS budgets.

## Annotation conventions

Standard annotations (keep them minimal and consistent):
- 🅐 **Anchor** — links from elsewhere on the site
- 🆄 **Utility** — functionality a developer needs to know about
- 🅼 **Mobile** — only behavior that differs on mobile
- 🅻 **Logic** — conditional rendering
- 🅰 **Accessibility** — keyboard / screen-reader notes
- 🅷 **Heading level** — H1/H2/H3 explicit, never decorative

Example:
```
[Hero block]
🅷 H1: "Ship faster with [product]"
🅻 If user is logged in: replace primary CTA with "Open dashboard"
🅼 Stack image below text on < 768px
🅰 Background gradient must not reduce text contrast below 4.5:1
🆄 Hero image lazy-loads with blur placeholder
```

## Handoff package

For each template, deliver:
1. **The wireframe** (Figma frame or Whimsical board)
2. **Block-by-block spec** (in the wireframe or a paired doc)
3. **Content requirements** (copy length, image count, video specs)
4. **Component map** (which existing design-system components to use)
5. **Open questions** (decisions still needed)

## Approval gate

Before moving to visual design, get explicit sign-off on:
- [ ] Page hierarchy (top-to-bottom block order)
- [ ] Primary CTA per page
- [ ] Block library (no surprises later)
- [ ] Mobile structural changes
- [ ] Required content fields per template

If the client wants to "see what it looks like" before approving wireframes,
explain that visual decisions made before structure is locked are throwaway
work.

## Common mistakes

- Drawing wireframes that look like designs (use boxes, not real images)
- One mega-template instead of templates by purpose
- Designing for content that doesn't exist yet (always check copy length)
- Forgetting the empty / loading / error states
- Not specifying mobile behavior for components that change significantly
- Treating wireframes as "draft designs" instead of structural contracts

## Don't forget the system pages

Easy to skip, easy to regret:
- 404 / error
- Search results
- Empty state
- Loading state
- Maintenance mode
- Cookie consent banner
- Email confirmation pages
- Form success / failure pages

## Tools

- **Mid-fi**: Whimsical, FigJam, Miro
- **Hi-fi wireframes**: Figma (native components)
- **Annotated specs**: Figma comments, or Markdown alongside the file
- **User flows linking wireframes**: Whimsical or FigJam connectors
