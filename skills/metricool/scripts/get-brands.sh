#!/bin/bash
# Get All Metricool Brands
#
# Lists all brands/profiles for the authenticated user
#
# Usage: ./get-brands.sh

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/metricool-request.sh" 2>/dev/null || true

# Check environment
if [ -z "${METRICOOL_USER_TOKEN:-}" ] || [ -z "${METRICOOL_USER_ID:-}" ] || [ -z "${METRICOOL_BLOG_ID:-}" ]; then
  echo "Error: Set METRICOOL_USER_TOKEN, METRICOOL_USER_ID, and METRICOOL_BLOG_ID"
  exit 1
fi

# Get brands
echo "Fetching brands..." >&2

curl -s -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/simpleProfiles?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID" | \
  jq '.'
