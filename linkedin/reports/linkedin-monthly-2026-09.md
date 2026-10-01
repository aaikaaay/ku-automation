# LinkedIn Blog Distribution — 2026-09 Rollup

_Generated 2026-10-01 09:00 Asia/Dubai_

---

## 📊 Top-line

- **Posts published:** 0
- **LinkedIn sessions to site (GA4):** manual entry needed
- **GA4 conversions from LinkedIn:** manual entry needed
- **Portal signups (total this month):** 0
- **Portal signups attributed to LinkedIn (UTM):** 0

---

## 📝 Posts published this month

_No posts found in ClickUp for this period._
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

- No portal signups this month.

---

## 🚦 Verdict

⚠️ **Cadence dropped.** Less than 2 posts this month. Reschedule if needed.

---

_Raw data: 0 ClickUp tasks, 0 GA4 rows, portal db OK._
