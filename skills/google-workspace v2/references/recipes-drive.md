# Recipes — Drive (8)

## bulk-download-folder
**Services:** Drive

```bash
# 1. List all files in folder
gws drive files list \
  --params '{"q":"'\''FOLDER_ID'\'' in parents and trashed=false","fields":"files(id,name,mimeType)"}' \
  --page-all

# 2. Regular files — download directly
gws drive files get --params '{"fileId":"FILE_ID","alt":"media"}' -o /tmp/filename.ext

# Google Docs — export as PDF
gws drive files export \
  --params '{"fileId":"FILE_ID","mimeType":"application/pdf"}' \
  -o /tmp/document.pdf

# Google Sheets — export as XLSX
gws drive files export \
  --params '{"fileId":"FILE_ID","mimeType":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}' \
  -o /tmp/sheet.xlsx
```

---

## create-shared-drive
**Services:** Drive

```bash
# 1. Create shared drive (requestId must be a unique UUID)
gws drive drives create \
  --params '{"requestId":"unique-uuid-here"}' \
  --json '{"name": "Team Projects"}'
# Note the drive ID

# 2. Add editor
gws drive permissions create \
  --params '{"fileId":"DRIVE_ID","supportsAllDrives":"true","sendNotificationEmail":"false"}' \
  --json '{"role":"writer","type":"user","emailAddress":"teammate@example.com"}'

# 3. List members
gws drive permissions list --params '{"fileId":"DRIVE_ID","supportsAllDrives":"true"}'
```

---

## share-folder-with-team
**Services:** Drive

```bash
# 1. Find the folder
gws drive files list \
  --params '{"q":"name='\''Project Folder'\'' and mimeType='\''application/vnd.google-apps.folder'\''"}' \
  | jq -r '.files[0].id'

# 2. Add editors
gws drive permissions create \
  --params '{"fileId":"FOLDER_ID","sendNotificationEmail":"false"}' \
  --json '{"role":"writer","type":"user","emailAddress":"editor@example.com"}'

# 3. Add viewers
gws drive permissions create \
  --params '{"fileId":"FOLDER_ID","sendNotificationEmail":"false"}' \
  --json '{"role":"reader","type":"user","emailAddress":"viewer@example.com"}'

# 4. Verify
gws drive permissions list --params '{"fileId":"FOLDER_ID"}'
```

---

## share-doc-and-notify
**Services:** Drive, Docs, Gmail

```bash
# 1. Find the doc
gws drive files list \
  --params '{"q":"name='\''Project Doc'\'' and mimeType='\''application/vnd.google-apps.document'\''"}' \
  | jq -r '.files[0].id'

# 2. Share as editor
gws drive permissions create \
  --params '{"fileId":"DOC_ID","sendNotificationEmail":"false"}' \
  --json '{"role":"writer","type":"user","emailAddress":"collaborator@example.com"}'

# 3. Get web link
gws drive files get --params '{"fileId":"DOC_ID","fields":"webViewLink"}'

# 4. Email collaborators
gws gmail +send \
  --to "collaborator@example.com" \
  --subject "Shared for Collaboration: Project Doc" \
  --body "You now have editor access: [webViewLink]"
```

---

## organize-drive-folder
**Services:** Drive

```bash
# 1. Create project root folder
gws drive files create \
  --json '{"name":"Project Alpha","mimeType":"application/vnd.google-apps.folder","parents":["PARENT_FOLDER_ID"]}'
# Note ROOT_ID

# 2. Create subfolders
for subfolder in "Assets" "Docs" "Reports"; do
  gws drive files create \
    --json "{\"name\":\"$subfolder\",\"mimeType\":\"application/vnd.google-apps.folder\",\"parents\":[\"ROOT_ID\"]}"
done

# 3. Move files into subfolders
gws drive files update \
  --params '{"fileId":"FILE_ID","addParents":"SUBFOLDER_ID","removeParents":"CURRENT_PARENT_ID"}'

# 4. Verify structure
gws drive files list --params '{"q":"'\''ROOT_ID'\'' in parents"}' --format table
```

---

## watch-drive-changes
**Services:** Drive (events)

```bash
# 1. Get initial page token
gws drive changes getStartPageToken

# 2. Subscribe to changes
gws events subscribe \
  --resource "https://www.googleapis.com/drive/v3/changes" \
  --params '{"pageToken":"TOKEN"}'
# Note subscription ID and expiration

# 3. List active subscriptions
gws events list

# 4. Renew before expiry (typically 1 week)
gws events renew --subscription-id "SUB_ID"
```

---

## find-large-files
**Services:** Drive

```bash
# 1. List files sorted by size descending
gws drive files list \
  --params '{
    "orderBy": "quotaBytesUsed desc",
    "pageSize": 20,
    "fields": "files(id,name,size,mimeType,owners,modifiedTime)"
  }' --format table

# 2. Filter to files over 100MB
gws drive files list \
  --params '{"q":"size > 104857600","orderBy":"quotaBytesUsed desc"}' \
  --format table
```

---

## share-event-materials
**Services:** Calendar, Drive

```bash
# 1. Get event attendees
gws calendar events get \
  --params '{"calendarId":"primary","eventId":"EVENT_ID"}' \
  | jq -r '.attendees[].email'

# 2. For each attendee, share the file
gws drive permissions create \
  --params '{"fileId":"FILE_ID","sendNotificationEmail":"false"}' \
  --json '{"role":"reader","type":"user","emailAddress":"attendee@example.com"}'

# 3. Verify permissions
gws drive permissions list --params '{"fileId":"FILE_ID"}'
```
