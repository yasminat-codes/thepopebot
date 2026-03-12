# Competitor Positioning

How to turn complaint themes from Stage 2 competitor_map into positioning angles.

**Core principle:** Never attack the competitor by name. Position toward what they are missing. The prospect already has the frustration — you are just naming the alternative direction.

---

## 10 Complaint-to-Positioning Templates

### 1. "too expensive" / "pricing is insane" / "costs too much"

**Positioning direction:** Accessible / right-sized / built for your stage

**Angle templates:**
- "Built for [company size] — not priced for Fortune 500"
- "You get [core outcome], not a platform you need a consultant to operate"
- "Same result at a fraction of the [Competitor] price tag"
- "[Outcome] without a six-figure contract"

**Avoid:** "cheaper than X" — positions you on price, not value. Instead position on right-fit.

---

### 2. "too complex" / "takes forever to set up" / "needs training just to use"

**Positioning direction:** Simple / done-for-you / no learning curve

**Angle templates:**
- "Running in [timeframe], not [their onboarding nightmare]"
- "Done-for-you setup — you don't touch the config"
- "If [Competitor] takes a consultant to implement, [your offer] takes an afternoon"
- "No 200-page documentation. No certification required."

---

### 3. "bad support" / "takes days to hear back" / "support is useless"

**Positioning direction:** White-glove / hands-on / personal

**Angle templates:**
- "Every client gets [founder/lead] on Slack, not a ticket queue"
- "You'll have a direct line, not a support portal"
- "When something breaks, you reach a person who built it"

---

### 4. "no automation" / "still manual" / "can't automate this"

**Positioning direction:** Fully automated / zero manual work

**Angle templates:**
- "100% automated — the only thing you do is review the result"
- "The [painful task] runs itself"
- "[Competitor] made you do it manually. This does it for you."

---

### 5. "doesn't integrate" / "nothing talks to each other" / "silos"

**Positioning direction:** Plays well with your stack / no rip-and-replace

**Angle templates:**
- "Connects to the tools you already use — no new platforms"
- "Works inside your existing [tool] without replacing it"
- "No rip-and-replace. Plugs into your stack in [timeframe]."

---

### 6. "one-size-fits-all" / "built for enterprise, not us" / "too generic"

**Positioning direction:** Purpose-built for [specific segment]

**Angle templates:**
- "Built specifically for [segment], not retrofitted from an enterprise product"
- "Every feature exists because [segment] asked for it"
- "Not a watered-down enterprise tool. Built from scratch for [segment]."

---

### 7. "slow" / "loads forever" / "keeps breaking"

**Positioning direction:** Reliable / fast / production-grade

**Angle templates:**
- "Built to handle [scale] without breaking"
- "The [process] completes in [timeframe], not [competitor's timeframe]"

---

### 8. "no reporting" / "can't see what's happening" / "no visibility"

**Positioning direction:** Full visibility / real-time / clear dashboards

**Angle templates:**
- "You'll see exactly what's happening, when, and why — without building a report"
- "Real-time visibility into [specific metric the prospect mentioned]"

---

### 9. "locked in" / "can't export data" / "hard to leave"

**Positioning direction:** Portable / no lock-in / you own your data

**Angle templates:**
- "Your data is yours — export any time, no fees, no friction"
- "No lock-in. If it's not working, you leave with everything."

---

### 10. "doesn't scale" / "breaks at [volume]" / "we outgrew it"

**Positioning direction:** Scales with you / grows as you grow

**Angle templates:**
- "Handles [lower volume] and [higher volume] — no rebuild required"
- "Grows with you from [stage A] to [stage B] without switching tools"

---

## Combining Multiple Weaknesses

When a competitor has 2+ complaint themes, combine them into one positioning statement.

**Formula:** `[Competitor] is [weakness 1] and [weakness 2]. [Your offer] is [opposite 1] and [opposite 2] — without [the thing they fear losing]`

**Example (HubSpot: "too expensive" + "too complex"):**
> "HubSpot is expensive and takes months to implement properly. This is a fully-configured pipeline that's live in a week, at a fraction of the cost — and you don't need a HubSpot admin to run it."

**Example (Salesforce: "too complex" + "bad support"):**
> "Salesforce implementations break and nobody picks up the phone. This is done-for-you, stays running, and you have a direct Slack line to the person who built it."

---

## How to Use This in Output

For each pain point with `competitors_mentioned`:

1. Look up each competitor in `competitor_map` from Stage 2 input
2. Match their `complaint_themes` to the 10 templates above
3. Write one `vs_competitor` sentence per solution that directly addresses the dominant complaint theme
4. Add top-level positioning angles to `positioning_angles[]` array in output — one per distinct competitor weakness pattern found across all pain points

**vs_competitor field format:**
One sentence. Specific. References the actual complaint theme.

Good: `"Unlike HubSpot which requires a six-month implementation and a dedicated admin, this is configured and live in one week with zero ongoing maintenance from your side."`

Bad: `"Better than HubSpot."`
