"""
P&ID Parser Demo - KU Automation
Extracts equipment, valves, and line data from P&ID diagrams using AI
"""

import os
import json
import base64
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="P&ID Parser - KU Automation")

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check if static folder exists before mounting
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Extraction prompt for P&ID analysis
PID_EXTRACTION_PROMPT = """You are an expert P&ID (Piping and Instrumentation Diagram) analyzer with deep knowledge of oil & gas, chemical, and process engineering.

Analyze this P&ID image and extract ALL of the following information. Be thorough and precise.

## Extract These Categories:

### 1. EQUIPMENT
For each piece of equipment found, extract:
- Tag (e.g., V-101, P-102, E-201)
- Type (e.g., Vessel, Pump, Heat Exchanger, Compressor, Tank, Reactor)
- Description/Name if visible
- Size/Capacity if shown

### 2. VALVES
For each valve found, extract:
- Tag (e.g., XV-101, PV-102, HV-201)
- Type (e.g., Gate, Globe, Ball, Check, Control, Relief, Butterfly)
- Size if shown (e.g., 2", 4", 6")
- Line Number it's on (if identifiable)

### 3. INSTRUMENTS
For each instrument found, extract:
- Tag (e.g., PT-101, FT-102, LT-201, TT-301)
- Type (e.g., Pressure, Flow, Level, Temperature)
- Function (Transmitter, Indicator, Controller, Alarm)

### 4. LINES/PIPING
For each line found, extract:
- Line Number (e.g., 4"-P-101, 6"-CW-201)
- Size (diameter)
- Service/Fluid (if shown)
- From (source equipment)
- To (destination equipment)

### 5. NOTES
- Any important notes, specifications, or design conditions visible

Return your analysis as a JSON object with this exact structure:
{
  "equipment": [
    {"tag": "...", "type": "...", "description": "...", "size": "..."}
  ],
  "valves": [
    {"tag": "...", "type": "...", "size": "...", "line_number": "..."}
  ],
  "instruments": [
    {"tag": "...", "type": "...", "function": "..."}
  ],
  "lines": [
    {"line_number": "...", "size": "...", "service": "...", "from": "...", "to": "..."}
  ],
  "notes": ["...", "..."],
  "summary": "Brief description of what this P&ID shows"
}

If you cannot identify certain fields, use "N/A" or leave empty. 
Be conservative - only extract what you can clearly see.
Return ONLY the JSON, no other text."""


def get_anthropic_client():
    """Lazy initialization of Anthropic client"""
    from anthropic import Anthropic
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    print(f"[APP] Initializing Anthropic client. API Key present: {bool(api_key)}")
    if not api_key:
        print("[APP ERROR] ANTHROPIC_API_KEY is missing!")
        raise HTTPException(500, "ANTHROPIC_API_KEY not configured")
    try:
        client = Anthropic(api_key=api_key)
        print("[APP] Anthropic client initialized successfully.")
        return client
    except Exception as e:
        print(f"[APP ERROR] Failed to initialize Anthropic client: {e}")
        raise HTTPException(500, f"Failed to initialize Anthropic client: {e}")


def encode_image_to_base64(file_content: bytes) -> str:
    """Convert image bytes to base64 string"""
    return base64.b64encode(file_content).decode('utf-8')


def convert_pdf_to_images(pdf_bytes: bytes) -> list[bytes]:
    """Convert PDF pages to PNG images using PyMuPDF"""
    import fitz  # PyMuPDF
    
    images = []
    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    for page_num in range(len(pdf_doc)):
        page = pdf_doc[page_num]
        # Render at 2x resolution for better quality
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        images.append(pix.tobytes("png"))
        print(f"[APP] Converted PDF page {page_num + 1}/{len(pdf_doc)} to image")
    
    pdf_doc.close()
    return images


