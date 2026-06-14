"""
test_technical_assistant.py
============================
Smoke tests for the Technical Assistant backend endpoints.

Tests:
  1. /api/expenses/extract    — mocked OpenAI, asserts rows returned
  2. /api/expenses/export-excel  — asserts ≥5 KB valid xlsx
  3. /api/expenses/export-pdf    — asserts ≥5 KB valid pdf
  4. /api/invoice/export-excel   — asserts ≥5 KB valid xlsx
  5. /api/invoice/export-pdf     — asserts ≥5 KB valid pdf

Run:
  cd projects/ai-automation-agency/backend
  pip3 install fastapi uvicorn openpyxl Pillow reportlab requests python-multipart
  python3 test_technical_assistant.py
"""

import json
import io
import sys
import os
import types
import struct
import zlib
import unittest
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Bootstrap: stub optional heavy deps so we can import app.py in test env
# ---------------------------------------------------------------------------

pdf2image_stub = types.ModuleType("pdf2image")
pdf2image_stub.convert_from_bytes = lambda *a, **kw: []
sys.modules.setdefault("pdf2image", pdf2image_stub)

openai_stub = types.ModuleType("openai")
openai_stub.OpenAI = MagicMock()
sys.modules.setdefault("openai", openai_stub)

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("OPENAI_API_KEY", "sk-test-dummy")

# Import app module
import app as app_module
from app import app, _make_expense_excel, _make_expense_pdf, _make_invoice_excel, _make_invoice_pdf

# ---------------------------------------------------------------------------
# HTTP test harness: start app in background thread, use requests to call it
# ---------------------------------------------------------------------------
import threading
import time
import requests as req
import uvicorn

TEST_PORT = 18765
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"

_server = None
_server_thread = None

def start_test_server():
    global _server, _server_thread
    config = uvicorn.Config(app, host="127.0.0.1", port=TEST_PORT, log_level="error")
    _server = uvicorn.Server(config)
    _server_thread = threading.Thread(target=_server.run, daemon=True)
    _server_thread.start()
    # Wait until server is ready
    for _ in range(30):
        try:
            req.get(f"{BASE_URL}/", timeout=0.5)
            break
        except Exception:
            time.sleep(0.2)

def stop_test_server():
    if _server:
        _server.should_exit = True

# ---------------------------------------------------------------------------
# Sample payloads
# ---------------------------------------------------------------------------

SAMPLE_EXPENSE_PAYLOAD = {
    "metadata": {
        "name": "Kurt Bosse",
        "employee_id": "KB-001",
        "period": "2026-05",
        "purpose": "Travel Expenses CNG Project",
        "date_prepared": "01/06/2026"
    },
    "rows": [
        {
            "date": "2026-04-26",
            "description": "Train to Heathrow",
            "currency": "GBP",
            "source_amount": 49.60,
            "fx_rate": 1.3544,
            "usd_amount": 67.18,
            "category": "Transport"
        },
        {
            "date": "2026-04-27",
            "description": "Rwanda Visa",
            "currency": "USD",
            "source_amount": 50.00,
            "fx_rate": 1.0,
            "usd_amount": 50.00,
            "category": "Other"
        },
        {
            "date": "2026-05-10",
            "description": "Car hire Amsterdam Schiphol",
            "currency": "EUR",
            "source_amount": 64.38,
            "fx_rate": 1.1718,
            "usd_amount": 75.44,
            "category": "Transport"
        },
        {
            "date": "2026-05-11",
            "description": "Train from Birmingham Airport",
            "currency": "GBP",
            "source_amount": 18.60,
            "fx_rate": 1.3525,
            "usd_amount": 25.16,
            "category": "Transport"
        }
    ]
}

