---
name: analytics-handover
description: Set up and hand over the full analytics stack — GA4, Search Console, Looker Studio dashboard, event taxonomy, conversion goals, and a quick-read monthly report template. Use in the final week before launch and as the recurring deliverable on a maintenance retainer.
---

# Analytics Handover

The site goes live; the client needs to see how it's performing. A naked
GA4 install is useless to non-analysts. A handover package gives them
charts they understand + alerts when things move.

## When to use

- Final week before launch
- After a major redesign (rebaseline metrics)
- When a new marketing lead joins the client
- As the recurring deliverable on a retainer

## Package contents

For a $50K project, deliver:
1. **GA4 property** configured + admin access transferred
2. **Search Console** verified + access shared
3. **Tag Manager** container with all events firing
4. **Server-side tracking** (if applicable for ad blockers)
5. **Event taxonomy** documented
6. **Looker Studio dashboard** — single-pane-of-glass for the team
7. **Monthly report template** — ready to send
8. **Alerts + automated reports** — Slack/email when something moves
9. **30-min walkthrough video** — how to read the dashboards

## Step 1: GA4 setup

In Google Tag Manager (preferred over hardcoded GA4):
- GA4 Configuration tag fires on All Pages
- Measurement ID injected from a constant variable
- Cookieless mode if Consent Mode v2 is configured (see `cookie-consent`)

Property settings to configure:
- Time zone + currency
- Data retention: max 14 months (the maximum)
- Cross-domain tracking (if multiple domains)
- Enhanced Measurement: ON for all events
- Internal traffic filter (your office IPs)
- Bot filter: ON
- IP anonymization: ON (GDPR)
- Google signals: OFF unless explicit consent (privacy-safer default)

## Step 2: event taxonomy

GA4 is event-driven. Without a taxonomy, you get inconsistent names.
Document these in a Google Sheet shared with the team:

| Event | Trigger | Parameters |
|---|---|---|
| `page_view` | (auto, Enhanced Measurement) | page_path, page_title |
| `scroll` | (auto, 90% scroll depth) | — |
| `click` | (custom) outbound links | link_url, link_domain |
| `form_start` | first interaction with form | form_name |
| `form_submit` | successful submit | form_name |
| `lead` | form_submit on lead-gen forms | form_name, value |
| `sign_up` | signup completion | method |
| `login` | login success | method |
| `add_to_cart` | (e-commerce) | items, value, currency |
| `begin_checkout` | (e-commerce) | items, value |
| `purchase` | (e-commerce) | transaction_id, items, value, tax, shipping |
| `view_item` | product page view | item_id, item_name, value |
| `cta_click` | clicks on a tracked CTA button | cta_label, cta_location |
| `video_play` | (auto with Enhanced Measurement) | video_title, video_provider |

**Naming rules**:
- Lowercase + snake_case (GA4 convention)
- Reuse Google's recommended events (`purchase`, `sign_up`) for free
  reporting templates
- Custom events should be specific (`pricing_card_click`) not vague (`click`)

## Step 3: conversions

Mark the events that matter as conversions in GA4 → Admin → Events:
- `purchase`, `lead`, `sign_up`, `login` → conversion
- Track conversion value where applicable

Soft conversions (engaged session, scroll, video) are useful for funnel
analysis but shouldn't pollute the conversion goal list.

## Step 4: Search Console

- Verify domain via DNS TXT record (preferred) — covers all subdomains
- Submit sitemap.xml
- Set preferred domain (with/without www)
- Link Search Console to GA4 (Admin → Property → Search Console links)
- Add the client's email as Owner

Check weekly for the first month after launch:
- Coverage: any new errors / soft 404s?
- Performance: queries + clicks per page (find SEO opportunities)
- Mobile usability: any new flagged issues?

## Step 5: Looker Studio dashboard

Build one dashboard. One. Don't proliferate dashboards.

Recommended structure (5 pages):

### Page 1: Executive summary
- 4 scorecards: sessions, users, conversions, conversion rate
- Comparison to previous period
- Trend chart: daily sessions last 30 days
- Top traffic sources (donut)
- Top performing pages (table)

