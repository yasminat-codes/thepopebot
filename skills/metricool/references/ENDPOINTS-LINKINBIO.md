# Link in Bio Endpoints

Instagram bio link management — catalogs, buttons, and images.

## Base URL

```
https://app.metricool.com/api
```

---

## Get Content

### GET /linkinbio/instagram/getbiocatalog

Get Instagram bio link catalog contents.

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/linkinbio/instagram/getbiocatalog?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

**Response:**
```json
[
  {
    "id": "item_123",
    "type": "image",
    "imageUrl": "https://...",
    "link": "https://example.com/product",
    "title": "Product Name"
  }
]
```

---

### GET /linkinbio/instagram/getbioButtons

Get Instagram bio buttons.

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/linkinbio/instagram/getbioButtons?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

**Response:**
```json
[
  {
    "id": "button_123",
    "text": "Shop Now",
    "link": "https://shop.example.com",
    "position": 1,
    "color": "#FF5733"
  }
]
```

---

## Add Content

### POST /linkinbio/instagram/addcatalogitems

Add pictures to Instagram bio link.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| picture | string | Yes | Image URL |
| igid | string | Yes | Instagram post ID |
| timestamp | integer | Yes | Timestamp |

**Example:**
```bash
curl -X POST -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"picture":"https://example.com/image.jpg","igid":"post_123","timestamp":1704067200}' \
  "https://app.metricool.com/api/linkinbio/instagram/addcatalogitems?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

### GET /linkinbio/instagram/addcatalogButton

Add button to Instagram bio link.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| textButton | string | Yes | Button text |
| link | string | Yes | Button URL |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/linkinbio/instagram/addcatalogButton?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&textButton=Shop%20Now&link=https://shop.example.com"
```

---

## Edit Content

### GET /linkinbio/instagram/editcatalogitem

Edit catalog item link.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| itemid | integer | Yes | Item ID |
| link | string | Yes | New link URL |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/linkinbio/instagram/editcatalogitem?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&itemid=123&link=https://newlink.com"
```

---

### GET /linkinbio/instagram/editcatalogbutton

Update button link and text.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| itemid | integer | Yes | Button ID |
| link | string | Yes | New link URL |
| text | string | Yes | New button text |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/linkinbio/instagram/editcatalogbutton?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&itemid=123&link=https://newlink.com&text=New%20Text"
```

---

### GET /linkinbio/instagram/updateButtonPosition

Update button position (reorder).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| itemid | integer | Yes | Button ID |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/linkinbio/instagram/updateButtonPosition?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&itemid=123"
```

---

## Delete Content

### DELETE /linkinbio/instagram/deletecatalogimage

Delete image from bio.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| itemid | integer | Yes | Image item ID |

**Example:**
```bash
curl -X DELETE -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/linkinbio/instagram/deletecatalogimage?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&itemid=123"
```

---

### DELETE /linkinbio/instagram/deletecatalogitem

Delete item from bio link.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| itemid | integer | Yes | Item ID |

**Example:**
```bash
curl -X DELETE -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/linkinbio/instagram/deletecatalogitem?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&itemid=123"
```

---

## Additional Endpoints (via /stats)

These endpoints are also available under `/stats/instagram/`:

| Endpoint | Purpose |
|----------|---------|
| `/stats/instagram/getbiocatalog` | Get bio catalog |
| `/stats/instagram/getbioButtons` | Get bio buttons |
| `/stats/instagram/addcatalogitem` | Add bio picture |
| `/stats/instagram/addcatalogButton` | Add bio button |
| `/stats/instagram/editcatalogitem` | Edit catalog item |
| `/stats/instagram/editcatalogbutton` | Edit bio button |
| `/stats/instagram/editcoloritem` | Update button color |
| `/stats/instagram/deletecatalogitem` | Delete bio item |
| `/stats/instagram/updateButtonPosition` | Reorder buttons |

---

## Complete Workflow Example

```bash
# 1. Get current catalog
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/linkinbio/instagram/getbiocatalog?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"

# 2. Add a button
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/linkinbio/instagram/addcatalogButton?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&textButton=Newsletter&link=https://newsletter.example.com"

# 3. Add an image
curl -X POST -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"picture":"https://example.com/product.jpg","igid":"post_456","timestamp":1704067200}' \
  "https://app.metricool.com/api/linkinbio/instagram/addcatalogitems?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"

# 4. Verify changes
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/linkinbio/instagram/getbioButtons?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```
