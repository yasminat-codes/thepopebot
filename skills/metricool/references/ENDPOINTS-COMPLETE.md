# Complete Endpoint Reference

Every single Metricool API endpoint with resilience notes.

## Endpoint Count: 100+

---

## Admin Service (13 endpoints)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/admin/simpleProfiles` | GET | List all user brands | ✓ | 60s |
| `/admin/profiles-auth` | GET | Authenticated user brands | ✓ | 60s |
| `/admin/max-profiles` | GET | Max profiles allowed | ✓ | 300s |
| `/admin/add-profile` | GET | Create new profile | ✗ | - |
| `/admin/delete-profile` | GET | Remove current brand | ✗ | - |
| `/admin/restore-profile` | GET | Restore deleted brand | ✗ | - |
| `/admin/update-label-blog` | GET | Update brand label | ✗ | - |
| `/admin/profile/setproperty` | GET | Set brand property | ✗ | - |
| `/admin/profile/getproperty` | GET | Get brand property | ✓ | 60s |
| `/admin/blog/profiles` | GET | Brand picture URL | ✓ | 300s |
| `/admin/detectwebsite` | GET | Detect website info | ✓ | 300s |
| `/admin/report-logo` | GET | Get report logo URL | ✓ | 300s |
| `/admin/other-free-connections` | DELETE | Delete free connections | ✗ | - |

---

## Profile Settings Service (4 endpoints)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/profile/lastsyncs` | GET | Get last sync times | ✓ | 60s |
| `/profile/subscription` | GET | Get user subscription | ✓ | 300s |
| `/profile/timezone` | POST | Set brand timezone | ✗ | - |
| `/profile/report/sections` | GET | Get report sections | ✓ | 300s |

---

## Stats Service - Instagram (12 endpoints)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/stats/instagram/posts` | GET | Instagram posts with metrics | ✓ | 300s |
| `/stats/instagram/reels` | GET | Instagram reels with metrics | ✓ | 300s |
| `/stats/instagram/stories` | GET | Instagram stories with metrics | ✓ | 300s |
| `/stats/instagram/getbiocatalog` | GET | Bio catalog contents | ✓ | 60s |
| `/stats/instagram/getbioButtons` | GET | Bio buttons | ✓ | 60s |
| `/stats/instagram/addcatalogitem` | GET | Add bio picture | ✗ | - |
| `/stats/instagram/addcatalogButton` | GET | Add bio button | ✗ | - |
| `/stats/instagram/editcatalogitem` | GET | Edit catalog item | ✗ | - |
| `/stats/instagram/editcatalogbutton` | GET | Edit bio button | ✗ | - |
| `/stats/instagram/editcoloritem` | GET | Update button color | ✗ | - |
| `/stats/instagram/deletecatalogitem` | GET | Delete bio item | ✗ | - |
| `/stats/instagram/updateButtonPosition` | GET | Reorder buttons | ✗ | - |

---

## Stats Service - Facebook (11 endpoints)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/stats/facebook/posts` | GET | Facebook page posts | ✓ | 300s |
| `/stats/fbgroup/posts` | GET | Facebook group posts | ✓ | 300s |
| `/stats/facebook/reels` | GET | Facebook reels | ✓ | 300s |
| `/stats/facebook/stories` | GET | Facebook stories | ✓ | 300s |
| `/stats/facebook/boost/{postId}` | GET | Boost published post | ✗ | - |
| `/stats/facebook/boost/pending/{postId}` | GET | Boost scheduled post | ✗ | - |
| `/stats/facebook/getvalue` | GET | Get boost budget | ✓ | 60s |

---

## Stats Service - Other Platforms (15 endpoints)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/stats/tiktok/videos` | GET | TikTok videos | ✓ | 300s |
| `/stats/youtube/videos` | GET | YouTube videos | ✓ | 300s |
| `/stats/linkedin/posts` | GET | LinkedIn posts | ✓ | 300s |
| `/stats/linkedin/stories` | GET | LinkedIn stories | ✓ | 300s |
| `/stats/twitter/posts` | GET | X/Twitter posts | ✓ | 300s |
| `/stats/twEvents/{type}` | GET | Twitter follow/unfollow events | ✓ | 300s |
| `/stats/twitch/videos` | GET | Twitch videos | ✓ | 300s |
| `/stats/twitch/clips` | GET | Twitch clips | ✓ | 300s |
| `/stats/twitch/video/clips` | GET | Channel clips | ✓ | 300s |
| `/stats/twitch/subscriptions` | GET | Twitch subscriptions | ✓ | 300s |
| `/stats/twitch/subscriptions/doughnut` | GET | Subscriber distribution | ✓ | 300s |

