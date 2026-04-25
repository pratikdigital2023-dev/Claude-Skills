---
name: maintenance-retainer-sow
description: Draft a post-launch maintenance retainer — scope, hours, SLAs, on-call definitions, change request process, and pricing tiers. Use to convert a one-time build client into a recurring revenue relationship.
---

# Maintenance Retainer SoW

The launch is the *start* of the relationship, not the end. A well-priced
retainer keeps the site healthy, converts to recurring revenue, and gives
the client a predictable line of support.

## When to use

- Final 2 weeks before launch (sell during the trust peak)
- 30 days post-launch (revisit after first month of usage)
- When client asks "what happens after launch?"
- Annual renewal conversations

## Retainer types (pick one)

| Type | Best for |
|---|---|
| **Block of hours** | Ad-hoc work, predictable monthly burn |
| **Fixed fee + scope** | Defined deliverables (e.g., 2 blog posts/mo) |
| **Tiered service plan** | Multiple support levels (Bronze / Silver / Gold) |
| **Hours + SLA** | Enterprise, defined response times |

For most $50K projects, **block of hours with SLA** is the right default.

## Standard inclusions (every retainer)

Build in these as baseline so clients see clear value:

### Maintenance (always-on)
- WordPress / CMS core + plugin updates (test, stage, deploy)
- Dependency security updates (npm audit, Renovate / Dependabot triage)
- SSL cert renewal monitoring
- Domain renewal monitoring
- Daily backup verification
- Uptime monitoring + incident response
- Performance monitoring (Lighthouse CI passing)
- Accessibility regression checks

### Reporting (monthly)
- Uptime + incident summary
- Performance trends (Core Web Vitals)
- Top traffic / conversion pages
- Sentry error trends
- Hours used vs. allocated
- Recommendations for next month

