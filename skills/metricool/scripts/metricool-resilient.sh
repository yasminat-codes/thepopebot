#!/bin/bash
# Metricool API Resilient Wrapper
#
# Production-grade API wrapper with:
# - Automatic retries with exponential backoff
# - Rate limit handling
# - Circuit breaker pattern
# - Response caching
# - Comprehensive error handling
#
# Usage:
#   ./metricool-resilient.sh <method> <endpoint> [params]
#   ./metricool-resilient.sh get "stats/instagram/posts" "start=1704067200&end=1706745600"
#   ./metricool-resilient.sh post "stats/report/savetemplate" '{"name":"Report"}'

set -euo pipefail

# Configuration
readonly BASE_URL="https://app.metricool.com/api"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly CACHE_DIR="${METRICOOL_CACHE_DIR:-$SCRIPT_DIR/.cache}"
readonly CIRCUIT_FILE="$SCRIPT_DIR/.circuit_state"
readonly STATS_FILE="$SCRIPT_DIR/.stats"

# Retry configuration
readonly MAX_RETRIES="${METRICOOL_MAX_RETRIES:-5}"
readonly BASE_DELAY="${METRICOOL_BASE_DELAY:-1}"
readonly MAX_DELAY="${METRICOOL_MAX_DELAY:-60}"
readonly CIRCUIT_THRESHOLD="${METRICOOL_CIRCUIT_THRESHOLD:-5}"
readonly CIRCUIT_TIMEOUT="${METRICOOL_CIRCUIT_TIMEOUT:-60}"

# Cache TTLs (seconds)
declare -A CACHE_TTL=(
    ["stats/instagram/posts"]=300
    ["stats/facebook/posts"]=300
    ["stats/tiktok/videos"]=300
    ["stats/youtube/videos"]=300
    ["stats/rt/values"]=30
    ["stats/rt/pvperhour"]=60
    ["admin/simpleProfiles"]=60
    ["admin/max-profiles"]=300
    ["stats/gender/"]=3600
    ["stats/age/"]=3600
    ["stats/country/"]=3600
    ["actions/"]=3600
)

# ============================================
# UTILITY FUNCTIONS
# ============================================

log() {
    local level="$1"
    shift
    local timestamp=$(date -Iseconds)
    echo "[$timestamp] [$level] $*" >&2
}

info() { log "INFO" "$@"; }
warn() { log "WARN" "$@"; }
error() { log "ERROR" "$@"; }
debug() { [[ "${METRICOOL_DEBUG:-0}" == "1" ]] && log "DEBUG" "$@" || true; }