---

## Stats Service - Ads (7 endpoints)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/stats/facebookads/campaigns` | GET | Facebook Ads campaigns | ✓ | 300s |
| `/stats/facebookads/metricvalue` | GET | Specific metric value | ✓ | 300s |
| `/stats/adwords/campaigns` | GET | Google Ads campaigns | ✓ | 300s |
| `/stats/adwords/keywords` | GET | Google Ads keywords | ✓ | 300s |
| `/stats/ads` | GET | Google Ads list | ✓ | 300s |
| `/stats/tiktokads/campaigns` | GET | TikTok Ads campaigns | ✓ | 300s |

---

## Stats Service - Demographics (8 endpoints)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/stats/gender/{provider}` | GET | Gender distribution | ✓ | 3600s |
| `/stats/gender-age/{provider}` | GET | Gender-age distribution | ✓ | 3600s |
| `/stats/age/{provider}` | GET | Age distribution | ✓ | 3600s |
| `/stats/country/{provider}` | GET | Country distribution | ✓ | 3600s |
| `/stats/city/{provider}` | GET | City distribution | ✓ | 3600s |
| `/stats/trafficsource/{provider}` | GET | Traffic source | ✓ | 3600s |

---

## Stats Service - Analytics (10 endpoints)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/stats/values/{category}` | GET | Metrics by category | ✓ | 300s |
| `/stats/timeline/{metric}` | GET | Time series data | ✓ | 300s |
| `/stats/aggregation/{metric}` | GET | Aggregated metric | ✓ | 300s |
| `/stats/aggregations/{category}` | GET | Aggregated by category | ✓ | 300s |
| `/stats/distribution/{type}` | GET | Geographic distribution | ✓ | 300s |
| `/stats/posts` | GET | Website posts | ✓ | 300s |
| `/stats/{provider}/posts/types` | GET | Posts by type | ✓ | 300s |
| `/stats/link/distribution/{type}` | GET | Link distribution | ✓ | 300s |

---

## Stats Service - Real-Time (5 endpoints)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/stats/rt/values` | GET | Real-time stats | ✓ | 30s |
| `/stats/rt/pvperhour` | GET | Pageviews per hour | ✓ | 60s |
| `/stats/rt/sessions` | GET | Visit list | ✓ | 30s |
| `/stats/rt/distribution/{type}` | GET | Real-time distribution | ✓ | 60s |
| `/stats/rt/twitter/tweets/{type}` | GET | Real-time tweets | ✓ | 60s |
| `/stats/rt/twitterProfile` | GET | Real-time Twitter profile | ✓ | 60s |

---

## Stats Service - Engagement (5 endpoints)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/stats/postmessage/{provider}` | GET | Post message/comment | ✗ | - |
| `/stats/deletecomment/{provider}` | GET | Delete comment | ✗ | - |
| `/stats/postlike/{provider}` | GET | Like/unlike comment | ✗ | - |
| `/stats/twitter/follow` | GET | Follow Twitter account | ✗ | - |
| `/stats/twitter/unfollow` | GET | Unfollow Twitter account | ✗ | - |

---

## Stats Service - GMB (5 endpoints)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/stats/gmb/review` | GET | GMB reviews | ✓ | 300s |
| `/stats/gmb/reviewbyid` | GET | Specific review | ✓ | 300s |
| `/stats/gmb/review/reply` | GET | Reply to review | ✗ | - |
| `/stats/gmb/review/reply/remove` | GET | Remove review reply | ✗ | - |
| `/stats/gmb/media/{type}` | GET | GMB media | ✓ | 300s |

---

