#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# retell-api.sh — Core Retell AI API wrapper
#
# Usage: source this file and call functions directly.
#   source retell-api.sh
#   retell_create_agent '{"response_engine": {...}, "voice_id": "..."}'
#   retell_create_agent --api-key "$CLIENT_KEY" '{"response_engine": {...}}'
#
# All functions:
#   retell_create_agent, retell_update_agent, retell_delete_agent,
#   retell_list_agents, retell_get_agent, retell_create_llm,
#   retell_update_llm, retell_delete_llm, retell_list_llms,
#   retell_get_llm, retell_list_voices, retell_create_phone_call,
#   retell_create_web_call, retell_get_call, retell_list_calls
# =============================================================================

RETELL_BASE_URL="https://api.retellai.com"

# ---------------------------------------------------------------------------
# Internal: resolve API key from --api-key flag or environment
# ---------------------------------------------------------------------------
_retell_resolve_key() {
  local api_key=""
  local args=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --api-key)
        api_key="$2"
        shift 2
        ;;
      *)
        args+=("$1")
        shift
        ;;
    esac
  done

  if [[ -z "$api_key" ]]; then
    api_key="${RETELL_API_KEY:-}"
  fi

  if [[ -z "$api_key" ]]; then
    echo "ERROR: No API key provided. Set RETELL_API_KEY or use --api-key flag." >&2
    return 1
  fi

  # Return key and remaining args separated by newline
  echo "$api_key"
  printf '%s\n' "${args[@]}"
}

# ---------------------------------------------------------------------------
# Internal: make an API request with retry logic
# ---------------------------------------------------------------------------
_retell_request() {
  local method="$1"
  local endpoint="$2"
  local api_key="$3"
  local body="${4:-}"

  local url="${RETELL_BASE_URL}${endpoint}"
  local max_attempts=3
  local attempt=1
  local delay=2

  while [[ $attempt -le $max_attempts ]]; do
    local curl_args=(
      -s
      -w "\n%{http_code}"
      -X "$method"
      -H "Authorization: Bearer $api_key"
      -H "Content-Type: application/json"
    )

    if [[ -n "$body" ]]; then
      curl_args+=(-d "$body")
    fi

    curl_args+=("$url")

    local response
    response=$(curl "${curl_args[@]}" 2>/dev/null) || {
      echo "ERROR: curl failed (attempt $attempt/$max_attempts)" >&2
      if [[ $attempt -lt $max_attempts ]]; then
        sleep $delay
        attempt=$((attempt + 1))
        delay=$((delay * 2))
        continue
      fi
      return 1
    }

    local http_code
    http_code=$(echo "$response" | tail -1)
    local response_body
    response_body=$(echo "$response" | head -n -1)

    # Success
    if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
      echo "$response_body"
      return 0
    fi

    # Client errors: do not retry
    if [[ "$http_code" -ge 400 && "$http_code" -lt 500 ]]; then
      echo "ERROR: HTTP $http_code — $response_body" >&2
      echo "$response_body"
      return 1
    fi

    # Server errors: retry
    if [[ "$http_code" -ge 500 ]]; then
      echo "WARNING: HTTP $http_code (attempt $attempt/$max_attempts)" >&2
      if [[ $attempt -lt $max_attempts ]]; then
        sleep $delay
        attempt=$((attempt + 1))
        delay=$((delay * 2))
        continue
      fi
      echo "ERROR: All $max_attempts attempts failed with HTTP $http_code" >&2
      echo "$response_body"
      return 1
    fi
  done
}

# ===========================================================================
# Agent Operations
# ===========================================================================

