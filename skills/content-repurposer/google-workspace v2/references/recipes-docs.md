# Recipes — Documents (2)

## create-doc-from-template
**Services:** Drive, Docs

```bash
# 1. Find the template
gws drive files list \
  --params '{"q":"name='\''Client Proposal Template'\''"}' \
  | jq -r '.files[0].id'

# 2. Copy the template
gws drive files copy \
  --params '{"fileId":"TEMPLATE_ID"}' \
  --json '{"name":"Client Proposal - Acme Corp", "parents":["DESTINATION_FOLDER_ID"]}'
# Note new file ID

# 3. Populate with content
gws docs +write --doc-id "NEW_DOC_ID" --content "[proposal content]"

# 4. Share with team
gws drive permissions create \
  --params '{"fileId":"NEW_DOC_ID","sendNotificationEmail":"false"}' \
  --json '{"role":"writer","type":"user","emailAddress":"team@smarterflo.com"}'
```

---

## create-presentation
**Services:** Slides, Drive

```bash
# 1. Create presentation
gws slides presentations create \
  --json '{"title": "Q1 Business Review"}'
# Note presentationId

# 2. Get presentation details
gws slides presentations get --params '{"presentationId":"PRESENTATION_ID"}'

# 3. Share with team
gws drive permissions create \
  --params '{"fileId":"PRESENTATION_ID","sendNotificationEmail":"false"}' \
  --json '{"role":"writer","type":"user","emailAddress":"team@smarterflo.com"}'
```
