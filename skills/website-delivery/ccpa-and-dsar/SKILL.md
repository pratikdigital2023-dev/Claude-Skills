---
name: ccpa-and-dsar
description: Implement California Consumer Privacy Act (CCPA/CPRA) requirements — "Do Not Sell or Share My Personal Information" link, Global Privacy Control signal handling, and the data subject access request (DSAR) workflow. Use for any site with significant California traffic or B2C data collection.
---

# CCPA / CPRA + DSAR Workflow

California's privacy law applies to most US sites that sell to consumers
or have $25M+ revenue. Even sites under the threshold often implement it
for hygiene and to align with state laws spreading across the US (CO, CT,
VA, UT, etc.).

## When to use

- Site has California users + meets CCPA thresholds
- Site uses ad tech, retargeting, or third-party analytics
- Building any data subject request (DSR) intake workflow
- Aligning with the wave of US state privacy laws

## Thresholds (any one applies)

CCPA applies if the business:
- Has annual gross revenue > $25M, OR
- Buys/sells/shares personal info of 100K+ consumers/households, OR
- Derives 50%+ of revenue from selling/sharing personal info

Even if you don't hit thresholds, applying these patterns reduces risk
across multiple state laws (CPA, CTDPA, VCDPA, UCPA, FDBR, OPLPA, etc.).

## Required user-facing elements

### 1. "Do Not Sell or Share My Personal Information" link
Must appear in the footer of every page, exact wording:
> "Do Not Sell or Share My Personal Information"

Or, alternately:
> "Your Privacy Choices"

with a specific icon (a small shield-with-toggle). California Attorney
General publishes the exact icon spec.

Click should:
- Open a preferences modal or dedicated `/privacy-choices` page
- Let user opt out of: data sales, cross-context behavioral advertising,
  profiling for significant decisions

### 2. Global Privacy Control (GPC) signal
GPC is a browser-emitted header (`Sec-GPC: 1`) and JS API that signals
"do not sell" globally. California **requires** sites to honor it as a valid
opt-out request — no user action needed beyond the browser setting.

```ts
// middleware.ts (Next.js)
export function middleware(req: NextRequest) {
  const gpc = req.headers.get('sec-gpc') === '1'
  if (gpc) {
    const res = NextResponse.next()
    res.cookies.set('opt_out_sale', '1', { path: '/' })
    return res
  }
}
```

Then your consent banner / ad-tech integrations must check this cookie /
header and suppress data sharing accordingly.

### 3. Privacy notice
Required disclosures in the privacy policy:
- Categories of personal info collected (last 12 months)
- Purposes of collection
- Categories of third parties data is shared/sold to
- Right to know / delete / correct / opt-out
- Right to limit use of sensitive personal info
- Right to non-discrimination for exercising rights
- Contact methods for requests
- Designated data privacy officer (if applicable)

## Data subject access request (DSAR) workflow

You must respond to:
- **Right to Know** — what data do you have on me?
- **Right to Delete** — delete it (with exceptions)
- **Right to Correct** — fix inaccurate data
- **Right to Opt Out** — stop selling/sharing
- **Right to Limit** — restrict use of sensitive info

### Intake form

Build at `/privacy-request` with fields:
- Type of request (radio: know / delete / correct / opt-out / limit)
- Identifying info (email, account ID, name)
- Verification method consent
- Description of correction (if applicable)
- Authorized agent? (if filing on behalf of someone else)

Pipe submissions into a tracked queue (Linear, Notion, dedicated DB table).

### Verification

You must verify identity before fulfilling — usually 2 of:
- Email confirmation (link clicked from registered email)
- Account login challenge
- Confirmation of recent transaction/data point only the user would know

Don't over-verify low-risk requests (e.g. opt-outs need almost no verification).

### Response SLA

| Request type | SLA |
|---|---|
| Confirm receipt | 10 business days |
| Substantive response | 45 calendar days (extendable +45 with notice) |
| Opt-out / GPC | 15 business days |

Build calendar reminders / a queue with deadlines visible.

### Fulfillment

For Right to Know: assemble a data export. Sources to query:
- Application DB (users, orders, sessions)
- Email service (Resend / Postmark / Mailchimp)
- CRM (HubSpot / Salesforce)
- Analytics (GA4 user-level export — limited)
- Ad platforms (Meta, Google Ads custom audiences)
- Customer support (Zendesk / Intercom)

Deliver as CSV/JSON via authenticated download link, expires in 7 days.

For Right to Delete: cascade delete or anonymize across all systems.
Document what was preserved (e.g., financial records you must legally
keep) and why.

### Audit log

Every DSAR must be logged with:
- Date received, date completed
- Type
- Verification method used
- Outcome (fulfilled / partially / denied + reason)
- Data sources queried
- Authorized agent (if applicable)

Retain logs for at least 24 months.

## Sensitive personal information (SPI)

Triggers extra obligations: SSN, drivers license, financial account, precise
geolocation, racial/ethnic origin, religious beliefs, mail/email content,
genetic, biometric, health, sexual orientation.

If you collect SPI:
- Add a "Limit Use of My Sensitive Personal Information" link
- Use only for the disclosed purpose
- Honor limit requests within 15 days

## Children (under 16)

Do not sell or share personal info of users under 16 without:
- Affirmative opt-in from the user (if 13–15)
- Parent/guardian opt-in (if under 13 — also COPPA)

If your site collects ages, gate the consent flow accordingly.

## Pre-launch checklist

- [ ] "Do Not Sell or Share" link in footer of every page
- [ ] `/privacy-choices` page or modal works on mobile + desktop
- [ ] GPC signal honored (test with EFF's Privacy Badger or GPC test page)
- [ ] DSAR intake form live at `/privacy-request`
- [ ] Internal queue / runbook for processing requests
- [ ] Verification method documented
- [ ] Data inventory complete (where does PI live across systems?)
- [ ] Privacy policy lists categories + sources + purposes
- [ ] Audit log table created
- [ ] Designated privacy contact (email + role)

## Anti-patterns

- Honoring DSARs only for users who can prove California residency (you
  must serve all users requesting; you can verify residency afterward)
- Asking for excessive verification (e.g., government ID for an opt-out)
- Charging a fee for first request (you can't, except for excessive/repeated)
- Auto-denying GPC because it's "automated" (still valid)
- DSAR fulfillment via "send us your data" form to an unmonitored inbox
- Sending the export over plaintext email (use authenticated link)

## Tooling

- DSAR intake / workflow: Osano, OneTrust, DataGrail (paid) or build in-house
- Data discovery: Securiti, BigID (paid) or manual inventory
- Audit log: simple DB table works fine for small businesses

## Pricing notes (for proposals)

- Self-built workflow: ~25–40 hours of dev
- Vendor (DataGrail, OneTrust): $5K–25K/yr
- Privacy policy generator + DSAR vendor (Termly, Iubenda): ~$50/mo

If client expects > 10 DSARs/month, recommend a vendor. Otherwise build
in-house.
