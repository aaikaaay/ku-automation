# Post 16 — AI Electrical Load List Review: Catching Generator and Transformer Sizing Errors Before They Hit Procurement

**Blog URL (UTM-tagged):** https://www.ku-automation.com/blog/ai-electrical-load-list-review-catching-generator-sizing-errors-before-procurement?utm_source=linkedin&utm_medium=social&utm_campaign=blog_weekly&utm_content=post_16_electrical_load
**Suggested time:** Tuesday 09:00 Dubai (best B2B reach for MENA + Europe morning)
**Image to attach:** `assets/linkedin-hero-mechanical-1080.jpg` (no electrical-specific hero exists — mechanical is the closest fit; consider creating `linkedin-hero-electrical-1080.jpg` for future posts)
**Format:** Text + image (NOT link preview — links go in comments for max reach)

---

## 🔥 HOOK OPTIONS (pick one)

**A — Contrarian (recommended):**
> The electrical load list was reviewed by two senior electrical engineers and signed off at IFC.
> The generator arrived on site three months later — 15% undersized.
> Nobody missed a load. They applied the wrong demand factors to 40% of them.

**B — Story:**
> A $280M onshore gas project. 1,200-line load list. Two independent electrical reviews.
> Commissioning day: the main generator tripped on overload 40 minutes into ramp-up.
> The cause wasn't a missing load. It was a demand factor of 0.6 applied to motors that run at 0.85 continuous duty.
> An error hiding in plain sight across 480 rows.

**C — Data-led:**
> Electrical load lists have one job: tell you how big to make the generator.
> Get the demand factors wrong across 500 motor loads and you've sized a 2.5MW genset for a 3.1MW plant.
> The rental cost of an emergency standby generator during commissioning: $80,000–$150,000 per month.
> AI doesn't get tired of checking demand factors on row 847.

---

## 📋 POST BODY (copy this verbatim)

> The electrical load list was reviewed by two senior electrical engineers and signed off at IFC.
>
> The generator arrived on site three months later — 15% undersized.
>
> Nobody missed a load. They applied the wrong demand factors to 40% of them.
>
> A load list has one job: tell procurement exactly how big to make the generator, the transformers, and the switchboard. Every electrical consumer in the plant goes in — motors, lighting, HVAC, heat tracing, instruments, UPS, telecoms. Each row carries a rated power, a demand factor, a power factor, and an operating/standby classification.
>
> Get those four fields wrong consistently and the entire electrical system is sized on false premises.
>
> When we built the AI load list reviewer into the KU Automation portal, we ran it against four EPC electrical packs. Here's what showed up in the first pass on every project:
>
> 🔴 **Demand factor inconsistency** — identical centrifugal pump motors assigned 0.65 in one section, 0.85 in another, with no engineering basis for the split
> 🔴 **Operating + standby both checked** — both columns populated for the same load, doubling its contribution to the connected load total
> 🔴 **Motor kW vs. process datasheet mismatch** — load list showing 55 kW for a pump the process datasheet specifies at 75 kW
> 🔴 **VFD harmonic derating not applied** — variable-speed drives require a generation derating factor; on one project, 34 VFD loads carried no derating
> 🔴 **ATEX equipment derating missing** — Zone 1 equipment in explosive atmospheres requires uprated supply; unmarked on 12 loads
> 🔴 **UPS-segregation errors** — critical instrument loads assigned to the non-UPS bus; loss of utility power would have blacked out the control room
> 🔴 **Heat tracing underestimated for winter design** — heat tracing loads calculated at ambient design temperature, not winter peak
>
> The AI doesn't check rows in sequence. It builds a complete model of the load list — cross-referencing every load against the equipment list, process datasheets, area classification drawing, and the project electrical philosophy document — then validates every field against every other.
>
> On one 1,200-row project, it found 41 demand factor inconsistencies and 6 operating/standby conflicts in 7 minutes.
>
> The manual electrical review team had been working on the same document for three weeks.
>
> The downstream consequence of those 41 inconsistencies: the connected load calculation was 18% low. The specified generator was undersized for the actual peak demand.
>
> Full methodology — including the load model we built, where human review reliably fails on load lists, and the cost of getting generator sizing wrong — is on the blog.
>
> Link in the comments 👇
>
> What does your current load list QA look like? Still colour-coded Excel and a senior engineer sign-off?
>
> #ElectricalEngineering #PowerSystems #EPC #OilAndGas #GeneratorSizing #EngineeringAI #DigitalEngineering #ElectricalDesign #ProjectDelivery #LowVoltage

---

## 💬 FIRST COMMENT (from Kingsley's personal profile, within 30 min)

> Full methodology + real-project numbers → https://www.ku-automation.com/blog/ai-electrical-load-list-review-catching-generator-sizing-errors-before-procurement?utm_source=linkedin&utm_medium=social&utm_campaign=blog_weekly&utm_content=post_16_electrical_load
>
> Running a load list review right now? The portal gives 2 free reviews on signup — upload the load list + equipment list and it'll run the full consistency check: https://services.ku-automation.com/services?utm_source=linkedin&utm_medium=social&utm_campaign=blog_weekly&utm_content=post_16_electrical_load

---

## 🔁 ENGAGEMENT PLAYBOOK (first 6 hours = 80% of reach)

| Time after post | Action |
|---|---|
| 0 min | Publish from Company Page |
| 0–2 min | Personal profile: like the post |
| 2–5 min | Personal profile: drop FIRST COMMENT above |
| 5–30 min | DM 5–10 electrical engineers / lead electrical designers: "Just wrote this up — would love your take on whether the demand factor issue matches what you see on your projects" |
| +2 hours | Reply to every comment from BOTH personal AND company page |
| +6 hours | Re-share to 1–2 relevant LinkedIn groups (Engineering AI, Oil & Gas Digital, Electrical Engineering Professionals) |
| +24 hours | Reshare from Company Page with a different angle ("Yesterday's post on generator sizing errors hit close to home for a lot of people…") |

**DM angle for electrical engineers:** "Curious if the demand factor drift issue we describe matches what you've seen — would love a practitioner's take before I push it wider."

---

## 🎯 SUCCESS METRICS

- **Good:** 500+ impressions, 10+ comments, 20+ blog clicks
- **Great:** 2,000+ impressions, 30+ comments, 80+ blog clicks, 2+ inbound DMs from electrical engineers or project managers
- **Viral (LinkedIn-grade):** 10k+ impressions, 50+ comments → run a paid boost targeting electrical/power engineers in GCC + UK + Australia

**Target audience:** Lead electrical engineers, electrical lead designers, engineering managers at EPC contractors, owner-operators with in-house electrical teams. GCC + UK + Australia are the primary markets.

---

## 📌 NOTE

LinkedIn algorithmically penalises posts with external links in the body — that's why the URL goes in the first comment. The 47-second delay between publish and pasting the comment from the personal profile maximises both reach AND click-through.

The generator rental cost angle ($80K–$150K/month) is the conversion hook — it positions the portal review as a zero-brainer ROI vs. the cost of a single incorrectly sized generator.

**Note on image:** No `linkedin-hero-electrical-1080.jpg` exists in assets/. `linkedin-hero-mechanical-1080.jpg` is used as the closest visual fit (equipment / power machinery). Consider requesting an electrical-discipline hero image for future posts.
