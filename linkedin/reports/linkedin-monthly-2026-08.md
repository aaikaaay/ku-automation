# LinkedIn Blog Distribution — 2026-08 Rollup

_Generated 2026-09-01 09:00 Asia/Dubai_

---

## 📊 Top-line

- **Posts published:** 5
- **LinkedIn sessions to site (GA4):** manual entry needed
- **GA4 conversions from LinkedIn:** manual entry needed
- **Portal signups (total this month):** 1
- **Portal signups attributed to LinkedIn (UTM):** 0

---

## 📝 Posts published this month

| Post | Status | Tags |
|---|---|---|
| LinkedIn: P&ID Diagram AI Extraction: From Drawing to Data in Minutes | to do |  |
| LinkedIn: Why Engineering Companies Lose Bids (And How AI Fixes It) | to do |  |
| LinkedIn: Agentic AI for Engineering | to do |  |
| LinkedIn: From Manual Datasheet Reviews to AI Analysis | to do |  |
| LinkedIn: Stop Vendor Document Chaos | to do |  |

---

## 🎯 GA4 (not connected yet)

To enable live GA4 numbers:
1. In Google Cloud Console → create service account → download JSON key
2. In GA4 admin → Account access management → grant Viewer to the service account email
3. Set env vars in `~/.zshrc`:
   ```bash
   export GA4_PROPERTY_ID="<your_property_id>"
   export GA4_SERVICE_ACCOUNT="$HOME/.openclaw/secrets/ga4-sa.json"
   ```
4. `pip install google-analytics-data`
5. Re-run this script.

**Until then,** pull these numbers manually from analytics.google.com:
- Reports → Acquisition → Traffic acquisition → filter `Session source = linkedin`
- Note total sessions, engaged sessions, and conversions for the month
- Log them in `state.json` under `posts.<post_id>.ga4_sessions` etc.

---

## 💼 Portal signup attribution

- 0 of 1 signups attributed to LinkedIn = **0%**
- ⚠️ Portal users table does not yet capture `utm_source` — attribution is undercounted until that field is added.

---

## 🚦 Verdict

📊 **Baseline established.** Compare to next month.

---

_Raw data: 5 ClickUp tasks, 0 GA4 rows, portal db OK._
