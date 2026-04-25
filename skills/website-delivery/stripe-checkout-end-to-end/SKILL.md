---
name: stripe-checkout-end-to-end
description: Implement a production Stripe checkout — products, prices, taxes, hosted checkout vs. embedded, webhooks, customer portal, refunds, and Strong Customer Authentication. Use for one-time purchases, services, donations, or any payment flow where Shopify is overkill.
---

# Stripe Checkout End-to-End

The full path from "client wants to take payments" to "money in the bank
with proper webhooks." Covers Stripe Checkout (hosted) and Payment Element
(embedded) paths.

## When to use

- Selling digital products, services, courses, donations
- Booking deposits or one-time fees
- Anywhere you need PCI-light card processing
- Avoid for: full retail catalogs (use Shopify), complex subscriptions
  (see `subscription-billing` for the deep dive)

## Decision: Hosted Checkout vs. Payment Element

| Factor | Hosted Checkout | Payment Element |
|---|---|---|
| Setup speed | Hours | Days |
| Customization | Limited (logo, colors) | Full |
| PCI scope | Lowest (SAQ A) | Higher |
| Mobile UX | Excellent (optimized by Stripe) | Depends on you |
| Wallets (Apple/Google Pay) | Auto | Manual config |
| Use when | Standard sales | Brand-critical UX |

Default to **Hosted Checkout** unless the client demands a fully embedded
flow.

## Setup steps

1. Create Stripe account → activate live mode
2. In Dashboard:
   - **Products & Prices**: create products with one-time or recurring prices
   - **Tax**: enable Stripe Tax for the regions you sell to
   - **Branding**: upload logo, set brand colors
   - **Customer portal**: configure features (cancel, update card, invoice
     history)
3. In code: install SDK
   ```bash
   npm install stripe @stripe/stripe-js
   ```
4. Set env vars: `STRIPE_SECRET_KEY`, `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`,
   `STRIPE_WEBHOOK_SECRET`

## Hosted Checkout flow

### Server: create session
```ts
// app/api/checkout/route.ts
import Stripe from 'stripe'
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)

export async function POST(req: Request) {
  const { priceId, quantity = 1 } = await req.json()
  const session = await stripe.checkout.sessions.create({
    mode: 'payment',
    line_items: [{ price: priceId, quantity }],
    success_url: `${process.env.SITE_URL}/checkout/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.SITE_URL}/checkout/cancel`,
    automatic_tax: { enabled: true },
    customer_creation: 'always',
    billing_address_collection: 'required',
    allow_promotion_codes: true,
    invoice_creation: { enabled: true },
  })
  return Response.json({ url: session.url })
}
```

### Client: redirect
```tsx
async function buy(priceId: string) {
  const res = await fetch('/api/checkout', {
    method: 'POST',
    body: JSON.stringify({ priceId }),
  })
  const { url } = await res.json()
  window.location.href = url
}
```

## Webhook (mandatory — don't skip)

Order is *not* fulfilled until the webhook fires. Never trust the
success_url alone (users can refresh, close, or fake it).

```ts
// app/api/webhooks/stripe/route.ts
import Stripe from 'stripe'
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)

export async function POST(req: Request) {
  const sig = req.headers.get('stripe-signature')!
  const body = await req.text()
  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(
      body, sig, process.env.STRIPE_WEBHOOK_SECRET!
    )
  } catch (err) {
    return new Response(`Webhook Error: ${err}`, { status: 400 })
  }

  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object as Stripe.Checkout.Session
      await fulfillOrder(session)
      await sendReceipt(session)
      break
    }
    case 'charge.refunded': await handleRefund(event); break
    case 'charge.dispute.created': await handleChargeback(event); break
    case 'invoice.payment_failed': await handlePaymentFailed(event); break
  }
  return Response.json({ received: true })
}
```

In Dashboard → Developers → Webhooks: add endpoint, select events, copy
the signing secret.

For local dev: `stripe listen --forward-to localhost:3000/api/webhooks/stripe`

## Idempotency

Webhooks can fire more than once. Always:
- Store `event.id` and skip if already processed
- Make `fulfillOrder` idempotent (insert with unique constraint on session.id)

## Customer portal

Let customers manage their own purchases:
```ts
const portal = await stripe.billingPortal.sessions.create({
  customer: customerId,
  return_url: `${SITE_URL}/account`,
})
return Response.redirect(portal.url)
```

Saves you support tickets. Configure features in Dashboard → Customer Portal.

## Tax handling

Use **Stripe Tax** (built-in):
- Auto-calculates VAT/GST/sales tax based on customer location
- Files returns in supported jurisdictions (paid feature)
- Charges 0.5% per transaction where used

If client has a separate tax provider (Avalara, TaxJar), use Stripe's tax
extensibility hooks instead.

## SCA / 3DS

Stripe handles Strong Customer Authentication automatically when using
PaymentIntents (which Checkout does under the hood). Don't disable it —
required by EU regs and reduces fraud everywhere.

## Receipts & invoices

- Email receipts: enable in Dashboard → Settings → Customer emails
- PDF invoices: enable on Checkout Session (`invoice_creation.enabled`)
- Branded: configure in Dashboard → Branding

## Refund handling

In Dashboard → Payments → click the charge → Refund. For programmatic:
```ts
await stripe.refunds.create({ charge: chargeId, amount: 1000 })
```
Subscribe to `charge.refunded` webhook to update your DB.

## Test cards

| Card | Outcome |
|---|---|
| `4242 4242 4242 4242` | Success |
| `4000 0000 0000 9995` | Insufficient funds |
| `4000 0027 6000 3184` | Requires 3DS |
| `4000 0000 0000 0002` | Generic decline |

Always exercise the 3DS path before launch — it changes the UX flow.

## Pre-launch checklist

- [ ] Live keys configured (not test)
- [ ] Webhook endpoint live + signing secret matches env
- [ ] Tax registered in all relevant regions
- [ ] Receipts test-sent and reviewed
- [ ] Refund policy documented in ToS
- [ ] Disputes / chargeback monitoring set up (email alerts)
- [ ] Customer portal enabled
- [ ] PCI compliance attestation (SAQ-A, auto-completed for Hosted Checkout)
- [ ] Bank account verified, payouts scheduled

## Anti-patterns

- Trusting `success_url` for fulfillment instead of webhooks
- Storing card details ever (let Stripe own this — PCI fire)
- Skipping idempotency, double-charging on webhook retries
- Hardcoding prices in code (use Price IDs from Dashboard)
- Disabling 3DS to "improve UX" (illegal in EU)
- No webhook for `charge.refunded` (refunds not synced to your DB)
- Different success_url per product (use session metadata instead)

## Pricing notes (for proposals)

Stripe fees: 2.9% + 30¢ per US card; 1.5% extra for international; 0.5%
extra for Tax. Quote these to the client up front so they price products
accordingly.