def analyze_pid_with_vision(image_base64: str, content_type: str = "image/png") -> dict:
    """Send image to Claude Vision API for P&ID analysis"""
    client = get_anthropic_client()
    
    # Determine media type (only images - PDFs should be converted first)
    if "png" in content_type:
        media_type = "image/png"
    elif "webp" in content_type:
        media_type = "image/webp"
    else:
        media_type = "image/jpeg"
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": PID_EXTRACTION_PROMPT
                    }
                ]
            }
        ]
    )
    
    # Parse the JSON response
    content = response.content[0].text
    print(f"[APP] Raw AI response length: {len(content) if content else 0} chars")
    
    if not content or not content.strip():
        print("[APP ERROR] Empty response from AI")
        raise ValueError("Empty response from AI")
    
    # Clean up response - extract JSON from various formats
    content = content.strip()
    
    # Remove markdown code blocks if present
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        parts = content.split("```")
        # Find the part that looks like JSON
        for part in parts:
            part = part.strip()
            if part.startswith("{") or part.startswith("["):
                content = part
                break
    
    # Try to find JSON object if there's text before/after
    content = content.strip()
    if not content.startswith("{") and "{" in content:
        content = content[content.index("{"):]
    if not content.endswith("}") and "}" in content:
        content = content[:content.rindex("}") + 1]
    
    print(f"[APP] Cleaned content preview: {content[:200]}...")
    
    return json.loads(content)


def create_excel_report(data: dict, filename: str) -> str:
    """Generate Excel report from extracted P&ID data"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    
    wb = Workbook()
    
    # Styles
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    def style_header(ws, row=1):
        for cell in ws[row]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
            cell.border = border
    
    def style_data(ws, start_row=2):
        for row in ws.iter_rows(min_row=start_row):
            for cell in row:
                cell.border = border
                cell.alignment = Alignment(horizontal='left')
    
    # === EQUIPMENT Sheet ===
    ws_equip = wb.active
    ws_equip.title = "Equipment"
    ws_equip.append(["Tag", "Type", "Description", "Size/Capacity"])
    for item in data.get("equipment", []):
        ws_equip.append([
            item.get("tag", ""),
            item.get("type", ""),
            item.get("description", ""),
            item.get("size", "")
        ])
    style_header(ws_equip)
    style_data(ws_equip)
    for col in ['A', 'B', 'C', 'D']:
        ws_equip.column_dimensions[col].width = 20
    
    # === VALVES Sheet ===
    ws_valves = wb.create_sheet("Valves")
    ws_valves.append(["Tag", "Type", "Size", "Line Number"])
    for item in data.get("valves", []):
        ws_valves.append([
            item.get("tag", ""),
            item.get("type", ""),
            item.get("size", ""),
            item.get("line_number", "")
        ])
    style_header(ws_valves)
    style_data(ws_valves)
    for col in ['A', 'B', 'C', 'D']:
        ws_valves.column_dimensions[col].width = 18
    
    # === INSTRUMENTS Sheet ===
    ws_inst = wb.create_sheet("Instruments")
    ws_inst.append(["Tag", "Type", "Function"])
    for item in data.get("instruments", []):
        ws_inst.append([
            item.get("tag", ""),
            item.get("type", ""),
            item.get("function", "")
        ])
    style_header(ws_inst)
    style_data(ws_inst)
    for col in ['A', 'B', 'C']:
        ws_inst.column_dimensions[col].width = 20
    
    # === LINES Sheet ===
    ws_lines = wb.create_sheet("Lines")
    ws_lines.append(["Line Number", "Size", "Service", "From", "To"])
    for item in data.get("lines", []):
        ws_lines.append([
            item.get("line_number", ""),
            item.get("size", ""),
            item.get("service", ""),
            item.get("from", ""),
            item.get("to", "")
        ])
    style_header(ws_lines)
    style_data(ws_lines)
    for col in ['A', 'B', 'C', 'D', 'E']:
        ws_lines.column_dimensions[col].width = 18
    
    # === SUMMARY Sheet ===
    ws_summary = wb.create_sheet("Summary")
    ws_summary.append(["P&ID Analysis Summary"])
    ws_summary['A1'].font = Font(bold=True, size=14)
    ws_summary.append([])
    ws_summary.append(["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    ws_summary.append(["Source File:", filename])
    ws_summary.append([])
    ws_summary.append(["Description:", data.get("summary", "N/A")])
    ws_summary.append([])
    ws_summary.append(["Item Counts:"])
    ws_summary.append(["  Equipment:", len(data.get("equipment", []))])
    ws_summary.append(["  Valves:", len(data.get("valves", []))])
    ws_summary.append(["  Instruments:", len(data.get("instruments", []))])
    ws_summary.append(["  Lines:", len(data.get("lines", []))])
    ws_summary.append([])
    ws_summary.append(["Notes:"])
    for note in data.get("notes", []):
        ws_summary.append(["  -", note])
    
    ws_summary.column_dimensions['A'].width = 15
    ws_summary.column_dimensions['B'].width = 60
    
    # Save to temp file
    output_path = tempfile.mktemp(suffix=".xlsx")
    wb.save(output_path)
    
    return output_path


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main page"""
    print("[APP] Attempting to serve static/index.html...")
    static_index = Path(__file__).parent / "static" / "index.html"
    if static_index.exists():
        print(f"[APP] Serving: {static_index}")
        return FileResponse(str(static_index))
    print("[APP] static/index.html not found. Serving default HTML.")
    return HTMLResponse("<h1>P&ID Parser API</h1><p>Use POST /api/analyze to analyze P&IDs</p>")


