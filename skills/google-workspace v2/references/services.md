# Google Workspace — Services Reference

Full API resource and method listing for all 13 services.

---

## Gmail (`gws gmail`)

```bash
gws gmail <resource> <method> [flags]
```

### API Resources

**users**
- `getProfile` — Get current user's Gmail profile
- `stop` — Stop push notifications for user mailbox
- `watch` — Set up push notification watch

**users.drafts**
- `create` — Create a new draft
- `delete` — Delete a draft
- `get` — Get a specific draft
- `list` — List drafts
- `send` — Send an existing draft
- `update` — Replace a draft

**users.labels**
- `create` — Create a label
- `delete` — Delete a label
- `get` — Get a label
- `list` — List all labels
- `patch` — Patch a label
- `update` — Update a label

**users.messages**
- `batchDelete` — Delete many messages
- `batchModify` — Modify labels on many messages
- `delete` — Delete a message permanently
- `get` — Get a message (`format=full|metadata|minimal|raw`)
- `import` — Import a message
- `insert` — Insert a message
- `list` — List messages (use `q` for search)
- `modify` — Add/remove labels
- `send` — Send a message
- `trash` — Move to Trash
- `untrash` — Remove from Trash
- `attachments.get` — Get an attachment

**users.threads**
- `delete` — Delete a thread
- `get` — Get a thread
- `list` — List threads
- `modify` — Modify labels on a thread
- `trash` — Trash a thread
- `untrash` — Untrash a thread

**users.settings**
- `getAutoForwarding`, `updateAutoForwarding`
- `getImap`, `updateImap`
- `getLanguage`, `updateLanguage`
- `getPop`, `updatePop`
- `getVacation`, `updateVacation`
- `filters.create`, `filters.delete`, `filters.get`, `filters.list`

### Helper Commands
```bash
gws gmail +send --to "email" --subject "subj" --body "text"
gws gmail +triage
gws gmail +watch
```

---

## Calendar (`gws calendar`)

```bash
gws calendar <resource> <method> [flags]
```

### API Resources

**calendarList**
- `list` — List calendars in user's list
- `get`, `insert`, `delete`, `patch`, `update`

**calendars**
- `get` — Get calendar metadata
- `insert` — Create a calendar
- `delete`, `patch`, `update`, `clear`

**events**
- `list` — List events (use `timeMin`, `timeMax`, `q`, `singleEvents`)
- `get` — Get an event
- `insert` — Create an event
- `patch` — Update fields of an event
- `update` — Replace an event
- `delete` — Delete an event
- `move` — Move to another calendar
- `quickAdd` — Create from text (e.g., "Meeting at 3pm tomorrow")
- `instances` — List recurring event instances

**freebusy**
- `query` — Query free/busy info for calendars/groups

**acl**
- `list`, `get`, `insert`, `delete`, `patch`, `update` — Manage access control

**settings**
- `list`, `get` — User settings

### Helper Commands
```bash
gws calendar +insert --summary "Title" --start "ISO8601" --end "ISO8601"
gws calendar +agenda
```

---

## Drive (`gws drive`)

```bash
gws drive <resource> <method> [flags]
```

### API Resources

**files**
- `list` — List files (use `q` for search, `orderBy`, `pageSize`)
- `get` — Get file metadata
- `create` — Create/upload a file
- `update` — Update file metadata or content
- `delete` — Permanently delete a file
- `copy` — Copy a file
- `export` — Export a Google Doc to another format
- `generateIds` — Generate file IDs
- `emptyTrash` — Empty the trash
- `watch` — Watch for file changes

**permissions**
- `list`, `get`, `create`, `delete`, `update` — Manage file sharing

**drives** (Shared Drives)
- `list`, `get`, `create`, `delete`, `update`, `hide`, `unhide`

**changes**
- `list` — List changes since a token
- `getStartPageToken` — Get initial change token
- `watch` — Watch for changes

**comments** / **replies**
- `list`, `get`, `create`, `delete`, `update`

**revisions**
- `list`, `get`, `delete`, `update`

**teamdrives** (legacy shared drives)
- `list`, `get`, `create`, `delete`, `update`

### Helper Commands
```bash
gws drive +upload --file "/path" --name "name.ext" --folder "FOLDER_ID"
```

### Common Search Queries (`q` param)
```
"name = 'My File'"
"mimeType = 'application/vnd.google-apps.folder'"
"'FOLDER_ID' in parents"
"trashed = false"
"modifiedTime > '2026-03-01T00:00:00'"
```

---

## Docs (`gws docs`)

```bash
gws docs <resource> <method> [flags]
```

### API Resources

**documents**
- `create` — Create a document
- `get` — Get document content and formatting
- `batchUpdate` — Apply list of document updates

### Helper Commands
```bash
gws docs +write --doc-id "DOC_ID" --content "Text"
```

---

## Sheets (`gws sheets`)

```bash
gws sheets <resource> <method> [flags]
```

### API Resources

