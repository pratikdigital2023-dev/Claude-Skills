---
name: scope-creep-guard
description: Detect, document, and price scope changes during a fixed-fee engagement. Generates change orders, decision logs, and politely-firm client emails. Use when the client asks for "one small thing", introduces a new stakeholder, or requests a feature outside the SoW.
---

# Scope Creep Guard

The most expensive mistake in a fixed-fee engagement is doing extra work for
free. This skill helps you identify scope changes early, document them, and
price them before they erode margin.

## When to use

- Client asks for "just one more thing"
- A new stakeholder appears with new requirements
- A feature wasn't in the SoW but is being assumed
- Round 3+ of revisions on the same deliverable
- Client says "I thought this was included"

## The scope-creep detection checklist

A request is scope creep if any are true:
- [ ] Not explicitly listed in the SoW deliverables
- [ ] Adds a new page, component, integration, or template
- [ ] Replaces a deliverable already approved (rework)
- [ ] Triggers research or design exploration not budgeted
- [ ] Crosses into a phase already signed off
- [ ] Comes from a stakeholder not in the original RACI

If 2+ are true: file a change order before doing the work.

## Change order template

```
CHANGE ORDER #[NN] — [Project Name]
Date: [YYYY-MM-DD]
Requested by: [name]

Original SoW reference: [section / page]

Change description:
[What's being added / changed in plain language]

Reason:
[Why the client is asking — capture their words]

Impact:
- Scope: [what's added or replaced]
- Timeline: [+X business days; new launch date if applicable]
- Cost: [+$X fixed | +X hours @ $Y/hr]

Approval required by: [date — calculate from current timeline]

Signed: ____________  Date: ________
```

## Pricing scope changes

Three pricing models, pick one in the MSA:

1. **Fixed add-on** — quote a flat fee per change order (preferred)
2. **Hourly with cap** — bill T&M up to a ceiling, then escalate
3. **Block of hours** — pre-purchased pool drawn against per change

Default rates for context:
- Junior dev/designer: $80–120/hr
- Senior dev/designer: $150–225/hr
- Strategy/architecture: $200–300/hr

## The polite-but-firm email

```
Subject: Scope question on [request]

Hi [name],

Thanks for sending [request]. I want to flag this so we handle it properly:
this falls outside the original SoW (specifically [reference]), so I'd treat
it as a change order.

Here's the impact:
• Adds: [what]
• Cost: $[X] fixed
• Timeline shift: [+N days]

If that works for you, reply "approved" and I'll send the change-order doc
for signature and start the work. If you'd rather defer it to a phase 2 or
descope something else to make room, happy to discuss.

Best,
[name]
```

## Decision log (running doc)

Maintain a single source of truth across the project:

| Date | Decision | Owner | Reasoning | Impact |
|---|---|---|---|---|
| 2025-04-01 | Use Sanity over Contentful | client lead | Editor experience | None |
| 2025-04-08 | Drop Spanish localization from v1 | client lead | Budget | -$8K |

Reference this in every change-order conversation. Memory is unreliable;
the log isn't.

## Common creep patterns + how to handle

| Pattern | Response |
|---|---|
| "Can we A/B test this?" | Out of scope. Phase 2 or change order. |
| "Add a blog" | Adds CMS schema + templates + content. CO. |
| "Make it look like [competitor]" mid-design | Triggers explore round. CO. |
| New stakeholder hates the design | Confirm decision-maker per RACI; if real, CO for revisions. |
| "Just translate it to French" | i18n is a multi-week add. CO. |
| "Quick mobile app version" | Hard no. Different project entirely. |

## When to absorb the cost (rarely)

Eat the cost only when:
- It's truly a defect against the SoW (you missed something)
- It's < 30 minutes of work and builds goodwill at a key moment
- The client is signing a retainer/phase 2 next month

Document absorbed work in the decision log so you don't repeat the pattern.

## Anti-patterns

- "We'll figure out billing at the end" — never works
- Verbal change-order approvals
- Doing the work first, billing after (you've lost leverage)
- Letting Slack DMs become unbilled scope expansions
- Not raising a CO because "it's only a few hours" (death by 1000 cuts)