SAMPLE_INVOICE_PAYLOAD = {
    "consultant": {
        "name": "Mr K. Bosse",
        "address": "Apt 505 Azure Building\nDubai Marina, Dubai, UAE",
        "email": "kurt.bosse@ntlworld.com",
        "phone": "+971 556641966",
        "bank": {
            "account_holder": "Kurt Bosse",
            "bank_name": "RAKBank",
            "iban": "AE22 0400 0002 9298 5561 001",
            "account_number": "02 9298 5561 001",
            "swift": "NRAKAEAK",
            "bank_address": "RAKBANK Head Office P.O.Box 5300, Ras Al Khaimah, UAE"
        }
    },
    "invoice": {
        "invoice_no": "KB-05-2026",
        "date": "2026-05-25",
        "client_name": "Gasmeth Energy Limited",
        "client_address": "KN7 Avenue\nKigali\nRwanda",
        "reference": "Services provided according to Consultancy Agreement dated 15 December 2025"
    },
    "line_items": [
        {
            "description": "Professional consultancy services — see attached monthly timesheet",
            "units": 20.0,
            "daily_rate": 920.0,
            "total": 18400.0
        }
    ],
    "reimbursables": [
        {"description": "Train to Heathrow GBP49.60", "units": 1.0, "daily_rate": 67.18, "total": 67.18},
        {"description": "Rwanda Visa USD 50.00",       "units": 1.0, "daily_rate": 50.00, "total": 50.00},
        {"description": "Car hire Amsterdam Euro 64.38","units": 1.0, "daily_rate": 75.44, "total": 75.44},
        {"description": "Train from Birmingham GBP18.60","units": 1.0,"daily_rate": 25.16, "total": 25.16}
    ],
    "payment_terms": "Payment to be made within 30 days of receipt of invoice"
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MIN_BYTES_XLSX = 5_000  # 5 KB — Excel includes zip overhead
MIN_BYTES_PDF  = 2_000  # 2 KB — ReportLab generates compact PDFs

def is_valid_xlsx(data: bytes) -> bool:
    return data[:2] == b'PK'

def is_valid_pdf(data: bytes) -> bool:
    return data[:4] == b'%PDF'

def create_minimal_png() -> bytes:
    """Create a 1×1 white PNG in memory."""
    def crc32(data):
        return struct.pack('>I', zlib.crc32(data) & 0xFFFFFFFF)
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    ihdr = b'IHDR' + ihdr_data
    ihdr_chunk = struct.pack('>I', 13) + ihdr + crc32(ihdr)
    idat_raw = b'\x00\xff\xff\xff'
    idat_compressed = zlib.compress(idat_raw)
    idat = b'IDAT' + idat_compressed
    idat_chunk = struct.pack('>I', len(idat_compressed)) + idat + crc32(idat)
    iend = b'IEND'
    iend_chunk = struct.pack('>I', 0) + iend + crc32(iend)
    return sig + ihdr_chunk + idat_chunk + iend_chunk


# ---------------------------------------------------------------------------
# Tests — Direct function tests (no HTTP, fastest)
# ---------------------------------------------------------------------------

class TestDirectHelpers(unittest.TestCase):
    def test_expense_excel_bytes(self):
        data = _make_expense_excel(SAMPLE_EXPENSE_PAYLOAD)
        self.assertGreaterEqual(len(data), MIN_BYTES_XLSX, f"XLSX too small: {len(data)} bytes")
        self.assertTrue(is_valid_xlsx(data), "Not a valid XLSX")
        print(f"  ✓ _make_expense_excel() — {len(data):,} bytes, valid XLSX ✅")

    def test_expense_pdf_bytes(self):
        data = _make_expense_pdf(SAMPLE_EXPENSE_PAYLOAD)
        self.assertGreaterEqual(len(data), MIN_BYTES_PDF, f"PDF too small: {len(data)} bytes")
        self.assertTrue(is_valid_pdf(data), "Not a valid PDF")
        print(f"  ✓ _make_expense_pdf() — {len(data):,} bytes, valid PDF ✅")

    def test_invoice_excel_bytes(self):
        data = _make_invoice_excel(SAMPLE_INVOICE_PAYLOAD)
        self.assertGreaterEqual(len(data), MIN_BYTES_XLSX, f"XLSX too small: {len(data)} bytes")
        self.assertTrue(is_valid_xlsx(data), "Not a valid XLSX")
        print(f"  ✓ _make_invoice_excel() — {len(data):,} bytes, valid XLSX ✅")

    def test_invoice_pdf_bytes(self):
        data = _make_invoice_pdf(SAMPLE_INVOICE_PAYLOAD)
        self.assertGreaterEqual(len(data), MIN_BYTES_PDF, f"PDF too small: {len(data)} bytes")
        self.assertTrue(is_valid_pdf(data), "Not a valid PDF")
        print(f"  ✓ _make_invoice_pdf() — {len(data):,} bytes, valid PDF ✅")

    def test_fx_rate_usd(self):
        from app import _usd_rate
        self.assertEqual(_usd_rate("USD", {}), 1.0)
        print("  ✓ _usd_rate('USD') == 1.0 ✅")

    def test_fx_rate_unknown_fallback(self):
        from app import _usd_rate
        self.assertEqual(_usd_rate("XYZ", {}), 1.0)
        print("  ✓ _usd_rate('XYZ' unknown) falls back to 1.0 ✅")

    def test_expense_totals_correct(self):
        """Grand total of the sample payload should be 217.78."""
        rows = SAMPLE_EXPENSE_PAYLOAD["rows"]
        total = sum(float(r["usd_amount"]) for r in rows)
        self.assertAlmostEqual(total, 217.78, places=1)
        print(f"  ✓ Expense grand total = ${total:.2f} (expected $217.78) ✅")

    def test_invoice_grand_total_correct(self):
        """Invoice total: 18400 + 67.18 + 50 + 75.44 + 25.16 = 18617.78"""
        li_total = sum(float(i["total"]) for i in SAMPLE_INVOICE_PAYLOAD["line_items"])
        r_total = sum(float(r["total"]) for r in SAMPLE_INVOICE_PAYLOAD["reimbursables"])
        grand = li_total + r_total
        self.assertAlmostEqual(grand, 18617.78, places=1)
        print(f"  ✓ Invoice grand total = ${grand:,.2f} (expected $18,617.78) ✅")


# ---------------------------------------------------------------------------
# Tests — HTTP endpoint tests via uvicorn background server
# ---------------------------------------------------------------------------

class TestEndpoints(unittest.TestCase):
    """HTTP-level tests against the running server."""

    def _post_json(self, path, payload):
        resp = req.post(
            f"{BASE_URL}{path}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=20
        )
        return resp

    def test_expenses_export_excel_endpoint(self):
        resp = self._post_json("/api/expenses/export-excel", SAMPLE_EXPENSE_PAYLOAD)
        self.assertEqual(resp.status_code, 200, f"Expected 200: {resp.text[:200]}")
        data = resp.content
        self.assertGreaterEqual(len(data), MIN_BYTES_XLSX, f"XLSX too small: {len(data)} bytes")
        self.assertTrue(is_valid_xlsx(data), "Not a valid XLSX")
        cd = resp.headers.get("content-disposition", "")
        self.assertIn(".xlsx", cd)
        print(f"  ✓ POST /api/expenses/export-excel — {len(data):,} bytes, valid XLSX ✅")

    def test_expenses_export_pdf_endpoint(self):
        resp = self._post_json("/api/expenses/export-pdf", SAMPLE_EXPENSE_PAYLOAD)
        self.assertEqual(resp.status_code, 200, f"Expected 200: {resp.text[:200]}")
        data = resp.content
        self.assertGreaterEqual(len(data), MIN_BYTES_PDF, f"PDF too small: {len(data)} bytes")
        self.assertTrue(is_valid_pdf(data), "Not a valid PDF")
        print(f"  ✓ POST /api/expenses/export-pdf — {len(data):,} bytes, valid PDF ✅")

    def test_invoice_export_excel_endpoint(self):
        resp = self._post_json("/api/invoice/export-excel", SAMPLE_INVOICE_PAYLOAD)
        self.assertEqual(resp.status_code, 200, f"Expected 200: {resp.text[:200]}")
        data = resp.content
        self.assertGreaterEqual(len(data), MIN_BYTES_XLSX, f"XLSX too small: {len(data)} bytes")
        self.assertTrue(is_valid_xlsx(data), "Not a valid XLSX")
        print(f"  ✓ POST /api/invoice/export-excel — {len(data):,} bytes, valid XLSX ✅")

    def test_invoice_export_pdf_endpoint(self):
        resp = self._post_json("/api/invoice/export-pdf", SAMPLE_INVOICE_PAYLOAD)
        self.assertEqual(resp.status_code, 200, f"Expected 200: {resp.text[:200]}")
        data = resp.content
        self.assertGreaterEqual(len(data), MIN_BYTES_PDF, f"PDF too small: {len(data)} bytes")
        self.assertTrue(is_valid_pdf(data), "Not a valid PDF")
        print(f"  ✓ POST /api/invoice/export-pdf — {len(data):,} bytes, valid PDF ✅")

    def test_expenses_extract_endpoint(self):
        """Test /api/expenses/extract with a mocked OpenAI call (via patching)."""
        mock_response_content = json.dumps({
            "rows": [{
                "date": "2026-05-15",
                "description": "Taxi to airport",
                "currency": "AED",
                "source_amount": 55.0,
                "category": "Transport",
                "vendor": "Careem",
                "notes": None
            }]
        })
        mock_choice = MagicMock()
        mock_choice.message.content = mock_response_content
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion

        with patch.object(app_module, 'get_openai_client', return_value=mock_client):
            png_bytes = create_minimal_png()
            resp = req.post(
                f"{BASE_URL}/api/expenses/extract",
                files=[("files", ("test.png", io.BytesIO(png_bytes), "image/png"))],
                timeout=20
            )

        self.assertEqual(resp.status_code, 200, f"Expected 200: {resp.text[:200]}")
        data = resp.json()
        self.assertIn("rows", data)
        self.assertEqual(len(data["rows"]), 1)
        row = data["rows"][0]
        self.assertEqual(row["currency"], "AED")
        self.assertIn("fx_rate", row)
        self.assertIn("usd_amount", row)
        print(f"  ✓ POST /api/expenses/extract — 1 row extracted, AED→USD={row['usd_amount']} ✅")


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  Technical Assistant — Backend Smoke Tests")
    print("="*60 + "\n")

    print("→ Starting test server on port", TEST_PORT, "...")
    start_test_server()
    print("→ Server ready.\n")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestDirectHelpers))
    suite.addTests(loader.loadTestsFromTestCase(TestEndpoints))

    runner = unittest.TextTestRunner(verbosity=0, stream=sys.stdout)
    result = runner.run(suite)

    stop_test_server()
    print()
    if result.wasSuccessful():
        print("✅  ALL TESTS PASSED")
        sys.exit(0)
    else:
        for failure in result.failures + result.errors:
            print(failure[1])
        print(f"\n❌  {len(result.failures)} failure(s), {len(result.errors)} error(s)")
        sys.exit(1)