**spreadsheets**
- `create` — Create a spreadsheet
- `get` — Get spreadsheet properties and sheets
- `batchUpdate` — Apply list of updates
- `getByDataFilter` — Get by filter

**spreadsheets.values**
- `get` — Read a range
- `update` — Write to a range
- `append` — Append rows
- `batchGet` — Read multiple ranges
- `batchUpdate` — Write to multiple ranges
- `batchClear` / `clear` — Clear ranges

**spreadsheets.sheets** (tabs)
- `copyTo` — Copy a sheet to another spreadsheet

**spreadsheets.developerMetadata**
- `get`, `search`

### Helper Commands
```bash
gws sheets +read --spreadsheet-id "ID" --range "Sheet1!A1:Z100"
gws sheets +append --spreadsheet-id "ID" --range "Sheet1" --json '[["val1","val2"]]'
```

---

## Slides (`gws slides`)

```bash
gws slides <resource> <method> [flags]
```

### API Resources

**presentations**
- `create` — Create a presentation
- `get` — Get presentation content
- `batchUpdate` — Apply list of updates

**presentations.pages**
- `get` — Get a specific page
- `getThumbnail` — Get page thumbnail image

---

## Tasks (`gws tasks`)

```bash
gws tasks <resource> <method> [flags]
```

### API Resources

**tasklists**
- `list` — List task lists
- `get`, `insert`, `delete`, `patch`, `update`

**tasks**
- `list` — List tasks (use `showCompleted`, `dueMin`, `dueMax`)
- `get`, `insert`, `delete`, `patch`, `update`
- `move` — Reorder a task
- `clear` — Clear completed tasks

---

## Chat (`gws chat`)

```bash
gws chat <resource> <method> [flags]
```

### API Resources

**spaces**
- `list` — List spaces
- `get`, `create`, `delete`, `patch`
- `findDirectMessage` — Find DM space with a user

**spaces.members**
- `list`, `get`, `create`, `delete`

**spaces.messages**
- `list`, `get`, `create`, `update`, `delete`

**spaces.messages.attachments**
- `get`

**spaces.spaceEvents**
- `list`, `get`

**users.spaces.spaceNotificationSetting**
- `get`, `patch`

### Helper Commands
```bash
gws chat +send --space "spaces/SPACE_ID" --text "Message"
```

---

## Meet (`gws meet`)

```bash
gws meet <resource> <method> [flags]
```

### API Resources

**spaces**
- `create` — Create a meeting space
- `get` — Get space details
- `patch` — Update space
- `endActiveConference` — End active conference

**conferenceRecords**
- `list` — List conference records
- `get` — Get a record

**conferenceRecords.participants**
- `list`, `get`

**conferenceRecords.participantSessions**
- `list`, `get`

**conferenceRecords.recordings**
- `list`, `get`

**conferenceRecords.transcripts**
- `list`, `get`

**conferenceRecords.transcripts.entries**
- `list`, `get`

---

## Forms (`gws forms`)

```bash
gws forms <resource> <method> [flags]
```

### API Resources

**forms**
- `create` — Create a form
- `get` — Get form
- `batchUpdate` — Update form structure
- `setPublishSettings` — Set publishing options

**forms.responses**
- `list` — List responses
- `get` — Get a specific response

**forms.watches**
- `list`, `create`, `delete`, `renew`

---

## Keep (`gws keep`)

```bash
gws keep <resource> <method> [flags]
```

### API Resources

**notes**
- `create` — Create a note
- `get` — Get a note
- `list` — List notes (use `filter` for label filtering)
- `delete` — Delete a note

**notes.permissions**
- `batchCreate`, `batchDelete`

**media**
- `download` — Download note media

---

## People (`gws people`)

```bash
gws people <resource> <method> [flags]
```

### API Resources

**people**
- `get` — Get a person's profile
- `getBatchGet` — Get multiple people
- `listDirectoryPeople` — List directory contacts
- `searchDirectoryPeople` — Search directory
- `createContact` — Create a contact
- `deleteContact` — Delete a contact
- `updateContact` — Update a contact
- `searchContacts` — Search personal contacts

**people.connections** (personal contacts)
- `list` — List contacts (use `personFields`)

**otherContacts**
- `list`, `copyOtherContactToMyContactsGroup`

**contactGroups**
- `list`, `get`, `create`, `delete`, `update`, `batchGet`

---

## Admin Reports (`gws admin`)

```bash
gws admin <resource> <method> [flags]
```

### API Resources

**activities**
- `list` — List audit log activities
  - `applicationName`: `login`, `admin`, `calendar`, `drive`, `groups`, `mobile`, `rules`, `saml`, `token`, `user_accounts`
- `watch` — Subscribe to activity notifications

**channels**
- `stop` — Stop a notification channel

**customerUsageReports**
- `get` — Aggregate usage data for the domain

**entityUsageReports**
- `get` — Usage data for specific entities (apps, devices)

**userUsageReport**
- `get` — Per-user usage data
