# Case Study
## AI-Assisted Engineering Document Review — ROI on a Live EPC Workflow

**Prepared by:** KU Automation Engineering Ltd
**Prepared for:** EPC engineering leadership
**Author:** Kingsley Uzowulu, CEng MIMechE (21+ years mechanical/piping)
**Date:** August 2026
**Length:** 2 pages
**Confidentiality:** Client identifiers redacted per NDA

---

### Executive summary

A mid-tier EPC contractor delivering brownfield oil & gas modifications was spending **~38% of senior engineer time on document review** — vendor prints, datasheets, isometrics, and MTOs. Review cycles were the single largest schedule risk on packages in the £2–8M range.

KU Automation deployed a supervised AI review workflow across three deliverable classes (pump datasheets, P&ID drawings, welding procedure specifications) over a 6-week pilot.

| Metric | Before | After | Δ |
|---|---|---|---|
| Review time per pump datasheet | 90 min | 12 min + 8 min CEng countersign | **−78%** |
| Findings per document (avg) | 6.2 | 14.8 (with severity flagging) | **+139%** |
| Critical findings missed (audit sample of 40 docs) | 3 (7.5%) | 0 (0%) | **−100%** |
| Comment register turnaround | 4.2 days | 0.6 days | **−86%** |
| Cost per review (blended) | £142 | £31 | **−78%** |
| Total pilot cost | — | £14,500 | — |
| Estimated annual saving on this workflow | — | £186,000 | **12.8× ROI Year 1** |

---

### The problem

Senior engineers on this project were reviewing 40–60 vendor documents per week per package. Three failure modes recurred:

1. **Fatigue drift.** Findings quality dropped materially after the third document of the day (accepted-finding rate fell from 71% to 43%).
2. **Silent drops on Rev-B.** Comments from Rev-A were re-issued unchanged 22% of the time — vendor "response accepted" without evidence.
3. **Cross-code blind spots.** A single pump datasheet is governed by API 610, NACE MR0175, project specs, and client engineering standards. No individual reviewer held all four in working memory.

The client's own audit (Q1 2026) flagged 3 critical findings missed on live packages. Estimated rework and change-order exposure: **£340k across two packages.**

---

### What we deployed

A supervised two-pass review workflow, delivered as a service (not shrink-wrap software):

**Pass 1 — AI review (5–8 minutes per document)**
- Document ingested via secure upload (EU-hosted, no training on client data)
- Cross-checked against relevant code editions (API 610 12th Ed., NACE MR0175:2021, ASME B31.3-2022, project-specific spec deck)
- Every finding cites: (a) exact clause, (b) location in the source document, (c) severity tier, (d) recommended action

**Pass 2 — CEng critique (6–10 minutes per document)**
- Chartered engineer reviews AI output before release
- Confirms severity classification (Critical / Major / Minor / Observation)
- Adds discipline judgement where AI is uncertain
- Signs the comment register

**Deliverables per document:**
- Comment register (project format, drop into EDMS)
- Marked-up source PDF with anchored findings
- Traceability log (clause → finding → recommended action)
- Rev-tracking so nothing silent-drops between revisions

---

### The results (verified against client audit — 40 documents, blind re-review)

- **0 critical findings missed** (vs. 3 in the pre-pilot audit sample)
- **97% accepted-finding rate** (vs. 58% baseline for the same reviewers under time pressure)
- **86% reduction** in comment register turnaround (Rev-A to issued-for-vendor)
- **£186k annual saving** on this single workflow, verified against timesheet data
- Two Principal Engineers redeployed from review-triage to design-development on higher-value packages

Client quote (redacted title):
> *"We stopped debating whether AI could review engineering documents about six weeks in. The comment registers coming back were the cleanest we'd seen in eighteen months, and every finding was defensible against the code clause. What changed our mind wasn't the AI — it was seeing a chartered engineer's signature at the bottom of every register."*
> — Head of Engineering, Tier-2 EPC (name withheld)

---

### What it costs

| Package | Scope | Investment | Typical payback |
|---|---|---|---|
| **48-hour supervised pilot** | Up to 10 documents, 1 discipline, full comment register | £1,200 | Weeks 2–3 |
| **Project pack** | 100 documents, up to 3 disciplines, EDMS-ready output | £7,500 | 6–10 weeks |
| **Team workspace** | Unlimited documents, workflow integration, monthly review calls | £3,500/mo | Month 2 |
| **Enterprise** | Multi-project, custom code libraries, dedicated CEng | From £45k/yr | Quarter 1 |

**Every tier includes CEng countersign. That's what makes findings defensible in a client audit.**

---

### Why this works when generic AI doesn't

1. **Codified engineering judgement** — 21 years of CEng review patterns encoded into the discipline libraries, not raw prompt engineering
2. **Traceable evidence** — every finding cites the code clause and source-document location; no "the AI thinks…" answers
3. **Human-supervised escalation** — chartered engineer signs off severity; the deliverable carries professional indemnity
4. **Rev-tracking built in** — no silent drops between vendor revisions
5. **Data isolation** — EU hosting, no cross-tenant model training, zero-retention option on request

---

### Next step

**Book a 48-hour supervised pilot on one of your live packages.** £1,200. Credited in full against your first project pack if you proceed.

Send 3–10 real deliverables (redacted or under NDA — we sign yours). You get back:
- A CEng-signed comment register
- Marked-up source PDFs
- A cost/time-saving report benchmarked against your own review data

**Contact:** contact@ku-automation.com
**Web:** ku-automation.com
**Direct:** Kingsley Uzowulu, CEng MIMechE

---

*KU Automation Engineering Ltd | Registered in England | ISO 42001 AI governance aligned | SOC 2 roadmap on request*
