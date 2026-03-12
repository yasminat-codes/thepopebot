#!/usr/bin/env bash
# =============================================================================
# validate-env.sh — LinkedIn Studio environment variable validator
# =============================================================================
#
# Checks that all required environment variables are set and optionally
# tests live connections to external services.
#
# Usage:
#   ./scripts/validate-env.sh                  # Check env vars only
#   ./scripts/validate-env.sh --verbose         # Show all vars (including optional)
#   ./scripts/validate-env.sh --test-connections # Check vars + test live connections
#   ./scripts/validate-env.sh --verbose --test-connections  # Full check
#
# Exit codes:
#   0 — All required variables are set (connections may still fail)
#   1 — One or more required variables are missing
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Colors and symbols
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

PASS="${GREEN}✓${RESET}"
FAIL="${RED}✗${RESET}"
WARN="${YELLOW}!${RESET}"
INFO="${CYAN}→${RESET}"

# ---------------------------------------------------------------------------
# Flags
# ---------------------------------------------------------------------------
VERBOSE=false
TEST_CONNECTIONS=false

for arg in "$@"; do
    case "$arg" in
        --verbose)          VERBOSE=true ;;
        --test-connections) TEST_CONNECTIONS=true ;;
        --help|-h)
            echo "Usage: $0 [--verbose] [--test-connections]"
            echo ""
            echo "  --verbose           Show all variables including optional ones"
            echo "  --test-connections  Test live connections to Neon, Metricool, Reddit, SerpAPI"
            echo "  --help, -h          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown flag: $arg (use --help for usage)"
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Counters
# ---------------------------------------------------------------------------
REQUIRED_TOTAL=0
REQUIRED_SET=0
OPTIONAL_TOTAL=0
OPTIONAL_SET=0
CONNECTION_PASS=0
CONNECTION_FAIL=0
CONNECTION_TOTAL=0

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

