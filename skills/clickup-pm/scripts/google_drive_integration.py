#!/usr/bin/env python3
"""
Google Drive Integration for ClickUp PM

Creates and manages folder structure:
📁 ClickUp PM
├── 📁 Clients
│   └── 📁 [Client Name]
│       ├── 📁 Projects
│       │   └── 📁 [Project Name]
│       ├── 📁 Research
│       ├── 📁 SOPs
│       └── 📁 Meeting Notes
├── 📁 Research (non-client)
│   ├── 📁 Niche
│   ├── 📁 Market
│   ├── 📁 Persona
│   └── 📁 Campaign
├── 📁 Templates
└── 📁 Internal

Usage:
    python google_drive_integration.py --setup                    # Initial setup
    python google_drive_integration.py --create-client "Acme"     # Create client folder
    python google_drive_integration.py --create-doc "Brief" --client "Acme" --project "Website"
    python google_drive_integration.py --list                     # List structure
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
# ]
# ///

from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = '/home/clawdbot/.config/google/service-account.json'
DELEGATED_USER = 'yasmine@smarterflo.com'
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents'
]

DATA_DIR = Path(__file__).parent.parent / "data"
CONFIG_FILE = DATA_DIR / "google_drive_config.json"

# Document templates
DOC_TEMPLATES = {
    "project_brief": {
        "title": "Project Brief",
        "content": """# Project Brief: {project_name}

**Client:** {client_name}
**Created:** {date}
**Status:** Draft

---

## Overview

[Brief description of the project]

## Objectives

- 
- 
- 

## Scope

### In Scope
- 

### Out of Scope
- 

## Timeline

| Phase | Duration | Dates |
|-------|----------|-------|
| Discovery | | |
| Design | | |
| Development | | |
| Testing | | |
| Launch | | |

## Deliverables

1. 
2. 
3. 

## Success Criteria

- 
- 

## Stakeholders

| Name | Role | Contact |
|------|------|---------|
| | | |

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| | | | |

---

*Document maintained by Smarterflo*
"""
    },
    "requirements": {
        "title": "Requirements Document",
        "content": """# Requirements: {project_name}

**Client:** {client_name}
**Created:** {date}
**Version:** 1.0

---

## Business Requirements

### Goals
- 

### Problems to Solve
- 

## Functional Requirements

### Must Have (P1)
- 

### Should Have (P2)
- 

### Nice to Have (P3)
- 

## Technical Requirements

### Platform/Stack
- 

### Integrations
- 

### Performance
- 

### Security
- 

## User Stories

### As a [user type], I want to [action] so that [benefit]

1. 
2. 

## Acceptance Criteria

- [ ] 
- [ ] 

## Constraints

- 

## Assumptions

- 

---

*Document maintained by Smarterflo*
"""
    },
    "technical_spec": {
        "title": "Technical Specification",
        "content": """# Technical Spec: {project_name}

**Client:** {client_name}
**Created:** {date}
**Author:** Yasmine Seidu

---

## Architecture Overview

[High-level architecture diagram or description]

## Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Frontend | | |
| Backend | | |
| Database | | |
| Hosting | | |

## Data Model

### Entities
- 

### Relationships
- 

## API Design

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| | | |

## Integrations

### External Services
- 

### Authentication
- 

## Error Handling

- 

## Monitoring & Logging

- 

## Deployment

### Environments
- Development
- Staging
- Production

### CI/CD
- 

## Security Considerations

- 

---

*Document maintained by Smarterflo*
"""
    },
    "sop": {
        "title": "Standard Operating Procedure",
        "content": """# SOP: {title}

**Client:** {client_name}
**Created:** {date}
**Last Updated:** {date}
**Owner:** Yasmine Seidu

---

## Purpose

[What this SOP covers]

## Scope

[Who should use this and when]

## Prerequisites

- 

## Procedure

### Step 1: [Title]
1. 
2. 
3. 

### Step 2: [Title]
1. 
2. 

### Step 3: [Title]
1. 
2. 

## Troubleshooting

| Issue | Solution |
|-------|----------|
| | |

## Related Documents

