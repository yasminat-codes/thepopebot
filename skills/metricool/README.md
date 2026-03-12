# Metricool API Integration

Complete wrapper for Metricool's 100+ API endpoints.

## What This Skill Provides

- **Full API coverage** — All documented Metricool endpoints
- **Multi-platform analytics** — Instagram, Facebook, TikTok, YouTube, LinkedIn, X, Pinterest, Twitch, Bluesky, Threads
- **Ads management** — Facebook Ads, Google Ads, TikTok Ads
- **Content scheduling** — Post scheduling, hashtag suggestions, best time analysis
- **Reports** — Templates, logos, PDF generation
- **Link in Bio** — Instagram bio link toolkit
- **Real-time analytics** — Live visitor tracking

## Requirements

- Metricool Advanced or Custom plan (API access required)
- API token from Account Settings → API tab

## Quick Start

```bash
export METRICOOL_USER_TOKEN="your-token"
export METRICOOL_USER_ID="your-user-id"
export METRICOOL_BLOG_ID="your-brand-id"

# Get your brands
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/simpleProfiles?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

## Files

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Main skill file with all endpoints |
| [QUICKSTART.md](QUICKSTART.md) | Get started in 5 minutes |
| [references/](references/) | Detailed endpoint documentation |
| [scripts/](scripts/) | Ready-to-use bash scripts |
| [assets/](assets/) | Curl collections and schemas |

## Documentation

- [API Authentication](references/API-AUTHENTICATION.md)
- [Analytics Endpoints](references/ENDPOINTS-ANALYTICS.md)
- [Ads Endpoints](references/ENDPOINTS-ADS.md)
- [Scheduling Endpoints](references/ENDPOINTS-SCHEDULING.md)
- [Platform Support Matrix](references/PLATFORM-SUPPORT.md)

## License

MIT
