---
name: uat-runbook
description: Run a structured user acceptance test (UAT) phase with the client — test scripts, sign-off forms, bug triage workflow, and decision rules for go/no-go. Use in the final 1–2 weeks before launch to get formal client sign-off.
---

# UAT Runbook

User Acceptance Testing is the client's formal "I approve, we can launch"
checkpoint. Done well, it surfaces gaps + builds confidence. Done poorly,
it becomes endless rework.

## When to use

- Final 1–2 weeks before launch
- After every major release for ongoing engagements
- When transferring ownership to a new client team

## Pre-UAT checklist

Before handing the client a test plan:
- [ ] Internal QA pass complete (zero P0/P1 bugs open)
- [ ] All content loaded (real, not lorem ipsum)
- [ ] All integrations on production keys (or sandbox if explicitly noted)
- [ ] Staging environment matches production stack
- [ ] Test accounts created for client team (admin + editor + customer roles)
- [ ] Browser/device matrix tested by your team

If any of these isn't done, **don't start UAT**. Premature UAT generates
noise instead of signal.

## UAT scope

Tell the client clearly what UAT is and isn't:

**UAT is**:
- Verifying the site does what was specified in the SoW
- Catching bugs and content issues
- Confirming the site is ready for the public

**UAT is NOT**:
- Reviewing the design (that happened in design phase)
- Adding new requirements (that's a change order)
- Finding "nice to haves" (note them for phase 2)
- Re-examining previously approved decisions

Put this in the UAT kickoff email.

## Test plan structure

A spreadsheet (Google Sheets / Notion table). One row per test case:

| ID | Area | Test case | Steps | Expected | Status | Tester | Notes |
|---|---|---|---|---|---|---|---|
| T-001 | Homepage | Hero CTA goes to signup | Click "Get started" | Lands on /signup | ⬜ | | |
| T-002 | Forms | Contact form submits | Fill form → submit | Success message + email received | ⬜ | | |
| T-003 | Checkout | Buy product with test card | Add → checkout → 4242 card | Order confirmation page + email | ⬜ | | |

Status values: ⬜ Not tested · ✅ Pass · ❌ Fail · 🟡 Pass with notes ·
🚫 Blocked

## Test case categories

For a typical website, cover:

### Content
- [ ] All copy reviewed for typos / brand voice
- [ ] All images appropriate + properly attributed
- [ ] Videos play on all pages
- [ ] Links don't 404 (run a crawl)
- [ ] Legal pages present and current

### Forms / interactions
- [ ] Each form submits + reaches its destination
- [ ] Validation messages clear
- [ ] Error states work
- [ ] Email confirmations sent + received
- [ ] CRM / ESP receives leads

### E-commerce / payments (if applicable)
- [ ] Products display correctly
- [ ] Cart adds / removes / persists
- [ ] Checkout completes with test card
- [ ] Receipts sent
- [ ] Refunds work
- [ ] Tax calculates correctly

### Auth / accounts (if applicable)
- [ ] Signup flow
- [ ] Login flow
- [ ] Password reset
- [ ] Email verification
- [ ] Logout
- [ ] Account settings

### CMS (must test from editor's perspective)
- [ ] Editor can log in
- [ ] Editor can create / edit a blog post
- [ ] Editor can preview before publish
- [ ] Editor can publish
- [ ] Published changes appear on site within X seconds

### Cross-device
- [ ] Site works on iPhone (latest)
- [ ] Site works on Android
- [ ] Site works on iPad
- [ ] Site works on Windows desktop
- [ ] Mobile menu works

### Performance
- [ ] Lighthouse score on target pages
- [ ] No layout shift on load
- [ ] Images load progressively

### Analytics / tracking
- [ ] Page views fire (test in GA4 real-time)
- [ ] Form submissions tracked
- [ ] E-commerce events fire (if applicable)
- [ ] Cookie banner respects opt-out

### Accessibility (sample)
- [ ] Tab through homepage with keyboard only
- [ ] Run axe on top 3 pages
- [ ] Test with screen reader on one page
- [ ] Confirm color contrast on critical text

### SEO
- [ ] Each page has unique title + meta
- [ ] OG images render in social preview
- [ ] sitemap.xml accessible
- [ ] robots.txt correct
- [ ] Schema / JSON-LD validates (Google Rich Results test)

## Bug triage

Every reported issue gets a severity:

| Severity | Definition | SLA |
|---|---|---|
| **P0 / Blocker** | Site can't launch (checkout broken, can't navigate) | Same day |
| **P1 / Critical** | Major feature broken, no workaround | < 48 hr |
| **P2 / Major** | Feature partially broken, workaround exists | Before launch |
| **P3 / Minor** | Small issue, doesn't block use | Backlog |
| **P4 / Cosmetic** | Visual nitpick | Backlog or out-of-scope |

