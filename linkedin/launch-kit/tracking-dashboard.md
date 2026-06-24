# LinkedIn → Blog → Portal Tracking Dashboard

Everything is now tagged with UTM parameters. Here's how to read the data and prove ROI.

---

## 🎯 What gets tracked

Every link in every LinkedIn post body and first comment carries:

```
?utm_source=linkedin
&utm_medium=social
&utm_campaign=blog_launch       # blog_weekly after launch week
&utm_content=post_XX_<slug>      # unique per post
```

GA4 (`G-BRQ8Q6W8N8`) automatically segments these. No setup required.

---

## 📊 Where to look (3 dashboards)

### 1️⃣ GA4 — Real-time traffic from LinkedIn

**URL:** https://analytics.google.com → KU Automation property

**Path:** Reports → Acquisition → **Traffic acquisition**

**Filter:**
- Session source = `linkedin`
- Or Session source / medium = `linkedin / social`

**You'll see:**
- Sessions per LinkedIn post
- Engagement rate per post
- Average engagement time
- Conversions (form fills, signups, downloads)
- Per-post breakdown via `utm_content` dimension

**To split by post:**
- Add secondary dimension → "Session campaign" (shows blog_launch / blog_weekly)
- Add secondary dimension → "Session manual term" (NOTE: GA4 surfaces `utm_content` as "Session manual ad content")

### 2️⃣ LinkedIn Company Page Analytics

**URL:** https://www.linkedin.com/company/ku-automation/admin/analytics/

**You'll see:**
- Impressions per post
- Unique impressions
- Reactions / comments / shares
- Click-through rate
- Follower growth
- Demographics (job titles, companies, locations)

### 3️⃣ ClickUp — Logged engagement per post

**URL:** https://app.clickup.com/90182415479/v/li/901819004786 (LinkedIn Posts list)

Three tasks pre-created. After each post, update the task with:
- 24h impressions / 24h clicks
- 72h impressions / 72h clicks
- 7-day final metrics
- Best comment / DM received (for testimonial use later)

---

## 🚦 Daily / weekly cadence

### Day 1 (post day)
- **+2h:** Log impressions + reactions → ClickUp task
- **+6h:** Reply to every comment
- **+24h:** Update task with 24h numbers

### Day 3
- Check GA4 for utm_content match → log click-through
- Reply to any late comments

### Day 7
- Final metrics in ClickUp
- Compare with target (see below)

---

## 🎯 Per-post targets

| Metric | OK | Good | Great | Viral |
|---|---|---|---|---|
| Impressions | <500 | 500-2k | 2k-10k | 10k+ |
| Clicks (UTM) | <10 | 10-30 | 30-100 | 100+ |
| Comments | <3 | 3-10 | 10-30 | 30+ |
| Portal signups | 0 | 1 | 3+ | 10+ |

**Decision rule:**
- If a post hits "Great" → re-share with different angle in 14 days
- If a post hits "Viral" → run a paid boost ($50 sponsored content)
- If a post stays at "OK" → kill that angle, try a different hook style

---

## 🔁 30-day rollup

End of every month, run this exec to get a clean summary:

```bash
cd ~/.openclaw/workspace && python3 projects/ai-automation-agency/linkedin/launch-kit/scripts/monthly-rollup.py
```

(Script generated separately — pulls GA4 + ClickUp + LinkedIn manual numbers into one markdown report.)

---

## 💡 What success looks like

**Month 1 (launch + 4 weekly posts = 7 posts):**
- 7 posts published
- 5,000+ total impressions
- 100+ clicks to blog (utm_source=linkedin)
- 5+ portal signups attributed to LinkedIn
- 1+ inbound DM about custom workflow

**Month 3 (compounding):**
- 12 posts on the Company Page (1 per week steady state)
- 500+ company page followers (vs ~0 today)
- 1,000+ blog clicks from LinkedIn over 90 days
- 20+ portal signups, 3-5 conversions
- 1-2 closed custom workflow projects ($2k-$25k range)

This is realistic for engineering-niche B2B with quality content + consistent posting + active personal-profile amplification.
