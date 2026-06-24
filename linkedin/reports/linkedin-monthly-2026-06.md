# LinkedIn Blog Distribution — 2026-06 Rollup

_Generated 2026-06-24 18:53 Asia/Dubai_

---

## 📊 Top-line

- **Posts published:** 3
- **LinkedIn sessions to site (GA4):** manual entry needed
- **GA4 conversions from LinkedIn:** manual entry needed
- **Portal signups (total this month):** 2
- **Portal signups attributed to LinkedIn (UTM):** 0

---

## 📝 Posts published this month

| Post | Status | Tags |
|---|---|---|
| LinkedIn Launch 3: 4 Hours to 4 Minutes (Doc Review) | to do | blog, launch, linkedin |
| LinkedIn Launch 2: Process Safety AI (PSV/HAZOP) | to do | blog, launch, linkedin |
| LinkedIn Launch 1: Two-Pass AI Engineering Reviews | to do | blog, launch, linkedin |

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

- 0 of 2 signups attributed to LinkedIn = **0%**
- ⚠️ Portal users table does not yet capture `utm_source` — attribution is undercounted until that field is added.

---

## 🚦 Verdict

📊 **Baseline established.** Compare to next month.

---

_Raw data: 3 ClickUp tasks, 0 GA4 rows, portal db OK._