**Go/no-go rule**: launch is blocked while any P0 or P1 is open. P2s must
have an owner + a fix-by date.

## Daily UAT cadence

For each day of the UAT period:
- AM: client team tests assigned cases
- Midday: agency triages overnight reports
- PM: 30-min standup with client (reviewed bugs, decisions, blockers)
- EOD: agency ships fixes; client retests

Use a single channel (Slack #uat) for async questions.

## Sign-off form

A formal go/no-go document:
```
PROJECT: Acme Website Redesign
UAT PERIOD: April 15 – April 22, 2025
TESTING TEAM: [names]
TEST PLAN VERSION: v1.2

SUMMARY
- Total test cases: 87
- Passed: 82
- Failed → fixed: 5
- Failed → deferred (with sign-off): 0
- Out of scope (logged for phase 2): 3

GO/NO-GO DECISION: GO ☑   NO-GO ☐

KNOWN OPEN ITEMS AT LAUNCH
- None

CONDITIONS / CAVEATS
- Phase 2 will address [items]

CLIENT SIGN-OFF
[name, title, signature, date]

AGENCY SIGN-OFF
[name, title, signature, date]
```

This document protects both parties. Any post-launch dispute references it.

## Test data

Provide:
- Test customer accounts (one per role)
- Test credit card numbers (`4242 4242 4242 4242`)
- Test email addresses (use `+uat@yourdomain` aliases)
- Sample content for forms
- A "happy path" scenario script for each persona

## When the client wants to add scope

Inevitable. Have a scripted response:
> "This isn't in the original SoW. I'm logging it as a phase-2 item. If you
> want to include it before launch, I'll write it up as a change order with
> impact on cost + timeline."

Don't get drawn into "but it's small" debates. The CO process exists
specifically so that conversation has a clear path.

## Pre-launch checklist (after UAT)

- [ ] All P0/P1 bugs closed
- [ ] All P2s assigned with fix-by date or signed-off as deferred
- [ ] Sign-off form completed and signed
- [ ] Outstanding items added to phase-2 backlog
- [ ] Final invoice prepared (UAT often triggers next milestone payment)

## Anti-patterns

- Starting UAT before internal QA is done (client finds your bugs)
- Open-ended UAT period (slips for weeks; set a hard end date)
- No bug triage process (every report becomes a fire)
- Letting client add scope under "UAT" cover (must be CO)
- Skipping the sign-off form (no clear approval audit trail)
- Testing only on the laptop the client uses daily (one-browser bias)
- Treating UAT as design review (force decisions back to design phase)

## Tools

- **Test plans**: Google Sheets, Notion table, Linear cycles
- **Bug tracking**: Linear (best DX), Jira (enterprise), GitHub Issues
- **Recording bugs**: Loom for repro videos, Jam.dev (great browser
  extension for bug capture)
- **Communication**: dedicated Slack channel; never DMs

## Pricing notes (for proposals)

UAT is part of the project plan, not extra. Budget:
- Internal QA: 5–10% of build time
- Client UAT: 1–2 weeks of calendar time, ~5% of dev time for fix iteration
- UAT bugs found are part of the engagement; new feature requests are CO