retell_create_agent() {
  local resolved
  resolved=$(_retell_resolve_key "$@") || return 1
  local api_key
  api_key=$(echo "$resolved" | head -1)
  local body
  body=$(echo "$resolved" | tail -n +2 | head -1)

  if [[ -z "$body" ]]; then
    echo "ERROR: Request body required. Provide JSON with response_engine and voice_id." >&2
    return 1
  fi

  # Validate required fields
  if ! echo "$body" | jq -e '.response_engine' > /dev/null 2>&1; then
    echo "ERROR: response_engine is required in request body." >&2
    return 1
  fi
  if ! echo "$body" | jq -e '.voice_id' > /dev/null 2>&1; then
    echo "ERROR: voice_id is required in request body." >&2
    return 1
  fi

  _retell_request "POST" "/create-agent" "$api_key" "$body"
}

retell_get_agent() {
  local resolved
  resolved=$(_retell_resolve_key "$@") || return 1
  local api_key
  api_key=$(echo "$resolved" | head -1)
  local agent_id
  agent_id=$(echo "$resolved" | tail -n +2 | head -1)

  if [[ -z "$agent_id" ]]; then
    echo "ERROR: agent_id required." >&2
    return 1
  fi

  _retell_request "GET" "/get-agent/$agent_id" "$api_key"
}

retell_update_agent() {
  local resolved
  resolved=$(_retell_resolve_key "$@") || return 1
  local api_key
  api_key=$(echo "$resolved" | head -1)
  local remaining
  remaining=$(echo "$resolved" | tail -n +2)
  local agent_id
  agent_id=$(echo "$remaining" | head -1)
  local body
  body=$(echo "$remaining" | tail -n +2 | head -1)

  if [[ -z "$agent_id" ]]; then
    echo "ERROR: agent_id required as first argument." >&2
    return 1
  fi
  if [[ -z "$body" ]]; then
    echo "ERROR: Update body required as second argument." >&2
    return 1
  fi

  _retell_request "PATCH" "/update-agent/$agent_id" "$api_key" "$body"
}

retell_delete_agent() {
  local resolved
  resolved=$(_retell_resolve_key "$@") || return 1
  local api_key
  api_key=$(echo "$resolved" | head -1)
  local agent_id
  agent_id=$(echo "$resolved" | tail -n +2 | head -1)

  if [[ -z "$agent_id" ]]; then
    echo "ERROR: agent_id required." >&2
    return 1
  fi

  _retell_request "DELETE" "/delete-agent/$agent_id" "$api_key"
}

retell_list_agents() {
  local resolved
  resolved=$(_retell_resolve_key "$@") || return 1
  local api_key
  api_key=$(echo "$resolved" | head -1)

  _retell_request "GET" "/list-agents" "$api_key"
}

# ===========================================================================
# LLM Operations
# ===========================================================================

retell_create_llm() {
  local resolved
  resolved=$(_retell_resolve_key "$@") || return 1
  local api_key
  api_key=$(echo "$resolved" | head -1)
  local body
  body=$(echo "$resolved" | tail -n +2 | head -1)

  if [[ -z "$body" ]]; then
    echo "ERROR: Request body required." >&2
    return 1
  fi

  if ! echo "$body" | jq -e '.start_speaker' > /dev/null 2>&1; then
    echo "ERROR: start_speaker is required in request body." >&2
    return 1
  fi

  _retell_request "POST" "/create-retell-llm" "$api_key" "$body"
}

retell_get_llm() {
  local resolved
  resolved=$(_retell_resolve_key "$@") || return 1
  local api_key
  api_key=$(echo "$resolved" | head -1)
  local llm_id
  llm_id=$(echo "$resolved" | tail -n +2 | head -1)

  if [[ -z "$llm_id" ]]; then
    echo "ERROR: llm_id required." >&2
    return 1
  fi

  _retell_request "GET" "/get-retell-llm/$llm_id" "$api_key"
}

