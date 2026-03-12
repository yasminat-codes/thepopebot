#!/usr/bin/env python3
"""
Waterfall Enrichment — Find → Verify → Catchall Resolution Pipeline.

Architecture:
  FINDERS (cascade): Tomba → Muraena → Icypeas → Voila Norbert → Nimbler → Anymailfinder → Findymail
  VERIFIER (mandatory): Reoon — verifies every found email
  CATCHALL VERIFIER (optional): Email Verify — resolves catchall results from Reoon

Flow per lead:
  1. Try finders in order until one returns an email
  2. Verify found email with Reoon
  3. If Reoon says valid → DB (confidence 90-100)
  4. If Reoon says catchall → Email Verify
  5. If Email Verify says valid → DB (confidence 70-85)
  6. If Email Verify says risky/invalid → RISKY or DISCARD
  7. If no finder finds email → not_found

Usage:
    # Single lead
    python3 enrich.py --first-name John --last-name Doe --domain example.com

    # Batch from CSV
    python3 enrich.py --input leads.csv --output enriched.csv

    # Resume interrupted batch
    python3 enrich.py --input leads.csv --output enriched.csv --resume

    # Large batch with custom batch size
    python3 enrich.py --input leads.csv --output enriched.csv --batch-size 50
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: 'requests' package required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_PATH = SKILL_DIR / "assets" / "config.json"
CHECKPOINT_FILE = "enrichment_checkpoint.json"

# --- Finder definitions (cascade order) ---

FINDERS = [
    {"name": "tomba", "env_keys": ["TOMBA_API_KEY", "TOMBA_SECRET"], "cost": 0.01},
    {"name": "muraena", "env_keys": ["MURAENA_API_KEY"], "cost": 0.02},
    {"name": "icypeas", "env_keys": ["ICYPEAS_API_KEY"], "cost": 0.01},
    {"name": "voilanorbert", "env_keys": ["VOILANORBERT_API_KEY"], "cost": 0.03},
    {"name": "nimbler", "env_keys": ["NIMBLER_API_KEY"], "cost": 0.08},
    {"name": "anymailfinder", "env_keys": ["ANYMAILFINDER_API_KEY"], "cost": 0.05},
    {"name": "findymail", "env_keys": ["FINDYMAIL_API_KEY"], "cost": 0.02},
]

# --- Verifier definitions ---

VERIFIERS = {
    "reoon": {"env_keys": ["REOON_API_KEY"], "cost": 0.003},
    "emailverify": {"env_keys": ["EMAILVERIFY_API_KEY"], "cost": 0.003},
}

# Personal email domains — skip these
PERSONAL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
    "icloud.com", "mail.com", "protonmail.com", "zoho.com", "yandex.com",
    "live.com", "msn.com", "me.com", "inbox.com", "gmx.com",
}


def log(level: str, message: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {level:5s} {message}", file=sys.stderr)


def load_config(config_path: Optional[str] = None) -> dict:
    path = Path(config_path) if config_path else CONFIG_PATH
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"batch_size": 100, "batch_delay": 2, "request_timeout": 30, "max_retries": 3}


def get_available_finders(config: dict) -> list:
    """Return finders that have API keys set and are enabled in config."""
    config_finders = {f["name"]: f for f in config.get("finders", [])}
    available = []
    for finder in FINDERS:
        name = finder["name"]
        cfg = config_finders.get(name, {})
        if cfg.get("enabled", True) is False:
            continue
        if all(os.environ.get(k) for k in finder["env_keys"]):
            available.append({**finder, **cfg})
    return available


def has_reoon() -> bool:
    return bool(os.environ.get("REOON_API_KEY"))


def has_emailverify() -> bool:
    return bool(os.environ.get("EMAILVERIFY_API_KEY"))


def validate_email_syntax(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def normalize_domain(domain: str) -> str:
    domain = domain.strip().lower()
    domain = re.sub(r'^https?://', '', domain)
    domain = re.sub(r'^www\.', '', domain)
    domain = domain.split('/')[0]
    return domain


def normalize_name(name: str) -> str:
    return name.strip().title() if name else ""


def api_request(method: str, url: str, timeout: int = 30, max_retries: int = 3,
                initial_delay: float = 1, **kwargs) -> Optional[dict]:
    """Make an API request with exponential backoff retry."""
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            resp = requests.request(method, url, timeout=timeout, **kwargs)
            if resp.status_code == 429:
                log("WARN", f"Rate limited on {url}, retry {attempt+1}/{max_retries}")
                time.sleep(delay)
                delay *= 2
                continue
            if resp.status_code == 401:
                log("ERROR", f"Auth failed for {url}")
                return {"_error": "AUTH_FAILED"}
            if resp.status_code == 402 or resp.status_code == 403:
                log("ERROR", f"Quota/forbidden {resp.status_code} on {url}")
                return {"_error": "QUOTA_EXCEEDED"}
            if resp.status_code >= 500:
                log("WARN", f"Server error {resp.status_code} on {url}, retry {attempt+1}/{max_retries}")
                time.sleep(delay)
                delay *= 2
                continue
            if resp.status_code == 404:
                return None
            return resp.json()
        except requests.exceptions.Timeout:
            log("WARN", f"Timeout on {url}, retry {attempt+1}/{max_retries}")
            time.sleep(delay)
            delay *= 2
        except requests.exceptions.RequestException as e:
            log("ERROR", f"Request failed: {e}")
            return None
        except json.JSONDecodeError:
            log("ERROR", f"Invalid JSON response from {url}")
            return None
    return None


# ============================================================
# FINDERS — Each returns {"email": "...", "raw": {...}} or None
# ============================================================

def find_tomba(first_name: str, last_name: str, domain: str, cfg: dict) -> Optional[dict]:
    api_key = os.environ.get("TOMBA_API_KEY")
    secret = os.environ.get("TOMBA_SECRET", "")
    url = f"https://api.tomba.io/v1/email-finder?domain={domain}&first_name={first_name}&last_name={last_name}"
    headers = {"X-Tomba-Key": api_key, "X-Tomba-Secret": secret}
    result = api_request("GET", url, timeout=cfg.get("timeout", 30),
                         max_retries=cfg.get("max_retries", 3),
                         initial_delay=cfg.get("min_delay", 3), headers=headers)
    if result and isinstance(result, dict) and result.get("_error"):
        return result
    if result and "data" in result and result["data"].get("email"):
        return {"email": result["data"]["email"], "raw": result}
    return None


def find_muraena(first_name: str, last_name: str, domain: str, cfg: dict) -> Optional[dict]:
    api_key = os.environ.get("MURAENA_API_KEY")
    url = "https://api.muraena.ai/v1/email-finder"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"first_name": first_name, "last_name": last_name, "domain": domain}
    result = api_request("POST", url, timeout=cfg.get("timeout", 30),
                         max_retries=cfg.get("max_retries", 2),
                         initial_delay=cfg.get("min_delay", 3), headers=headers, json=payload)
    if result and isinstance(result, dict) and result.get("_error"):
        return result
    if result and result.get("email"):
        return {"email": result["email"], "raw": result}
    return None


def find_icypeas(first_name: str, last_name: str, domain: str, cfg: dict) -> Optional[dict]:
    api_key = os.environ.get("ICYPEAS_API_KEY")
    url = "https://app.icypeas.com/api/email-search"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"first_name": first_name, "last_name": last_name, "domain_name": domain}
    result = api_request("POST", url, timeout=cfg.get("timeout", 30),
                         max_retries=cfg.get("max_retries", 3),
                         initial_delay=cfg.get("min_delay", 1), headers=headers, json=payload)
    if result and isinstance(result, dict) and result.get("_error"):
        return result
    if result and result.get("email"):
        return {"email": result["email"], "raw": result}
    return None


def find_voilanorbert(first_name: str, last_name: str, domain: str, cfg: dict) -> Optional[dict]:
    api_key = os.environ.get("VOILANORBERT_API_KEY")
    url = "https://api.voilanorbert.com/2018-01-08/search/name"
    data = {"name": f"{first_name} {last_name}", "domain": domain}
    result = api_request("POST", url, timeout=cfg.get("timeout", 30),
                         max_retries=cfg.get("max_retries", 3),
                         initial_delay=cfg.get("min_delay", 2),
                         auth=(api_key, ""), data=data)
    if result and isinstance(result, dict) and result.get("_error"):
        return result
    if result and "email" in result:
        email_data = result["email"] if isinstance(result["email"], dict) else {"email": result["email"]}
        email = email_data.get("email", "")
        if email and not result.get("searching", False):
            return {"email": email, "raw": result}
    return None


def find_nimbler(first_name: str, last_name: str, domain: str, cfg: dict) -> Optional[dict]:
    api_key = os.environ.get("NIMBLER_API_KEY")
    url = "https://api.nimbler.com/v1/enrich"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"first_name": first_name, "last_name": last_name, "company_domain": domain}
    result = api_request("POST", url, timeout=cfg.get("timeout", 30),
                         max_retries=cfg.get("max_retries", 2),
                         initial_delay=cfg.get("min_delay", 3), headers=headers, json=payload)
    if result and isinstance(result, dict) and result.get("_error"):
        return result
    if result and (result.get("work_email") or result.get("personal_email")):
        email = result.get("work_email") or result.get("personal_email")
        return {"email": email, "raw": result}
    return None


def find_anymailfinder(first_name: str, last_name: str, domain: str, cfg: dict) -> Optional[dict]:
    api_key = os.environ.get("ANYMAILFINDER_API_KEY")
    url = "https://api.anymailfinder.com/v5.1/find-email/person"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"first_name": first_name, "last_name": last_name, "domain": domain}
    result = api_request("POST", url, timeout=cfg.get("timeout", 120),
                         max_retries=cfg.get("max_retries", 2),
                         initial_delay=cfg.get("min_delay", 5), headers=headers, json=payload)
    if result and isinstance(result, dict) and result.get("_error"):
        return result
    if result and result.get("email"):
        return {"email": result["email"], "raw": result}
    return None


def find_findymail(first_name: str, last_name: str, domain: str, cfg: dict) -> Optional[dict]:
    api_key = os.environ.get("FINDYMAIL_API_KEY")
    url = "https://app.findymail.com/api/search/name"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"first_name": first_name, "last_name": last_name, "domain": domain}
    result = api_request("POST", url, timeout=cfg.get("timeout", 30),
                         max_retries=cfg.get("max_retries", 3),
                         initial_delay=cfg.get("min_delay", 2), headers=headers, json=payload)
    if result and isinstance(result, dict) and result.get("_error"):
        return result
    if result and result.get("email"):
        return {"email": result["email"], "raw": result}
    return None


FINDER_FUNCTIONS = {
    "tomba": find_tomba,
    "muraena": find_muraena,
    "icypeas": find_icypeas,
    "voilanorbert": find_voilanorbert,
    "nimbler": find_nimbler,
    "anymailfinder": find_anymailfinder,
    "findymail": find_findymail,
}


# ============================================================
# VERIFIERS — Reoon (primary) and Email Verify (catchall)
# ============================================================

def verify_reoon(email: str, config: dict) -> dict:
    """Verify email with Reoon. Returns status dict."""
    api_key = os.environ.get("REOON_API_KEY")
    if not api_key:
        return {"status": "error", "error": "NO_API_KEY"}

    mode = config.get("verifiers", {}).get("reoon", {}).get("mode", "power")
    url = f"https://emailverifier.reoon.com/api/v1/verify?email={email}&key={api_key}&mode={mode}"

    result = api_request("GET", url, timeout=30, max_retries=5, initial_delay=0.5)

    if result is None:
        return {"status": "error", "error": "REOON_DOWN"}
    if isinstance(result, dict) and result.get("_error"):
        return {"status": "error", "error": f"REOON_{result['_error']}"}

    reoon_status = result.get("status", "unknown").lower()
    is_catchall = result.get("is_catchall", False)

    if reoon_status == "valid" and not is_catchall:
        return {"status": "valid", "catchall": False, "raw": result}
    elif reoon_status in ("valid", "catch_all", "accept_all") and is_catchall:
        return {"status": "catchall", "catchall": True, "raw": result}
    elif reoon_status == "catch_all" or is_catchall:
        return {"status": "catchall", "catchall": True, "raw": result}
    elif reoon_status == "invalid":
        return {"status": "invalid", "catchall": False, "raw": result}
    elif reoon_status == "disposable":
        return {"status": "invalid", "catchall": False, "raw": result}
    elif reoon_status == "unknown":
        # Treat unknown as catchall for safety
        return {"status": "catchall", "catchall": True, "raw": result}
    else:
        return {"status": "unknown", "catchall": False, "raw": result}


def verify_emailverify(email: str, config: dict) -> dict:
    """Resolve catchall with Email Verify. Returns status dict."""
    api_key = os.environ.get("EMAILVERIFY_API_KEY")
    if not api_key:
        return {"status": "skipped", "error": "NO_API_KEY"}

    url = f"https://api.email-verify.com/api/verify?email={email}&key={api_key}"
    result = api_request("GET", url, timeout=30, max_retries=3, initial_delay=1)

    if result is None:
        return {"status": "error", "error": "EV_DOWN"}
    if isinstance(result, dict) and result.get("_error"):
        return {"status": "error", "error": f"EV_{result['_error']}"}

    ev_status = result.get("status", "unknown").lower()

    if ev_status == "valid":
        return {"status": "valid", "raw": result}
    elif ev_status == "risky":
        return {"status": "risky", "raw": result}
    elif ev_status == "invalid":
        return {"status": "invalid", "raw": result}
    else:
        return {"status": "unknown", "raw": result}


# ============================================================
# MAIN ENRICHMENT PIPELINE
# ============================================================

def enrich_lead(first_name: str, last_name: str, domain: str, config: dict,
                finders: list, disabled_finders: set, stats: dict) -> dict:
    """
    Full pipeline for one lead:
    1. Pre-checks (name, domain, personal domain)
    2. Finder cascade (stop on first email found)
    3. Reoon verification
    4. Email Verify for catchall resolution
    """
    first_name = normalize_name(first_name)
    last_name = normalize_name(last_name)
    domain = normalize_domain(domain)

    # Pre-checks
    if not first_name or not last_name or not domain:
        return _result(status="invalid_input")

    if domain in PERSONAL_DOMAINS:
        log("INFO", f"phase=precheck lead=\"{first_name} {last_name}\" domain={domain} skip=personal_domain")
        return _result(status="skipped_personal")

    # --- PHASE 1: FIND ---
    found_email = None
    finder_source = None

    for finder in finders:
        name = finder["name"]
        if name in disabled_finders:
            continue

        find_fn = FINDER_FUNCTIONS.get(name)
        if not find_fn:
            continue

        log("INFO", f"phase=find provider={name} lead=\"{first_name} {last_name}\" domain={domain}")
        start = time.time()

        try:
            result = find_fn(first_name, last_name, domain, finder)
        except Exception as e:
            log("ERROR", f"phase=find provider={name} error={e}")
            stats["finder_errors"][name] = stats["finder_errors"].get(name, 0) + 1
            continue

        elapsed = time.time() - start
        stats["finder_calls"][name] = stats["finder_calls"].get(name, 0) + 1
        stats["finder_time"][name] = stats["finder_time"].get(name, 0) + elapsed

        # Check for auth/quota errors — disable finder for rest of run
        if isinstance(result, dict) and result.get("_error"):
            error = result["_error"]
            if error in ("AUTH_FAILED", "QUOTA_EXCEEDED"):
                log("WARN", f"phase=find provider={name} error={error} action=disabled_for_run")
                disabled_finders.add(name)
            continue

        if result and result.get("email") and validate_email_syntax(result["email"]):
            found_email = result["email"]
            finder_source = name
            stats["finder_hits"][name] = stats["finder_hits"].get(name, 0) + 1
            log("INFO", f"phase=find provider={name} status=found email={found_email} time={elapsed:.1f}s")
            # Apply min_delay before next API call
            min_delay = finder.get("min_delay", 1)
            if min_delay > elapsed:
                time.sleep(min_delay - elapsed)
            break
        else:
            log("INFO", f"phase=find provider={name} status=not_found time={elapsed:.1f}s")
            # Apply min_delay
            min_delay = finder.get("min_delay", 1)
            if min_delay > elapsed:
                time.sleep(min_delay - elapsed)

    if not found_email:
        return _result(status="not_found")

    # --- PHASE 2: VERIFY with Reoon ---
    log("INFO", f"phase=verify provider=reoon email={found_email}")
    start = time.time()
    reoon_result = verify_reoon(found_email, config)
    elapsed = time.time() - start
    stats["reoon_calls"] = stats.get("reoon_calls", 0) + 1

    reoon_status = reoon_result.get("status", "error")

    if reoon_status == "error":
        error = reoon_result.get("error", "UNKNOWN")
        log("ERROR", f"phase=verify provider=reoon email={found_email} error={error}")
        if "AUTH" in error:
            # Critical — cannot continue without verifier
            return _result(status="verifier_error", email=found_email, finder_source=finder_source,
                          verification_status="error")
        # Treat verification failure as risky
        return _result(status="risky", email=found_email, finder_source=finder_source,
                      confidence=40, verification_status="error", catch_all=False)

    if reoon_status == "valid":
        log("INFO", f"phase=verify provider=reoon email={found_email} status=valid time={elapsed:.1f}s")
        stats["reoon_valid"] = stats.get("reoon_valid", 0) + 1
        return _result(status="verified", email=found_email, finder_source=finder_source,
                      confidence=95, verification_status="valid", catch_all=False)

    if reoon_status == "invalid":
        log("INFO", f"phase=verify provider=reoon email={found_email} status=invalid time={elapsed:.1f}s")
        stats["reoon_invalid"] = stats.get("reoon_invalid", 0) + 1
        return _result(status="invalid", email=found_email, finder_source=finder_source,
                      confidence=0, verification_status="invalid", catch_all=False)

    if reoon_status == "catchall":
        log("INFO", f"phase=verify provider=reoon email={found_email} status=catchall time={elapsed:.1f}s")
        stats["reoon_catchall"] = stats.get("reoon_catchall", 0) + 1

        # --- PHASE 3: CATCHALL RESOLUTION with Email Verify ---
        if has_emailverify():
            log("INFO", f"phase=catchall provider=emailverify email={found_email}")
            start2 = time.time()
            ev_result = verify_emailverify(found_email, config)
            elapsed2 = time.time() - start2
            stats["ev_calls"] = stats.get("ev_calls", 0) + 1

            ev_status = ev_result.get("status", "error")

            if ev_status == "valid":
                log("INFO", f"phase=catchall provider=emailverify email={found_email} status=valid time={elapsed2:.1f}s")
                stats["ev_valid"] = stats.get("ev_valid", 0) + 1
                return _result(status="catchall_verified", email=found_email, finder_source=finder_source,
                              confidence=80, verification_status="catchall", catch_all=True,
                              ev_status="valid")

            elif ev_status == "risky":
                log("INFO", f"phase=catchall provider=emailverify email={found_email} status=risky time={elapsed2:.1f}s")
                stats["ev_risky"] = stats.get("ev_risky", 0) + 1
                return _result(status="risky", email=found_email, finder_source=finder_source,
                              confidence=55, verification_status="catchall", catch_all=True,
                              ev_status="risky")

            elif ev_status == "invalid":
                log("INFO", f"phase=catchall provider=emailverify email={found_email} status=invalid time={elapsed2:.1f}s")
                stats["ev_invalid"] = stats.get("ev_invalid", 0) + 1
                return _result(status="invalid", email=found_email, finder_source=finder_source,
                              confidence=0, verification_status="catchall", catch_all=True,
                              ev_status="invalid")

            else:
                log("WARN", f"phase=catchall provider=emailverify email={found_email} status={ev_status}")
                return _result(status="risky", email=found_email, finder_source=finder_source,
                              confidence=50, verification_status="catchall", catch_all=True,
                              ev_status=ev_status)
        else:
            # No Email Verify key — catchall stays risky
            log("INFO", f"phase=catchall provider=none email={found_email} status=risky_no_ev")
            return _result(status="risky", email=found_email, finder_source=finder_source,
                          confidence=50, verification_status="catchall", catch_all=True,
                          ev_status="")

    # Unknown Reoon status — treat as risky
    return _result(status="risky", email=found_email, finder_source=finder_source,
                  confidence=40, verification_status=reoon_status, catch_all=False)


def _result(status: str, email: str = "", finder_source: str = "", confidence: int = 0,
            verification_status: str = "", catch_all: bool = False, ev_status: str = "") -> dict:
    return {
        "email": email,
        "confidence": confidence,
        "finder_source": finder_source,
        "verification_status": verification_status,
        "catch_all": catch_all,
        "ev_status": ev_status,
        "status": status,
    }


# ============================================================
# CSV I/O
# ============================================================

def load_csv(filepath: str) -> list:
    leads = []
    with open(filepath, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append({
                "first_name": row.get("first_name", "").strip(),
                "last_name": row.get("last_name", "").strip(),
                "company": row.get("company", "").strip(),
                "domain": row.get("domain", "").strip(),
                "title": row.get("title", "").strip(),
                "linkedin_url": row.get("linkedin_url", "").strip(),
                "location": row.get("location", "").strip(),
            })
    return leads


OUTPUT_FIELDS = [
    "first_name", "last_name", "company", "domain", "title",
    "email", "confidence", "finder_source", "verification_status",
    "catch_all", "ev_status", "status", "enriched_at"
]


def save_results(filepath: str, results: list, append: bool = False):
    mode = 'a' if append else 'w'
    write_header = not append or not os.path.exists(filepath) or os.path.getsize(filepath) == 0

    with open(filepath, mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        if write_header:
            writer.writeheader()
        for r in results:
            writer.writerow({
                "first_name": r.get("first_name", ""),
                "last_name": r.get("last_name", ""),
                "company": r.get("company", ""),
                "domain": r.get("domain", ""),
                "title": r.get("title", ""),
                "email": r.get("email", ""),
                "confidence": r.get("confidence", 0),
                "finder_source": r.get("finder_source", ""),
                "verification_status": r.get("verification_status", ""),
                "catch_all": r.get("catch_all", False),
                "ev_status": r.get("ev_status", ""),
                "status": r.get("status", ""),
                "enriched_at": datetime.now(timezone.utc).isoformat(),
            })


# ============================================================
# CHECKPOINT / RESUME
# ============================================================

def save_checkpoint(filepath: str, input_file: str, output_file: str,
                    total: int, processed: int, batch: int, stats: dict,
                    disabled_finders: set):
    checkpoint = {
        "input_file": input_file,
        "output_file": output_file,
        "total_leads": total,
        "processed": processed,
        "last_batch": batch,
        "disabled_finders": list(disabled_finders),
        "stats": stats,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(filepath, 'w') as f:
        json.dump(checkpoint, f, indent=2)


def load_checkpoint(filepath: str) -> Optional[dict]:
    if os.path.exists(filepath):
        with open(filepath) as f:
            return json.load(f)
    return None


# ============================================================
# DEDUPLICATION
# ============================================================

def deduplicate_leads(leads: list) -> list:
    """Remove duplicates by (first_name + last_name + domain) key."""
    seen = set()
    unique = []
    for lead in leads:
        key = (
            lead["first_name"].lower().strip(),
            lead["last_name"].lower().strip(),
            lead["domain"].lower().strip(),
        )
        if key not in seen:
            seen.add(key)
            unique.append(lead)
        else:
            log("INFO", f"phase=precheck duplicate=\"{lead['first_name']} {lead['last_name']}\" domain={lead['domain']}")
    if len(leads) != len(unique):
        log("INFO", f"phase=precheck deduplicated {len(leads)} → {len(unique)} leads ({len(leads) - len(unique)} duplicates removed)")
    return unique


# ============================================================
# BATCH PROCESSING
# ============================================================

def run_batch(leads: list, config: dict, finders: list, output_file: str,
              batch_size: int = 100, batch_delay: int = 2, resume_from: int = 0,
              input_file: str = "", disabled_finders: set = None, stats: dict = None):
    total = len(leads)
    if disabled_finders is None:
        disabled_finders = set()
    if stats is None:
        stats = init_stats()
    all_results = []

    for batch_start in range(resume_from, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        batch_num = batch_start // batch_size + 1
        batch = leads[batch_start:batch_end]

        log("INFO", f"batch={batch_num} processing leads {batch_start+1}-{batch_end} of {total}")

        batch_results = []
        for lead in batch:
            result = enrich_lead(
                lead["first_name"], lead["last_name"], lead["domain"],
                config, finders, disabled_finders, stats
            )

            # Check for critical verifier error
            if result["status"] == "verifier_error":
                log("ERROR", "CRITICAL: Reoon verifier failed with auth error. Stopping batch.")
                log("ERROR", f"Processed {batch_start + len(batch_results)}/{total} leads before failure.")
                save_results(output_file, batch_results, append=(batch_start > 0 or resume_from > 0))
                save_checkpoint(CHECKPOINT_FILE, input_file, output_file, total,
                              batch_start + len(batch_results), batch_num, stats, disabled_finders)
                print_summary(all_results + batch_results, stats)
                sys.exit(2)

            enriched = {**lead, **result}
            batch_results.append(enriched)

        save_results(output_file, batch_results, append=(batch_start > 0 or resume_from > 0))
        all_results.extend(batch_results)

        save_checkpoint(CHECKPOINT_FILE, input_file, output_file, total, batch_end,
                       batch_num, stats, disabled_finders)

        found_in_batch = sum(1 for r in batch_results if r.get("email"))
        log("INFO", f"batch={batch_num} complete. {batch_end}/{total} processed. "
            f"{found_in_batch}/{len(batch_results)} found in batch.")

        if batch_end < total:
            time.sleep(batch_delay)

    # Clean up checkpoint on successful completion
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)

    return all_results, stats


def init_stats() -> dict:
    return {
        "finder_calls": {},
        "finder_hits": {},
        "finder_errors": {},
        "finder_time": {},
        "reoon_calls": 0,
        "reoon_valid": 0,
        "reoon_invalid": 0,
        "reoon_catchall": 0,
        "ev_calls": 0,
        "ev_valid": 0,
        "ev_risky": 0,
        "ev_invalid": 0,
    }


# ============================================================
# SUMMARY OUTPUT
# ============================================================

def print_summary(results: list, stats: dict):
    total = len(results)
    if total == 0:
        print("\nNo results to summarize.")
        return

    found = sum(1 for r in results if r.get("email"))
    verified = sum(1 for r in results if r.get("status") == "verified")
    catchall_verified = sum(1 for r in results if r.get("status") == "catchall_verified")
    risky = sum(1 for r in results if r.get("status") == "risky")
    not_found = sum(1 for r in results if r.get("status") == "not_found")
    invalid = sum(1 for r in results if r.get("status") == "invalid")

    print(f"\n{'='*55}")
    print(f"  WATERFALL ENRICHMENT SUMMARY")
    print(f"{'='*55}")
    print(f"  Total leads:         {total}")
    print(f"  Emails found:        {found} ({found/total*100:.1f}%)")
    print(f"  Verified (safe):     {verified} ({verified/total*100:.1f}%)")
    print(f"  Catchall-verified:   {catchall_verified} ({catchall_verified/total*100:.1f}%)")
    print(f"  Risky:               {risky} ({risky/total*100:.1f}%)")
    print(f"  Invalid (discarded): {invalid} ({invalid/total*100:.1f}%)")
    print(f"  Not found:           {not_found} ({not_found/total*100:.1f}%)")
    print()

    # Finder performance
    if stats.get("finder_calls"):
        print(f"  FINDER PERFORMANCE")
        print(f"  {'Provider':<18s} {'Searched':>8s} {'Found':>7s} {'Hit Rate':>9s} {'Avg Time':>9s}")
        print(f"  {'-'*54}")
        for name in ["tomba", "muraena", "icypeas", "voilanorbert", "nimbler", "anymailfinder", "findymail"]:
            calls = stats["finder_calls"].get(name, 0)
            if calls == 0:
                continue
            hits = stats["finder_hits"].get(name, 0)
            total_time = stats["finder_time"].get(name, 0)
            avg_time = total_time / calls if calls else 0
            hit_rate = hits / calls * 100 if calls else 0
            print(f"  {name:<18s} {calls:>8d} {hits:>7d} {hit_rate:>8.1f}% {avg_time:>8.1f}s")
        print()

    # Verifier performance
    print(f"  VERIFIER PERFORMANCE")
    reoon_calls = stats.get("reoon_calls", 0)
    if reoon_calls:
        print(f"  Reoon:        {reoon_calls} calls — {stats.get('reoon_valid', 0)} valid, "
              f"{stats.get('reoon_catchall', 0)} catchall, {stats.get('reoon_invalid', 0)} invalid")
    ev_calls = stats.get("ev_calls", 0)
    if ev_calls:
        print(f"  Email Verify: {ev_calls} calls — {stats.get('ev_valid', 0)} valid, "
              f"{stats.get('ev_risky', 0)} risky, {stats.get('ev_invalid', 0)} invalid")
    elif not has_emailverify():
        print(f"  Email Verify: not configured (catchall emails marked as risky)")
    print()

    # Bounce risk estimate
    v_bounce = verified * 0.005
    cv_bounce = catchall_verified * 0.03
    r_bounce = risky * 0.10
    sendable = verified + catchall_verified + risky
    if sendable > 0:
        blended = (v_bounce + cv_bounce + r_bounce) / sendable * 100
        print(f"  BOUNCE RISK ESTIMATE")
        print(f"  Blended bounce: {blended:.1f}% (target: <3%)")
        status = "WITHIN TARGET" if blended < 3.0 else "ABOVE TARGET"
        print(f"  Status: {status}")
    print(f"\n{'='*55}\n")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Waterfall Enrichment — Find → Verify → Catchall Resolution Pipeline")
    parser.add_argument("--first-name", help="First name (single lead mode)")
    parser.add_argument("--last-name", help="Last name (single lead mode)")
    parser.add_argument("--domain", help="Domain (single lead mode)")
    parser.add_argument("--company", help="Company name (optional)")
    parser.add_argument("--input", help="Input CSV file path")
    parser.add_argument("--output", help="Output CSV file path", default="enriched_leads.csv")
    parser.add_argument("--config", help="Config JSON file path")
    parser.add_argument("--batch-size", type=int, help="Leads per batch")
    parser.add_argument("--batch-delay", type=int, help="Seconds between batches")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--no-resume", action="store_true", help="Ignore checkpoint, start fresh")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument("--json", action="store_true", help="Output as JSON (single lead mode)")

    args = parser.parse_args()
    config = load_config(args.config)

    if args.batch_size:
        config["batch_size"] = args.batch_size
    if args.batch_delay:
        config["batch_delay"] = args.batch_delay

    # Check for Reoon (mandatory)
    if not has_reoon():
        log("ERROR", "REOON_API_KEY not set. Reoon verification is mandatory.")
        print("Error: REOON_API_KEY is required. Cannot enrich without verification.", file=sys.stderr)
        sys.exit(1)

    # Check for finders
    finders = get_available_finders(config)
    if not finders:
        log("ERROR", "No finder providers configured.")
        print("Error: No finder API keys set. Set at least one:", file=sys.stderr)
        for f in FINDERS:
            print(f"  {f['env_keys'][0]}", file=sys.stderr)
        sys.exit(1)

    finder_names = [f["name"] for f in finders]
    log("INFO", f"finders available: {finder_names}")
    log("INFO", f"reoon: configured")
    log("INFO", f"emailverify: {'configured' if has_emailverify() else 'not configured (catchall → risky)'}")

    # Single lead mode
    if args.first_name and args.last_name and args.domain:
        stats = init_stats()
        disabled_finders = set()
        result = enrich_lead(args.first_name, args.last_name, args.domain,
                            config, finders, disabled_finders, stats)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("email"):
                print(f"Email:        {result['email']}")
                print(f"Confidence:   {result['confidence']}")
                print(f"Finder:       {result['finder_source']}")
                print(f"Reoon:        {result['verification_status']}")
                print(f"Catch-all:    {result['catch_all']}")
                if result.get("ev_status"):
                    print(f"Email Verify: {result['ev_status']}")
                print(f"Status:       {result['status']}")
            else:
                print(f"No email found. Status: {result['status']}")
        sys.exit(0 if result.get("email") else 1)

    # Batch mode
    if args.input:
        if not os.path.exists(args.input):
            log("ERROR", f"Input file not found: {args.input}")
            sys.exit(1)

        leads = load_csv(args.input)
        log("INFO", f"loaded {len(leads)} leads from {args.input}")

        # Deduplicate
        leads = deduplicate_leads(leads)

        resume_from = 0
        disabled_finders = set()
        stats = init_stats()

        if args.resume and not args.no_resume:
            checkpoint = load_checkpoint(CHECKPOINT_FILE)
            if checkpoint and checkpoint.get("input_file") == args.input:
                resume_from = checkpoint["processed"]
                disabled_finders = set(checkpoint.get("disabled_finders", []))
                stats = checkpoint.get("stats", init_stats())
                log("INFO", f"resuming from lead {resume_from}")
                if disabled_finders:
                    log("INFO", f"disabled finders from checkpoint: {disabled_finders}")
            else:
                log("WARN", "no valid checkpoint found, starting from beginning")

        results, stats = run_batch(
            leads, config, finders, args.output,
            batch_size=config.get("batch_size", 100),
            batch_delay=config.get("batch_delay", 2),
            resume_from=resume_from,
            input_file=args.input,
            disabled_finders=disabled_finders,
            stats=stats,
        )

        print_summary(results, stats)
        log("INFO", f"output saved to {args.output}")
        sys.exit(0)

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
