# Why Most AI Pilots Stall at Procurement — And the Fix

## The Silent Killer of AI Momentum in Engineering

You've secured budget. You've identified a high-ROI use case—datasheet parsing, P&ID validation, or MTO extraction. Your team is excited. You've even picked the AI vendor.

Then procurement happens.

Eight weeks later, you're still negotiating a Statement of Work. The contract language conflicts with your data governance policy. The vendor wants unfettered access to production models. Your legal team flags "IP indemnification gaps." Your information security team demands attestation for SOC 2 compliance that the vendor doesn't have—or won't provide for another six months.

Meanwhile, the budget lapses. The project loses momentum. Leadership asks, "Where's the ROI?" The AI pilot becomes another stalled initiative, filed away with lessons-learned documentation nobody reads.

This scenario is **not unique**. It is the de facto failure mode for 60% of AI pilots in engineering firms—not technical failure, but procurement gridlock.

---

## Why Procurement Becomes the Bottleneck

### 1. **Data Governance Complexity**

Engineering firms hold sensitive intellectual property: vendor datasheets, P&IDs, equipment models, test data, and cost estimates. Procurement teams are trained to assume *everything* is proprietary.

When you propose uploading even anonymized P&ID fragments to an AI service, procurement asks:
- "Can the vendor train on our data?"
- "Do they have sub-processors in GDPR jurisdictions?"
- "What happens to our data after the pilot ends?"

These are legitimate questions. But the answers often require vendor responses that take 4–8 weeks, or don't exist in the vendor's documentation.

### 2. **Vendor Readiness Mismatch**

Many AI vendors are young, technically sophisticated, but operationally immature. They have SOC 2 **in progress**. They use sub-processors they haven't formally documented. Their contract is a one-size-fits-all SaaS agreement built for B2C customers, not enterprises with data residency requirements.

Meanwhile, your procurement team expects:
- DPA (Data Processing Agreement)
- Business Associate Agreement (BAA) if HIPAA-adjacent
- Vendor risk assessment completed
- References from similar-sized firms in your sector

The vendor may say, "We've never done this before." Procurement pauses and de-risks by saying "no."

### 3. **Conflicting Risk Tolerances**

Your engineering leadership is optimistic: "Let's test it on a small dataset." Your procurement and legal teams operate from the opposite assumption: "Assume maximum risk unless proven otherwise."

This creates a stalemate:
- Engineering wants a 30-day test with raw data
- Procurement demands a full contractual framework, data residency guarantees, and IP indemnification *before* any data moves

Both viewpoints are defensible. But without a shared playbook, the project freezes.

### 4. **Scope Creep in Contract Negotiation**

A simple pilot ("Extract MTOs from 10 datasheets using our internal compute") balloons into contractual negotiations about:
- Liability caps ($1M? $5M?)
- Insurance minimums
- Warranty disclaimers
- Indemnification for third-party IP used in the AI model
- Renewal terms and data retention post-contract

Each addition extends the cycle by 2–3 weeks.

---

## The Data: Why Delays Cost Real Money

Consider a typical EPC firm with 200 engineers:

| Activity | Hours Lost | Cost (@ $150/hr) | Weeks Delayed |
|----------|-----------|-----------------|---------------|
| Vendor evaluation & RFI cycles | 40 | $6,000 | 1–2 |
| Initial procurement submission + revision cycles | 80 | $12,000 | 2–3 |
| Legal/security review + vendor responses | 120 | $18,000 | 3–4 |
| Contract negotiation (2–3 rounds) | 100 | $15,000 | 2–3 |
| Final sign-off & project restart | 40 | $6,000 | 1–2 |
| **Total** | **380 hours** | **$57,000** | **8–12 weeks** |

That $57K of overhead **reduces** the perceived ROI of a pilot that itself costs only $15K.

Worse: by week 12, the champion engineer who identified the use case has moved on to another project. You've lost institutional knowledge of *why* the pilot mattered.

---

## The Fix: A Pre-Emptive Procurement Playbook

### Step 1: Segment Your AI Vendors (Before You Buy)

**Tier 1: Enterprise-Ready Vendors** (SOC 2, DPA ready, mature ops)
- Examples: OpenAI (Enterprise), Anthropic (API), Google Cloud (AI APIs)
- Procurement path: 4–6 weeks
- Best for: High-stakes or production workloads

**Tier 2: Startup Vendors** (Strong product, SOC 2 in progress, willing to negotiate)
- Examples: Specialized domain vendors, research spinouts
- Procurement path: 6–10 weeks
- Best for: Pilots with data residency flexibility

**Tier 3: Open-Source or Internal Deploy** (No SaaS risk, full data control)
- Examples: Llama, Mistral, self-hosted services
- Procurement path: 2 weeks (infra + policy approval only)
- Best for: Maximum data sensitivity or offline-required workloads

**Decisions to make *before* technical evaluation:**
- Will your pilot require cloud processing or can it run on-premise?
- Is training on your data a requirement, or is fine-tuning acceptable?
- What's your data sensitivity threshold (public benchmark data vs. proprietary)?

If your use case allows Tier 3 (open-source on-prem), you **bypass 90% of procurement friction**. For Tier 2, you frontload vendor maturity screening.

### Step 2: Pre-Build a Pilot Data Governance Framework

