# API Authentication

Complete guide to authenticating with the Metricool API.

## Required Credentials

All Metricool API calls require **three parameters**:

| Parameter | Location | Description |
|-----------|----------|-------------|
| `userToken` | Header `X-Mc-Auth` | API token from Account Settings → API tab |
| `userId` | Query parameter | User identifier for your Metricool account |
| `blogId` | Query parameter | Brand identification number |

## Finding Your Credentials

### User Token (userToken)

1. Log into Metricool
2. Navigate to **Account Settings**
3. Click on **API** tab
4. Copy your API token

**Note:** API access requires **Advanced or Custom plan**.

### User ID (userId)

Your user identifier is visible in:
- Account Settings → API tab
- Browser URL when logged in (look for `userId=` parameter)

### Blog ID (blogId)

The blog ID (brand ID) can be found:
- In the browser URL when viewing a brand: `metricool.com/dashboard?blogId=123456`
- Via the `/admin/simpleProfiles` endpoint

## Request Format

```bash
curl -H "X-Mc-Auth: YOUR_USER_TOKEN" \
  "https://app.metricool.com/api/ENDPOINT?blogId=YOUR_BLOG_ID&userId=YOUR_USER_ID"
```

## Example: List Brands

```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/simpleProfiles?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

Response:
```json
[
  {
    "id": "123456",
    "name": "My Brand",
    "type": "instagram",
    "picture": "https://..."
  }
]
```

## Environment Variables

Set these in your shell or `.env` file:

```bash
export METRICOOL_USER_TOKEN="your-token-here"
export METRICOOL_USER_ID="your-user-id"
export METRICOOL_BLOG_ID="your-brand-id"
```

## Security Best Practices

- **Never commit tokens to version control**
- Use environment variables for all credentials
- Rotate tokens periodically
- Use separate tokens for development and production
- Limit token permissions when possible

## API Plan Requirements

| Plan | API Access |
|------|------------|
| Free | ❌ No |
| Basic | ❌ No |
| Advanced | ✅ Yes |
| Custom | ✅ Yes |

## Troubleshooting

### 401 Unauthorized

**Cause:** Invalid or missing token

**Fix:**
1. Verify token is correct in Account Settings → API
2. Check header format: `X-Mc-Auth: your-token`
3. Ensure no extra spaces or newlines in token

### 403 Forbidden

**Cause:** API access not enabled for your plan

**Fix:** Upgrade to Advanced or Custom plan

### 404 Not Found

**Cause:** Invalid userId or blogId

**Fix:**
1. Verify userId matches your account
2. Verify blogId matches an existing brand
3. Check brand exists in Metricool dashboard
