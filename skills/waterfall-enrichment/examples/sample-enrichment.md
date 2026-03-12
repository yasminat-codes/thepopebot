# Sample Enrichment Flow

End-to-end examples of the waterfall enrichment pipeline.

---

## Example 1: Single Lead — Found and Verified

```bash
export REOON_API_KEY="your-key"
export TOMBA_API_KEY="your-key"
export TOMBA_SECRET="your-secret"

python3 /home/clawdbot/shared/skills/waterfall-enrichment/scripts/enrich.py \
  --first-name "Sarah" \
  --last-name "Connor" \
  --domain "cyberdyne.com"
```

**What happens:**
1. Tomba searches for sarah.connor@cyberdyne.com → **found**
2. Reoon verifies → **valid** (not catchall)
3. Result: verified, confidence 95

**Output:**
```
Email:        sarah.connor@cyberdyne.com
Confidence:   95
Finder:       tomba
Reoon:        valid
Catch-all:    False
Status:       verified
```

---

## Example 2: Single Lead — Catchall Domain

```bash
python3 /home/clawdbot/shared/skills/waterfall-enrichment/scripts/enrich.py \
  --first-name "Michael" \
  --last-name "Brown" \
  --domain "smallbiz.io"
```

**What happens:**
1. Tomba searches → **found** michael@smallbiz.io
2. Reoon verifies → **catchall** (domain accepts all addresses)
3. Email Verify checks → **valid** (mailbox likely exists)
4. Result: catchall_verified, confidence 80

**Output:**
```
Email:        michael@smallbiz.io
Confidence:   80
Finder:       tomba
Reoon:        catchall
Catch-all:    True
Email Verify: valid
Status:       catchall_verified
```

---

## Example 3: Single Lead — Not Found by First Finder

```bash
python3 /home/clawdbot/shared/skills/waterfall-enrichment/scripts/enrich.py \
  --first-name "Rare" \
  --last-name "Person" \
  --domain "obscure-company.com"
```

**What happens:**
1. Tomba searches → **not found**
2. Muraena searches → **not found**
3. Icypeas searches → **found** rare.person@obscure-company.com
4. Reoon verifies → **valid**
5. Result: verified, confidence 95, finder was Icypeas

---

## Example 4: Batch from CSV

### Step 1: Prepare input CSV

```csv
first_name,last_name,company,domain
Sarah,Connor,Cyberdyne Systems,cyberdyne.com
John,Smith,Acme Corp,acme.com
Lisa,Johnson,TechStart,techstart.io
Michael,Brown,SmallBiz,smallbiz.io
Emily,Davis,Initech,initech.com
```

Save as `leads.csv`.

### Step 2: Run enrichment

```bash
python3 /home/clawdbot/shared/skills/waterfall-enrichment/scripts/enrich.py \
  --input leads.csv \
  --output enriched_leads.csv
```

### Step 3: Check results

```csv
first_name,last_name,company,domain,title,email,confidence,finder_source,verification_status,catch_all,ev_status,status,enriched_at
Sarah,Connor,Cyberdyne Systems,cyberdyne.com,,sarah.connor@cyberdyne.com,95,tomba,valid,False,,verified,2026-02-23T10:30:00+00:00
John,Smith,Acme Corp,acme.com,,john.smith@acme.com,95,tomba,valid,False,,verified,2026-02-23T10:30:05+00:00
Lisa,Johnson,TechStart,techstart.io,,,0,,,False,,not_found,2026-02-23T10:30:30+00:00
Michael,Brown,SmallBiz,smallbiz.io,,michael@smallbiz.io,80,muraena,catchall,True,valid,catchall_verified,2026-02-23T10:30:40+00:00
Emily,Davis,Initech,initech.com,,emily.davis@initech.com,95,icypeas,valid,False,,verified,2026-02-23T10:30:55+00:00
```

### Step 4: Generate report

```bash
python3 /home/clawdbot/shared/skills/waterfall-enrichment/scripts/report.py \
  --input enriched_leads.csv
```

---

## Example 5: Large Batch (10K+ Leads)

### Step 1: Split into chunks

```bash
python3 /home/clawdbot/shared/skills/waterfall-enrichment/scripts/split_csv.py \
  --input big_list.csv \
  --chunk-size 5000 \
  --dedupe \
  --output-dir ./chunks/
```

Output:
```
Loaded 22,000 leads from big_list.csv
Removed 1,200 duplicates (22,000 → 20,800)
Splitting into 5 chunks of 5000:
  big_list_chunk_001.csv: 5000 leads
  big_list_chunk_002.csv: 5000 leads
  big_list_chunk_003.csv: 5000 leads
  big_list_chunk_004.csv: 5000 leads
  big_list_chunk_005.csv: 800 leads
```

### Step 2: Enrich each chunk

```bash
# Run each chunk (can run sequentially or on separate machines)
python3 scripts/enrich.py --input chunks/big_list_chunk_001.csv --output chunks/enriched_001.csv
python3 scripts/enrich.py --input chunks/big_list_chunk_002.csv --output chunks/enriched_002.csv
# ... etc
```

### Step 3: If interrupted, resume

```bash
python3 scripts/enrich.py --input chunks/big_list_chunk_003.csv --output chunks/enriched_003.csv --resume
```

### Step 4: Report on each chunk

```bash
python3 scripts/report.py --input chunks/enriched_001.csv
```

---

## Example 6: JSON Output (Single Lead)

```bash
python3 /home/clawdbot/shared/skills/waterfall-enrichment/scripts/enrich.py \
  --first-name "John" \
  --last-name "Doe" \
  --domain "example.com" \
  --json
```

**Output:**
```json
{
  "email": "john.doe@example.com",
  "confidence": 95,
  "finder_source": "tomba",
  "verification_status": "valid",
  "catch_all": false,
  "ev_status": "",
  "status": "verified"
}
```

---

## Example 7: No Email Verify Key (Catchall Stays Risky)

When `EMAILVERIFY_API_KEY` is not set:

```bash
# Only Reoon + finders configured, no Email Verify
unset EMAILVERIFY_API_KEY

python3 scripts/enrich.py \
  --first-name "Michael" \
  --last-name "Brown" \
  --domain "smallbiz.io"
```

**What happens:**
1. Tomba finds michael@smallbiz.io
2. Reoon says catchall
3. No Email Verify available → stays RISKY (confidence 50)

**Output:**
```
Email:        michael@smallbiz.io
Confidence:   50
Finder:       tomba
Reoon:        catchall
Catch-all:    True
Status:       risky
```