check_env() {
    local missing=()
    [ -z "${METRICOOL_USER_TOKEN:-}" ] && missing+=("METRICOOL_USER_TOKEN")
    [ -z "${METRICOOL_USER_ID:-}" ] && missing+=("METRICOOL_USER_ID")
    [ -z "${METRICOOL_BLOG_ID:-}" ] && missing+=("METRICOOL_BLOG_ID")

    if [ ${#missing[@]} -gt 0 ]; then
        error "Missing environment variables: ${missing[*]}"
        error ""
        error "Set them with:"
        error "  export METRICOOL_USER_TOKEN=your-token"
        error "  export METRICOOL_USER_ID=your-user-id"
        error "  export METRICOOL_BLOG_ID=your-brand-id"
        exit 1
    fi
}

# ============================================
# CIRCUIT BREAKER
# ============================================

get_circuit_state() {
    if [ -f "$CIRCUIT_FILE" ]; then
        source "$CIRCUIT_FILE" 2>/dev/null || true
        echo "${CIRCUIT_STATE:-CLOSED}:${CIRCUIT_FAILURES:-0}:${CIRCUIT_LAST_FAILURE:-0}"
    else
        echo "CLOSED:0:0"
    fi
}

set_circuit_state() {
    local state="$1"
    local failures="${2:-0}"
    local last_failure="${3:-$(date +%s)}"
    echo "CIRCUIT_STATE=$state" > "$CIRCUIT_FILE"
    echo "CIRCUIT_FAILURES=$failures" >> "$CIRCUIT_FILE"
    echo "CIRCUIT_LAST_FAILURE=$last_failure" >> "$CIRCUIT_FILE"
}

record_success() {
    set_circuit_state "CLOSED" 0 0
    debug "Circuit breaker: CLOSED"
}

record_failure() {
    local current
    current=$(get_circuit_state)
    local failures=$((current#*:*:} + 1))
    local last_failure=$(date +%s)

    if [ $failures -ge $CIRCUIT_THRESHOLD ]; then
        set_circuit_state "OPEN" $failures $last_failure
        warn "Circuit breaker: OPEN (failures: $failures)"
    else
        set_circuit_state "CLOSED" $failures $last_failure
        debug "Circuit breaker: CLOSED (failures: $failures)"
    fi
}

can_execute() {
    local current
    current=$(get_circuit_state)
    local state="${current%%:*}"
    local last_failure="${current##*:}"

    if [ "$state" == "CLOSED" ]; then
        return 0
    fi

    if [ "$state" == "OPEN" ]; then
        local now=$(date +%s)
        local elapsed=$((now - last_failure))

        if [ $elapsed -ge $CIRCUIT_TIMEOUT ]; then
            # Transition to HALF_OPEN
            set_circuit_state "HALF_OPEN" "${current#*:}"
            info "Circuit breaker: HALF_OPEN (testing)"
            return 0
        fi

        error "Circuit breaker OPEN - rejecting request (${elapsed}s/${CIRCUIT_TIMEOUT}s)"
        return 1
    fi

    # HALF_OPEN - allow one request
    return 0
}

# ============================================
# CACHE MANAGEMENT
# ============================================

get_cache_key() {
    local method="$1"
    local endpoint="$2"
    local params="$3"
    echo -n "${method}:${endpoint}:${params}" | md5sum | cut -d' ' -f1
}

get_cache_ttl() {
    local endpoint="$1"
    for pattern in "${!CACHE_TTL[@]}"; do
        if [[ "$endpoint" == *"$pattern"* ]]; then
            echo "${CACHE_TTL[$pattern]}"
            return
        fi
    done
    echo "300"  # Default 5 minutes
}

get_cached() {
    local key="$1"
    local cache_file="$CACHE_DIR/${key}.json"

    if [ -f "$cache_file" ]; then
        local cache_time=$(stat -c %Y "$cache_file" 2>/dev/null || stat -f %m "$cache_file")
        local now=$(date +%s)
        local ttl="$2"
        local age=$((now - cache_time))

        if [ $age -lt $ttl ]; then
            cat "$cache_file"
            return 0
        fi
    fi
    return 1
}

set_cache() {
    local key="$1"
    local data="$2"
    mkdir -p "$CACHE_DIR"
    echo "$data" > "$CACHE_DIR/${key}.json"
}

# ============================================
# STATISTICS
# ============================================

increment_stat() {
    local stat="$1"
    mkdir -p "$(dirname "$STATS_FILE")"
    touch "$STATS_FILE"

    local current=$(grep "^$stat=" "$STATS_FILE" 2>/dev/null | cut -d= -f2 || echo "0")
    echo "$stat=$((current + 1))" >> "$STATS_FILE.tmp"
    grep -v "^$stat=" "$STATS_FILE" 2>/dev/null >> "$STATS_FILE.tmp" || true
    mv "$STATS_FILE.tmp" "$STATS_FILE"
}

show_stats() {
    if [ -f "$STATS_FILE" ]; then
        info "=== Client Statistics ==="
        cat "$STATS_FILE" >&2
    fi
}

# ============================================
# RETRY LOGIC
# ============================================

calculate_delay() {
    local attempt="$1"
    local delay=$((BASE_DELAY * (2 ** attempt)))

    # Cap at MAX_DELAY
    if [ $delay -gt $MAX_DELAY ]; then
        delay=$MAX_DELAY
    fi

    # Add jitter (±25%)
    local jitter=$((delay / 4))
    local sign=$((RANDOM % 2))
    if [ $sign -eq 0 ]; then
        delay=$((delay + (RANDOM % jitter)))
    else
        delay=$((delay - (RANDOM % jitter)))
    fi

    echo $delay
}

should_retry() {
    local status_code="$1"
    case "$status_code" in
        408|429|500|502|503|504) return 0 ;;
        *) return 1 ;;
    esac
}

# ============================================
# API REQUEST
# ============================================

api_request() {
    local method="${1:-GET}"
    local endpoint="$2"
    local params="${3:-}"
    local data="${4:-}"

    # Build URL
    local url="${BASE_URL}/${endpoint}?blogId=${METRICOOL_BLOG_ID}&userId=${METRICOOL_USER_ID}"
    [ -n "$params" ] && url="${url}&${params}"

    # Check circuit breaker
    if ! can_execute; then
        error "Circuit breaker is OPEN - request rejected"
        return 1
    fi

    # Check cache for GET requests
    if [ "$method" == "GET" ] && [ "${METRICOOL_NO_CACHE:-0}" != "1" ]; then
        local cache_key
        cache_key=$(get_cache_key "$method" "$endpoint" "$params")
        local ttl
        ttl=$(get_cache_ttl "$endpoint")

        local cached
        if cached=$(get_cached "$cache_key" "$ttl"); then
            debug "Cache HIT for $endpoint"
            increment_stat "cache_hits"
            echo "$cached"
            return 0
        fi
        increment_stat "cache_misses"
    fi

    # Execute with retries
    local attempt=0
    local delay

    while [ $attempt -lt $MAX_RETRIES ]; do
        increment_stat "requests"

        debug "Request: $method $endpoint (attempt $((attempt + 1)))"

        # Build curl command
        local curl_args=(-s -w "\n%{http_code}" -H "X-Mc-Auth: $METRICOOL_USER_TOKEN")

        if [ "$method" != "GET" ]; then
            curl_args+=(-X "$method")
            [ -n "$data" ] && curl_args+=(-H "Content-Type: application/json" -d "$data")
        fi

        curl_args+=("$url")

        # Make request
        local response
        local http_code
        local body

        response=$(curl "${curl_args[@]}" 2>&1) || {
            error "curl failed: $response"
            record_failure
            return 1
        }

        http_code=$(echo "$response" | tail -n 1)
        body=$(echo "$response" | sed '$d')

        case "$http_code" in
            200)
                record_success
                # Cache GET requests
                if [ "$method" == "GET" ] && [ "${METRICOOL_NO_CACHE:-0}" != "1" ]; then
                    set_cache "$cache_key" "$body"
                fi
                echo "$body"
                return 0
                ;;

            429)
                increment_stat "retries"
                # Try to get retry-after from response
                local retry_after=$(echo "$body" | jq -r '.retryAfter // 60' 2>/dev/null || echo "60")
                warn "Rate limited, waiting ${retry_after}s (attempt $((attempt + 1)))"

                if [ $attempt -lt $((MAX_RETRIES - 1)) ]; then
                    sleep "$retry_after"
                    attempt=$((attempt + 1))
                    continue
                fi
                ;;

            401)
                record_failure
                increment_stat "errors"
                error "Authentication failed - check METRICOOL_USER_TOKEN"
                return 1
                ;;

            403)
                record_failure
                increment_stat "errors"
                error "Forbidden - API access requires Advanced or Custom plan"
                return 1
                ;;

            404)
                record_failure
                increment_stat "errors"
                error "Not found - check endpoint, userId, and blogId"
                return 1
                ;;

            500|502|503|504)
                increment_stat "retries"
                delay=$(calculate_delay $attempt)
                warn "Server error ($http_code), retrying in ${delay}s (attempt $((attempt + 1)))"

                if [ $attempt -lt $((MAX_RETRIES - 1)) ]; then
                    sleep "$delay"
                    attempt=$((attempt + 1))
                    continue
                fi
                ;;

            *)
                record_failure
                increment_stat "errors"
                error "HTTP $http_code: $body"
                return 1
                ;;
        esac

        attempt=$((attempt + 1))
    done

    # Max retries exceeded
    record_failure
    increment_stat "errors"
    error "Max retries ($MAX_RETRIES) exceeded"
    return 1
}

# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

ping() {
    local result
    if result=$(api_request GET "mtr/ping" "" 2>/dev/null); then
        info "API Status: OK"
        return 0
    else
        error "API Status: FAILED"
        return 1
    fi
}

get_brands() {
    api_request GET "admin/simpleProfiles"
}

get_analytics() {
    local platform="$1"
    local start="$2"
    local end="$3"

    local endpoint
    case "$platform" in
        instagram) endpoint="stats/instagram/posts" ;;
        instagram-reels) endpoint="stats/instagram/reels" ;;
        instagram-stories) endpoint="stats/instagram/stories" ;;
        facebook) endpoint="stats/facebook/posts" ;;
        tiktok) endpoint="stats/tiktok/videos" ;;
        youtube) endpoint="stats/youtube/videos" ;;
        linkedin) endpoint="stats/linkedin/posts" ;;
        twitter|x) endpoint="stats/twitter/posts" ;;
        *)
            error "Unknown platform: $platform"
            return 1
            ;;
    esac

    api_request GET "$endpoint" "start=$start&end=$end"
}

# ============================================
# MAIN
# ============================================

show_help() {
    cat << 'EOF'
Metricool API Resilient Wrapper

Usage:
  ./metricool-resilient.sh <command> [args...]

Commands:
  get <endpoint> [params]     Make GET request
  post <endpoint> [data]      Make POST request
  ping                        Test API connectivity
  brands                      List all brands
  analytics <platform> <start> <end>  Get platform analytics
  stats                       Show client statistics
  clear-cache                 Clear response cache
  reset-circuit               Reset circuit breaker

Environment:
  METRICOOL_USER_TOKEN    API token (required)
  METRICOOL_USER_ID       User ID (required)
  METRICOOL_BLOG_ID       Brand ID (required)
  METRICOOL_MAX_RETRIES   Max retry attempts (default: 5)
  METRICOOL_NO_CACHE      Set to 1 to disable cache
  METRICOOL_DEBUG         Set to 1 for debug output

Examples:
  # Test connection
  ./metricool-resilient.sh ping

  # List brands
  ./metricool-resilient.sh brands

  # Get Instagram posts
  ./metricool-resilient.sh get "stats/instagram/posts" "start=1704067200&end=1706745600"

  # Get analytics for a platform
  ./metricool-resilient.sh analytics instagram 1704067200 1706745600

  # Show statistics
  ./metricool-resilient.sh stats
EOF
}

main() {
    check_env

    if [ $# -lt 1 ]; then
        show_help
        exit 1
    fi

    local command="$1"
    shift

    case "$command" in
        get)
            api_request GET "$1" "${2:-}"
            ;;
        post)
            api_request POST "$1" "" "${2:-}"
            ;;
        put)
            api_request PUT "$1" "" "${2:-}"
            ;;
        delete)
            api_request DELETE "$1" "${2:-}"
            ;;
        ping)
            ping
            ;;
        brands)
            get_brands
            ;;
        analytics)
            get_analytics "$1" "$2" "$3"
            ;;
        stats)
            show_stats
            ;;
        clear-cache)
            rm -rf "$CACHE_DIR"
            info "Cache cleared"
            ;;
        reset-circuit)
            rm -f "$CIRCUIT_FILE"
            info "Circuit breaker reset"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