### Page 2: Traffic
- Source / medium breakdown
- Top organic landing pages
- Top referring domains
- Geographic distribution
- Device breakdown

### Page 3: Engagement
- Average engagement time
- Bounce rate (engagement rate inverse) by page
- Scroll depth heatmap
- Top exit pages

### Page 4: Conversions
- Conversion volume by event
- Conversion rate by source
- Top converting pages
- Funnel: page view → form_start → form_submit
- E-commerce: revenue, AOV, top products (if applicable)

### Page 5: Search Console
- Top queries (with impressions, clicks, CTR, position)
- Top landing pages from organic search
- Query growth over time
- Branded vs non-branded split

Use connectors:
- GA4 → Looker Studio (native)
- Search Console → Looker Studio (native)
- Optional: Stripe / Shopify / Mailchimp via paid connectors (Supermetrics,
  Funnel)

## Step 6: monthly report template

A 1-page narrative + the dashboard link. Email layout:
```
Subject: [Acme] Monthly site report — [Month YYYY]

Summary
- Sessions: 12,450 (+18% vs prev month)
- Conversions: 142 (+22%)
- Conversion rate: 1.14% (+3%)

What went well
- Organic traffic up 25% — three blog posts ranked top 3
- Pricing page conversion up to 4.2% (was 3.5%)

What needs attention
- Mobile bounce rate climbed to 62% (previously 55%)
- Checkout completion fell 5% — investigating

Actions for next month
- Optimize mobile hero (hypothesis: image load too slow)
- Add SEO content for "[keyword] alternatives"

Full dashboard: [Looker Studio URL]
```

Send by 3rd of each month. Predictability builds trust.

## Step 7: alerts

Set custom insights / alerts in GA4:
- Conversion rate drops > 20% week-over-week → email
- Traffic spike > 200% → email (might indicate viral or bot)
- New landing page in top 10 → email (opportunity)

For Looker Studio, schedule emailed snapshots (weekly Monday + monthly
1st).

For deeper alerting, consider an analytics monitor (Avo, Iteratively) or
custom serverless function checking GA4 Data API.

## Step 8: server-side tagging (optional but valuable)

Why: ad blockers + iOS privacy nuke 20–40% of client-side analytics.

Setup:
- Server-side GTM container deployed on a custom subdomain (`m.acme.com`)
- Cloudflare Workers or Google Cloud Run hosting
- Client-side GA4 sends to your subdomain → forwarded to GA4

Cost: ~$15/mo for a small site, recovers significant data.

## Step 9: cross-domain or multi-domain

If client has multiple domains:
- Add all as data streams to one GA4 property OR
- Configure cross-domain tracking with `linker` parameter
- Set up referral exclusions for own subdomains

## Step 10: handover meeting

30-minute Zoom:
1. Tour the GA4 interface (10 min)
2. Walk through the Looker dashboard (10 min)
3. Show the monthly report template (5 min)
4. Q&A (5 min)

Record + share. Then schedule a 30-day check-in.

## Pre-launch checklist

- [ ] GA4 property created + Measurement ID in code
- [ ] GTM container live, all events firing in DebugView
- [ ] Conversions configured
- [ ] Search Console verified + sitemap submitted
- [ ] Looker dashboard built + access shared
- [ ] Monthly report template prepared
- [ ] Alerts configured
- [ ] Internal traffic filter active (your IP)
- [ ] Cookie consent properly gates analytics scripts
- [ ] Privacy policy lists GA4 + GTM as processors

## Anti-patterns

- Hardcoding GA4 ID instead of using GTM (locks future changes to dev)
- No event taxonomy (random event names)
- 12 dashboards (no one reads any)
- Sharing GA4 with the client and calling it "analytics handover"
- Reporting only sessions + bounce rate (vanity metrics)
- No connection between events and business outcomes
- Loading GA4 before consent (privacy violation)
- Email reports with raw screenshots (use a tool like Bezurk that pulls
  fresh data into a styled email)

## Pricing notes (for proposals)

- GA4 + Search Console: free
- Looker Studio: free
- Server-side tagging: ~$15/mo
- Setup time: 15–30 hours for full package
- Monthly retainer reporting: 2–4 hours/mo
