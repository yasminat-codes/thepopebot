#!/bin/bash
# config.sh - Instantly.ai configuration

# API Configuration
INSTANTLY_API_KEY="${INSTANTLY_API_KEY:-}"
INSTANTLY_BASE_URL="https://api.instantly.ai/api/v2"

# Check if API key is set
check_api_key() {
  if [[ -z "$INSTANTLY_API_KEY" ]]; then
    echo "Error: INSTANTLY_API_KEY environment variable not set"
    echo "Set it with: export INSTANTLY_API_KEY='your_api_key'"
    echo ""
    echo "Get your API key from: https://app.instantly.ai/app/settings/integrations"
    echo "The key should be the base64-encoded string from the dashboard."
    exit 1
  fi
}
