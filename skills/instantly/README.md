# Instantly.ai CLI

Comprehensive command-line interface for the Instantly.ai v2 API.

## Quick Start

```bash
# Set your API key
export INSTANTLY_API_KEY="your_api_key"

# List campaigns
./instantly campaigns list

# Add a lead
./instantly leads add \
  --email test@example.com \
  --campaign-id abc123 \
  --first-name John

# Get analytics
./instantly analytics campaign --id abc123
```

## Features

✅ **Modular Structure** - Organized by endpoint category  
✅ **Full Coverage** - Leads, campaigns, inbox, subsequences, analytics  
✅ **Raw API Access** - Call any endpoint directly with `instantly api`  
✅ **Easy to Extend** - Add new modules without touching core code  
✅ **Type-Safe Params** - Built-in validation and help for each command  

## Documentation

See [SKILL.md](SKILL.md) for complete documentation.

## Structure

- **instantly** - Main CLI entry point
- **lib/** - Modular endpoint handlers
  - config.sh - API configuration
  - http.sh - HTTP helpers + raw API caller
  - leads.sh - Lead management
  - campaigns.sh - Campaign management
  - inbox.sh - Inbox and replies
  - subsequences.sh - Email subsequences
  - analytics.sh - Analytics and reporting

## Philosophy

This skill demonstrates best practices for **API CLIs with many endpoints**:

1. **Organized by category** - Each endpoint group gets its own module
2. **Shared infrastructure** - Common HTTP/auth logic in one place
3. **Escape hatch** - Raw API access for anything not yet modularized
4. **Self-documenting** - Each command has help text
5. **Composable** - Easy to add new categories without refactoring

Perfect for APIs with 20+ endpoints that naturally group into categories.
