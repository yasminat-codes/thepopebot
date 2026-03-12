# Report Endpoints

Template management, logo customization, and report generation.

## Base URL

```
https://app.metricool.com/api
```

---

## Template Management

### GET /stats/report/reporttemplateName

Get all report templates for the user.

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/report/reporttemplateName?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

**Response:**
```json
[
  {
    "id": "template_123",
    "name": "Monthly Report",
    "createdAt": 1704067200,
    "sections": ["instagram", "facebook", "tiktok"]
  }
]
```

---

### POST /stats/report/savetemplate

Save a report template.

**Body:** JSON with template configuration

**Example:**
```bash
curl -X POST -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Weekly Report","sections":["instagram","facebook"]}' \
  "https://app.metricool.com/api/stats/report/savetemplate?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

### GET /stats/report/deletetemplate

Delete a template.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| templateId | string | Yes | Template ID to delete |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/report/deletetemplate?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&templateId=template_123"
```

---

### GET /stats/report/duplicatetemplate

Duplicate a template with a new name.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| templateId | string | Yes | Source template ID |
| templateName | string | Yes | New template name |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/report/duplicatetemplate?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&templateId=template_123&templateName=Copy%20of%20Report"
```

---

### GET /stats/report/reporttemplateparam

Get parameters of a specific template.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| templateId | integer | Yes | Template ID |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/report/reporttemplateparam?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&templateId=123"
```

---

### GET /stats/report/template/default-resources

Get default template resources.

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/report/template/default-resources?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

## Logo Management

### POST /stats/report/updatereportlogo

Save a logo for reports.

**Body:** Multipart form data with image

**Example:**
```bash
curl -X POST -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  -F "logo=@logo.png" \
  "https://app.metricool.com/api/stats/report/updatereportlogo?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

### GET /stats/report/deletepicture

Delete the report logo.

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/report/deletepicture?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

## Profile Reports

### GET /profile/report/sections

Get report sections configuration.

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/profile/report/sections?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

**Response:**
```json
{
  "sections": [
    {"id": "summary", "name": "Summary", "enabled": true},
    {"id": "instagram", "name": "Instagram", "enabled": true},
    {"id": "facebook", "name": "Facebook", "enabled": true},
    {"id": "tiktok", "name": "TikTok", "enabled": false}
  ]
}
```

---

## Common Use Cases

### Create Monthly Report Template

```bash
# Save template
curl -X POST -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monthly Marketing Report",
    "sections": ["summary", "instagram", "facebook", "tiktok", "youtube"],
    "dateRange": "last_30_days"
  }' \
  "https://app.metricool.com/api/stats/report/savetemplate?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"

# Upload logo
curl -X POST -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  -F "logo=@company_logo.png" \
  "https://app.metricool.com/api/stats/report/updatereportlogo?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

### List and Duplicate Template

```bash
# List templates
TEMPLATES=$(curl -s -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/report/reporttemplateName?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID")

# Extract first template ID
TEMPLATE_ID=$(echo "$TEMPLATES" | jq -r '.[0].id')

# Duplicate
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/report/duplicatetemplate?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&templateId=$TEMPLATE_ID&templateName=Q1%202024%20Report"
```
