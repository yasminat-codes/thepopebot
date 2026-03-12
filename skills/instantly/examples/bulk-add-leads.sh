#!/bin/bash
# Example: Bulk add leads from a CSV file to an Instantly campaign

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTANTLY_CLI="$SCRIPT_DIR/../instantly"

# Usage check
if [[ $# -lt 2 ]]; then
  cat << EOF
Usage: $0 <csv_file> <campaign_id>

CSV format (no header):
email,first_name,last_name,company

Example:
  $0 leads.csv abc123xyz
EOF
  exit 1
fi

CSV_FILE="$1"
CAMPAIGN_ID="$2"

if [[ ! -f "$CSV_FILE" ]]; then
  echo "Error: File not found: $CSV_FILE"
  exit 1
fi

echo "Adding leads from $CSV_FILE to campaign $CAMPAIGN_ID..."
echo

added=0
failed=0

while IFS=, read -r email first_name last_name company; do
  # Skip empty lines
  [[ -z "$email" ]] && continue
  
  echo "Adding: $email ($first_name $last_name)"
  
  if "$INSTANTLY_CLI" leads add \
    --email "$email" \
    --first-name "$first_name" \
    --last-name "$last_name" \
    --company "$company" \
    --campaign-id "$CAMPAIGN_ID" > /dev/null 2>&1; then
    ((added++))
    echo "  ✓ Success"
  else
    ((failed++))
    echo "  ✗ Failed"
  fi
  
  # Rate limiting: wait 100ms between requests
  sleep 0.1
done < "$CSV_FILE"

echo
echo "Summary:"
echo "  Added: $added"
echo "  Failed: $failed"
echo "  Total: $((added + failed))"
