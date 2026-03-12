#!/bin/bash
# Test Meeting Prep V2
# Creates folder structure with intelligence doc, talking points doc, and Gamma slides

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: ./test_v2.sh <lead_name> <company_name> [email] [domain]"
    echo ""
    echo "Example:"
    echo "  ./test_v2.sh \"Sarah Johnson\" \"Acme Corp\" [email protected] acme.com"
    exit 1
fi

LEAD_NAME="$1"
COMPANY_NAME="$2"
EMAIL="${3:-}"
DOMAIN="${4:-}"

cd "$(dirname "$0")"

CMD="uv run scripts/meeting_prep_orchestrator_v2.py \"$LEAD_NAME\" \"$COMPANY_NAME\""

if [ -n "$EMAIL" ]; then
    CMD="$CMD --email $EMAIL"
fi

if [ -n "$DOMAIN" ]; then
    CMD="$CMD --domain $DOMAIN"
fi

echo "🎯 Running Meeting Prep V2..."
echo "   Lead: $LEAD_NAME"
echo "   Company: $COMPANY_NAME"
echo ""

eval $CMD
