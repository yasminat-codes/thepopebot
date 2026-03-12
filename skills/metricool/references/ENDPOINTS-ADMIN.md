# Admin & Profile Endpoints

Manage brands, profiles, and account settings.

## Base URL

```
https://app.metricool.com/api
```

## Authentication

All endpoints require:
- Header: `X-Mc-Auth: YOUR_TOKEN`
- Query params: `blogId`, `userId`

---

## GET /admin/simpleProfiles

List all brands for the authenticated user.

**Parameters:** None (beyond auth)

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/simpleProfiles?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

**Response:**
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

---

## GET /admin/profiles-auth

Get authenticated user brands with full details.

**Parameters:** None

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/profiles-auth?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

## GET /admin/max-profiles

Get maximum number of brands allowed for the authenticated user.

**Parameters:** None

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/max-profiles?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

**Response:** `10` (integer)

---

## GET /admin/add-profile

Create a new profile/brand.

**Parameters:** None

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/add-profile?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

## GET /admin/delete-profile

Remove the current brand.

**Parameters:** None

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/delete-profile?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

**Response:** `true` (boolean)

---

## GET /admin/restore-profile

Restore a previously deleted brand.

**Parameters:** None

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/restore-profile?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

## GET /admin/update-label-blog

Update brand label/name.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| newName | string | Yes | New brand name |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/update-label-blog?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&newName=New%20Brand%20Name"
```

---

## GET /admin/profile/setproperty

Update a brand property.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| name | string | Yes | Property name |
| value | string | Yes | Property value |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/profile/setproperty?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&name=timezone&value=America/New_York"
```

---

## GET /admin/profile/getproperty

Get a brand property value.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| name | string | Yes | Property name |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/profile/getproperty?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&name=timezone"
```

---

## GET /admin/blog/profiles

Get brand picture URL.

**Parameters:** None

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/blog/profiles?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

## DELETE /admin/other-free-connections

Delete other free connections.

**Parameters:** None

**Example:**
```bash
curl -X DELETE -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/other-free-connections?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

## GET /admin/detectwebsite

Detect website information.

**Parameters:** None

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/detectwebsite?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

## GET /admin/report-logo

Get report logo URL.

**Parameters:** None

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/report-logo?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```
