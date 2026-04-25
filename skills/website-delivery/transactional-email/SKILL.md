---
name: transactional-email
description: Set up production transactional email — Resend or Postmark, React Email templates, DKIM/SPF/DMARC DNS records, bounce/complaint handling, and deliverability monitoring. Use for any site that sends order confirmations, password resets, welcome emails, or notifications.
---

# Transactional Email

Transactional ≠ marketing. This is the email your app *must* send: receipts,
password resets, magic links, order confirmations. Inbox placement is
non-negotiable; bouncing one of these hurts your business.

## When to use

- Any site with user accounts, payments, or contact forms
- Replacing a noreply address with a real domain
- Migrating off a host's built-in mailer (almost always worth it)

## Provider choice

| Provider | When |
|---|---|
| **Resend** | Best DX for React/Next, fair pricing, modern API |
| **Postmark** | Highest deliverability, best for high-stakes mail (banks, healthcare) |
| **AWS SES** | Cheapest at scale, more setup, no templating UI |
| **SendGrid** | Avoid unless already there — deliverability has slipped |

Default for $50K builds: **Resend** (or Postmark if compliance-heavy).

## DNS setup (mandatory)

Three records prevent your mail going to spam:

### SPF
```
TYPE: TXT
NAME: @ (or root)
VALUE: v=spf1 include:_spf.resend.com ~all
```

If you also send from Google Workspace:
```
v=spf1 include:_spf.google.com include:_spf.resend.com ~all
```
**Only one SPF record per domain** — merge includes.

### DKIM
Provider gives you a CNAME or TXT record (often 3 records). Add exactly as
provided. **Never modify the value.**

### DMARC
```
TYPE: TXT
NAME: _dmarc
VALUE: v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com; pct=100
```

Start with `p=none` for 30 days to monitor reports, then move to
`p=quarantine`, then `p=reject` once confident.

### BIMI (optional, brand impact)
Show your logo in Gmail/Apple Mail with a verified BIMI record. Requires a
VMC certificate ($1500/yr from Entrust) — usually only for big brands.

## Send domain strategy

- **Don't send from your apex domain** (`yourdomain.com`) — risky.
- **Use a subdomain** like `mail.yourdomain.com` or `notifications.yourdomain.com`.
- This isolates reputation: marketing email problems don't poison
  transactional, and vice versa.

## Setup with Resend (Next.js example)

```bash
npm install resend react-email @react-email/components
```

```ts
// emails/welcome.tsx
import { Body, Container, Heading, Text, Button } from '@react-email/components'

export default function Welcome({ name, loginUrl }) {
  return (
    <Body style={{ background: '#f4f4f4', fontFamily: 'sans-serif' }}>
      <Container>
        <Heading>Welcome, {name}!</Heading>
        <Text>Click below to verify your email and get started.</Text>
        <Button href={loginUrl} style={{ background: '#000', color: '#fff', padding: '12px 24px' }}>
          Verify email
        </Button>
      </Container>
    </Body>
  )
}
```

```ts
// app/api/welcome/route.ts
import { Resend } from 'resend'
import Welcome from '@/emails/welcome'

const resend = new Resend(process.env.RESEND_API_KEY)

await resend.emails.send({
  from: 'Acme <hello@mail.acme.com>',
  to: user.email,
  subject: 'Welcome to Acme',
  react: Welcome({ name: user.name, loginUrl }),
  headers: { 'X-Entity-Ref-ID': `user-${user.id}` },  // for tracing
})
```

## Template inventory (typical $50K project)

Build these from one shared layout:
1. Welcome / verify email
2. Password reset
3. Magic-link login
4. Order confirmation / receipt
5. Shipping notification
6. Refund issued
7. Subscription started / renewed / cancelled
8. Payment failed (dunning)
9. Contact-form submission notification (to client)
10. Lead notification (to client sales team)
11. Account deletion confirmation
12. Generic system alert (errors)

Build a shared `<Layout>` component with header, footer, unsubscribe link
(even on transactional, for trust).

## Bounce + complaint handling

Subscribe to provider webhooks:
- `email.bounced` (hard) → mark user email as invalid, stop sending
- `email.complained` → mark as do-not-mail forever (CAN-SPAM requirement)
- `email.delivered` → log for trace
- `email.opened` / `email.clicked` → don't store for transactional (privacy)

```ts
// app/api/webhooks/resend/route.ts
const event = await req.json()
if (event.type === 'email.bounced') {
  await db.user.update({ where: { email: event.data.to[0] },
    data: { emailValid: false } })
}
```

## Deliverability rules

- **Warm up new domains slowly** — start with 100/day, double weekly
- **Match `From` to authenticated domain** (no spoofing)
- **Plain-text alternative** — Resend / React Email auto-generates
- **List-Unsubscribe header** even on transactional (Gmail rewards it)
- **Don't use URL shorteners** — bit.ly looks like spam
- **Avoid spammy words** in subject ("FREE", "ACT NOW", excessive emojis)
- **Test before send**: Mail Tester (mail-tester.com), Litmus

## Subject line conventions (transactional)

Keep them functional, not marketing-y:
- ✅ "Your Acme receipt #12345"
- ✅ "Reset your password"
- ❌ "🎉 You're IN!! Check this out"

## Monitoring

- Daily: bounce rate (< 2%), complaint rate (< 0.1%)
- Weekly: deliverability via Postmaster Tools (Google) + SNDS (Microsoft)
- Set up Sentry / log alerts on send failures

## Pre-launch checklist

- [ ] SPF + DKIM + DMARC records published and verified
- [ ] Send domain isolated from apex (subdomain)
- [ ] All 10–15 templates built + reviewed
- [ ] Bounces/complaints webhook live
- [ ] Test sent to Gmail, Outlook, Apple Mail, mobile
- [ ] DMARC report monitoring email is monitored
- [ ] Domain warmed up (if new) or reputation checked
- [ ] Unsubscribe / preference center linked from every template

## Anti-patterns

- Sending from `gmail.com` or `noreply@apex` (instant spam)
- No DKIM (≈ guaranteed spam folder)
- One SPF record per provider (causes lookups > 10, breaks SPF)
- Treating receipts like ads (sending coupons in the order confirmation)
- No bounce handling (keep emailing dead addresses, kill reputation)
- Cron-blasting marketing email through a transactional provider
- Using `cc` for "transactional" notifications (privacy violation)

## Pricing notes (for proposals)

- Resend: 3K emails/mo free, then $20+/mo
- Postmark: 100 emails/mo free, then $15+/mo
- SES: $0.10 per 1K (cheapest, most setup)
- Budget: $20–50/mo for typical $50K project's first year
