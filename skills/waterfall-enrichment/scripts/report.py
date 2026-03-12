#!/usr/bin/env python3
"""
Waterfall Enrichment Report Generator

Generates coverage reports from enriched lead CSVs.
Separates finder performance from verifier performance.

Usage:
    python3 report.py --input enriched_leads.csv
    python3 report.py --input enriched_leads.csv --json
"""

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone

# Cost per call for estimating spend
FINDER_COSTS = {
    "tomba": 0.01, "muraena": 0.02, "icypeas": 0.01,
    "voilanorbert": 0.03, "nimbler": 0.08, "anymailfinder": 0.05, "findymail": 0.02,
}
VERIFIER_COSTS = {"reoon": 0.003, "emailverify": 0.003}


def load_results(filepath: str) -> list:
    results = []
    with open(filepath, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["confidence"] = int(row.get("confidence", 0) or 0)
            row["catch_all"] = str(row.get("catch_all", "")).lower() in ("true", "1", "yes")
            results.append(row)
    return results


def generate_report(results: list) -> dict:
    total = len(results)
    if total == 0:
        return {"error": "No results to report"}

    found = [r for r in results if r.get("email")]
    verified = [r for r in results if r.get("status") == "verified"]
    catchall_verified = [r for r in results if r.get("status") == "catchall_verified"]
    risky = [r for r in results if r.get("status") == "risky"]
    invalid = [r for r in results if r.get("status") == "invalid"]
    not_found = [r for r in results if r.get("status") == "not_found"]

    # Finder stats
    finder_counter = Counter(r.get("finder_source", "") for r in found if r.get("finder_source"))
    finder_stats = {}
    for source, count in finder_counter.most_common():
        cost = count * FINDER_COSTS.get(source, 0.02)
        finder_stats[source] = {
            "found": count,
            "rate": round(count / total * 100, 1),
            "cost_estimate": round(cost, 2),
        }

    # Verifier stats
    reoon_verified = len(verified)
    reoon_catchall = len(catchall_verified) + len(risky)
    reoon_invalid = len(invalid)
    reoon_total = reoon_verified + reoon_catchall + reoon_invalid
    reoon_cost = round(reoon_total * VERIFIER_COSTS["reoon"], 2)

    ev_total = len(catchall_verified) + len([r for r in risky if r.get("ev_status")])
    ev_valid = len(catchall_verified)
    ev_risky_count = len([r for r in risky if r.get("ev_status") == "risky"])
    ev_invalid_count = len([r for r in results if r.get("ev_status") == "invalid"])
    ev_cost = round(ev_total * VERIFIER_COSTS["emailverify"], 2)

    # Confidence distribution
    conf_dist = {
        "90_100": sum(1 for r in found if r["confidence"] >= 90),
        "70_89": sum(1 for r in found if 70 <= r["confidence"] < 90),
        "50_69": sum(1 for r in found if 50 <= r["confidence"] < 70),
        "0_49": sum(1 for r in found if 0 < r["confidence"] < 50),
    }

    # Catchall domains
    catchall_domains = Counter()
    for r in results:
        if r.get("catch_all"):
            catchall_domains[r.get("domain", "unknown")] += 1

    # Bounce risk
    v_bounce = len(verified) * 0.005
    cv_bounce = len(catchall_verified) * 0.03
    r_bounce = len(risky) * 0.10
    sendable = len(verified) + len(catchall_verified) + len(risky)
    blended_bounce = round((v_bounce + cv_bounce + r_bounce) / sendable * 100, 1) if sendable else 0

    # Cost totals
    finder_total_cost = sum(s["cost_estimate"] for s in finder_stats.values())
    verifier_total_cost = reoon_cost + ev_cost
    grand_total = round(finder_total_cost + verifier_total_cost, 2)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_leads": total,
            "emails_found": len(found),
            "coverage_rate": round(len(found) / total * 100, 1),
            "verified": len(verified),
            "catchall_verified": len(catchall_verified),
            "risky": len(risky),
            "invalid": len(invalid),
            "not_found": len(not_found),
        },
        "finders": finder_stats,
        "verifiers": {
            "reoon": {
                "total_calls": reoon_total,
                "verified": reoon_verified,
                "catchall": reoon_catchall,
                "invalid": reoon_invalid,
                "cost_estimate": reoon_cost,
            },
            "emailverify": {
                "total_calls": ev_total,
                "valid": ev_valid,
                "risky": ev_risky_count,
                "invalid": ev_invalid_count,
                "cost_estimate": ev_cost,
            },
        },
        "confidence_distribution": conf_dist,
        "catch_all_domains": dict(catchall_domains.most_common(10)),
        "cost": {
            "finders": round(finder_total_cost, 2),
            "verifiers": verifier_total_cost,
            "total": grand_total,
            "per_lead": round(grand_total / total, 3) if total else 0,
            "per_found": round(grand_total / len(found), 3) if found else 0,
        },
        "bounce_risk": {
            "blended_estimate": blended_bounce,
            "within_target": blended_bounce < 3.0,
            "target": "< 3%",
        },
    }


