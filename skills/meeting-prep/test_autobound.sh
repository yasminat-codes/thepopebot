#!/bin/bash
# Test Autobound integration
# Usage: ./test_autobound.sh <email> [company_domain]

if [ -z "$1" ]; then
    echo "Usage: ./test_autobound.sh <email> [company_domain]"
    echo ""
    echo "Example:"
    echo "  ./test_autobound.sh [email protected] example.com"
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$SCRIPT_DIR" && uv run scripts/autobound_client.py "$@"
