# KU Automation LinkedIn Blog Distribution Kit

**Strategy:** Drive ku-automation.com/blog traffic via Company Page posts + amplified by Kingsley's personal engagement within 30 min.

**Two-track per 2026-06-19 decision:**
- **Company Page** = all posts
- **Personal Profile** = like + first comment within 30 min, reply to every comment under the post

---

## ⚡ Launch Week (3 posts)

| # | Post | When to publish | File |
|---|------|-----------------|------|
| 1 | Two-Pass AI Reviews | **Tue 09:00 Dubai** | `post-01-two-pass.md` |
| 2 | Process Safety AI (PSV/HAZOP) | **Thu 09:00 Dubai** | `post-02-process-safety.md` |
| 3 | 4 Hours → 4 Minutes (Doc Review) | **Mon next week 09:00 Dubai** | `post-03-doc-review.md` |

Why these three:
- All published, all 1300+ words, all have clear conversion hooks
- Each maps to a paid service category (review tier, process safety, doc review)
- Mix of methodology (Two-Pass), discipline-specific (Process Safety), and outcome-driven (Time savings)

---

## 📅 Recurring Schedule (1 post / week)

After launch week, post 1 deep blog/week. Cron set to remind every **Tuesday 08:30 Dubai** with the next-up post pre-filled.

Backlog priority order (highest-value first):
1. Multi-Agent AI for Integrated Engineering Design Reviews
2. ISO 42001 AI Governance Playbook
3. RAG Systems for HAZOP Lookups
4. Digital Twins + Vibration Analytics
5. Stop Vendor Document Chaos
6. From Manual Datasheet Reviews to AI Analysis
7. Agentic AI for Engineering
8. Why Engineering Companies Lose Bids
9. P&ID Diagram AI Extraction
10. Engineering Knowledge Base AI

---

## 🔁 Per-post workflow (8 min total)

1. Open `post-XX-*.md`
2. Copy the **POST BODY** block
3. Open https://www.linkedin.com/company/ku-automation/admin/ → New post
4. Paste body. Attach the listed image (path in the file)
5. Add the **first link** in comments (LinkedIn down-ranks posts with links in body)
6. Publish
7. Switch to personal profile → **like + paste the "FIRST COMMENT" block**
8. Set a phone reminder to check comments at +2h and +6h

---

## 📊 Track in ClickUp

After each post, log in ClickUp list **📣 LinkedIn Posts** (`901819004786`):
- Post URL
- Date published
- Impressions @ 24h / 72h
- Comments / reactions / shares
- UTM clicks from GA4 (filter by `utm_source=linkedin`)

Target metrics (per 2026-06-18 playbook): 200 website clicks / 30 days from LinkedIn.

## 🔗 UTM tagging convention

Every blog/portal URL in a LinkedIn post must carry:

```
?utm_source=linkedin&utm_medium=social&utm_campaign=blog_launch&utm_content=post_XX_<slug>
```

- `utm_source=linkedin` — always
- `utm_medium=social` — always
- `utm_campaign=blog_launch` for launch week, `blog_weekly` for the recurring schedule
- `utm_content=post_XX_<short_slug>` — unique per post for attribution

**Why:** GA4 (`G-BRQ8Q6W8N8`) automatically segments by these params → visible in Reports → Acquisition → Traffic acquisition → filter by Session source.

See `projects/ai-automation-agency/linkedin/launch-kit/tracking-dashboard.md` for how to read the data.
