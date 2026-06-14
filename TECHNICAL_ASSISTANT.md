# Technical Assistant — KU Automation

AI admin dashboard for engineering consultants.  
**URL:** `https://www.ku-automation.com/technical-assistant`  
**File:** `technical-assistant.html`  
**Backend:** `backend/app.py` (deployed on Railway)

---

## Feature Status

### ✅ LIVE — Phase 1

| Tab | Feature | Endpoints |
|-----|---------|-----------|
| 1 | **Expenses Tracker** | `POST /api/expenses/extract`, `POST /api/expenses/export-excel`, `POST /api/expenses/export-pdf` |
| 2 | **Invoice Generator** | `POST /api/invoice/export-excel`, `POST /api/invoice/export-pdf` |

### 🔜 Coming — July / August / September 2026

| Tab | Feature | ETA |
|-----|---------|-----|
| 3 | Timesheet Generator | July 2026 |
| 4 | Meeting Minutes (transcript/audio → structured) | July 2026 |
| 5 | Technical Memo (AI-drafted engineering memo) | July 2026 |
| 6 | Daily Progress Report (site DPR) | August 2026 |
| 7 | Document Transmittal register | August 2026 |
| 8 | Standards Lookup (ASME/API/ISO clause search) | September 2026 |
| 9 | MTO / BoQ Cleanup (normalise messy Excel MTOs) | September 2026 |

---

## API Endpoint Reference

All endpoints served from `https://ku-automation-production.up.railway.app`.

### `POST /api/expenses/extract`
**Type:** `multipart/form-data`  
**Field:** `files` (one or many: PDF, JPG, PNG, WebP)

**Flow:**
1. Each file is vision-analysed by `gpt-4o` with a structured extraction prompt
2. Returns rows with ISO date, ISO currency code, source amount, category
3. Each row is enriched with `fx_rate` (USD-base, 24h cached from open.er-api.com) and `usd_amount`

**Response:**
```json
{
  "rows": [
    {
      "date": "2026-05-10",
      "description": "Car hire Amsterdam",
      "currency": "EUR",
      "source_amount": 64.38,
      "category": "Transport",
      "vendor": "Hertz",
      "notes": null,
      "fx_rate": 1.0856,
      "usd_amount": 69.85,
      "id": "1234567890.0"
    }
  ],
  "fx_rates": { "EUR": 1.0856, "GBP": 1.2671, ... }
}
```

---

### `POST /api/expenses/export-excel`
**Type:** `application/json`

**Body:**
```json
{
  "metadata": {
    "name": "Alex Mercer",
    "employee_id": "AM-001",
    "period": "2026-05",
    "purpose": "Site Visit — Northwind Pilot, Houston",
    "date_prepared": "01/06/2026"
  },
  "rows": [
    {
      "date": "2026-05-03",
      "description": "Uber to DXB Airport",
      "currency": "AED",
      "source_amount": 220.00,
      "fx_rate": 0.2723,
      "usd_amount": 59.91,
      "category": "Transport"
    }
  ]
}
```

**Response:** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`  
**Filename:** `Expenses_{Name}_{Period}.xlsx`

**Layout (consultant expense template):**
- Title: "Expense Summary" (blue header)
- Header block: Date Prepared, Name, Employee ID, Period Covered, Purpose
- Summary panel: "Expenses at a glance" — Flights & Hotels / Transport / Meals / Other / Total
- Main table: Date | Description | Currency | Source Amount | FX | Amount USD | Flights & Hotels | Transport | Meals | Other | Total USD
- Subtotals row (light blue background)
- Approver block: Name / Position / Signature

---

### `POST /api/expenses/export-pdf`
Same JSON body as export-excel.  
**Response:** `application/pdf`  
**Filename:** `Expenses_{Name}_{Period}.pdf`  
**Layout:** Mirrors the Excel — ReportLab A4 with same header, summary, and table structure.

---

### `POST /api/invoice/export-excel`
**Type:** `application/json`

**Body:**
```json
{
  "consultant": {
    "name": "Mr A. Mercer",
    "address": "Suite 1402, Marina Heights\nJBR, Dubai, UAE",
    "email": "alex.mercer@example.com",
    "phone": "+971 50 123 4567",
    "bank": {
      "account_holder": "Alex Mercer",
      "bank_name": "Emirates NBD",
      "iban": "AE07 0331 2345 6789 0123 456",
      "account_number": "0123 456 789 012",
      "swift": "EBILAEAD",
      "bank_address": "Emirates NBD Head Office, P.O. Box 777, Dubai, UAE"
    }
  },
  "invoice": {
    "invoice_no": "INV-2026-0142",
    "date": "2026-05-31",
    "client_name": "Northwind Energy Corp",
    "client_address": "2200 Energy Plaza\nHouston, TX 77002, USA",
    "reference": "Services provided per Consultancy Agreement dated 12 January 2026 — Phase 2 Process Engineering"
  },
  "line_items": [
    { "description": "Professional consultancy services", "units": 18.0, "daily_rate": 980.0, "total": 17640.0 }
  ],
  "reimbursables": [
    { "description": "Uber to DXB Airport AED 220.00", "units": 1.0, "daily_rate": 59.91, "total": 59.91 }
  ],
  "payment_terms": "Payment to be made within 30 days of receipt of invoice"
}
```

**Response:** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`  
**Filename:** `Invoice_{InvoiceNo}_{ClientName}.xlsx`