def print_text_report(report: dict):
    s = report["summary"]
    print(f"\n{'='*55}")
    print(f"  WATERFALL ENRICHMENT REPORT")
    print(f"  Generated: {report['generated_at'][:19]}")
    print(f"{'='*55}")
    print()

    print(f"  COVERAGE SUMMARY")
    print(f"    Total leads:         {s['total_leads']}")
    print(f"    Emails found:        {s['emails_found']} ({s['coverage_rate']}%)")
    print(f"    Verified (safe):     {s['verified']}")
    print(f"    Catchall-verified:   {s['catchall_verified']}")
    print(f"    Risky:               {s['risky']}")
    print(f"    Invalid (discarded): {s['invalid']}")
    print(f"    Not found:           {s['not_found']}")
    print()

    if report["finders"]:
        print(f"  FINDER PERFORMANCE")
        print(f"    {'Provider':<18s} {'Found':>7s} {'Rate':>8s} {'Cost':>10s}")
        print(f"    {'-'*45}")
        for provider, stats in report["finders"].items():
            print(f"    {provider:<18s} {stats['found']:>7d} {stats['rate']:>7.1f}% ${stats['cost_estimate']:>8.2f}")
        print()

    v = report["verifiers"]
    print(f"  VERIFIER PERFORMANCE")
    r = v["reoon"]
    print(f"    Reoon:        {r['total_calls']} calls — "
          f"{r['verified']} valid, {r['catchall']} catchall, {r['invalid']} invalid "
          f"(${r['cost_estimate']:.2f})")
    e = v["emailverify"]
    if e["total_calls"] > 0:
        print(f"    Email Verify: {e['total_calls']} calls — "
              f"{e['valid']} valid, {e['risky']} risky, {e['invalid']} invalid "
              f"(${e['cost_estimate']:.2f})")
    print()

    c = report["cost"]
    print(f"  COST BREAKDOWN")
    print(f"    Finders:     ${c['finders']:.2f}")
    print(f"    Verifiers:   ${c['verifiers']:.2f}")
    print(f"    TOTAL:       ${c['total']:.2f}")
    print(f"    Per lead:    ${c['per_lead']:.3f}")
    print(f"    Per found:   ${c['per_found']:.3f}")
    print()

    cd = report["confidence_distribution"]
    print(f"  CONFIDENCE DISTRIBUTION")
    print(f"    90-100 (verified):     {cd['90_100']}")
    print(f"    70-89  (catchall-ok):  {cd['70_89']}")
    print(f"    50-69  (risky):        {cd['50_69']}")
    print(f"    1-49   (low):          {cd['0_49']}")
    print()

    if report["catch_all_domains"]:
        print(f"  TOP CATCHALL DOMAINS")
        for domain, count in report["catch_all_domains"].items():
            print(f"    {domain:<30s} {count} leads")
        print()

    br = report["bounce_risk"]
    status = "WITHIN TARGET" if br["within_target"] else "ABOVE TARGET"
    print(f"  BOUNCE RISK ESTIMATE")
    print(f"    Blended bounce: {br['blended_estimate']}% (target: {br['target']})")
    print(f"    Status:         {status}")
    print(f"\n{'='*55}\n")


def main():
    parser = argparse.ArgumentParser(description="Waterfall Enrichment Report Generator")
    parser.add_argument("--input", required=True, help="Enriched CSV file path")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        results = load_results(args.input)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    report = generate_report(results)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text_report(report)


if __name__ == "__main__":
    main()
