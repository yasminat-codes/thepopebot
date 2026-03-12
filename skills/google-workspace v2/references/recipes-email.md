# Recipes — Email (9)

## create-gmail-filter
**Services:** Gmail

```bash
# 1. Create the label
gws gmail users labels create \
  --params '{"userId":"me"}' \
  --json '{"name": "Clients/Acme", "labelListVisibility": "labelShow"}'
# Note the label ID from response

# 2. Create the filter
gws gmail users settings filters create \
  --params '{"userId":"me"}' \
  --json '{
    "criteria": {"from": "acme.com"},
    "action": {
      "addLabelIds": ["LABEL_ID"],
      "removeLabelIds": ["INBOX"]
    }
  }'

# 3. Verify
gws gmail users settings filters list --params '{"userId":"me"}'
```

---

## label-and-archive-emails
**Services:** Gmail

```bash
# 1. Search for matching messages
gws gmail users messages list \
  --params '{"userId":"me","q":"from:newsletter@example.com is:inbox","maxResults":50}'

# 2. Bulk label + archive
gws gmail users messages batchModify \
  --params '{"userId":"me"}' \
  --json '{
    "ids": ["MSG_ID_1", "MSG_ID_2"],
    "addLabelIds": ["LABEL_ID"],
    "removeLabelIds": ["INBOX"]
  }'
```

---

## forward-labeled-emails
**Services:** Gmail

```bash
# 1. Find messages with the label
gws gmail users messages list \
  --params '{"userId":"me","labelIds":["LABEL_ID"],"maxResults":20}'

# 2. Get message content
gws gmail users messages get \
  --params '{"userId":"me","id":"MSG_ID","format":"full"}'
# Extract subject, body from payload

# 3. Send forward
gws gmail +send \
  --to "forward-to@example.com" \
  --subject "Fwd: Original Subject" \
  --body "--- Forwarded message ---\n[original body]"
```

---

## save-email-to-doc
**Services:** Gmail, Docs

```bash
# 1. Find the email
gws gmail users messages list \
  --params '{"userId":"me","q":"subject:\"Important Report\"","maxResults":1}'

# 2. Get email content
gws gmail users messages get \
  --params '{"userId":"me","id":"MSG_ID","format":"full"}'
# Extract body from payload.parts[].body.data (base64 decode)

# 3. Create a new Doc
gws docs documents create --json '{"title": "Email: Important Report"}'

# 4. Write email content to the doc
gws docs +write --doc-id "DOC_ID" --content "[decoded email body]"
```

---

## save-email-attachments
**Services:** Gmail, Drive

```bash
# 1. Search for emails with attachments
gws gmail users messages list \
  --params '{"userId":"me","q":"has:attachment from:client@example.com"}' \
  | jq -r '.messages[].id' > /tmp/msg_ids.txt

# 2. Get message to find attachment IDs
# Email bodies are base64url-encoded in the API response
gws gmail users messages get \
  --params '{"userId":"me","id":"MSG_ID","format":"full"}' > /tmp/message.json

# Extract attachment IDs from nested parts
cat /tmp/message.json | jq '.payload.parts[] | select(.body.attachmentId != null) | {filename: .filename, attachmentId: .body.attachmentId}'

# Also check nested parts (attachments may be 2 levels deep)
cat /tmp/message.json | jq '.. | objects | select(.attachmentId?) | {filename: .filename, attachmentId: .attachmentId}'

# 3. Download each attachment (response body.data is base64url-encoded)
gws gmail users messages attachments get \
  --params '{"userId":"me","messageId":"MSG_ID","id":"ATTACHMENT_ID"}' > /tmp/att_response.json

# Decode base64url to file
cat /tmp/att_response.json | jq -r '.data' | tr '_-' '/+' | base64 -d > /tmp/attachment.pdf

# 4. Upload to Drive
gws drive files create \
  --json '{"name":"attachment.pdf","parents":["FOLDER_ID"]}' \
  --upload /tmp/attachment.pdf
```

---

## draft-email-from-doc
**Services:** Docs, Gmail

```bash
# 1. Get doc content
gws docs documents get --params '{"documentId":"DOC_ID"}'
# Extract text from body.content[].paragraph.elements[].textRun.content

# 2. Send email using doc content as body
gws gmail +send \
  --to "recipient@example.com" \
  --subject "Document Title" \
  --body "[extracted doc content]"
```

---

## create-vacation-responder
**Services:** Gmail

```bash
# 1. Enable vacation responder
gws gmail users settings updateVacation \
  --params '{"userId":"me"}' \
  --json '{
    "enableAutoReply": true,
    "responseSubject": "Out of Office",
    "responseBodyPlainText": "I am out of office from March 10-17. I will respond when I return.",
    "startTime": "1741564800000",
    "endTime": "1742256000000",
    "restrictToContacts": false
  }'

# 2. Verify
gws gmail users settings getVacation --params '{"userId":"me"}'

# When returning, disable it:
gws gmail users settings updateVacation \
  --params '{"userId":"me"}' \
  --json '{"enableAutoReply": false}'
```

---

## send-team-announcement
**Services:** Gmail, Chat

```bash
# 1. Send email to team
gws gmail +send \
  --to "team@smarterflo.com" \
  --subject "Announcement: New Process" \
  --body "Hi team, [announcement content]"

# 2. Post to Chat space
gws chat spaces messages create \
  --params '{"parent":"spaces/SPACE_ID"}' \
  --json '{"text": "Announcement: New Process — [summary]. Check email for details."}'
```

---

## email-drive-link
**Services:** Drive, Gmail

```bash
# 1. Find the file
gws drive files list --params '{"q":"name='\''Report Q1'\''"}' \
  | jq -r '.files[0].id'

# 2. Share with recipient
gws drive permissions create \
  --params '{"fileId":"FILE_ID","sendNotificationEmail":"false"}' \
  --json '{"role":"reader","type":"user","emailAddress":"recipient@example.com"}'

# 3. Get the file's webViewLink
gws drive files get \
  --params '{"fileId":"FILE_ID","fields":"webViewLink,name"}'

# 4. Email the link
gws gmail +send \
  --to "recipient@example.com" \
  --subject "Shared: Report Q1" \
  --body "Here is the document: [webViewLink]"
```
