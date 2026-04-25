---
name: dns-ssl-cdn-setup
description: Configure DNS, SSL/TLS, and CDN/WAF for a production site — Cloudflare zone setup, A/CNAME/MX/TXT records, edge certs, WAF rules, rate limits, and DDoS protection. Use during the launch phase, before pointing domains at the new site.
---

# DNS / SSL / CDN Setup

DNS misconfiguration is the most common cause of a busted launch. Get it
right once, document it, and you'll avoid the worst kind of late-night
incident.

## When to use

- Pre-launch: setting up the production zone
- Migration: moving DNS from one provider to another
- Adding SSL or CDN in front of an existing site
- Adding a subdomain (status, mail, docs, app)

## Recommended stack

For a $50K project: **Cloudflare for DNS + WAF + CDN**, even if the site is
hosted on Vercel/Netlify (which have their own CDN). Cloudflare adds:
- Free DDoS protection
- WAF / bot management
- Rate limiting
- Page Rules / Cache Rules
- Best-in-class DNS speed

The "double CDN" concern is overblown — set Cloudflare's cache to bypass
HTML and let Vercel handle ISR. CSS/JS/images get edge-cached on both.

## Domain ownership + transfer

Before launch:
- [ ] Confirm the client owns the domain (check WHOIS)
- [ ] Get registrar credentials in writing (or transfer to your management)
- [ ] Enable registrar 2FA
- [ ] Enable registry-lock if available (prevents social-engineering hijack)
- [ ] Domain auto-renew on, paid for 5–10 years out

If transferring domain registration: requires authorization code (EPP) from
old registrar. Plan 5–7 days; doesn't affect DNS during transfer if you
keep nameservers pointed at Cloudflare/etc.

## DNS zone setup (Cloudflare)

1. Add domain in Cloudflare dashboard
2. Cloudflare scans existing DNS records
3. **Update nameservers at registrar** to Cloudflare's two NS records
4. Wait for propagation (usually < 1 hour, max 48)
5. Audit imported records — delete anything you don't recognize

## Records you need

| Record | Name | Type | Value | Proxy |
|---|---|---|---|---|
| Apex web | `@` (or root) | A or AAAA | Vercel/Netlify IP, or `CNAME flattening` | ON |
| WWW redirect | `www` | CNAME | apex domain | ON |
| Email (Google Workspace) | `@` | MX | `1 smtp.google.com` | OFF (orange cloud) |
| Email SPF | `@` | TXT | `v=spf1 include:_spf.google.com include:_spf.resend.com ~all` | n/a |
| Email DKIM (per provider) | `selector._domainkey` | CNAME or TXT | provider value | OFF |
| Email DMARC | `_dmarc` | TXT | `v=DMARC1; p=quarantine; rua=mailto:dmarc@acme.com` | n/a |
| Verification (Google, etc.) | `@` | TXT | provider value | n/a |
| Subdomains | e.g. `app`, `status`, `cms` | CNAME | provider hostname | varies |

### Apex domain on Vercel
Vercel gives you an A record (76.76.21.21) and an AAAA. Or use Cloudflare's
**CNAME flattening** to point apex at `cname.vercel-dns.com`.

### Subdomains
Always CNAME to the host's hostname (not IP — IPs change):
- `app.acme.com` → `cname.vercel-dns.com.`
- `cms.acme.com` → `acme.sanity.studio.`

## SSL / TLS configuration

### Edge certs (Cloudflare → your visitor)
Cloudflare issues a free Universal SSL cert for apex + www. Verify:
- "SSL/TLS" → "Edge Certificates" → status: Active
- Apex + first-level wildcard `*.acme.com` covered by Universal
- For deeper wildcards (`*.app.acme.com`): Advanced Certificate ($10/mo) or
  bring your own

### Origin certs (Cloudflare → your origin)
Set "SSL/TLS" → "Overview" → encryption mode to **Full (strict)**:
- Cloudflare connects to origin only over HTTPS
- Origin must present a valid cert
- Vercel/Netlify auto-provision via Let's Encrypt

Avoid **Flexible** mode — encrypts user→Cloudflare but not Cloudflare→origin
(insecure, breaks `cookies.secure`).

