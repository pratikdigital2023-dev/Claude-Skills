# Claude-Skills

A curated, installable collection of **1,826 Claude skills** aggregated from
fourteen open-source skill repositories. Every skill in this repo is a standard
[Claude Code Skill](https://docs.claude.com/en/docs/claude-code/skills) — a
folder containing a `SKILL.md` file with YAML frontmatter (`name`,
`description`) and any supporting scripts/resources Claude needs to load on
demand.

## Quick install

To make every skill in this repo available to Claude Code on your machine,
symlink (or copy) the desired collection into your skills directory.

```bash
# clone this repo somewhere persistent
git clone <this-repo-url> ~/Claude-Skills

# user-level skills (available across all projects)
mkdir -p ~/.claude/skills
ln -s ~/Claude-Skills/skills/* ~/.claude/skills/

# OR project-level skills (only in current project)
mkdir -p .claude/skills
ln -s ~/Claude-Skills/skills/<collection>/<skill-name> .claude/skills/
```

After linking, run `/skills` in Claude Code to see them listed.

## What's included

| Collection | Skills | Source |
|---|---:|---|
| [awesome-claude-skills](skills/awesome-claude-skills) | 864 | hesreallyhim/awesome-claude-skills (composio + community) |
| [claude-skills-marketplace](skills/claude-skills-marketplace) | 540 | claude-skills marketplace (team-organized + flat) |
| [ai-skills](skills/ai-skills) | 20 | AI-tool integration skills (Atlassian, Google Workspace, etc.) |
| [bencium-marketplace](skills/bencium-marketplace) | 14 | bencium design + UX marketplace |
| [claude-code](skills/claude-code) | 10 | Anthropic claude-code official plugins |
| [pg-aiguide](skills/pg-aiguide) | 8 | Postgres / Timescale / pgvector skills |
| [ui-ux-pro-max](skills/ui-ux-pro-max) | 7 | UI/UX design system skills |
| [prisma](skills/prisma) | 7 | Prisma ORM skills |
| [agent-skills](skills/agent-skills) | 7 | React / Vercel agent skills |
| [claude-marketplace](skills/claude-marketplace) | 4 | accesslint accessibility skills |
| [caveman-claude](skills/caveman-claude) | 1 | "caveman" coding-style skill |
| [antigravity-guanyang](skills/antigravity-guanyang) | 40 | guanyang/antigravity-skills (unique only) |
| [antigravity-rmyndharis](skills/antigravity-rmyndharis) | 304 | rmyndharis/antigravity-skills (unique only) |

**Total: 1,826 skills, ~64 MB.** (Antigravity collections are deduplicated
against the rest of the repo by skill name; 20 overlapping names — e.g.
`code-reviewer`, `mcp-builder`, `canvas-design` — were skipped.)

## Structure

```
skills/
├── agent-skills/                # React, Vercel, deploy
├── ai-skills/                   # Atlassian, Google Workspace, mssql, etc.
├── awesome-claude-skills/
│   ├── composio-skills/         # 832 Composio API automation skills
│   └── document-skills/         # docx, xlsx, pptx, pdf
├── bencium-marketplace/         # Design / UX / typography
├── caveman-claude/              # Single skill
├── claude-code/                 # Anthropic plugin-dev, hookify, frontend-design
├── claude-marketplace/
│   └── accesslint/              # Accessibility (contrast, link-purpose, etc.)
├── claude-skills-marketplace/
│   ├── _flat-skills/            # 301 flat skills (Gemini-format export)
│   ├── engineering/             # 60 engineering skills
│   ├── marketing-skill/         # 45 marketing skills
│   ├── c-level-advisor/         # 34 advisor skills
│   └── ...                      # finance, ra-qm, product-team, etc.
├── pg-aiguide/                  # Postgres, Timescale, pgvector
├── prisma/                      # Prisma ORM
└── ui-ux-pro-max/               # Banner, brand, design-system, slides
```

Each leaf folder with a `SKILL.md` is a standalone, self-contained skill.

## Usage notes

- **Naming collisions**: a few skill names (e.g. `code-reviewer`,
  `postgres`) appear in multiple collections. Symlink or copy only one to
  `~/.claude/skills/` to avoid ambiguous activation.
- **License**: each skill retains its upstream license. See each collection's
  README (where present) for details.
- **Updating**: re-running the import script will overwrite the collection;
  local edits should be made in your `~/.claude/skills/` working copy.

## Source archives imported

1. agent-skills (main)
2. ai-skills (main)
3. awesome-claude-skills (main + master)
4. bencium-marketplace (main)
5. caveman-claude-skill (master)
6. claude-code (main)
7. claude-marketplace (main)
8. claude-skills (main)
9. pg-aiguide (main)
10. skills / Prisma (main)
11. ui-ux-pro-max-skill (main)
12. guanyang/antigravity-skills (cloned from GitHub, unique skills only)
13. rmyndharis/antigravity-skills (cloned from GitHub, unique skills only)
