#!/usr/bin/env python3
"""
Split CSV — Break large lead files into smaller chunks for batch processing.

For large lists (10K-50K+), split before enriching to:
- Manage memory usage
- Enable parallel processing across multiple runs
- Reduce risk of losing progress on very large batches

Usage:
    # Split into chunks of 5000
    python3 split_csv.py --input leads.csv --chunk-size 5000

    # Split into chunks of 2000 with custom output directory
    python3 split_csv.py --input leads.csv --chunk-size 2000 --output-dir ./chunks/

    # Split and deduplicate
    python3 split_csv.py --input leads.csv --chunk-size 5000 --dedupe
"""

import argparse
import csv
import os
import sys
from pathlib import Path


def load_csv(filepath: str) -> tuple:
    """Load CSV and return (headers, rows)."""
    with open(filepath, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)
    return headers, rows


def deduplicate(rows: list) -> list:
    """Remove duplicates by (first_name + last_name + domain)."""
    seen = set()
    unique = []
    dupes = 0
    for row in rows:
        key = (
            row.get("first_name", "").lower().strip(),
            row.get("last_name", "").lower().strip(),
            row.get("domain", "").lower().strip(),
        )
        if key not in seen:
            seen.add(key)
            unique.append(row)
        else:
            dupes += 1
    if dupes > 0:
        print(f"Removed {dupes} duplicates ({len(rows)} → {len(unique)})")
    return unique


def split_and_write(headers: list, rows: list, chunk_size: int, output_dir: str, base_name: str):
    """Split rows into chunks and write each as a CSV."""
    os.makedirs(output_dir, exist_ok=True)
    total = len(rows)
    chunks = []

    for i in range(0, total, chunk_size):
        chunk_num = i // chunk_size + 1
        chunk_rows = rows[i:i + chunk_size]
        filename = f"{base_name}_chunk_{chunk_num:03d}.csv"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(chunk_rows)

        chunks.append({"file": filepath, "leads": len(chunk_rows)})
        print(f"  {filename}: {len(chunk_rows)} leads")

    return chunks


def main():
    parser = argparse.ArgumentParser(description="Split large CSV files into chunks for batch enrichment")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--chunk-size", type=int, default=5000, help="Leads per chunk (default: 5000)")
    parser.add_argument("--output-dir", help="Output directory for chunks (default: same dir as input)")
    parser.add_argument("--dedupe", action="store_true", help="Remove duplicates before splitting")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    headers, rows = load_csv(args.input)
    print(f"Loaded {len(rows)} leads from {args.input}")

    if args.dedupe:
        rows = deduplicate(rows)

    base_name = Path(args.input).stem
    output_dir = args.output_dir or str(Path(args.input).parent)

    num_chunks = (len(rows) + args.chunk_size - 1) // args.chunk_size
    print(f"Splitting into {num_chunks} chunks of {args.chunk_size}:")

    chunks = split_and_write(headers, rows, args.chunk_size, output_dir, base_name)

    print(f"\nDone. {len(chunks)} files created in {output_dir}/")
    print(f"\nTo enrich each chunk:")
    for chunk in chunks:
        print(f"  python3 enrich.py --input \"{chunk['file']}\" --output \"{chunk['file'].replace('.csv', '_enriched.csv')}\"")


if __name__ == "__main__":
    main()
