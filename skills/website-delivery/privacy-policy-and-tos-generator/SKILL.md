---
name: privacy-policy-and-tos-generator
description: Generate a complete legal-page suite — Privacy Policy, Terms of Service, Cookie Policy, Acceptable Use, and DPA — tailored to the site's data practices, jurisdictions, and business model. Use before launch to satisfy GDPR, CCPA, and platform requirements (Apple, Google, Stripe).
---

# Privacy Policy + ToS Generator

Legal pages aren't decorative. They're required by GDPR, CCPA, and every
major payment / app-store platform. Generic templates create liability —
they don't match your actual data practices.

## When to use

- Pre-launch (always)
- After adding a new data processor (e.g., adopting a new analytics tool)
- After expanding to new jurisdictions
- When applying to App Store / Google Play / payment processors

## Required documents

| Doc | Required when |
|---|---|
| **Privacy Policy** | Always — every site that collects any data |
| **Terms of Service / Terms of Use** | Always — limits liability, sets governing law |
| **Cookie Policy** | If using non-essential cookies (almost always) |
| **Acceptable Use Policy** | User-generated content, SaaS, marketplaces |
| **DPA (Data Processing Agreement)** | B2B SaaS — you process EU customer data |
| **SLA (Service Level Agreement)** | Paid SaaS, especially enterprise |
| **Cookie Notice (banner copy)** | Always (see `cookie-consent`) |
| **Refund / Cancellation Policy** | E-commerce, subscriptions |
| **Accessibility Statement** | See `accessibility-statement` |

## Two paths to draft

### Path A: lawyer-reviewed template (recommended for $50K+ projects)
- Use a generator: **Termly**, **Iubenda**, **TermsFeed**, **PrivacyPolicies.com**
- Cost: $50–500/yr
- Output: customized doc you should still have a lawyer skim
- Don't ship the generator's footer link if it's optional

### Path B: lawyer-drafted (recommended for regulated industries)
- Healthcare, finance, anything with SPI / children / health data
- Budget: $1.5K–5K for the suite
- Find a tech-aware attorney; generic business attorneys produce bloated docs

**Never** copy-paste another company's policy. It's both copyright
infringement and likely doesn't match your data practices.

## Privacy policy: required content

A compliant privacy policy answers:

### What data do you collect?
List every category with examples:
- Identifiers (name, email, IP, device ID, cookies)
- Commercial info (purchases, subscriptions)
- Internet activity (pages visited, time on page, referrer)
- Geolocation (IP-based or precise)
- Audio/visual (if you use camera/mic)
- Professional/employment (if collected)
- Inferences drawn from above

### How do you collect it?
- Directly from user (forms, account creation)
- Automatically (cookies, server logs, analytics)
- From third parties (payment processors, social logins)

### Why?
- Provide the service
- Marketing / advertising
- Legal compliance
- Fraud prevention
- Analytics / improvement

### Who do you share it with?
List every processor by category and name:
- Hosting (Vercel, AWS)
- Analytics (Google, Plausible)
- Payment (Stripe, PayPal)
- Email (Resend, Postmark, Mailchimp)
- CRM (HubSpot, Salesforce)
- Customer support (Intercom, Zendesk)
- Advertising (Google Ads, Meta, LinkedIn)

### How long do you keep it?
For each category, state retention period:
- Account data: until deletion + 30-day grace
- Order data: 7 years (tax law)
- Marketing data: until unsubscribe
- Analytics: 14 months (GA4 default)
- Server logs: 30–90 days

### What rights do users have?
- Access, delete, correct, port, restrict, object, withdraw consent
- How to exercise (link to DSAR form)
- Right to lodge a complaint with a supervisory authority

### International transfers
If data leaves user's country: legal basis (SCCs, adequacy decision, BCRs).

### Children
COPPA (US under 13), GDPR (under 16, varies).

### Updates
How you'll notify (email + in-app banner for material changes).

### Contact
- DPO email or general privacy contact
- Mailing address
- Supervisory authority contact (for EU users)

## Terms of Service: required content

- **Acceptance of terms** (how user agrees: clickwrap > browsewrap)
- **Service description** (what you provide)
- **Account responsibilities** (security, accurate info)
- **Prohibited uses** (what users can't do)
- **Intellectual property** (your IP + user-generated content licensing)
- **Payment terms** (if applicable: pricing, billing, refunds)
- **Termination** (when you can, when user can)
- **Disclaimer of warranties** ("AS IS")
- **Limitation of liability** (caps)
- **Indemnification**
- **Dispute resolution** (arbitration vs. court, class action waiver)
- **Governing law + venue**
- **Changes to terms** (notice period)
- **Contact**

## Cookie policy

Auto-generate from your cookie scanner output (Cookiebot does this).
Must list every cookie with: name, purpose, provider, type, duration,
category.

## DPA (B2B SaaS)

Required by GDPR Art. 28 when you process EU customer data on their behalf.
- Subject matter + duration of processing
- Nature + purpose
- Type of personal data
- Categories of data subjects
- Controller's rights
- Sub-processor list (and notification process for changes)
- Security measures (Annex 1)
- International transfers (SCCs, attached as Annex 2)
- Audit rights
- Termination + return/deletion of data

Have one ready as PDF/Markdown for procurement teams to redline.

## Acceptable use policy

Required for any UGC site, SaaS with file storage, marketplace. Prohibits:
- Illegal content
- IP infringement
- Malware, spam, phishing
- Harassment / hate speech
- CSAM (with NCMEC / CCAII reporting commitment)
- Resource abuse (mining crypto, etc.)

Tie to enforcement: warning → suspension → termination.

## Distribution / placement

- Footer link on every page
- Linked from signup form (clickwrap: "I agree to ToS and Privacy Policy")
- Linked from cookie banner
- Linked from emails (footer)
- Versioned (`?v=2025-04`) — keep old versions accessible

## Versioning

- Date the doc ("Last updated: April 25, 2025")
- Keep a changelog at the bottom
- For material changes, email all users 30 days before effective date
- Archive old versions at `/legal/privacy-2024-01.html`

## Pre-launch checklist

- [ ] Privacy Policy live, lists every processor
- [ ] Terms of Service live, governs the service properly
- [ ] Cookie Policy generated from scanner
- [ ] DPA available (if B2B)
- [ ] AUP live (if UGC / marketplace)
- [ ] Refund policy live (if e-commerce)
- [ ] Accessibility statement live
- [ ] Footer links to all on every page
- [ ] Signup flow has clickwrap with TOS + PP links
- [ ] Email footer has unsubscribe + privacy link
- [ ] Lawyer (or legal generator) has reviewed final docs

## Anti-patterns

- Copy-paste from another company (copyright + factually wrong)
- Generic AI-written policy with no review (often misses jurisdiction)
- "Browsewrap" consent ("by using this site you agree") — not enforceable
  in many jurisdictions
- No DPA when B2B EU customers are coming (sales blocker)
- Forgetting to update when you add a new processor
- Single-page mega-doc combining ToS + Privacy + Cookie (confusing)
- Linking to "policy.html" with no version, no archive

## Tools

- **Termly** — $99–250/yr, good for SaaS
- **Iubenda** — €9–€49/mo, multi-language, includes cookie scanner
- **TermsFeed** — one-time fee per doc
- **Custom counsel** — Cooley, Fenwick, or boutique privacy firms; $1.5K–5K
  for full suite

## Pricing notes (for proposals)

- Generator subscription: $50–500/yr — line item to client
- Lawyer review: $1K–3K, recommended
- Custom drafting: $5K–15K, only for regulated industries
