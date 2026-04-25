---
name: user-journey-mapper
description: Map user journeys from awareness to conversion to retention, identifying touchpoints, friction, and the page-level success metric for each step. Use during discovery and IA, before wireframing, to ensure every page in the sitemap exists for a reason.
---

# User Journey Mapper

A user journey shows how a real person gets from "first heard of you" to "took
the action you wanted." Every page in the site should serve a step in at
least one journey. Pages that don't serve a journey are dead weight.

## When to use

- After persona/audience definition, before sitemap finalization
- When stakeholders disagree about page priority
- When the site has lots of traffic but low conversion
- When designing a new conversion flow (signup, checkout, contact)

## Inputs

- 1–3 personas (don't try to map for 7 audiences — pick the top 3)
- Top business goals (what does the site need to *cause*?)
- Current funnel data if available (GA4, segment, ads)
- User research artifacts: interviews, support tickets, sales calls

## The framework

For each persona, map four phases:

| Phase | User mindset | Site's job |
|---|---|---|
| **Awareness** | "I have a problem" | Be findable; explain the problem clearly |
| **Consideration** | "Could you solve it?" | Demonstrate fit; reduce risk |
| **Decision** | "Why you over alternatives?" | Differentiate; remove friction |
| **Adoption / retention** | "Did I get value?" | Onboard, support, deepen relationship |

## Per-step columns

For every step in every journey, capture:
| Step | Channel | User question | Page / asset | Friction | Success metric |

Example (B2B SaaS persona "ops manager evaluating tools"):

| Step | Channel | Question | Page | Friction | Metric |
|---|---|---|---|---|---|
| 1. Search | Google | "best [category] tool" | /comparison/[us-vs-x] | Trust the comparison | CTR from SERP |
| 2. Land | Direct | "Are you for me?" | /home or /[role] | Generic homepage | Scroll depth >60% |
| 3. Evaluate | On-site | "How does it work?" | /product, /demo-video | Long video | Demo CTA clicks |
| 4. Compare | On-site | "What's the cost?" | /pricing | Pricing hidden | Pricing → demo |
| 5. Convert | Form | "Will I get spammed?" | /book-demo | Long form | Form submits |
| 6. Onboard | Email + product | "How do I start?" | /welcome, in-app | Empty state | Activation event |

## Rules of thumb

- **One primary CTA per page** matched to the journey step the page serves.
- **Surface the next step**, not 12 alternatives. (A "consideration" page
  shouldn't dump 6 CTAs at the user.)
- **Eliminate steps where you can.** Every extra page is dropoff.
- **Mobile journeys differ.** Map them separately if traffic split is > 30/70.
- **Friction can be intentional.** A demo form that filters out tire-kickers
  is good friction. A pricing page that hides numbers is bad friction.

## Visual format

Two recommended:
1. **Swimlane diagram** — phases across top, persona rows down the side
2. **Bowtie diagram** — left side awareness funnel, right side retention funnel

Tools: Whimsical, FigJam, Miro, or just a spreadsheet. Don't over-tool this.

## Critical analysis questions

After mapping, ask:
- Where in the journey do we lose people today? (analytics)
- Which step has the most friction we control?
- Which step happens off-site that we could pull on-site?
- Are there steps where competitors win (we should defensively address)?
- What proof / social proof / risk reduction does each step need?

## Output

1. Journey map per persona (visual + spreadsheet)
2. Page-by-page CTA + success metric document
3. Friction inventory (top 5 to reduce in v1)
4. Measurement plan (which events, which page goals)

## Anti-patterns

- Mapping for "everyone" instead of specific personas
- Treating awareness/consideration/decision as discrete (they overlap)
- Mapping the journey you wish for, not the one analytics shows
- One mega-page trying to serve all phases at once
- Skipping retention/adoption ("we just need traffic")
- Stuffing 4 CTAs onto one page because "they help different journeys"

## Tie-in to other skills

- Feeds into `sitemap-and-ia` (page list)
- Feeds into `wireframe-spec` (per-page content priority)
- Feeds into `analytics-handover` (event taxonomy)
- Feeds into `page-cro` (which pages to optimize first)