Don't wait until you have a vendor. Draft a **Pilot Data Governance Addendum** that covers:

1. **Data Classification**
   - Which datasets are allowed (e.g., "anonymized P&IDs with equipment types removed")
   - Which are forbidden (e.g., "cost estimates, vendor pricing")

2. **Data Residency**
   - "All data remains in [region]" or "self-hosted compute only"
   - Acceptable jurisdictions for sub-processors

3. **Post-Pilot Data Handling**
   - "Vendor must delete all project data within 30 days of contract end"
   - Or: "Vendor may retain only aggregate statistical summaries, not raw inputs"

4. **IP and Training**
   - "Vendor shall not train on or incorporate Project Data into models"
   - "Vendor shall share back any derived improvements"

**Share this framework with procurement *now***. When a vendor arrives later, you say: "We've pre-approved this data governance model. Confirm compliance and we move forward in 2 weeks instead of 8."

### Step 3: Establish a Procurement Fast-Track for Low-Risk Pilots

Work with your procurement team to define **low-risk pilot criteria**:

- Pilot duration ≤ 90 days
- Budget < $50K (or your materiality threshold)
- No production data; test datasets only
- Vendor liability capped at pilot cost (e.g., $25K indemnification)
- Data deleted automatically at contract end

If a vendor meets these criteria **and your pre-built governance framework**, negotiate a **Pilot Addendum** rather than a full MSA. This is a 10-page document, not a 50-page contract.

Example structure:
- Use vendor's standard SaaS agreement **as-is**
- Overlay a Pilot Addendum that modifies sections for data handling, liability, and termination
- Sign in 3–4 weeks instead of 8–10

### Step 4: Assign a Procurement Champion

Designate one person (not a rotating committee) as **Procurement Sponsor** for AI pilots. This person:

- Knows the pre-built governance framework
- Has pre-authorized vendor contacts (to speed RFI cycles)
- Can escalate vendor-side blockers directly (not email chains)
- Owns the timeline: "We have 30 days to contract sign or we cancel"

This human continuity is worth weeks of compressed timing.

### Step 5: Build a Vendor Readiness Scorecard

Before entering procurement, score vendors on:

| Criterion | Weight | Tier 1 | Tier 2 | Tier 3 |
|-----------|--------|--------|--------|--------|
| SOC 2 Type II or equivalent | 20% | ✅ | ⏳ (in progress) | N/A |
| DPA template available | 15% | ✅ | ⏳ (custom) | N/A |
| Sub-processor list transparent | 15% | ✅ | ✅ | N/A |
| Pilot-friendly commercial model | 20% | ✅ | ✅ | ✅ |
| Data residency options | 15% | ✅ | ⏳ (limited) | ✅ |
| Engineering fit for use case | 15% | ✅ | ✅ | ✅ |

**Decision rule:** Tier 1 vendors can skip operational red flags. Tier 2 requires high engineering scores to justify procurement risk. Tier 3 is fast-tracked if technical fit is proven.

---

## Case Study: From Stalled to Shipped

**The Company:** A mid-sized EPC firm with 150 engineers

**The Challenge:** Extract equipment lists from isometric drawings (currently 6 person-weeks per project).

**The Initial Misstep:**
- Engineering team found a startup AI vendor (excellent technical fit)
- Submitted vendor request to procurement in week 1
- Vendor had zero SOC 2 attestation or DPA template
- Procurement flagged it as "high-risk" and demanded 8-week security audit
- Project stalled for 10 weeks

**The Pivot:**
- Leadership authorized a re-evaluation under the "Pilot Fast-Track" framework
- Team segmented vendors: Tier 2 (startup, willing to negotiate) vs. Tier 3 (open-source, on-prem)
- Chose Tier 3 (run open-source model on-prem) to eliminate SaaS risk entirely
- Drafted Pilot Data Governance Addendum (2 days)
- Procurement approved in 3 weeks
- Pilot began in week 4 vs. originally week 12

**The ROI:**
- Saved $40K in overhead
- Recovered 8 weeks of momentum
- Proved 40% time savings on equipment extraction
- Progressed to production contract (now with confidence)

---

## The Bottom Line

AI pilots fail at procurement not because of bad intentions, but because of **process misalignment**. Engineering optimism meets procurement risk-aversion with no shared framework.

The fix is not to blame procurement. It's to:

1. **Pre-segment vendors** by operational maturity
2. **Pre-build data governance** standards
3. **Create fast-track paths** for low-risk pilots
4. **Assign accountability** for pace
5. **Use a vendor scorecard** to de-risk earlier decisions

If you do these five things *before* you have a vendor, procurement becomes a 3–4 week administrative gate, not an 8–12 week bottleneck.

Your AI pilots will move from "stalled at procurement" to "running by week 5."

---

## Next Steps

1. **This week:** Draft your Pilot Data Governance Addendum (use your current ISMS as a template)
2. **Next week:** Schedule a meeting with your procurement lead; share the addendum and ask for fast-track criteria
3. **Before your next AI vendor evaluation:** Run vendors through your Tier 1/2/3 scorecard; only Tier 1 vendors skip to direct negotiation

One simple playbook can compress 8–10 weeks of overhead into 3–4 weeks of clean negotiation. Your AI ROI improves immediately.
