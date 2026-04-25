---
name: sitemap-and-ia
description: Build the information architecture for a website — sitemap, URL taxonomy, navigation model, and redirect map. Translates business goals + audience research into a structured page inventory. Use early in a website project, after discovery and before wireframes.
---

# Sitemap & Information Architecture

The sitemap is the project's blueprint. Get it wrong and every downstream
deliverable — wireframes, copy, CMS schema, redirects — has to be redone.

## When to use

- After discovery, before wireframes
- Migrating an existing site (must precede content migration)
- Adding a major section to a live site
- Replatforming (CMS or framework change)

## Inputs

- Discovery answers: business goals, audiences, primary user journeys
- Current site analytics (top pages by traffic, conversion, depth)
- Content inventory (CSV: URL, title, page type, traffic, action)
- Competitive sitemaps (3 reference sites)
- SEO keyword groups (cluster pages by intent)

## Process

### 1. Card sort the existing pages
Export current URLs → categorize by page type:
- Marketing (home, about, contact)
- Product/service detail
- Programmatic (location pages, comparison pages)
- Resource (blog, guides, case studies)
- Conversion (pricing, demo, signup, checkout)
- Legal/footer (privacy, ToS, accessibility)

### 2. Map to user journeys
For each persona, list the 1–3 actions you need them to take. Trace the
shortest path from any entry point to that action. Pages that don't help
any journey are candidates to cut.

### 3. Draft sitemap (3 levels max)
```
/
├── /products
│   ├── /products/[slug]
│   └── /products/compare
├── /pricing
├── /customers              (case studies)
│   └── /customers/[slug]
├── /resources
│   ├── /resources/blog
│   ├── /resources/blog/[slug]
│   └── /resources/guides/[slug]
├── /about
├── /contact
└── /legal
    ├── /privacy
    ├── /terms
    └── /accessibility
```

Rule of thumb: if a page is more than 3 clicks from home, it's effectively
invisible to users and crawlers.

### 4. URL taxonomy
- Lowercase, hyphenated, no trailing slash (or all trailing — pick one)
- No file extensions (`.html`, `.php`)
- No query params for canonical content (use them for filters only)
- No verbs in paths (`/about` not `/learn-about`)
- Date-free for evergreen content (`/blog/[slug]` not `/2024/01/slug`)

### 5. Navigation model
- **Primary nav**: 5–7 items max
- **Mega-menu**: only if you have > 15 destinations to surface
- **Utility nav** (top right): login, locale, support
- **Footer**: comprehensive sitemap (helps SEO + accessibility)
- **Mobile**: hamburger or bottom nav; same top items, no nesting > 1 level

### 6. Redirect map (for migrations)
For every URL on the old site:
| Old URL | New URL | Type | Notes |
|---|---|---|---|
| /about-us | /about | 301 | rename |
| /services/web-design | /products/web | 301 | restructure |
| /old-blog-post-1 | /resources/blog/[new-slug] | 301 | rename |
| /404-test | (gone) | 410 | intentional removal |

Rules:
- 301 (permanent) for renames and restructures
- 410 (gone) for intentional removals (better than soft 404)
- No redirect chains (A→B→C); always direct A→C
- Test 100% of redirects before launch (use sitemap tools below)

## Sitemap deliverables

1. **Visual sitemap** — Whimsical, FigJam, or OmniGraffle
2. **Spreadsheet** — every page with: URL, page type, template, primary CTA,
   target keyword, audience, owner, status
3. **JSON sitemap** — for programmatic generation
4. **`sitemap.xml`** — auto-generated at build time (most CMSes/frameworks
   handle this)

## CMS schema implications

Once the sitemap is locked, derive:
- **Page templates needed** (home, product, blog post, customer, legal)
- **Content models** (Post, Product, Author, Category, etc.)
- **Reusable components** (hero, CTA block, FAQ, testimonial, comparison)
- **Required fields per template** (e.g. blog post: title, slug, hero image,
  excerpt, body, author, published date, tags, related posts)

## Tools

- **Card sorts**: Optimal Workshop, Maze
- **Sitemap diagrams**: Whimsical, FigJam, OmniGraffle, Lucid
- **URL crawl**: Screaming Frog (free under 500 URLs), Sitebulb
- **Redirect testing**: httpstatus.io, Screaming Frog list mode

## Anti-patterns

- 4+ level nesting ("dropdown of dropdowns")
- Different navigation per page (kills mental model)
- Putting product in footer-only ("hidden gems")
- URL slugs with timestamps for evergreen content
- Skipping the redirect map on a migration (kills SEO)
- Building the CMS schema before the sitemap (always wrong order)

## Hand-off checklist

Before declaring IA complete:
- [ ] Every page has a primary CTA defined
- [ ] Every page maps to at least one persona journey
- [ ] Redirect map covers 100% of existing URLs
- [ ] Nav fits on smallest target viewport
- [ ] Page types are deduplicated (no two templates doing the same job)
- [ ] Client has signed off in writing