**Layout (consultant invoice template):**
- Title: "INVOICE" (large, centered)
- Consultant header block (top-left) + Invoice No/Date box (top-right, light blue)
- "Invoice to" + client address (bordered boxes)
- Reference line
- Line items table: Description | Units | Daily Rate (USD) | Total (USD)
- Travel expenses section header + reimbursable rows
- Grand Total row (blue)
- Signature line
- Payment terms + full banking footer (7-row bordered table)

---

### `POST /api/invoice/export-pdf`
Same JSON body as export-excel.  
**Response:** `application/pdf`  
**Filename:** `Invoice_{InvoiceNo}_{ClientName}.pdf`

---

## LocalStorage Keys

| Key | Contents | Where used |
|-----|---------|-----------|
| `ku_ta_expenses_draft` | `{ rows: [...], meta: { name, employee_id, period, purpose } }` | Expenses tab — auto-save on every edit |
| `ku_ta_invoice_draft` | `{ line_items, reimbursables, invoice: {...} }` | Invoice tab — auto-save on every edit |
| `ku_ta_consultant_profile` | `{ name, address, email, phone, bank: {...} }` | Consultant profile section — persists across sessions |

Draft data survives page refresh. Cleared only by the user via DevTools or browser storage clear.

---

## Railway Deploy Steps

After Kings triggers deploy, these are the only changes since last deploy:

**Files modified:**
- `backend/app.py` — added 5 new endpoints + helper functions (starts after the existing `if __name__` block)
- `backend/requirements.txt` — added `reportlab>=4.0.0` and `requests>=2.31.0`

**Files created:**
- `technical-assistant.html` — new demo page (Vercel auto-deploys from root HTML files)
- `TECHNICAL_ASSISTANT.md` — this file
- `backend/test_technical_assistant.py` — smoke tests

**Deploy command (Railway):**
```bash
# Railway auto-detects requirements.txt and pip-installs on build
# No new environment variables needed — uses existing MYKEY_XYZ123 / KU_OPENAI_SECRET / OPENAI_API_KEY
# Just push to the connected GitHub branch:
git add backend/app.py backend/requirements.txt technical-assistant.html demos.html TECHNICAL_ASSISTANT.md backend/test_technical_assistant.py
git commit -m "feat: Technical Assistant — expenses & invoice endpoints + demo page"
git push
```

Railway will:
1. Detect `requirements.txt` changes → install `reportlab` and `requests`
2. Restart the FastAPI process
3. New endpoints available within ~60s of push

**Vercel** auto-deploys `technical-assistant.html` + `demos.html` changes from the same push (if the repo root is the Vercel project root).

**No new environment variables required.**  
FX rates fetched from `open.er-api.com` (free, no key) with 24h in-process cache.

---

## Known Limitations

### Phase 1 (Live)

| Limitation | Detail |
|-----------|--------|
| FX rates are cached 24h | May be slightly stale; user can override in the table |
| PDF font is Helvetica (built-in) | No custom fonts; acceptable for consulting use |
| Receipt extraction may miss handwritten receipts | `gpt-4o` best-effort; manual row add available |
| No auth / quota limiting on endpoints | Railway free tier — add API key auth before scaling |
| Draft only stored client-side | No cloud backup of form data between devices |

### Coming Soon Tabs — What Each Needs to Ship

| Feature | Engineering Required | Rough Estimate |
|---------|---------------------|----------------|
| **Timesheet** | HTML form + daily-row table, export to XLSX matching a template | 8h |
| **Meeting Minutes** | Whisper API for audio, GPT-4o structuring prompt, Word export via `python-docx` | 12h |
| **Technical Memo** | Guided form → GPT-4o structured draft → Word export | 8h |
| **Daily Report** | Form + photo upload, PDF export with images via reportlab | 12h |
| **Transmittal** | Table entry form, sequential ref numbers, Excel export | 6h |
| **Standards Lookup** | RAG over ASME/API PDFs or GPT-4o with document context | 20h |
| **MTO / BoQ Cleanup** | openpyxl upload parsing + GPT-4o normalisation + export | 16h |

All use $0-cost AI (existing OpenAI key) — costs are engineering hours only.

---

## Visual Design Notes

- **Brand palette:** Primary indigo (#4f46e5) for tab bar, amber→rose gradient accent for Technical Assistant branding
- **Tab bar:** Pill-style, active tab = solid primary with shadow, inactive = gray text hover
- **Soon panels:** Intentionally polished — amber "Available [month]" badge, 3 bullet points, "Get early access" Calendly CTA
- **Fonts:** Inter (Google Fonts) — consistent with all other demo pages
- **Responsive:** Split panel (upload+table) on lg screens, stacked on mobile; invoice form+preview stacked on xl