- 

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| {date} | 1.0 | Initial version | Yasmine |

---

*Document maintained by Smarterflo*
"""
    },
    "meeting_notes": {
        "title": "Meeting Notes",
        "content": """# Meeting Notes: {title}

**Date:** {date}
**Client:** {client_name}
**Attendees:** 

---

## Agenda

1. 
2. 
3. 

## Discussion

### Topic 1
- 

### Topic 2
- 

## Decisions Made

- 

## Action Items

| Action | Owner | Due Date |
|--------|-------|----------|
| | | |

## Next Steps

- 

## Next Meeting

**Date:** 
**Topics:** 

---

*Notes by Smarterflo*
"""
    },
    "research": {
        "title": "Research Document",
        "content": """# {research_type} Research: {subject}

**Created:** {date}
**Researcher:** Lena (AI Assistant)
**Status:** In Progress

---

## Executive Summary

[Key findings in 2-3 sentences]

## Research Objectives

- 
- 

## Methodology

- Sources: Perplexity, Tavily, Google, Brave, Reddit
- Date Range: 

## Findings

### Section 1
- 

### Section 2
- 

### Section 3
- 

## Key Insights

1. 
2. 
3. 

## Recommendations

- 

## Sources & Citations

1. 
2. 

## Appendix

[Raw data, additional details]

---

*Research conducted by Smarterflo AI*
"""
    }
}


def get_credentials():
    """Get Google API credentials."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
        subject=DELEGATED_USER
    )
    return credentials

def get_drive_service():
    """Get Google Drive service."""
    creds = get_credentials()
    return build('drive', 'v3', credentials=creds)

def get_docs_service():
    """Get Google Docs service."""
    creds = get_credentials()
    return build('docs', 'v1', credentials=creds)

def load_config() -> dict:
    """Load drive config."""
    DATA_DIR.mkdir(exist_ok=True)
    if CONFIG_FILE.exists():
        return json.load(open(CONFIG_FILE))
    return {"root_folder_id": None, "folders": {}}