@app.get("/health")
async def health():
    """Health check endpoint"""
    print("[APP] Health check requested.")
    return {"status": "healthy", "service": "P&ID Parser"}


@app.post("/api/analyze")
async def analyze_pid(file: UploadFile = File(...)):
    """Analyze uploaded P&ID and return extracted data"""
    
    print(f"[APP] /api/analyze called for file: {file.filename} (Type: {file.content_type})")
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "application/pdf"]
    if file.content_type not in allowed_types:
        print(f"[APP ERROR] Invalid file type: {file.content_type}")
        raise HTTPException(400, f"Invalid file type. Allowed: {', '.join(allowed_types)}")
    
    # Read file
    content = await file.read()
    print(f"[APP] File read, size: {len(content)} bytes.")
    
    # Check file size (max 20MB)
    if len(content) > 20 * 1024 * 1024:
        print("[APP ERROR] File too large.")
        raise HTTPException(400, "File too large. Maximum size is 20MB.")
    
    # Handle PDF files - convert to images first
    if file.content_type == "application/pdf":
        print("[APP] PDF detected, converting to images...")
        try:
            page_images = convert_pdf_to_images(content)
            print(f"[APP] Converted PDF to {len(page_images)} page(s)")
            # Use first page for analysis (P&IDs are usually single page)
            content = page_images[0]
            content_type = "image/png"
        except Exception as e:
            print(f"[APP ERROR] PDF conversion failed: {e}")
            raise HTTPException(500, f"Failed to convert PDF: {str(e)}")
    else:
        content_type = file.content_type
    
    # Encode to base64
    image_base64 = encode_image_to_base64(content)
    print("[APP] Image encoded to base64.")
    
    try:
        # Analyze with Vision API
        print("[APP] Calling OpenAI Vision API...")
        extracted_data = analyze_pid_with_vision(image_base64, content_type)
        print("[APP] OpenAI Vision API call complete.")
        
        # Generate Excel report
        excel_path = create_excel_report(extracted_data, file.filename)
        print("[APP] Generated Excel report.")
        
        # Read Excel file for response
        with open(excel_path, "rb") as f:
            excel_base64 = base64.b64encode(f.read()).decode('utf-8')
        print("[APP] Excel file read to base64.")
        
        # Clean up temp file
        os.unlink(excel_path)
        print(f"[APP] Cleaned up temporary Excel file: {excel_path}")
        
        return {
            "success": True,
            "data": extracted_data,
            "excel": excel_base64,
            "filename": f"PID_Extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(500, f"Failed to parse AI response: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")


if __name__ == "__main__":
    print("[APP] Running app directly with uvicorn.")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
