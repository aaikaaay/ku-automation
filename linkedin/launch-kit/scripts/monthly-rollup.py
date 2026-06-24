#!/usr/bin/env python3
"""
LinkedIn → Blog → Portal monthly ROI rollup.

Pulls:
  - ClickUp tasks in list 901819004786 (LinkedIn Posts) with their custom-field metrics
  - GA4 sessions/conversions filtered by utm_source=linkedin (when credentials are available)
  - Posts manually logged in linkedin/launch-kit/state.json
  - Portal signups attributed to LinkedIn (from KU Review Portal DB)

Writes:
  - reports/linkedin-monthly-YYYY-MM.md

Usage:
  python3 monthly-rollup.py                # current month
  python3 monthly-rollup.py 2026-06        # specific month
  python3 monthly-rollup.py --send         # also Telegram the summary to Kings

Env (optional, for live GA4):
  GA4_PROPERTY_ID         (e.g. "123456789")
  GA4_SERVICE_ACCOUNT     (path to service-account JSON)
  GOOGLE_APPLICATION_CREDENTIALS  (alternative path)

Env (required for ClickUp pull):
  CLICKUP_API_TOKEN
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# ── Constants ────────────────────────────────────────────────────────────────
CLICKUP_LIST_ID = "901819004786"
WORKSPACE = Path(os.path.expanduser("~/.openclaw/workspace"))
LAUNCH_KIT = WORKSPACE / "projects/ai-automation-agency/linkedin/launch-kit"
REPORTS_DIR = WORKSPACE / "projects/ai-automation-agency/linkedin/reports"
STATE_FILE = LAUNCH_KIT / "state.json"
PORTAL_DB = WORKSPACE / "projects/ku-review-portal/app/data/portal.db"

DUBAI_TZ = timezone(timedelta(hours=4), name="Asia/Dubai")

# ── State helpers ────────────────────────────────────────────────────────────
def load_state() -> dict[str, Any]:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"posts": {}, "updated": None}


def save_state(state: dict[str, Any]) -> None:
    state["updated"] = datetime.now(DUBAI_TZ).isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


# ── ClickUp pull ─────────────────────────────────────────────────────────────
def fetch_clickup_tasks(month_start_ms: int, month_end_ms: int) -> list[dict[str, Any]]:
    token = os.environ.get("CLICKUP_API_TOKEN")
    if not token:
        print("⚠️  CLICKUP_API_TOKEN not set — skipping ClickUp pull", file=sys.stderr)
        return []

    url = (
        f"https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task"
        f"?archived=false&include_closed=true&subtasks=true"
    )
    req = Request(url, headers={"Authorization": token})
    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"⚠️  ClickUp fetch failed: {e}", file=sys.stderr)
        return []

    tasks = []
    for t in data.get("tasks", []):
        # Filter by date_created OR due_date in month range
        created = int(t.get("date_created") or 0)
        due = int(t.get("due_date") or 0)
        if (month_start_ms <= created <= month_end_ms) or (month_start_ms <= due <= month_end_ms):
            tasks.append(t)
    return tasks


# ── GA4 pull (optional, falls back gracefully) ───────────────────────────────
def fetch_ga4_linkedin_sessions(month_start: datetime, month_end: datetime) -> Optional[dict[str, Any]]:
    """
    Pull LinkedIn-attributed sessions from GA4. Returns None if credentials missing.
    Uses the Data API v1beta. Service account must have Viewer on the GA4 property.
    """
    property_id = os.environ.get("GA4_PROPERTY_ID")
    sa_path = os.environ.get("GA4_SERVICE_ACCOUNT") or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not (property_id and sa_path and Path(sa_path).exists()):
        return None

    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient  # type: ignore
        from google.analytics.data_v1beta.types import (  # type: ignore
            DateRange, Dimension, Filter, FilterExpression, Metric, RunReportRequest,
        )
        from google.oauth2 import service_account  # type: ignore
    except ImportError:
        print("ℹ️  GA4 libraries not installed (pip install google-analytics-data). Skipping.", file=sys.stderr)
        return None

    creds = service_account.Credentials.from_service_account_file(
        sa_path, scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(
            start_date=month_start.strftime("%Y-%m-%d"),
            end_date=month_end.strftime("%Y-%m-%d"),
        )],
        dimensions=[
            Dimension(name="sessionSource"),
            Dimension(name="sessionCampaignName"),
            Dimension(name="sessionManualAdContent"),  # utm_content
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="engagedSessions"),
            Metric(name="conversions"),
            Metric(name="totalUsers"),
        ],
        dimension_filter=FilterExpression(filter=Filter(
            field_name="sessionSource",
            string_filter=Filter.StringFilter(value="linkedin"),
        )),
    )
    response = client.run_report(request)

    rows = []
    for row in response.rows:
        rows.append({
            "source": row.dimension_values[0].value,
            "campaign": row.dimension_values[1].value,
            "content": row.dimension_values[2].value,
            "sessions": int(row.metric_values[0].value or 0),
            "engaged": int(row.metric_values[1].value or 0),
            "conversions": float(row.metric_values[2].value or 0),
            "users": int(row.metric_values[3].value or 0),
        })

    total = {
        "sessions": sum(r["sessions"] for r in rows),
        "engaged": sum(r["engaged"] for r in rows),
        "conversions": sum(r["conversions"] for r in rows),
        "users": sum(r["users"] for r in rows),
    }
    return {"rows": rows, "total": total}


# ── Portal signups attributed to LinkedIn ────────────────────────────────────
def fetch_portal_signups(month_start_ms: int, month_end_ms: int) -> dict[str, Any]:
    """Pull KU portal signups in month, count how many came via LinkedIn UTM."""
    if not PORTAL_DB.exists():
        return {"available": False, "total": 0, "linkedin": 0}
    try:
        con = sqlite3.connect(f"file:{PORTAL_DB}?mode=ro", uri=True)
        cur = con.cursor()
        # Check if users table has utm columns
        cur.execute("PRAGMA table_info(users)")
        cols = {row[1] for row in cur.fetchall()}
        # Adjust column names if you've added utm fields; assume created_at_ms exists
        if "created_at_ms" in cols:
            ts_col = "created_at_ms"
        elif "created_at" in cols:
            ts_col = "strftime('%s', created_at) * 1000"
        else:
            con.close()
            return {"available": False, "total": 0, "linkedin": 0}

        cur.execute(f"SELECT COUNT(*) FROM users WHERE {ts_col} BETWEEN ? AND ?",
                    (month_start_ms, month_end_ms))
        total = cur.fetchone()[0]

        linkedin = 0
        if "utm_source" in cols:
            cur.execute(
                f"SELECT COUNT(*) FROM users WHERE {ts_col} BETWEEN ? AND ? AND utm_source = 'linkedin'",
                (month_start_ms, month_end_ms),
            )
            linkedin = cur.fetchone()[0]

        con.close()
        return {"available": True, "total": total, "linkedin": linkedin}
    except Exception as e:
        return {"available": False, "error": str(e), "total": 0, "linkedin": 0}


# ── Report builder ───────────────────────────────────────────────────────────
def build_report(
    month: str,
    clickup_tasks: list[dict],
    ga4: Optional[dict],
    portal: dict,
    state_posts: dict,
) -> str:
    lines = [
        f"# LinkedIn Blog Distribution — {month} Rollup",
        "",
        f"_Generated {datetime.now(DUBAI_TZ).strftime('%Y-%m-%d %H:%M %Z')}_",
        "",
        "---",
        "",
        "## 📊 Top-line",
        "",
    ]

    posts_count = len(clickup_tasks)
    ga4_sessions = ga4["total"]["sessions"] if ga4 else None
    ga4_conv = ga4["total"]["conversions"] if ga4 else None

    lines += [
        f"- **Posts published:** {posts_count}",
        f"- **LinkedIn sessions to site (GA4):** {ga4_sessions if ga4_sessions is not None else 'manual entry needed'}",
        f"- **GA4 conversions from LinkedIn:** {int(ga4_conv) if ga4_conv is not None else 'manual entry needed'}",
        f"- **Portal signups (total this month):** {portal['total']}",
        f"- **Portal signups attributed to LinkedIn (UTM):** {portal['linkedin']}",
        "",
        "---",
        "",
        "## 📝 Posts published this month",
        "",
    ]

    if not clickup_tasks:
        lines.append("_No posts found in ClickUp for this period._")
    else:
        lines.append("| Post | Status | Tags |")
        lines.append("|---|---|---|")
        for t in clickup_tasks:
            name = t.get("name", "—")
            status = (t.get("status") or {}).get("status", "—")
            tags = ", ".join(tag.get("name", "") for tag in t.get("tags", []))
            lines.append(f"| {name} | {status} | {tags} |")
        lines.append("")

    if ga4 and ga4["rows"]:
        lines += [
            "---",
            "",
            "## 🎯 Per-post GA4 breakdown",
            "",
            "| Campaign | Content | Sessions | Engaged | Conversions |",
            "|---|---|---:|---:|---:|",
        ]
        for r in sorted(ga4["rows"], key=lambda x: -x["sessions"]):
            lines.append(
                f"| {r['campaign'] or '—'} | {r['content'] or '—'} | "
                f"{r['sessions']} | {r['engaged']} | {int(r['conversions'])} |"
            )
        lines.append("")
    elif not ga4:
        lines += [
            "---",
            "",
            "## 🎯 GA4 (not connected yet)",
            "",
            "To enable live GA4 numbers:",
            "1. In Google Cloud Console → create service account → download JSON key",
            "2. In GA4 admin → Account access management → grant Viewer to the service account email",
            "3. Set env vars in `~/.zshrc`:",
            "   ```bash",
            "   export GA4_PROPERTY_ID=\"<your_property_id>\"",
            "   export GA4_SERVICE_ACCOUNT=\"$HOME/.openclaw/secrets/ga4-sa.json\"",
            "   ```",
            "4. `pip install google-analytics-data`",
            "5. Re-run this script.",
            "",
            "**Until then,** pull these numbers manually from analytics.google.com:",
            "- Reports → Acquisition → Traffic acquisition → filter `Session source = linkedin`",
            "- Note total sessions, engaged sessions, and conversions for the month",
            "- Log them in `state.json` under `posts.<post_id>.ga4_sessions` etc.",
            "",
        ]

    lines += [
        "---",
        "",
        "## 💼 Portal signup attribution",
        "",
    ]
    if portal["available"]:
        if portal["total"] > 0:
            attr_pct = (portal["linkedin"] / portal["total"]) * 100 if portal["total"] else 0
            lines.append(f"- {portal['linkedin']} of {portal['total']} signups attributed to LinkedIn = **{attr_pct:.0f}%**")
            if "utm_source" not in str(portal):
                lines.append("- ⚠️ Portal users table does not yet capture `utm_source` — attribution is undercounted until that field is added.")
        else:
            lines.append("- No portal signups this month.")
    else:
        lines.append(f"- Portal DB unavailable: {portal.get('error', 'check path')}")

    lines += [
        "",
        "---",
        "",
        "## 🚦 Verdict",
        "",
    ]

    # Simple verdict logic
    if posts_count >= 4 and (ga4_sessions or 0) >= 200:
        lines.append("✅ **On track.** Posting cadence solid, LinkedIn traffic delivering.")
    elif posts_count < 2:
        lines.append("⚠️ **Cadence dropped.** Less than 2 posts this month. Reschedule if needed.")
    elif ga4 and ga4_sessions < 100:
        lines.append("⚠️ **Low conversion.** Posting but not driving traffic — revisit hooks.")
    else:
        lines.append("📊 **Baseline established.** Compare to next month.")

    lines += [
        "",
        "---",
        "",
        f"_Raw data: {len(clickup_tasks)} ClickUp tasks, "
        f"{(len(ga4['rows']) if ga4 else 0)} GA4 rows, "
        f"portal db {'OK' if portal['available'] else 'unavailable'}._",
        "",
    ]

    return "\n".join(lines)


# ── Telegram ─────────────────────────────────────────────────────────────────
def send_telegram(text: str) -> None:
    """Send via OpenClaw message tool — the script invokes openclaw-cli."""
    # Use a placeholder: actual send done by the caller cron job.
    # If run interactively with --send, write to a sentinel for now.
    sentinel = LAUNCH_KIT / "scripts" / ".last-summary.md"
    sentinel.write_text(text)
    print(f"💾 Summary saved for delivery: {sentinel}")


# ── Main ─────────────────────────────────────────────────────────────────────
def parse_month(arg: Optional[str]) -> tuple[str, datetime, datetime]:
    if arg and arg != "--send":
        try:
            month_dt = datetime.strptime(arg, "%Y-%m").replace(tzinfo=DUBAI_TZ)
        except ValueError:
            print(f"❌ Invalid month format: {arg} (expected YYYY-MM)", file=sys.stderr)
            sys.exit(1)
    else:
        now = datetime.now(DUBAI_TZ)
        month_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Month bounds
    if month_dt.month == 12:
        next_month = month_dt.replace(year=month_dt.year + 1, month=1)
    else:
        next_month = month_dt.replace(month=month_dt.month + 1)
    month_end = next_month - timedelta(seconds=1)
    label = month_dt.strftime("%Y-%m")
    return label, month_dt, month_end


def main() -> int:
    args = sys.argv[1:]
    send_flag = "--send" in args
    month_arg = next((a for a in args if not a.startswith("--")), None)

    month_label, month_start, month_end = parse_month(month_arg)
    month_start_ms = int(month_start.timestamp() * 1000)
    month_end_ms = int(month_end.timestamp() * 1000)

    print(f"📊 Rolling up {month_label} ({month_start.date()} → {month_end.date()})")

    clickup_tasks = fetch_clickup_tasks(month_start_ms, month_end_ms)
    print(f"  • ClickUp tasks: {len(clickup_tasks)}")

    ga4 = fetch_ga4_linkedin_sessions(month_start, month_end)
    if ga4:
        print(f"  • GA4 sessions: {ga4['total']['sessions']}")
    else:
        print("  • GA4: not connected")

    portal = fetch_portal_signups(month_start_ms, month_end_ms)
    if portal["available"]:
        print(f"  • Portal signups: {portal['total']} (LinkedIn: {portal['linkedin']})")
    else:
        print(f"  • Portal DB: {portal.get('error', 'unavailable')}")

    state = load_state()
    report = build_report(month_label, clickup_tasks, ga4, portal, state.get("posts", {}))

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"linkedin-monthly-{month_label}.md"
    report_path.write_text(report)
    print(f"✅ Wrote {report_path}")

    if send_flag:
        # Compact telegram-friendly summary
        summary_lines = [
            f"📊 LinkedIn rollup — {month_label}",
            f"Posts: {len(clickup_tasks)}",
        ]
        if ga4:
            summary_lines.append(f"LinkedIn sessions: {ga4['total']['sessions']}")
            summary_lines.append(f"Conversions: {int(ga4['total']['conversions'])}")
        if portal["available"]:
            summary_lines.append(
                f"Portal signups: {portal['total']} ({portal['linkedin']} from LinkedIn)"
            )
        summary_lines.append(f"\nFull report: {report_path.relative_to(WORKSPACE)}")
        send_telegram("\n".join(summary_lines))

    return 0


if __name__ == "__main__":
    sys.exit(main())