def save_config(config: dict):
    """Save drive config."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def create_folder(service, name: str, parent_id: str = None) -> dict:
    """Create a folder in Google Drive."""
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]
    
    folder = service.files().create(
        body=file_metadata,
        fields='id, name, webViewLink'
    ).execute()
    
    return folder

def find_folder(service, name: str, parent_id: str = None) -> dict:
    """Find a folder by name."""
    query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    results = service.files().list(
        q=query,
        fields="files(id, name, webViewLink)"
    ).execute()
    
    files = results.get('files', [])
    return files[0] if files else None

def get_or_create_folder(service, name: str, parent_id: str = None) -> dict:
    """Get existing folder or create new one."""
    folder = find_folder(service, name, parent_id)
    if folder:
        return folder
    return create_folder(service, name, parent_id)

def setup_folder_structure(service) -> dict:
    """Set up the complete folder structure."""
    print("Setting up ClickUp PM folder structure...")
    
    config = load_config()
    
    # Create root folder
    root = get_or_create_folder(service, "ClickUp PM")
    config["root_folder_id"] = root["id"]
    config["root_folder_link"] = root.get("webViewLink")
    print(f"  ✓ Root folder: ClickUp PM")
    
    # Create main subfolders
    subfolders = {
        "clients": "Clients",
        "research": "Research",
        "templates": "Templates",
        "internal": "Internal"
    }
    
    config["folders"] = {}
    
    for key, name in subfolders.items():
        folder = get_or_create_folder(service, name, root["id"])
        config["folders"][key] = {
            "id": folder["id"],
            "link": folder.get("webViewLink")
        }
        print(f"  ✓ {name}")
    
    # Create research subfolders
    research_types = ["Niche", "Market", "Persona", "Campaign", "Industry", "Competitor"]
    config["folders"]["research_types"] = {}
    
    for rtype in research_types:
        folder = get_or_create_folder(service, rtype, config["folders"]["research"]["id"])
        config["folders"]["research_types"][rtype.lower()] = {
            "id": folder["id"],
            "link": folder.get("webViewLink")
        }
        print(f"    ✓ Research/{rtype}")
    
    save_config(config)
    print(f"\n✅ Folder structure created!")
    print(f"   Root: {config.get('root_folder_link', 'N/A')}")
    
    return config

def create_client_folder(service, client_name: str) -> dict:
    """Create folder structure for a new client."""
    config = load_config()
    
    if not config.get("root_folder_id"):
        print("Run --setup first to create folder structure")
        return None
    
    clients_folder_id = config["folders"]["clients"]["id"]
    
    # Create client folder
    client_folder = get_or_create_folder(service, client_name, clients_folder_id)
    print(f"✓ Created client folder: {client_name}")
    
    # Create subfolders
    subfolders = ["Projects", "Research", "SOPs", "Meeting Notes"]
    client_config = {
        "id": client_folder["id"],
        "link": client_folder.get("webViewLink"),
        "subfolders": {}
    }
    
    for subfolder in subfolders:
        folder = get_or_create_folder(service, subfolder, client_folder["id"])
        client_config["subfolders"][subfolder.lower().replace(" ", "_")] = {
            "id": folder["id"],
            "link": folder.get("webViewLink")
        }
        print(f"  ✓ {client_name}/{subfolder}")
    
    # Save to config
    if "clients" not in config:
        config["clients"] = {}
    config["clients"][client_name] = client_config
    save_config(config)
    
    return client_config

def create_project_folder(service, client_name: str, project_name: str) -> dict:
    """Create folder for a specific project."""
    config = load_config()
    
    # Get or create client folder
    if client_name not in config.get("clients", {}):
        create_client_folder(service, client_name)
        config = load_config()
    
    projects_folder_id = config["clients"][client_name]["subfolders"]["projects"]["id"]
    
    # Create project folder
    project_folder = get_or_create_folder(service, project_name, projects_folder_id)
    print(f"✓ Created project folder: {client_name}/{project_name}")
    
    # Create Deliverables subfolder
    deliverables = get_or_create_folder(service, "Deliverables", project_folder["id"])
    print(f"  ✓ Deliverables subfolder")
    
    project_config = {
        "id": project_folder["id"],
        "link": project_folder.get("webViewLink"),
        "deliverables_id": deliverables["id"]
    }
    
    # Save to config
    if "projects" not in config["clients"][client_name]:
        config["clients"][client_name]["projects"] = {}
    config["clients"][client_name]["projects"][project_name] = project_config
    save_config(config)
    
    return project_config

def create_google_doc(docs_service, drive_service, doc_type: str, 
                      folder_id: str, variables: dict) -> dict:
    """Create a Google Doc from template."""
    if doc_type not in DOC_TEMPLATES:
        return {"error": f"Unknown doc type: {doc_type}"}
    
    template = DOC_TEMPLATES[doc_type]
    
    # Prepare variables
    variables["date"] = datetime.now().strftime("%Y-%m-%d")
    
    # Format title and content
    title = template["title"]
    if "project_name" in variables:
        title = f"{title} - {variables['project_name']}"
    elif "title" in variables:
        title = f"{template['title']}: {variables['title']}"
    elif "subject" in variables:
        title = f"{template['title']}: {variables['subject']}"
    
    content = template["content"]
    for key, value in variables.items():
        content = content.replace(f"{{{key}}}", str(value))
    
    # Create the doc
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]
    
    # Add content
    requests = [{
        "insertText": {
            "location": {"index": 1},
            "text": content
        }
    }]
    
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": requests}
    ).execute()
    
    # Move to correct folder
    drive_service.files().update(
        fileId=doc_id,
        addParents=folder_id,
        removeParents='root',
        fields='id, parents'
    ).execute()
    
    # Get the doc link
    doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"
    
    return {
        "id": doc_id,
        "title": title,
        "link": doc_link,
        "type": doc_type
    }

def create_project_docs(client_name: str, project_name: str, doc_types: list = None) -> list:
    """Create all standard docs for a project."""
    drive_service = get_drive_service()
    docs_service = get_docs_service()
    config = load_config()
    
    # Ensure project folder exists
    project_config = create_project_folder(drive_service, client_name, project_name)
    folder_id = project_config["id"]
    
    if doc_types is None:
        doc_types = ["project_brief", "requirements"]
    
    variables = {
        "client_name": client_name,
        "project_name": project_name
    }
    
    created_docs = []
    
    for doc_type in doc_types:
        print(f"Creating {doc_type} doc...")
        doc = create_google_doc(docs_service, drive_service, doc_type, folder_id, variables)
        if "error" not in doc:
            created_docs.append(doc)
            print(f"  ✓ {doc['title']}: {doc['link']}")
        else:
            print(f"  ✗ {doc['error']}")
    
    return created_docs

def list_structure() -> dict:
    """List the current folder structure."""
    config = load_config()
    return config

def main():
    parser = argparse.ArgumentParser(description="Google Drive Integration")
    parser.add_argument("--setup", action="store_true", help="Initial setup")
    parser.add_argument("--create-client", help="Create client folder")
    parser.add_argument("--create-project", nargs=2, metavar=("CLIENT", "PROJECT"),
                        help="Create project folder")
    parser.add_argument("--create-doc", help="Document type to create")
    parser.add_argument("--client", help="Client name")
    parser.add_argument("--project", help="Project name")
    parser.add_argument("--title", help="Document title (for SOPs, meetings)")
    parser.add_argument("--list", action="store_true", help="List structure")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    if args.setup:
        service = get_drive_service()
        config = setup_folder_structure(service)
        if args.json:
            print(json.dumps(config, indent=2))
    
    elif args.create_client:
        service = get_drive_service()
        result = create_client_folder(service, args.create_client)
        if args.json and result:
            print(json.dumps(result, indent=2))
    
    elif args.create_project:
        service = get_drive_service()
        client, project = args.create_project
        result = create_project_folder(service, client, project)
        if args.json and result:
            print(json.dumps(result, indent=2))
    
    elif args.create_doc:
        if not args.client:
            print("--client required for doc creation")
            return
        
        drive_service = get_drive_service()
        docs_service = get_docs_service()
        config = load_config()
        
        # Determine folder
        if args.project:
            # Project doc
            project_config = create_project_folder(drive_service, args.client, args.project)
            folder_id = project_config["id"]
        else:
            # Client-level doc (SOP, meeting notes)
            if args.client not in config.get("clients", {}):
                create_client_folder(drive_service, args.client)
                config = load_config()
            
            if args.create_doc in ["sop"]:
                folder_id = config["clients"][args.client]["subfolders"]["sops"]["id"]
            elif args.create_doc in ["meeting_notes"]:
                folder_id = config["clients"][args.client]["subfolders"]["meeting_notes"]["id"]
            else:
                folder_id = config["clients"][args.client]["id"]
        
        variables = {
            "client_name": args.client,
            "project_name": args.project or "",
            "title": args.title or args.create_doc.replace("_", " ").title()
        }
        
        doc = create_google_doc(docs_service, drive_service, args.create_doc, folder_id, variables)
        
        if args.json:
            print(json.dumps(doc, indent=2))
        else:
            if "error" in doc:
                print(f"❌ {doc['error']}")
            else:
                print(f"✅ Created: {doc['title']}")
                print(f"   Link: {doc['link']}")
    
    elif args.list:
        config = list_structure()
        if args.json:
            print(json.dumps(config, indent=2))
        else:
            print("\n📁 ClickUp PM Folder Structure\n")
            if config.get("root_folder_link"):
                print(f"Root: {config['root_folder_link']}")
            print(f"\nClients: {len(config.get('clients', {}))}")
            for client_name in config.get("clients", {}).keys():
                print(f"  - {client_name}")
    
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python google_drive_integration.py --setup")
        print('  python google_drive_integration.py --create-client "Acme Corp"')
        print('  python google_drive_integration.py --create-project "Acme Corp" "Website Redesign"')
        print('  python google_drive_integration.py --create-doc project_brief --client "Acme" --project "Website"')
        print('  python google_drive_integration.py --create-doc sop --client "Acme" --title "Email Setup"')

if __name__ == "__main__":
    main()
