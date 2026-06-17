---
slug: two-pass-ai-engineering-review-critique-pass-that-transforms-output-into-consultant-deliverable
title: "Two-Pass AI Engineering Reviews: The Critique Pass That Turns AI Output Into a Real Consultant Deliverable"
excerpt: Most AI review tools stop at the first pass. Discover how a two-pass self-critique protocol culls weak findings, sharpens language, and produces code-grade engineering deliverables.
date: 2026-06-17
modified: 2026-06-17
published: true
featured: false
image: /assets/blog/two-pass-ai-engineering-review-critique-pass-that-transforms-output-into-consultant-deliverable.png
tags:
  - AI Engineering Reviews
  - Quality Assurance
  - Process Safety
  - Owner's Engineering
  - AI Review Methodology
readTime: 8
wordCount: 1650
author:
  name: Kingsley Uzowulu
  title: Founder & Lead Engineer, CEng MIMechE
  avatar: https://ai-automation-agency-gilt.vercel.app/assets/avatar-kingsley.png
  bio: Chartered Engineer with 21+ years of experience in oil & gas, EPC, and manufacturing. Passionate about applying AI to solve real engineering challenges.
  linkedin: https://linkedin.com/in/kingsleyuzowulu
---

There is a credibility gap sitting at the heart of every AI engineering review tool on the market today. Ask most platforms to check a P&ID or a pump datasheet, and you will get output. Plenty of output. Findings padded with hedging language, code citations that look plausible but cannot be traced back to an actual clause number, and location references so vague they are useless on a live drawing — "the heat exchanger area may potentially have a concern."

That is not a consultant deliverable. That is a first draft that a junior engineer would be embarrassed to send.

The difference between an AI tool that generates findings and one that produces something a senior engineer would actually sign off on comes down to a single architectural decision: does the system review its own work?

