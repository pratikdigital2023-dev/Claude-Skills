---
name: client-training-handbook
description: Produce a client-facing training package — written guides, Loom videos, and a live training session — covering CMS editing, image uploads, publishing workflow, common tasks, and "who to contact for what". Use in the final week before launch to make the client self-sufficient.
---

# Client Training Handbook

A trained client posts updates without bothering you. An untrained client
sends you a Slack DM every time they want to fix a typo. Training is a
project deliverable, not optional.

## When to use

- 1 week before launch
- After adding a new CMS or feature the client manages
- When the client's team rotates (new editor joins)
- As a one-time refresher 90 days post-launch

## Deliverable package

For a $50K project, hand over:
1. **Quick-start guide** — 1-page PDF: "How to make your first edit"
2. **Full handbook** — 15–30 page PDF or Notion doc covering every CMS task
3. **Loom video library** — 8–15 videos, 2–5 min each, narrated walkthroughs
4. **Live training session** — 60–90 minutes, recorded
5. **Cheatsheet** — single-page quick reference (image specs, brand rules)
6. **Support flowchart** — "What to do when X breaks"

## Handbook outline (typical)

```
1. Welcome + how to use this guide
2. Logging in to the CMS
3. The editor interface tour
4. Editing an existing page
5. Creating a new page (if applicable)
6. Editing a blog post
7. Adding / managing images
   - Recommended sizes
   - Alt text best practices
   - Where to find royalty-free options
8. Working with components / blocks
9. Drafts vs publishing
10. Preview before publishing
11. Scheduling a future publish
12. Editing site settings (nav, footer, etc.)
13. Managing forms / submissions
14. Reading analytics (basic)
15. Common tasks cheatsheet
16. What you should NOT change
17. Brand voice + style do's and don'ts
18. Who to contact for what
```

## Loom video library

Record bite-sized videos. Title them by task:
1. "How to edit a page (3 min)"
2. "How to publish a blog post (4 min)"
3. "How to add images correctly (3 min)"
4. "How to update the navigation (2 min)"
5. "How to schedule a post (2 min)"
6. "How to handle a form submission (3 min)"
7. "How to use the design system components (5 min)"
8. "How to review analytics (4 min)"
9. "What to do if something looks broken (2 min)"
10. "How to request changes from the agency (1 min)"

Tips:
- Record at 1080p with mic + screen
- Use cursor highlight + click animations
- Cut hesitations — keep videos tight
- Title screen + closing card with brand
- Host in client's own Loom workspace if possible (transferable)

## Live training session

90-minute Zoom, recorded. Agenda:
- 0:00 Welcome + intros (5)
- 0:05 Walkthrough: logging in, editor tour (10)
- 0:15 Editing existing content — live demo (15)
- 0:30 Creating new content — live demo (15)
- 0:45 Hands-on practice (each attendee makes one edit) (20)
- 1:05 Brand + voice guidelines (10)
- 1:15 Q&A (15)

Send the recording + transcript afterward.

## Brand + voice guide (1-page version)

For editors:
```
DO write in second person ("you")
DO keep paragraphs to 3 sentences max
DO use active voice
DO use sentence case for headings
DO end blog posts with a CTA
DO compress images to < 500KB before uploading

DON'T use exclamation points (sparingly!!)
DON'T use marketing-speak ("revolutionary", "synergy")
DON'T uppercase WORDS for emphasis
DON'T link to competitors
DON'T publish without preview
DON'T edit code or templates (contact us)
```

## Image specs cheatsheet

| Use | Dimensions | Format | Max size | Notes |
|---|---|---|---|---|
| Hero (page top) | 2400 × 1350 | JPG/WebP | 500 KB | 16:9 |
| Blog thumbnail | 1200 × 630 | JPG/WebP | 200 KB | 1.91:1 (also OG) |
| Inline blog | 1600 wide max | JPG/WebP | 200 KB | any ratio |
| Author avatar | 400 × 400 | JPG/PNG | 50 KB | square |
| Logo (light bg) | SVG preferred | SVG/PNG | n/a | |
| Logo (dark bg) | SVG preferred | SVG/PNG | n/a | |
| Favicon | 512 × 512 source | PNG | 50 KB | we'll generate sizes |

Print this and give to the marketing team.

## Support flowchart

```
Something looks wrong on the site?
├── Is it a typo or content issue I can fix?
│   └── YES → fix it in CMS, publish
├── Is something broken (page won't load, error)?
│   └── YES → file ticket via [link/email]
├── Do I need a new feature?
│   └── YES → email account@agency.com (change order)
├── Is the site down completely?
│   └── YES → email urgent@agency.com (P0 alert)
├── Do I need an account / permission?
│   └── YES → email account@agency.com
└── Is it a marketing question (SEO, CRO)?
    └── YES → email strategy@agency.com (or use retainer hours)
```

## Permissions / account list

Maintain a single source of truth for client-side accounts:
| System | URL | Admin | Editor accounts | Reset link |
|---|---|---|---|---|
| CMS | cms.acme.com | Sarah | Mike, Liz, Tom | Forgot password link |
| GA4 | analytics.google.com | Sarah | Mike, Liz | Google account |
| Search Console | search.google.com | Sarah | Mike | Google account |
| Stripe | dashboard.stripe.com | Sarah | Mike (read-only) | Stripe SSO |
| Hosting | vercel.com/acme | Agency PM | none | Agency manages |
| DNS | Cloudflare | Sarah + Agency | none | 2FA required |

## What clients commonly break

Pre-emptively warn them:
- **Renaming a page slug** → breaks all inbound links
- **Deleting a published page** → breaks navigation
- **Uploading 10 MB iPhone photos** → crashes mobile load times
- **Editing footer links** → may break required legal links
- **Removing the "decorative" image on the homepage** → it's actually load-bearing
- **Disabling cookie banner** → instant GDPR violation

For each, document why it's risky.

## 90-day check-in

Schedule a 30-min call 90 days after launch:
- Quick metrics review
- Outstanding questions
- Upgrade / phase-2 conversation
- Confirm everyone is comfortable

This is also when retainer conversations happen naturally.

## Pre-launch checklist

- [ ] Quick-start PDF written
- [ ] Full handbook written + reviewed
- [ ] All Loom videos recorded + accessible to client
- [ ] Live training session scheduled + run
- [ ] Cheatsheet PDF printable
- [ ] Support flowchart ready
- [ ] Account list current with correct contacts
- [ ] Test account: client successfully made an edit themselves before launch
- [ ] Recording of training session shared

## Anti-patterns

- "Here's the CMS, good luck" (guarantees support tickets for trivial things)
- One marathon training session with no follow-up materials
- Video-only or doc-only (different learners need different formats)
- Training on a Friday afternoon (no one retains it)
- Training before content is loaded (nothing realistic to practice on)
- No brand voice guide (editors invent their own tone)
- Training the wrong people (the person who attends isn't the one editing)

## Pricing notes (for proposals)

Training is part of project scope, not extra. Budget:
- Handbook: 6–10 hours of writing
- Loom videos: 4–8 hours of recording + editing
- Live session: 2 hours (1 prep + 1.5 delivery)

For a $50K project, allot ~$2–3K of effort to training. Consider also
offering a paid retainer for "quarterly refreshers" or "new editor
onboarding."
