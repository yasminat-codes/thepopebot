"""Generate a shareable excalidraw.com URL from a .excalidraw file.

Excalidraw supports loading diagrams via URL hash using lz-string compression:
  https://excalidraw.com/#json=<lz-compressed-base64>

Usage:
    uv run python excalidraw_url.py <path-to-file.excalidraw>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import lzstring


def generate_url(excalidraw_path: Path) -> str:
    data = json.loads(excalidraw_path.read_text(encoding="utf-8"))
    compressed = lzstring.LZString().compressToEncodedURIComponent(json.dumps(data))
    return f"https://excalidraw.com/#json={compressed}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python excalidraw_url.py <file.excalidraw>", file=sys.stderr)
        sys.exit(1)
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    print(generate_url(path))