retell_update_llm() {
  local resolved
  resolved=$(_retell_resolve_key "$@") || return 1
  local api_key
  api_key=$(echo "$resolved" | head -1)
  local remaining
  remaining=$(echo "$resolved" | tail -n +2)
  local llm_id
  llm_id=$(echo "$remaining" | head -1)
  local body
  body=$(echo "$remaining" | tail -n +2 | head -1)

  if [[ -z "$llm_id" ]]; then
    echo "ERROR: llm_id required as first argument." >&2
    return 1
  fi
  if [[ -z "$body" ]]; then
    echo "ERROR: Update body required as second argument." >&2
    return 1
  fi

  _retell_request "PATCH" "/update-retell-llm/$llm_id" "$api_key" "$body"
}

retell_delete_llm() {
  local resolved
  resolved=$(_retell_resolve_key "$@") || return 1
  local api_key
  api_key=$(echo "$resolved" | head -1)
  local llm_id
  llm_id=$(echo "$resolved" | tail -n +2 | head -1)

  if [[ -z "$llm_id" ]]; then
    echo "ERROR: llm_id required." >&2
    return 1
  fi

  _retell_request "DELETE" "/delete-retell-llm/$llm_id" "$api_key"
}

retell_list_llms() {
  local resolved
  resolved=$(_retell_resolve_key "$@") || return 1
  local api_key
  api_key=$(echo "$resolved" | head -1)

  _retell_request "GET" "/list-retell-llms" "$api_key"
}

# ===========================================================================
# Voice Operations
# ===========================================================================

retell_list_voices() {
  local resolved
  resolved=$(_retell_resolve_key "$@") || return 1
  local api_key
  api_key=$(echo "$resolved" | head -1)

  _retell_request "GET" "/list-voices" "$api_key"
}

# ===========================================================================
# Call Operations
# ===========================================================================

retell_create_phone_call() {
  local resolved
  resolved=$(_retell_resolve_key "$@") || return 1
  local api_key
  api_key=$(echo "$resolved" | head -1)
  local body
  body=$(echo "$resolved" | tail -n +2 | head -1)

  if [[ -z "$body" ]]; then
    echo "ERROR: Request body required with from_number, to_number, agent_id." >&2
    return 1
  fi

  for field in from_number to_number agent_id; do
    if ! echo "$body" | jq -e ".$field" > /dev/null 2>&1; then
      echo "ERROR: $field is required in request body." >&2
      return 1
    fi
  done

  _retell_request "POST" "/v2/create-phone-call" "$api_key" "$body"
}

retell_create_web_call() {
  local resolved
  resolved=$(_retell_resolve_key "$@") || return 1
  local api_key
  api_key=$(echo "$resolved" | head -1)
  local body
  body=$(echo "$resolved" | tail -n +2 | head -1)

  if [[ -z "$body" ]]; then
    echo "ERROR: Request body required with agent_id." >&2
    return 1
  fi

  if ! echo "$body" | jq -e '.agent_id' > /dev/null 2>&1; then
    echo "ERROR: agent_id is required in request body." >&2
    return 1
  fi

  _retell_request "POST" "/v2/create-web-call" "$api_key" "$body"
}

retell_get_call() {
  local resolved
  resolved=$(_retell_resolve_key "$@") || return 1
  local api_key
  api_key=$(echo "$resolved" | head -1)
  local call_id
  call_id=$(echo "$resolved" | tail -n +2 | head -1)

  if [[ -z "$call_id" ]]; then
    echo "ERROR: call_id required." >&2
    return 1
  fi

  _retell_request "GET" "/v2/get-call/$call_id" "$api_key"
}

retell_list_calls() {
  local resolved
  resolved=$(_retell_resolve_key "$@") || return 1
  local api_key
  api_key=$(echo "$resolved" | head -1)
  local query_string
  query_string=$(echo "$resolved" | tail -n +2 | head -1)

  local endpoint="/v2/list-calls"
  if [[ -n "${query_string:-}" ]]; then
    endpoint="/v2/list-calls?$query_string"
  fi

  _retell_request "GET" "$endpoint" "$api_key"
}