## Planner Service (10 endpoints)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/actions/setTimeZone` | GET | Set timezone | ✗ | - |
| `/actions/twitter/suggestions` | GET | Twitter suggestions | ✓ | 3600s |
| `/actions/bluesky/suggestions` | GET | Bluesky suggestions | ✓ | 3600s |
| `/actions/facebook/suggestions` | GET | Facebook suggestions | ✓ | 3600s |
| `/actions/instagram/suggestions/hashtags` | GET | Hashtag suggestions | ✓ | 3600s |
| `/actions/linkedin/suggestions` | GET | LinkedIn suggestions | ✓ | 3600s |
| `/actions/normalize/image/url` | GET | Validate image URL | ✓ | 86400s |
| `/actions/instagram/required-scopes-to-post` | GET | Required Instagram scopes | ✓ | 86400s |
| `/actions/instagram/auto-candidate-posts-count-for-automation` | GET | Automation candidate count | ✓ | 300s |
| `/actions/facebook/search-location` | GET | Facebook locations | ✓ | 86400s |

---

## Link in Bio Service (9 endpoints)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/linkinbio/instagram/getbiocatalog` | GET | Bio catalog | ✓ | 60s |
| `/linkinbio/instagram/getbioButtons` | GET | Bio buttons | ✓ | 60s |
| `/linkinbio/instagram/addcatalogitems` | POST | Add catalog items | ✗ | - |
| `/linkinbio/instagram/addcatalogButton` | GET | Add button | ✗ | - |
| `/linkinbio/instagram/editcatalogbutton` | GET | Edit button | ✗ | - |
| `/linkinbio/instagram/editcatalogitem` | GET | Edit item | ✗ | - |
| `/linkinbio/instagram/deletecatalogimage` | DELETE | Delete image | ✗ | - |
| `/linkinbio/instagram/deletecatalogitem` | DELETE | Delete item | ✗ | - |
| `/linkinbio/instagram/updateButtonPosition` | GET | Update position | ✗ | - |

---

## Report Service (8 endpoints)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/stats/report/reporttemplateName` | GET | All templates | ✓ | 300s |
| `/stats/report/savetemplate` | POST | Save template | ✗ | - |
| `/stats/report/deletetemplate` | GET | Delete template | ✗ | - |
| `/stats/report/duplicatetemplate` | GET | Duplicate template | ✗ | - |
| `/stats/report/reporttemplateparam` | GET | Template parameters | ✓ | 300s |
| `/stats/report/template/default-resources` | GET | Default resources | ✓ | 86400s |
| `/stats/report/updatereportlogo` | POST | Save report logo | ✗ | - |
| `/stats/report/deletepicture` | GET | Delete logo | ✗ | - |

---

## GIF Service (1 endpoint)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/gifs/search` | GET | Search GIFs | ✓ | 86400s |

---

## Health Check (1 endpoint)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/mtr/ping` | GET | Health check | ✓ | 0s |

---

## Partner Service (1 endpoint)

| Endpoint | Method | Purpose | Retry | Cache |
|----------|--------|---------|-------|-------|
| `/partner/stackCoupon` | PUT | Add coupon | ✗ | - |

---

## Resilience Legend

| Symbol | Meaning |
|--------|---------|
| ✓ Retry | Automatic retry with exponential backoff on transient failures |
| ✗ Retry | No retry (mutation operation) |
| Cache Ns | Response cached for N seconds |

---

## Recommended Cache TTLs

| Data Type | TTL | Reason |
|-----------|-----|--------|
| Real-time stats | 30s | Changes frequently |
| Analytics (posts, videos) | 300s | 5 minutes, reasonable staleness |
| Demographics | 3600s | Changes slowly |
| Suggestions | 3600s | Can be stale for an hour |
| Static data (scopes, resources) | 86400s | Rarely changes |

---

## Rate Limit Handling

All endpoints respect rate limits via:

1. **Header Parsing**: Read `X-RateLimit-Remaining`, `X-RateLimit-Reset`
2. **Proactive Waiting**: Sleep before reset time if approaching limit
3. **429 Handling**: Wait for `Retry-After` header value
4. **Exponential Backoff**: Double delay on each retry

See [RESILIENCE.md](references/RESILIENCE.md) for implementation details.
