# Platform Support Matrix

Metrics and endpoints available for each social platform.

## Supported Platforms

| Platform | Analytics | Posts | Ads | Scheduling | Stories | Reels |
|----------|-----------|-------|-----|------------|---------|-------|
| Instagram | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| Facebook | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| TikTok | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| YouTube | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| LinkedIn | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| X (Twitter) | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Pinterest | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Twitch | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Bluesky | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Threads | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Google My Business | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |

---

## Instagram

### Endpoints
- `/stats/instagram/posts` - Posts with metrics
- `/stats/instagram/reels` - Reels with metrics
- `/stats/instagram/stories` - Stories with metrics
- `/stats/gender/instagram` - Gender distribution
- `/stats/age/instagram` - Age distribution
- `/stats/country/instagram` - Country distribution
- `/stats/city/instagram` - City distribution

### Metrics
- Likes, comments, saves, reach, impressions
- Engagement rate, profile visits
- Story views, exits, replies

### Scheduling
- Post scheduling available
- Hashtag suggestions
- Best time to post analysis

---

## Facebook

### Endpoints
- `/stats/facebook/posts` - Page posts
- `/stats/fbgroup/posts` - Group posts
- `/stats/facebook/reels` - Reels
- `/stats/facebook/stories` - Stories
- `/stats/facebookads/campaigns` - Ads campaigns
- `/stats/facebook/boost/{postId}` - Boost posts

### Metrics
- Reach, impressions, engagement
- Shares, comments, reactions
- Video views, click-through rate

### Ads
- Facebook Ads campaigns
- Post boosting
- Campaign metrics (spend, impressions, clicks, conversions)

---

## TikTok

### Endpoints
- `/stats/tiktok/videos` - Videos with metrics
- `/stats/tiktokads/campaigns` - TikTok Ads campaigns

### Metrics
- Views, likes, comments, shares
- Watch time, average watch time
- Traffic sources

### Ads
- TikTok Ads campaigns
- Campaign performance metrics

---

## YouTube

### Endpoints
- `/stats/youtube/videos` - Videos with metrics

### Metrics
- Views, watch time, subscribers
- Likes, dislikes, comments
- Estimated revenue
- Traffic sources

---

## LinkedIn

### Endpoints
- `/stats/linkedin/posts` - Posts with metrics
- `/stats/linkedin/stories` - Stories
- `/actions/linkedin/suggestions` - Company suggestions

### Metrics
- Impressions, clicks, engagement rate
- Followers gained/lost
- Demographics (seniority, industry, company size)

---

## X (Twitter)

### Endpoints
- `/stats/twitter/posts` - Tweets with metrics (deprecated)
- `/stats/twEvents/{type}` - Follow/unfollow events
- `/stats/rt/twitter/tweets/{type}` - Real-time tweets/mentions
- `/stats/rt/twitterProfile` - Real-time profile
- `/actions/twitter/suggestions` - Account suggestions
- `/stats/twitter/follow` - Follow account
- `/stats/twitter/unfollow` - Unfollow account

### Metrics
- Impressions, retweets, likes, replies
- Profile visits, followers
- Tweet engagement rate

---

## Pinterest

### Endpoints
- Via `/stats/timeline/{metric}` with `pinterestEngagement`

### Metrics
- Saves, impressions, clicks
- Closeups, pin clicks

---

## Twitch

### Endpoints
- `/stats/twitch/videos` - Videos with metrics
- `/stats/twitch/clips` - Clips from video
- `/stats/twitch/video/clips` - Channel clips
- `/stats/twitch/subscriptions` - Subscriptions
- `/stats/twitch/subscriptions/doughnut` - Subscriber distribution

### Metrics
- Views, clips created
- Subscriptions by tier
- Average viewers

---

## Bluesky

### Endpoints
- `/stats/bluesky/posts` - Posts with metrics
- `/actions/bluesky/suggestions` - Account suggestions

### Metrics
- Likes, reposts, replies
- Follower count

---

## Threads

### Endpoints
- `/stats/threads/posts` - Posts with metrics

### Metrics
- Likes, quotes, replies
- Reposts

---

## Google My Business

### Endpoints
- `/stats/gmb/review` - Reviews
- `/stats/gmb/reviewbyid` - Specific review
- `/stats/gmb/review/reply` - Reply to review
- `/stats/gmb/review/reply/remove` - Remove reply
- `/stats/gmb/media/{type}` - Media (photos/videos)

### Metrics
- Review count, average rating
- Photo/video views
- Search impressions, actions

---

## Demographics Endpoints

All platforms support these demographic endpoints:

| Endpoint | Description |
|----------|-------------|
| `/stats/gender/{provider}` | Followers by gender |
| `/stats/gender-age/{provider}` | Followers by gender and age |
| `/stats/age/{provider}` | Followers by age |
| `/stats/country/{provider}` | Followers by country |
| `/stats/city/{provider}` | Followers by city |
| `/stats/trafficsource/{provider}` | Traffic source distribution |

Replace `{provider}` with: `instagram`, `facebook`, `tiktok`, `youtube`, `linkedin`, `x`, `pinterest`, `twitch`, `bluesky`, `threads`.

---

## Content Type Support

| Content Type | Instagram | Facebook | TikTok | YouTube | LinkedIn | X |
|--------------|-----------|----------|--------|---------|----------|---|
| Posts | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Reels/Shorts | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Stories | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| Live | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