At KU Automation, we shipped a two-pass self-critique protocol on 17 June 2026 as a mandatory part of every Detailed-and-above review on the marketplace at [services.ku-automation.com](https://services.ku-automation.com). This article explains exactly how it works, why it matters, and what the output difference looks like in practice — using real numbers from validation runs against a live electrostatic coalescer P&ID.

## Why a Single-Pass AI Review Is Not Enough

A single-pass LLM review runs one prompt: "act as a senior engineer, review this document against the following checklist, return findings." The model does its best. But three failure modes are endemic to this architecture.

**Hallucinated code citations.** LLMs will confidently cite "API 520 §7.4.2" or "IEC 61511 §9.3.1.4" when those clause numbers are incorrect, do not exist, or refer to a different topic entirely. An engineer relying on a fabricated citation to justify a design decision faces a serious liability exposure.

**Weak, hedged findings.** The default LLM register is cautious and passive. "It is observed that the pressure relief arrangement may potentially not be in full conformance with the applicable standard" tells an engineer nothing actionable. It cannot be assigned a severity. It cannot be closed out.

**Vague location anchors.** "On the compressor suction line" is useless on a P&ID with eight compressor trains across four sheets. A finding without a precise sheet-and-zone reference, or a section-and-paragraph reference in a report, cannot be acted on in the field.

These are not edge cases. They appear in every single-pass AI engineering review we have tested, including our own early builds. The critique pass was designed specifically to eliminate them.

## The Two-Pass Architecture: Draft, Then Challenge

Every Detailed-and-above review on the KU Automation marketplace now runs two sequential Claude calls against the uploaded document.

### Pass 1: Senior-Engineer Draft

The first call runs the document against the full discipline-specific checklist. For a P&ID review, that checklist covers items drawn from ISA 5.1 (symbology), ISA 18.2 (alarm management), API RP 14C (surface safety systems for offshore), IEC 61511 (functional safety), and applicable process-specific codes. For a process calculation, the checklist spans the governing equation, input assumptions, contingency factors, and code method selection.

Pass 1 is deliberately unconstrained. The model is instructed to find everything that could be a finding. Over-detection is acceptable at this stage. The output is an internal draft, not the deliverable.

### Pass 2: Lead-Reviewer Critique

The second call receives the Pass 1 draft and a critique instruction set. The critique model's job is adversarial. It is explicitly instructed to:

- **Cull weak findings.** Any finding that cannot be linked to a specific code clause or project specification requirement is removed. Findings based on "best practice" alone, without a citable basis, are also removed unless the discipline checklist explicitly includes them.
- **Sharpen language.** Every passive or hedged construction is rewritten in direct, declarative engineering language. "It appears that the NPSH margin may potentially be insufficient" becomes a specific finding with numbers: "Datasheet shows NPSH-A 3.5 m vs NPSH-R 3.2 m — margin 0.3 m, below API 610 §6.1.11 minimum 1.0 m for hydrocarbon service. Critical."
- **Verify code citations.** The critique pass checks that every cited clause is consistent with the code's structure. If a clause number is inconsistent with the standard's known numbering format, the finding is flagged and the citation is either corrected or removed entirely.
- **Enforce mandatory location anchors.** Every finding must carry a precise location reference. For a P&ID: sheet number plus zone (e.g., "Sheet 2, Zone D–E/3–4"). For a process report: section number plus paragraph or table reference. Findings without anchors are sent back to Pass 1 logic for re-extraction or removed.
- **Re-rate severity.** Severity assignments from Pass 1 are reviewed against the actual consequence of each finding. A vague observation inflated to "Major" is downgraded. A specific finding with clear safety implications that was logged as "Minor" is escalated.
- **Add 1–2 positive observations.** The critique pass is not purely subtractive. Where the document demonstrates good engineering practice — a well-specified high-integrity protection layer, a conservative approach to corrosion allowance, a clearly documented HOLD — it records that. Balanced reviews build credibility.
- **Sharpen the executive summary.** The summary is rewritten to reflect only the culled, sharpened findings, with a clear statement of the most critical items requiring action before approval.

**Measurable Outcome:** In internal testing across 12 review runs, the critique pass culled an average of 22% of Pass 1 findings as insufficiently substantiated, revised the language of 67% of retained findings, and corrected or removed fabricated code citations in 100% of cases where they appeared.

## Before and After: Language Transformation in Practice

The clearest way to demonstrate the value of the critique pass is side-by-side comparison. These examples are drawn from the validation run against the electrostatic coalescer P&ID conducted on 17 June 2026.

**NPSH margin finding:**
- *Pass 1 output:* "It is observed that the NPSH available for the coalescer feed pump may potentially not be adequate considering the system operating conditions. Consideration should be given to verifying the NPSH margin against API requirements."
- *Pass 2 output:* "Coalescer feed pump — datasheet shows NPSH-A 3.5 m vs NPSH-R 3.2 m at rated flow. Margin 0.3 m. API 610 §6.1.11 requires minimum 1.0 m margin for hydrocarbon service. Current margin is inadequate. Severity: Critical. Sheet 1, Zone C/4–5."

**Control loop finding:**
- *Pass 1 output:* "The DP control loop in the coalescer section may have some issues related to its configuration that could potentially affect process performance under certain operating conditions."
- *Pass 2 output:* "DP control loop (FIC-201) — no low-flow cut-off or override interlock shown on P&ID. ISA 18.2 §6.4.3 requires rationalization documentation for process-critical control loops; no note shown linking to alarm rationalization register. Severity: Major. Sheet 2, Zone D–E/3–4."

The difference is not cosmetic. The Pass 2 finding has a tag number, a code clause, a precise location, and a severity that can be entered directly into a project action register.

## Validation: Electrostatic Coalescer P&ID, End-to-End

The two-pass protocol was validated end-to-end against a real electrostatic coalescer P&ID on 17 June 2026. The results:

| Severity | Count |
|---|---|
| Critical | 5 |
| Major | 7 |
| Minor | 6 |
| Observation | 3 |

Every finding carried a sheet-and-zone anchor. Zero fabricated code citations appeared in the final output. The total AI compute cost for both passes was **$0.64**. Elapsed time from upload to final report: **10 minutes**.

A comparable independent senior review from an external consultant would typically cost £1,200–£2,500 per review day, with turnaround measured in weeks during peak project phases.

**Measurable Outcome:** 21 substantiated, anchored, severity-rated findings at $0.64 compute cost and 10 minutes elapsed time. No invented clause numbers. No unlocated findings.

## Universal Voice and Register Rules

The critique pass enforces a mandatory list of banned AI-tell phrases across every review. These are constructions that immediately signal to an experienced engineer that they are reading machine output, not professional advice:

- "It is observed that…"
- "It is noted that…"
- "Consideration should be given to…"
- "It appears that…"
- "…may potentially…"
- "…could possibly…"
- "It is recommended that consideration be given to…"

Every finding must open with either the affected equipment tag, the drawing reference, or the document section — not a passive observation construction. The register is the same one a chartered engineer uses when writing a peer review comment: direct, referenced, actionable.

This matters because findings that read like AI output are ignored. Engineers are busy. If a finding does not tell them exactly what is wrong, exactly where it is, and exactly what code requires differently, it goes into the "AI hallucinated something" pile and the value of the review is lost.

## What This Means for Engineering Managers Evaluating AI Review Tools

If you are evaluating AI review tools for your organisation, the single most important question to ask is: does the system review its own work?

A one-pass tool will give you volume. A two-pass tool gives you signal. The distinction becomes critical on high-stakes reviews — FEED packages, IFC drawing sets, HAZOP-linked P&IDs, or safety case documentation — where a finding that cannot be verified and located is worse than no finding at all, because it wastes engineer time and erodes trust in the tool.

The two-pass architecture is now live across all Detailed and above review tiers on the KU Automation marketplace at [services.ku-automation.com](https://services.ku-automation.com). Disciplines covered include Piping (11 specialist reviewers), Process (P&ID, PFD, process calculations, design philosophies), Mechanical (pump datasheets), and Civil (foundation drawings) — 17 live products in total, priced from $19 for a Quick Review to $79 for a Detailed Review.

If you want to see the protocol in action on one of your own documents, request a free pilot review via the marketplace. Upload a P&ID, a process calculation, or a design philosophy document and we will return the full two-pass output — including the internal Pass 1 draft alongside the final critique-refined deliverable — so you can judge the delta for yourself.

The gap between AI output and a professional engineering deliverable is real. The two-pass critique pass is how we close it.

---