check_var() {
    local var_name="$1"
    local required="$2"    # "required" | "optional" | "auto"
    local description="$3"

    local value="${!var_name:-}"

    if [[ "$required" == "required" ]]; then
        REQUIRED_TOTAL=$((REQUIRED_TOTAL + 1))
        if [[ -n "$value" ]]; then
            REQUIRED_SET=$((REQUIRED_SET + 1))
            if [[ "$VERBOSE" == true ]]; then
                # Mask the value — show first 4 chars then asterisks
                local masked
                if [[ ${#value} -gt 8 ]]; then
                    masked="${value:0:4}$(printf '*%.0s' $(seq 1 $((${#value} - 4))))"
                else
                    masked="****"
                fi
                echo -e "  ${PASS} ${BOLD}${var_name}${RESET} ${DIM}= ${masked}${RESET}"
            else
                echo -e "  ${PASS} ${var_name}"
            fi
        else
            echo -e "  ${FAIL} ${var_name}  ${RED}— MISSING (${description})${RESET}"
        fi
    elif [[ "$required" == "optional" ]]; then
        OPTIONAL_TOTAL=$((OPTIONAL_TOTAL + 1))
        if [[ -n "$value" ]]; then
            OPTIONAL_SET=$((OPTIONAL_SET + 1))
            if [[ "$VERBOSE" == true ]]; then
                echo -e "  ${PASS} ${var_name} ${DIM}(optional)${RESET}"
            fi
        else
            if [[ "$VERBOSE" == true ]]; then
                echo -e "  ${WARN} ${var_name}  ${YELLOW}— not set (${description})${RESET}"
            fi
        fi
    elif [[ "$required" == "auto" ]]; then
        OPTIONAL_TOTAL=$((OPTIONAL_TOTAL + 1))
        if [[ -n "$value" ]]; then
            OPTIONAL_SET=$((OPTIONAL_SET + 1))
        fi
        if [[ "$VERBOSE" == true ]]; then
            if [[ -n "$value" ]]; then
                echo -e "  ${PASS} ${var_name} ${DIM}(auto — custom value)${RESET}"
            else
                echo -e "  ${INFO} ${var_name} ${DIM}(auto — using default)${RESET}"
            fi
        fi
    fi
}

test_connection() {
    local service="$1"
    local description="$2"
    shift 2

    CONNECTION_TOTAL=$((CONNECTION_TOTAL + 1))
    echo -e "  ${INFO} Testing ${BOLD}${service}${RESET}... ${DIM}${description}${RESET}"

    if "$@"; then
        CONNECTION_PASS=$((CONNECTION_PASS + 1))
        echo -e "  ${PASS} ${service} — connection successful"
    else
        CONNECTION_FAIL=$((CONNECTION_FAIL + 1))
        echo -e "  ${FAIL} ${service} — connection failed"
    fi
}

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
echo ""
echo -e "${BOLD}LinkedIn Studio — Environment Validator${RESET}"
echo -e "${DIM}$(date '+%Y-%m-%d %H:%M:%S')${RESET}"
echo ""

# ---------------------------------------------------------------------------
# Group 1: Neon PostgreSQL
# ---------------------------------------------------------------------------
echo -e "${CYAN}Neon PostgreSQL${RESET}"
check_var "NEON_DATABASE_URL"  "required" "Neon connection string — https://console.neon.tech"
check_var "NEON_POOL_SIZE"     "auto"     "Connection pool size (default: 5)"
echo ""

# ---------------------------------------------------------------------------
# Group 2: Metricool
# ---------------------------------------------------------------------------
echo -e "${CYAN}Metricool${RESET}"
check_var "METRICOOL_API_KEY"  "required" "Metricool API key — Settings > API"
check_var "METRICOOL_USER_ID"  "required" "Metricool numeric user ID"
check_var "METRICOOL_BASE_URL" "auto"     "Metricool API base URL (default: https://app.metricool.com/api/v2)"
echo ""

# ---------------------------------------------------------------------------
# Group 3: Reddit
# ---------------------------------------------------------------------------
echo -e "${CYAN}Reddit (PRAW)${RESET}"
check_var "REDDIT_CLIENT_ID"     "required" "Reddit app client ID — reddit.com/prefs/apps"
check_var "REDDIT_CLIENT_SECRET" "required" "Reddit app client secret"
check_var "REDDIT_USERNAME"      "required" "Reddit account username"
check_var "REDDIT_PASSWORD"      "required" "Reddit account password"
check_var "REDDIT_USER_AGENT"    "auto"     "User agent string (default: linkedin-studio/1.0)"
check_var "PUSHSHIFT_BASE_URL"   "auto"     "Pushshift API URL (default: https://api.pushshift.io/reddit)"
echo ""

# ---------------------------------------------------------------------------
# Group 4: SerpAPI
# ---------------------------------------------------------------------------
echo -e "${CYAN}SerpAPI${RESET}"
check_var "SERPAPI_KEY"      "required" "SerpAPI key — serpapi.com/manage-api-key"
check_var "SERPAPI_BASE_URL" "auto"     "SerpAPI base URL (default: https://serpapi.com/search)"
echo ""

# ---------------------------------------------------------------------------
# Group 5: Canva (optional)
# ---------------------------------------------------------------------------
echo -e "${CYAN}Canva MCP${RESET}"
check_var "CANVA_API_KEY" "optional" "Canva API key for carousel/image design"
echo ""

# ---------------------------------------------------------------------------
# Group 6: OpenAI (optional)
# ---------------------------------------------------------------------------
echo -e "${CYAN}OpenAI${RESET}"
check_var "OPENAI_API_KEY"     "optional" "OpenAI API key for DALL-E 3 + embeddings"
check_var "OPENAI_IMAGE_MODEL" "auto"     "Image model (default: dall-e-3)"
echo ""

# ---------------------------------------------------------------------------
# Group 7: Google Imagen (optional)
# ---------------------------------------------------------------------------
echo -e "${CYAN}Google Imagen${RESET}"
check_var "GOOGLE_IMAGEN_PROJECT_ID"       "optional" "GCP project ID for Vertex AI Imagen"
check_var "GOOGLE_APPLICATION_CREDENTIALS" "optional" "Path to GCP service account JSON"
echo ""

# ---------------------------------------------------------------------------
# Group 8: Playwright (auto)
# ---------------------------------------------------------------------------
echo -e "${CYAN}Playwright${RESET}"
check_var "PLAYWRIGHT_HEADLESS"   "auto" "Run headless (default: true)"
check_var "PLAYWRIGHT_TIMEOUT_MS" "auto" "Page timeout in ms (default: 30000)"
echo ""

# ---------------------------------------------------------------------------
# Connection tests (optional)
# ---------------------------------------------------------------------------
if [[ "$TEST_CONNECTIONS" == true ]]; then
    echo -e "${BOLD}Connection Tests${RESET}"
    echo ""

    # -- Neon --
    if [[ -n "${NEON_DATABASE_URL:-}" ]]; then
        if command -v psql &>/dev/null; then
            test_connection "Neon" "SELECT 1 via psql" \
                psql "${NEON_DATABASE_URL}" -c "SELECT 1" -t -q &>/dev/null
        else
            echo -e "  ${WARN} Neon — ${YELLOW}psql not found, skipping connection test${RESET}"
            echo -e "        ${DIM}Install with: brew install libpq${RESET}"
        fi
    else
        echo -e "  ${FAIL} Neon — skipped (NEON_DATABASE_URL not set)"
    fi

    # -- Metricool --
    if [[ -n "${METRICOOL_API_KEY:-}" && -n "${METRICOOL_USER_ID:-}" ]]; then
        if command -v curl &>/dev/null; then
            METRICOOL_URL="${METRICOOL_BASE_URL:-https://app.metricool.com/api/v2}"
            test_connection "Metricool" "GET /user via API" \
                bash -c "curl -sf -o /dev/null -w '%{http_code}' \
                    -H 'Authorization: Bearer ${METRICOOL_API_KEY}' \
                    '${METRICOOL_URL}/user/${METRICOOL_USER_ID}' | grep -q '200'"
        else
            echo -e "  ${WARN} Metricool — ${YELLOW}curl not found, skipping connection test${RESET}"
        fi
    else
        echo -e "  ${FAIL} Metricool — skipped (API key or user ID not set)"
    fi

    # -- Reddit --
    if [[ -n "${REDDIT_CLIENT_ID:-}" && -n "${REDDIT_CLIENT_SECRET:-}" ]]; then
        if command -v curl &>/dev/null; then
            test_connection "Reddit" "OAuth token request" \
                bash -c "curl -sf -o /dev/null -w '%{http_code}' \
                    -X POST -d 'grant_type=client_credentials' \
                    -u '${REDDIT_CLIENT_ID}:${REDDIT_CLIENT_SECRET}' \
                    -A '${REDDIT_USER_AGENT:-linkedin-studio/1.0}' \
                    'https://www.reddit.com/api/v1/access_token' | grep -q '200'"
        else
            echo -e "  ${WARN} Reddit — ${YELLOW}curl not found, skipping connection test${RESET}"
        fi
    else
        echo -e "  ${FAIL} Reddit — skipped (client ID or secret not set)"
    fi

    # -- SerpAPI --
    if [[ -n "${SERPAPI_KEY:-}" ]]; then
        if command -v curl &>/dev/null; then
            SERP_URL="${SERPAPI_BASE_URL:-https://serpapi.com/search}"
            test_connection "SerpAPI" "Account info request" \
                bash -c "curl -sf -o /dev/null -w '%{http_code}' \
                    'https://serpapi.com/account?api_key=${SERPAPI_KEY}' | grep -q '200'"
        else
            echo -e "  ${WARN} SerpAPI — ${YELLOW}curl not found, skipping connection test${RESET}"
        fi
    else
        echo -e "  ${FAIL} SerpAPI — skipped (SERPAPI_KEY not set)"
    fi

    echo ""
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo -e "${BOLD}Summary${RESET}"
echo ""

if [[ $REQUIRED_SET -eq $REQUIRED_TOTAL ]]; then
    echo -e "  ${PASS} Required:  ${GREEN}${REQUIRED_SET}/${REQUIRED_TOTAL} set${RESET}"
else
    MISSING=$((REQUIRED_TOTAL - REQUIRED_SET))
    echo -e "  ${FAIL} Required:  ${RED}${REQUIRED_SET}/${REQUIRED_TOTAL} set (${MISSING} missing)${RESET}"
fi

echo -e "  ${INFO} Optional:  ${OPTIONAL_SET}/${OPTIONAL_TOTAL} set"

if [[ "$TEST_CONNECTIONS" == true ]]; then
    if [[ $CONNECTION_FAIL -eq 0 && $CONNECTION_TOTAL -gt 0 ]]; then
        echo -e "  ${PASS} Connections: ${GREEN}${CONNECTION_PASS}/${CONNECTION_TOTAL} passed${RESET}"
    elif [[ $CONNECTION_TOTAL -gt 0 ]]; then
        echo -e "  ${FAIL} Connections: ${RED}${CONNECTION_PASS}/${CONNECTION_TOTAL} passed${RESET}"
    fi
fi

echo ""

# ---------------------------------------------------------------------------
# Exit code
# ---------------------------------------------------------------------------
if [[ $REQUIRED_SET -eq $REQUIRED_TOTAL ]]; then
    echo -e "${GREEN}All required environment variables are set.${RESET}"
    echo ""
    exit 0
else
    echo -e "${RED}Missing required environment variables. See above for details.${RESET}"
    echo -e "${DIM}Tip: Copy .env.example and fill in your credentials, or set vars in ~/.claude/settings.json under \"env\".${RESET}"
    echo ""
    exit 1
fi