### Reactive support
- Bug fixes (reported by client)
- Content updates (if not in client's CMS workflow)
- Account / permissions admin
- "How do I…?" questions

### Out of scope (require change order or additional engagement)
- New features / major design changes
- New page templates
- New integrations
- Content production (copywriting, video, photography)
- SEO content strategy
- A/B testing setup

Make this list explicit. Ambiguity = scope creep.

## Tier example (block of hours)

| Tier | Hours/mo | Price | SLA |
|---|---|---|---|
| **Care** | 5 hrs | $750/mo | Response 2 biz days, fix when scheduled |
| **Standard** | 10 hrs | $1,400/mo | Response 1 biz day, urgent same day |
| **Plus** | 20 hrs | $2,600/mo | Response 4 biz hours, P0 on-call |
| **Enterprise** | 40+ hrs | $5,000+/mo | 24/7 on-call, dedicated PM |

Hourly rate ~$130–175 within retainer (15–20% off blended rate for
commitment).

## SLA definitions

Define what each severity means + the response/resolution clock:

| Severity | Definition | Response | Resolution target |
|---|---|---|---|
| **P0 / Outage** | Site down or checkout broken | 1 hr (Plus+), 4 hr (Standard) | 4 hrs |
| **P1 / Critical** | Major feature broken | 4 hr (Plus+), next biz day | 1 biz day |
| **P2 / Degraded** | Feature impaired, workaround exists | Next biz day | 5 biz days |
| **P3 / Minor** | Small bug, no rush | 2 biz days | Backlog (next sprint) |
| **P4 / Request** | "Can you change…?" | 2 biz days | Scheduled |

Clarify business hours: e.g., M–F 9am–6pm Pacific. Outside hours = next
business day unless P0 + on-call coverage included.

## Hours rollover policy

Three options:
1. **Use it or lose it** — simplest, but clients hate it
2. **Roll forward 1 month** — middle ground, default recommendation
3. **Bank indefinitely** — risky (clients hoard then dump 40 hours in March)

Rollover is conditional on the client paying on time.

## Overage pricing

When hours exceed allocation:
- Notify client at 80% of monthly allocation
- Soft cap at 100% — work pauses pending CO or auth
- Hard cap with explicit overage rate (1.25× hourly, billed monthly)

## What kills retainers (avoid)

- **Invisible work** — if the client doesn't see the value, they cancel.
  Send the monthly report religiously.
- **No proactive recommendations** — pure reactive support gets commoditized
- **Slow responses** — once you miss SLA twice, trust erodes
- **Scope drift** — letting "small" requests pile into the next major release

## Sample SoW language

```
1. SERVICES INCLUDED (10 hrs/month)
   1.1 Software updates: monthly review and patching of CMS, dependencies,
       and plugins, with staging verification before production push.
   1.2 Backups: verification of daily DB + asset backups; test restore
       quarterly.
   1.3 Monitoring: 24/7 uptime monitoring, performance monitoring (Lighthouse
       CI), error tracking (Sentry).
   1.4 Reactive support: bug fixes, content updates, account admin, and
       general questions submitted via [system].
   1.5 Monthly reporting: written report covering uptime, performance,
       hours used, and recommendations.

2. SERVICE LEVEL
   2.1 Business hours: Monday–Friday, 9:00am–6:00pm Pacific Time, excluding
       US Federal holidays.
   2.2 Response times by severity: see Schedule A.
   2.3 P0 incidents trigger same-day response 24/7.

3. EXCLUSIONS
   3.1 New feature development, major redesigns, new integrations, and
       new page templates are not included; these are scoped separately.
   3.2 Content production (copywriting, photography, video) is not included.
   3.3 Third-party service costs (hosting, SaaS subscriptions) are
       passed through at cost.

4. HOURS
   4.1 Allocated: 10 hours per calendar month.
   4.2 Unused hours: roll forward 1 month, then expire.
   4.3 Overage: billed at $175/hr, capped at 5 additional hours/month
       without prior written approval.

5. PRICING
   5.1 Monthly fee: $1,400, invoiced on the 1st of each month, due NET 15.
   5.2 Late payment may pause services until current.

6. TERM + TERMINATION
   6.1 Initial term: 6 months from launch date.
   6.2 After initial term: month-to-month.
   6.3 Termination: 30 days written notice from either party.

7. ACCESS + OWNERSHIP
   7.1 Client retains ownership of all code, content, and accounts.
   7.2 Agency requires admin access to designated systems for the term
       of this agreement.

8. CONFIDENTIALITY + IP
   [Reference MSA]
```

## Pricing math (sanity check)

If your blended rate is $175/hr and you offer a 10-hour retainer at $1,400:
- Effective rate: $140/hr (20% off)
- Margin (assuming 50% utilization on retainer hours): healthy
- Risk: clients who use 100% of hours every month → lower-margin work

Build in: utilization assumption, response-time burden, on-call cost.

## Selling the retainer

Start the conversation 2 weeks before launch:
> "Most clients want some kind of post-launch support — security updates,
> bug fixes, the occasional content tweak. We package this into a monthly
> care plan starting at [tier]. Want me to walk through the options before
> launch so we have it lined up?"

Avoid:
- Mentioning it the day of launch (looks opportunistic)
- Aggressive upsell language
- Long sales decks (retainer should be obvious value)

Tactic: include the first 30 days of "warranty" support free in the build
SoW. Then transition to paid retainer for ongoing.

## Onboarding the retainer

Day 1 of retainer:
- Confirm access to all systems
- Confirm point-of-contact on both sides
- Confirm support intake channel (Slack / email / ticket form)
- First monthly reporting cycle date

Send a welcome email with: "what to expect", "how to file a request", "how
to reach us in an emergency".

## Common objections + responses

**"$1,400/mo is a lot for what we use."**
> "Most of the value is in monitoring + incident prevention you don't see.
> If you'd prefer reactive-only, we can offer hourly support at $200/hr
> with no SLA, but most clients prefer the predictability."

**"We have a developer in-house who can do this."**
> "Great. We can do a 'monitoring + escalation' tier at $350/mo where we
> own uptime + alerts and your dev handles requests."

**"We just spent $50K, we don't have budget."**
> "Understand. A bare-bones tier at $400/mo covers updates + monitoring
> only. We can revisit upgrade in 90 days."

## Pre-launch retainer checklist

- [ ] Retainer SoW drafted
- [ ] Tiers + pricing aligned with client budget
- [ ] SLAs defined per tier
- [ ] Inclusions + exclusions explicit
- [ ] Conversation scheduled 2 weeks before launch
- [ ] First-month invoice prepared (auto-send on launch day)
- [ ] Onboarding email template ready

## Anti-patterns

- Free "warranty" indefinitely (you'll be supporting them in year 5)
- Vague scope ("general support") — invites scope creep
- No SLA (clients don't know when to expect responses)
- Hourly billing with no minimum (irregular revenue, hard to plan)
- One-size-fits-all retainer (different clients need different tiers)
- No monthly reporting (invisible work = cancellation risk)
- Letting hours roll over indefinitely (clients hoard, then dump)

## Pricing notes (for proposals)

Industry benchmarks (2024–25):
- Small business / SMB site: $400–1,500/mo
- Mid-market: $1,500–5,000/mo
- Enterprise: $5,000–25,000+/mo

For a $50K build project, an attached $1,200–2,000/mo retainer is realistic
and adds $14K–24K/yr to the engagement.