### HSTS
After verifying everything works, enable HSTS:
- Max age: 6 months → 1 year → 2 years
- Include subdomains: yes (after testing)
- Preload: optional, irreversible — opt in only if you're sure

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

### Certificate Authority Authorization (CAA)
Pin which CAs can issue certs for your domain — prevents unauthorized
issuance:
```
@ CAA 0 issue "letsencrypt.org"
@ CAA 0 issue "digicert.com"
@ CAA 0 issuewild "letsencrypt.org"
```

## WAF + bot rules

Cloudflare WAF rules to enable on day one:
- **Managed Rules**: enable Cloudflare Managed Ruleset + OWASP Core Ruleset
- **Rate limiting**: 100 req/min per IP on `/api/*`, 5 req/min on `/api/login`
- **Bot Fight Mode**: ON (free)
- **Country block**: only if you have legal reason (sanctioned regions)
- **Challenge bad ASNs**: known scraper / VPN / TOR networks

```
Rule: rate-limit login
If: URI path matches "/api/login"
Then: rate limit 5/min per IP, action: block 10 min
```

## Page rules / cache rules

| Rule | Action |
|---|---|
| `acme.com/wp-admin/*` (if WP) | Cache: bypass |
| `acme.com/api/*` | Cache: bypass; security: high |
| `acme.com/_next/static/*` | Cache: 1 year, immutable |
| `acme.com/*` | Cache: standard, edge TTL respect origin |

## Email-specific records (don't break these)

When changing DNS, **never touch MX/SPF/DKIM/DMARC** without coordinating
with the team that owns email. A misconfigured SPF can take all outbound
email to spam folders for days.

## Subdomain delegation

Common subdomains:
- `www` → main site
- `app` → web app (if separate)
- `api` → API
- `cms` → headless CMS admin
- `status` → status page
- `docs` → documentation
- `mail` → email send domain (subdomain isolation)
- `email` → email open/click tracking
- `track` → ad/analytics tracking (avoid — ad blockers)

## Pre-launch verification

```bash
# Check propagation
dig acme.com +short
dig www.acme.com +short
dig MX acme.com +short

# Check SSL
curl -sI https://acme.com/ | head -1
echo | openssl s_client -connect acme.com:443 -servername acme.com 2>/dev/null | openssl x509 -noout -dates

# Check redirects
curl -sI http://acme.com/ | grep -i location
curl -sI https://www.acme.com/ | grep -i location

# Check security headers
curl -sI https://acme.com/ | grep -iE 'strict-transport|x-frame|x-content|content-security'

# Check email reputation (for send domain)
# https://www.mail-tester.com (send a test email there)
```

Or use **securityheaders.com** + **ssllabs.com/ssltest** for graded reports.

## Cutover checklist

When pointing domain at new site:
- [ ] All DNS records prepared in Cloudflare
- [ ] TTL on existing records lowered to 5 min the day before
- [ ] New origin tested via `curl -H 'Host: acme.com' https://new-origin/`
- [ ] Email records double-checked (do NOT change unless intentional)
- [ ] Cloudflare zone proxied for HTTP/S, DNS-only for MX/email
- [ ] SSL/TLS mode: Full (strict)
- [ ] Old origin kept warm for 24 hours (rollback path)
- [ ] Status page incident scheduled (if applicable)

## Anti-patterns

- Pointing apex at IP without DNSSEC / monitoring (IP drift)
- Setting `Flexible SSL` mode (mixed content + insecure cookies)
- Modifying email records during a web migration
- HSTS preload before testing thoroughly (irreversible)
- No CAA records (any CA can issue certs)
- Long TTLs (24h+) before a cutover (rollback impossible)
- Removing nameservers before propagation completes (downtime)
- Not auto-renewing the domain (fatal)

## Pricing notes (for proposals)

- Cloudflare Free: covers most $50K projects
- Cloudflare Pro: $25/mo, image resizing + Polish + extra WAF
- Cloudflare Business: $250/mo, prioritized support, 100% uptime SLA
- Bring-your-own SSL cert: $0 (Let's Encrypt) to $200/yr (EV)

For most builds: free Cloudflare zone is sufficient at launch.
