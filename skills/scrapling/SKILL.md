---
name: scrapling
description: >-
  Scrape websites with Cloudflare bypass, dynamic JS content support, and
  concurrent crawling. Use PROACTIVELY when user says "scrape this site",
  "bypass Cloudflare", "dynamic scraping", "crawl pages", "extract content",
  "scrape with JavaScript", "concurrent scraping", "scrapling", "stealth scraping",
  or "bot protection bypass". Use when standard HTTP requests fail due to bot
  protection or when JavaScript rendering is required.
allowed-tools: Read Bash WebFetch
argument-hint: "[url] (optional)"
disable-model-invocation: false
user-invocable: true
model: sonnet
license: Proprietary
metadata:
  author: yasmine-seidu
  version: "1.0.0"
  category: data-collection
context: fork
agent: general-purpose
---

# Scrapling Web Scraping Skill

**Version:** 1.0  
**Created:** 2026-02-23  
**Python Path:** `/home/clawdbot/venvs/scrapling/bin/python3`

---

## When to Use

Use Scrapling for web scraping when:

- ✅ Need to bypass anti-bot systems (Cloudflare Turnstile, etc.)
- ✅ Website has dynamic content (JavaScript-rendered)
- ✅ Website structure changes frequently (use adaptive mode)
- ✅ Need fast, concurrent crawling
- ✅ Scraping multiple pages from same site (use sessions)
- ✅ Need structured data extraction with selectors

**Do NOT use when:**
- ❌ Simple static pages (use built-in `web_fetch` tool instead)
- ❌ API exists (always prefer API over scraping)
- ❌ Single page, simple extraction (web_fetch is faster)

---

## Quick Start

### Basic HTTP Scraping
```bash
~/shared/skills/scrapling/scripts/scrape.sh <url> [css_selector]
```

### Stealth Mode (Bypass Anti-Bot)
```bash
~/shared/skills/scrapling/scripts/scrape_stealth.sh <url> [css_selector]
```

### Examples
```bash
# Get all quotes from quotes.toscrape.com
~/shared/skills/scrapling/scripts/scrape.sh "https://quotes.toscrape.com/" ".quote .text::text"

# Bypass Cloudflare
~/shared/skills/scrapling/scripts/scrape_stealth.sh "https://protected-site.com/" ".product"

# Get full text content
~/shared/skills/scrapling/scripts/scrape.sh "https://example.com/"
```

---

## Available Scripts

| Script | Purpose | Speed | Anti-Bot |
|--------|---------|-------|----------|
| `scrape.sh` | Fast HTTP requests | ⚡ Fast | Basic |
| `scrape_stealth.sh` | Headless browser | 🐌 Slow | ✅ Advanced |
| `scrape_adaptive.sh` | Adaptive selectors | ⚡ Fast | Basic |
| `competitor_pricing.py` | Monitor competitor prices | ⚡ Fast | Basic |
| `lead_scraper.py` | Extract leads from directories | ⚡ Fast | Basic |

---

## Python API

For Python-based agents, use directly:

```python
from scrapling.fetchers import Fetcher, StealthyFetcher

# Fast HTTP
page = Fetcher.get('https://example.com/')
data = page.css('.selector').getall()

# Stealth mode
page = StealthyFetcher.fetch('https://protected-site.com/', 
                              headless=True, 
                              solve_cloudflare=True)
data = page.css('.selector').getall()
```

**Python path:** `/home/clawdbot/venvs/scrapling/bin/python3`

---

## Installation Check

```bash
~/venvs/scrapling/bin/python3 -c "from scrapling.fetchers import Fetcher; print('✅ Scrapling installed')"
```

---

## Documentation

Full setup guide: `~/shared/docs/setup/scrapling-setup.md`

Key concepts:
- CSS selectors: `.class`, `#id`, `tag[attr]`
- Pseudo-elements: `::text`, `::attr(href)`
- Chaining: `page.css('.parent').css('.child')`
- Adaptive mode: Auto-relocate elements when site changes

---

## Use Cases

### Competitor Research (Noor)
Monitor competitor pricing, features, content:
```bash
~/shared/skills/scrapling/scripts/competitor_pricing.py \
  "https://competitor.com/pricing" \
  --output competitor_pricing.json
```

### Lead Generation (Qamar, Laila)
Scrape industry directories for leads:
```bash
~/shared/skills/scrapling/scripts/lead_scraper.py \
  "https://directory.com/companies" \
  --output leads.json
```

### Content Research (Zahra)
Extract competitor blog content for gap analysis:
```bash
~/shared/skills/scrapling/scripts/scrape.sh \
  "https://competitor-blog.com/article" \
  ".article-content"
```

---

## Troubleshooting

**Cloudflare blocking:**
```bash
# Use stealth mode
~/shared/skills/scrapling/scripts/scrape_stealth.sh <url>
```

**Selector not found:**
```bash
# Use adaptive mode (survives site changes)
~/shared/skills/scrapling/scripts/scrape_adaptive.sh <url> <selector>
```

**Script not found:**
```bash
# Check file exists and is executable
ls -la ~/shared/skills/scrapling/scripts/
chmod +x ~/shared/skills/scrapling/scripts/*.sh
```

---

## Support

- Setup guide: `~/shared/docs/setup/scrapling-setup.md`
- Official docs: https://scrapling.readthedocs.io
- GitHub: https://github.com/D4Vinci/Scrapling
- Discord: https://discord.gg/EMgGbDceNQ

---

**Status:** ✅ Installed and tested  
**Last updated:** 2026-02-23 18:55 UTC
