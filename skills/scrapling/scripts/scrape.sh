#!/bin/bash
# Scrapling - Fast HTTP Scraping
# Usage: scrape.sh <url> [css_selector]

URL="$1"
SELECTOR="${2:-}"

if [ -z "$URL" ]; then
    echo "Usage: $0 <url> [css_selector]"
    exit 1
fi

/home/clawdbot/venvs/scrapling/bin/python3 << EOF
import sys
import json
from scrapling.fetchers import Fetcher

url = "$URL"
selector = "$SELECTOR"

try:
    page = Fetcher.get(url)
    
    if selector:
        results = page.css(selector).getall()
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        # Return full text content
        print(page.text)
        
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
EOF
