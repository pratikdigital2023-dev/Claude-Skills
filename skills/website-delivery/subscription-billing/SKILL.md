---
name: subscription-billing
description: Implement recurring subscription billing on Stripe — plans, trials, proration, dunning, customer portal, metered usage, tax, and webhook-driven entitlement. Use when the client sells access (SaaS, memberships, content), not one-time products.
---

# Subscription Billing

The full path from "we want a subscription product" to "MRR in the bank
with healthy churn metrics." Built on Stripe Billing.

## When to use

- Recurring SaaS / membership / content sites
- Tiered pricing with monthly/annual toggle
- Free trials, paid trials, freemium → paid upgrades
- Usage-based or metered billing
- Avoid for: one-time purchases (use `stripe-checkout-end-to-end`)

## Decision tree

| Need | Pattern |
|---|---|
| Simple flat tiers | Stripe Checkout (Subscription mode) |
| Trial + auto-convert | Checkout with `subscription_data.trial_period_days` |
| Custom upgrade/downgrade UX | Stripe Billing API + custom UI |
| Usage-based / metered | Stripe Billing meters + reporting events |
| Per-seat pricing | Quantity-based price + customer portal |

## Setup in Stripe Dashboard

1. **Products & Prices**: create product → add Price → choose
   "Recurring", select interval (month/year), currency
2. **Tax**: enable Stripe Tax (EU VAT, US sales tax, etc.)
3. **Customer portal**: enable, configure features:
   - Cancel subscription
   - Update payment method
   - Switch plan
   - View invoices
4. **Billing settings**: configure dunning (retry schedule), email reminders

## Subscription flow with Checkout

```ts
// app/api/subscribe/route.ts
const session = await stripe.checkout.sessions.create({
  mode: 'subscription',
  line_items: [{ price: priceId, quantity: 1 }],
  subscription_data: {
    trial_period_days: 14,
    metadata: { userId },  // critical for matching back
  },
  success_url: `${SITE_URL}/welcome?session_id={CHECKOUT_SESSION_ID}`,
  cancel_url: `${SITE_URL}/pricing`,
  customer_email: userEmail,
  allow_promotion_codes: true,
  billing_address_collection: 'auto',
  automatic_tax: { enabled: true },
})
```

## Webhook events (the critical ones)

```ts
switch (event.type) {
  case 'customer.subscription.created':
  case 'customer.subscription.updated':
    // grant/revoke entitlement based on subscription.status
    await syncSubscription(event.data.object)
    break
  case 'customer.subscription.deleted':
    await revokeAccess(event.data.object.customer)
    break
  case 'invoice.payment_succeeded':
    // first charge after trial, or renewal
    await markPaid(event.data.object)
    break
  case 'invoice.payment_failed':
    // dunning starts; flag account
    await markPastDue(event.data.object)
    break
  case 'customer.subscription.trial_will_end':
    // 3 days before trial ends — send reminder email
    await sendTrialEndingEmail(event.data.object)
    break
}
```

## Entitlement model

Don't put "is_premium" on the user. Instead:
```sql
-- subscriptions table mirrors Stripe
id, user_id, stripe_subscription_id, stripe_customer_id,
status,        -- trialing | active | past_due | canceled | unpaid
price_id, quantity, current_period_end, cancel_at_period_end
```

Compute access at request time:
```ts
const sub = await db.subscription.findFirst({ where: { userId } })
const hasAccess = sub && ['trialing', 'active'].includes(sub.status)
  && sub.current_period_end > new Date()
```

## Plan changes (upgrade / downgrade)

```ts
const sub = await stripe.subscriptions.retrieve(subId)
await stripe.subscriptions.update(subId, {
  items: [{ id: sub.items.data[0].id, price: newPriceId }],
  proration_behavior: 'create_prorations',
  // 'always_invoice' to charge now; 'none' to apply on next cycle
})
```

UX rules:
- Upgrades → effective immediately, prorated charge
- Downgrades → effective at period end (no refund)
- Annual → monthly switch always at period end

## Trials

| Pattern | When |
|---|---|
| No-card trial (`trial_period_days` + `payment_method_collection: 'if_required'`) | Friction-free, higher trial-to-paid ratio variance |
| Card-required trial (default) | Higher trial conversion, lower trial start rate |

Send trial-ending emails at -3 days and -1 day. Stripe fires
`customer.subscription.trial_will_end` 3 days out.

## Metered / usage-based billing

```ts
// Report usage
await stripe.subscriptionItems.createUsageRecord(subItemId, {
  quantity: 1000,
  timestamp: Math.floor(Date.now() / 1000),
  action: 'increment',  // or 'set'
})
```

Use Stripe **meters** (newer API) for sub-cent unit pricing or complex
aggregation.

## Dunning (failed payment recovery)

Configure in Settings → Billing → Subscriptions and emails:
- 3 retry attempts over 21 days (Stripe Smart Retries — recommended)
- Email reminders at each retry
- After final retry: cancel, mark as `unpaid`, notify your app via webhook

Industry-average dunning recovers ~30% of failed payments.

## Customer portal (must-have)

```ts
const portal = await stripe.billingPortal.sessions.create({
  customer: customerId,
  return_url: `${SITE_URL}/account`,
})
return Response.redirect(portal.url)
```

Configure portal in Dashboard → Settings → Customer Portal:
- Allow plan switching (and which plans show)
- Allow cancellation (immediate vs. period-end)
- Allow updating payment method
- Branding

## Tax

Enable **Stripe Tax** for subscription billing — handles VAT MOSS,
nexus tracking, invoice tax lines automatically. Costs 0.5% per txn.

## Annual prepay incentive

UI pattern: "Save 20% with annual billing" toggle on pricing page.
Always show **per-month equivalent** when annual is selected (not the
annual lump sum) — converts better.

## Pre-launch checklist

- [ ] Live mode keys + webhook endpoint
- [ ] All recurring Price IDs configured
- [ ] Tax enabled in all relevant regions
- [ ] Trial-ending email configured
- [ ] Past-due / payment-failed email configured
- [ ] Customer portal enabled + branded
- [ ] Cancellation flow tested (entitlement revoked correctly)
- [ ] Plan upgrade tested (proration math reviewed)
- [ ] Reactivation flow tested (formerly cancelled customer subscribes again)
- [ ] Metrics dashboard set up (MRR, churn, LTV)

## Anti-patterns

- Boolean `is_premium` on users (can't model trial / past-due / cancel-at-end)
- Using `success_url` for entitlement (bypasses tax + webhooks)
- Manual cancellation only (build the portal — saves support tickets)
- No `trial_will_end` email (kills trial conversion)
- Letting `past_due` users keep full access indefinitely
- No idempotency on webhook handlers (double-charges on retries)
- Storing card data ever

## Pricing notes (for proposals)

- Stripe Billing: 0.5% per recurring transaction + standard processing fees
- Stripe Tax: +0.5%
- For SaaS pricing $20–$200/mo, total fees land around 4–5% of revenue
