#!/bin/bash
# http.sh - HTTP helpers for Instantly.ai API with rate limiting and retry

# Rate limiting
RATE_LIMIT_DELAY=0.5  # 500ms between requests
LAST_REQUEST_TIME=0

# Retry configuration
MAX_RETRIES=3
RETRY_DELAY=2  # Initial retry delay in seconds

# Rate limit: ensure minimum delay between requests
rate_limit() {
  local current_time=$(date +%s.%N)
  local elapsed=$(echo "$current_time - $LAST_REQUEST_TIME" | bc)
  local sleep_time=$(echo "$RATE_LIMIT_DELAY - $elapsed" | bc)
  
  if (( $(echo "$sleep_time > 0" | bc -l) )); then
    sleep "$sleep_time"
  fi
  
  LAST_REQUEST_TIME=$(date +%s.%N)
}

# Make API request with retry logic
# Usage: api_request METHOD ENDPOINT [DATA]
api_request() {
  check_api_key
  
  local method="$1"
  local endpoint="$2"
  local data="${3:-}"
  
  # Remove leading slash if present
  endpoint="${endpoint#/}"
  
  local url="${INSTANTLY_BASE_URL}/${endpoint}"
  
  local attempt=0
  while [[ $attempt -lt $MAX_RETRIES ]]; do
    # Rate limiting
    rate_limit
    
    local curl_args=(
      -s
      -w "\n%{http_code}"
      -X "$method"
      -H "Authorization: Bearer ${INSTANTLY_API_KEY}"
    )
    
    # Add Content-Type header for non-DELETE requests
    if [[ "$method" != "DELETE" ]]; then
      curl_args+=(-H "Content-Type: application/json")
    fi
    
    # Add data for POST/PUT/PATCH requests
    if [[ -n "$data" ]]; then
      curl_args+=(-d "$data")
    fi
    
    # Make request
    local response=$(curl "${curl_args[@]}" "$url")
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    # Check HTTP status
    if [[ "$http_code" == "200" || "$http_code" == "201" || "$http_code" == "204" ]]; then
      # Success
      if [[ -n "$body" ]]; then
        echo "$body"
      else
        echo '{"success": true}'
      fi
      return 0
    elif [[ "$http_code" == "429" ]]; then
      # Rate limited - exponential backoff
      local wait_time=$((RETRY_DELAY * (2 ** attempt)))
      >&2 echo "Rate limited (429). Retrying in ${wait_time}s... (attempt $((attempt + 1))/$MAX_RETRIES)"
      sleep "$wait_time"
      ((attempt++))
    elif [[ "$http_code" == "401" ]]; then
      # Authentication error - no retry
      >&2 echo "Authentication failed (401). Check your API key."
      echo "$body"
      return 1
    elif [[ "$http_code" =~ ^5[0-9][0-9]$ ]]; then
      # Server error - retry with backoff
      local wait_time=$((RETRY_DELAY * (2 ** attempt)))
      >&2 echo "Server error ($http_code). Retrying in ${wait_time}s... (attempt $((attempt + 1))/$MAX_RETRIES)"
      sleep "$wait_time"
      ((attempt++))
    else
      # Other error - return immediately
      >&2 echo "Request failed with status $http_code"
      echo "$body"
      return 1
    fi
  done
  
  >&2 echo "Max retries ($MAX_RETRIES) exceeded"
  echo '{"error": "Max retries exceeded"}'
  return 1
}

# Raw API call handler (for the 'api' command)
# Usage: instantly api GET /campaign/list
# Usage: instantly api POST /lead/add '{"email":"test@example.com"}'
handle_raw_api() {
  if [[ $# -lt 2 ]]; then
    cat << EOF
Usage: instantly api <METHOD> <ENDPOINT> [JSON_DATA]

Examples:
  instantly api GET campaigns?limit=10
  instantly api POST leads '{"email":"test@example.com","campaign_id":"abc123"}'
  instantly api PATCH campaigns/abc123 '{"name":"Updated Name"}'
  instantly api DELETE campaigns/abc123

Methods: GET, POST, PUT, PATCH, DELETE
EOF
    exit 1
  fi
  
  local method="$1"
  local endpoint="$2"
  local data="${3:-}"
  
  api_request "$method" "$endpoint" "$data" | jq '.'
}

# Pretty print JSON response
pretty_json() {
  jq '.' 2>/dev/null || cat
}

# Inspect endpoint schema (returns example payload from docs)
inspect_endpoint() {
  local endpoint="$1"
  echo "Fetching schema for: $endpoint"
  echo "Documentation: https://developer.instantly.ai/api/v2"
  echo ""
  echo "Tip: Use 'instantly api GET <endpoint>' to test the endpoint"
  echo "     Check the API docs for required fields and payload structure"
}
