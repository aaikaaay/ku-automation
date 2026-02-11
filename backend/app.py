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
PID_EXTRACTION_PROMPT = """You are an expert P&ID (Piping and Instrumentation Diagram) analyzer specializing in oil & gas, petrochemical, and process engineering drawings.

CRITICAL: Examine the image VERY CAREFULLY. Look at ALL text labels, tag numbers, and annotations. P&IDs contain dense information - zoom in mentally on each section.

## LINE NUMBER FORMAT
Oil & Gas line numbers typically follow formats like:
- "4"-OC-41-012-N1A1" (Size-Service-Area-Sequence-Spec)
- "6"-HC-40-001" (Size-Service-Unit-Number)
- "3"-PG-2001" (Size-Service-Number)
The FIRST number before the dash is usually the pipe SIZE in inches.

## Extract These Categories:

### 1. EQUIPMENT
For each piece of equipment (vessels, pumps, exchangers, coalescers, separators, etc.):
- Tag: The alphanumeric identifier (e.g., 40-V-2005, P-101, E-201)
- Type: Equipment type (Vessel, Pump, Heat Exchanger, Coalescer, Separator, Compressor)
- Description: Full name if shown in title block or callout
- Size: Capacity, diameter, or rating if visible

### 2. VALVES  
For EVERY valve symbol found (gate, globe, ball, check, control, butterfly, relief):
- Tag: Full valve tag number (e.g., XV-40-20051, HV-101, PV-2001)
- Type: Valve type based on symbol (Gate, Globe, Ball, Check, Control, Relief, Butterfly)
- Size: Pipe size the valve is on - look at adjacent line number or valve callout
- Line Number: The line number the valve is installed on - trace the pipe to find it

### 3. INSTRUMENTS
For every instrument bubble/tag (PT, LT, FT, TT, PI, LI, etc.):
- Tag: COMPLETE instrument tag including all digits (e.g., PT-41-20271-010CNS-H)
- Type: Measurement type (Pressure, Level, Flow, Temperature)
- Function: Device function (Transmitter, Indicator, Controller, Switch, Alarm)

### 4. LINES/PIPING
For EACH distinct pipe line shown:
- Line Number: FULL line designation exactly as written (e.g., "4"-OC-41-012-N1A1")
- Size: Pipe diameter (extract from line number or annotation)
- Service: Fluid service code (OC=Crude Oil, HC=Hydrocarbon, CW=Cooling Water, etc.)
- From: Source equipment or boundary
- To: Destination equipment or boundary

### 5. NOTES
- Design conditions, operating parameters, or special requirements visible

IMPORTANT: Do NOT put "N/A" if the information exists but is hard to read - make your best attempt to read it. Only use "N/A" if truly not shown.

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

# Datasheet extraction prompt
DATASHEET_EXTRACTION_PROMPT = """You are an expert engineering document analyzer specializing in equipment datasheets for oil & gas, petrochemical, and process industries.

CRITICAL: Examine the datasheet VERY CAREFULLY. Extract ALL technical specifications, operating parameters, and equipment details visible.

## Extract These Categories:

### 1. GENERAL INFORMATION
- Manufacturer: Company name
- Model: Model number/name
- Tag Number: Equipment tag if shown (e.g., P-101, V-2001)
- Serial Number: If visible
- Equipment Type: Pump, Valve, Vessel, Instrument, Heat Exchanger, etc.
- Service/Application: What the equipment is used for

### 2. OPERATING CONDITIONS
- Design Pressure: Maximum design pressure with units
- Operating Pressure: Normal operating pressure with units
- Design Temperature: Maximum design temperature with units
- Operating Temperature: Normal operating temperature with units
- Flow Rate: Capacity/flow with units
- Fluid/Medium: What fluid it handles

### 3. PHYSICAL SPECIFICATIONS
- Size/Dimensions: Overall dimensions, connection sizes
- Weight: Dry/wet weight
- Materials: Body material, trim, internals, seals
- Connections: Flange ratings, sizes, types

### 4. PERFORMANCE DATA
- Efficiency: If applicable
- Power Requirements: HP, kW, voltage
- Speed/RPM: Rotational speed
- Head/Differential Pressure: For pumps
- Cv/Kv: For valves

### 5. CERTIFICATIONS & STANDARDS
- Design Code: ASME, API, etc.
- Certifications: ATEX, CE, PED, etc.
- Material Certificates: MTR requirements

### 6. ADDITIONAL INFORMATION
- Accessories: Included items
- Spare Parts: Recommended spares
- Notes: Special requirements, installation notes

Return your analysis as a JSON object with this exact structure:
{
  "general": {
    "manufacturer": "...",
    "model": "...",
    "tag_number": "...",
    "serial_number": "...",
    "equipment_type": "...",
    "service": "..."
  },
  "operating_conditions": {
    "design_pressure": "...",
    "operating_pressure": "...",
    "design_temperature": "...",
    "operating_temperature": "...",
    "flow_rate": "...",
    "fluid_medium": "..."
  },
  "physical": {
    "dimensions": "...",
    "weight": "...",
    "materials": "...",
    "connections": "..."
  },
  "performance": {
    "power": "...",
    "speed": "...",
    "efficiency": "...",
    "head_dp": "...",
    "cv_kv": "..."
  },
  "certifications": {
    "design_code": "...",
    "certifications": "...",
    "material_certs": "..."
  },
  "additional": {
    "accessories": "...",
    "spare_parts": "...",
    "notes": "..."
  },
  "all_specs": [
    {"parameter": "...", "value": "...", "unit": "..."}
  ],
  "summary": "Brief description of this equipment"
}

The "all_specs" array should contain EVERY specification you can find, even if not categorized above.
If you cannot identify certain fields, use "N/A" or leave empty.
Return ONLY the JSON, no other text."""


# Legend extraction prompt
LEGEND_EXTRACTION_PROMPT = """You are analyzing a P&ID (Piping and Instrumentation Diagram) LEGEND or SYMBOL SHEET.

Extract and summarize ALL the symbol definitions, abbreviations, and conventions shown. This includes:

1. **EQUIPMENT SYMBOLS**: What shapes/icons represent vessels, pumps, exchangers, etc.
2. **VALVE SYMBOLS**: Gate, globe, ball, check, control, relief valve symbols
3. **INSTRUMENT SYMBOLS**: Circles, bubbles, and their letter codes (PT=Pressure Transmitter, etc.)
4. **LINE TYPES**: Solid, dashed, thick, thin lines and what they represent
5. **ABBREVIATIONS**: All abbreviation definitions (e.g., OC=Oil Crude, CW=Cooling Water)
6. **SERVICE CODES**: Fluid/service type codes and their meanings
7. **SPEC BREAKS**: Specification change symbols
8. **ANY OTHER SYMBOLS**: Control signals, electrical, pneumatic, etc.

Return a comprehensive JSON summary:
{
  "equipment_symbols": [{"symbol": "description", "icon_description": "what it looks like"}],
  "valve_symbols": [{"type": "valve type", "symbol_description": "how to identify it"}],
  "instrument_codes": [{"code": "XX", "meaning": "description"}],
  "line_types": [{"type": "description", "appearance": "solid/dashed/etc"}],
  "abbreviations": {"CODE": "Full meaning"},
  "service_codes": {"CODE": "Fluid/service type"},
  "other_symbols": [{"symbol": "description"}],
  "notes": ["any important notes or conventions"]
}

Be thorough - this legend will be used to interpret the actual P&ID drawings.
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


def analyze_legend(image_base64: str, media_type: str = "image/png") -> dict:
    """Analyze a P&ID legend/symbol sheet and extract symbol definitions"""
    client = get_anthropic_client()
    
    print("[APP] Analyzing legend/symbol sheet...")
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
                        "text": LEGEND_EXTRACTION_PROMPT
                    }
                ]
            }
        ]
    )
    
    content = response.content[0].text
    print(f"[APP] Legend analysis response length: {len(content) if content else 0} chars")
    
    # Parse JSON response
    content = content.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        parts = content.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("{"):
                content = part
                break
    
    content = content.strip()
    if not content.startswith("{") and "{" in content:
        content = content[content.index("{"):]
    if not content.endswith("}") and "}" in content:
        content = content[:content.rindex("}") + 1]
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("[APP] Could not parse legend JSON, returning raw text")
        return {"raw_legend": content}


def analyze_pid_with_vision(image_base64: str, content_type: str = "image/png", legend_context: dict = None) -> dict:
    """Send image to Claude Vision API for P&ID analysis"""
    client = get_anthropic_client()
    
    # Determine media type (only images - PDFs should be converted first)
    if "png" in content_type:
        media_type = "image/png"
    elif "webp" in content_type:
        media_type = "image/webp"
    else:
        media_type = "image/jpeg"
    
    # Build the prompt - include legend context if available
    prompt = PID_EXTRACTION_PROMPT
    if legend_context:
        legend_text = json.dumps(legend_context, indent=2)
        prompt = f"""IMPORTANT: Use this LEGEND/SYMBOL REFERENCE when analyzing the P&ID:

{legend_text}

Apply these symbol definitions, abbreviations, and conventions to interpret the drawing accurately.

---

{PID_EXTRACTION_PROMPT}"""
        print("[APP] Using legend context for enhanced analysis")
    
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
                        "text": prompt
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
    legend_context = None
    if file.content_type == "application/pdf":
        print("[APP] PDF detected, converting to images...")
        try:
            page_images = convert_pdf_to_images(content)
            num_pages = len(page_images)
            print(f"[APP] Converted PDF to {num_pages} page(s)")
            
            # Multi-page PDF: analyze first page as legend, use page 2+ for P&ID
            if num_pages > 1:
                print("[APP] Multi-page PDF detected - analyzing page 1 as legend...")
                legend_base64 = encode_image_to_base64(page_images[0])
                try:
                    legend_context = analyze_legend(legend_base64, "image/png")
                    print("[APP] Legend analysis complete")
                except Exception as e:
                    print(f"[APP WARNING] Legend analysis failed: {e} - continuing without legend")
                
                # Use page 2 for main P&ID analysis
                content = page_images[1]
                print(f"[APP] Using page 2 for P&ID analysis (with legend context)")
            else:
                # Single page - analyze directly
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
        print("[APP] Calling Claude Vision API...")
        extracted_data = analyze_pid_with_vision(image_base64, content_type, legend_context)
        print("[APP] Claude Vision API call complete.")
        
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


def analyze_datasheet_with_vision(image_base64: str, content_type: str = "image/png") -> dict:
    """Send datasheet image to Claude Vision API for analysis"""
    client = get_anthropic_client()
    
    # Determine media type
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
                        "text": DATASHEET_EXTRACTION_PROMPT
                    }
                ]
            }
        ]
    )
    
    content = response.content[0].text
    print(f"[APP] Datasheet analysis response length: {len(content) if content else 0} chars")
    
    if not content or not content.strip():
        raise ValueError("Empty response from AI")
    
    # Clean up response - extract JSON
    content = content.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        parts = content.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("{"):
                content = part
                break
    
    content = content.strip()
    if not content.startswith("{") and "{" in content:
        content = content[content.index("{"):]
    if not content.endswith("}") and "}" in content:
        content = content[:content.rindex("}") + 1]
    
    return json.loads(content)


def create_datasheet_excel_report(data: dict, filename: str) -> str:
    """Generate Excel report from extracted datasheet data"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    
    wb = Workbook()
    
    # Styles
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="059669", end_color="059669", fill_type="solid")
    section_font = Font(bold=True, size=12)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # === MAIN Sheet ===
    ws = wb.active
    ws.title = "Datasheet Extract"
    
    row = 1
    
    # General Information
    ws.cell(row=row, column=1, value="GENERAL INFORMATION").font = section_font
    row += 1
    general = data.get("general", {})
    for key, label in [("manufacturer", "Manufacturer"), ("model", "Model"), 
                       ("tag_number", "Tag Number"), ("serial_number", "Serial Number"),
                       ("equipment_type", "Equipment Type"), ("service", "Service/Application")]:
        ws.cell(row=row, column=1, value=label)
        ws.cell(row=row, column=2, value=general.get(key, "N/A"))
        row += 1
    row += 1
    
    # Operating Conditions
    ws.cell(row=row, column=1, value="OPERATING CONDITIONS").font = section_font
    row += 1
    operating = data.get("operating_conditions", {})
    for key, label in [("design_pressure", "Design Pressure"), ("operating_pressure", "Operating Pressure"),
                       ("design_temperature", "Design Temperature"), ("operating_temperature", "Operating Temperature"),
                       ("flow_rate", "Flow Rate"), ("fluid_medium", "Fluid/Medium")]:
        ws.cell(row=row, column=1, value=label)
        ws.cell(row=row, column=2, value=operating.get(key, "N/A"))
        row += 1
    row += 1
    
    # Physical Specifications
    ws.cell(row=row, column=1, value="PHYSICAL SPECIFICATIONS").font = section_font
    row += 1
    physical = data.get("physical", {})
    for key, label in [("dimensions", "Dimensions"), ("weight", "Weight"),
                       ("materials", "Materials"), ("connections", "Connections")]:
        ws.cell(row=row, column=1, value=label)
        ws.cell(row=row, column=2, value=physical.get(key, "N/A"))
        row += 1
    row += 1
    
    # Performance Data
    ws.cell(row=row, column=1, value="PERFORMANCE DATA").font = section_font
    row += 1
    perf = data.get("performance", {})
    for key, label in [("power", "Power Requirements"), ("speed", "Speed/RPM"),
                       ("efficiency", "Efficiency"), ("head_dp", "Head/DP"), ("cv_kv", "Cv/Kv")]:
        ws.cell(row=row, column=1, value=label)
        ws.cell(row=row, column=2, value=perf.get(key, "N/A"))
        row += 1
    row += 1
    
    # Certifications
    ws.cell(row=row, column=1, value="CERTIFICATIONS & STANDARDS").font = section_font
    row += 1
    certs = data.get("certifications", {})
    for key, label in [("design_code", "Design Code"), ("certifications", "Certifications"),
                       ("material_certs", "Material Certificates")]:
        ws.cell(row=row, column=1, value=label)
        ws.cell(row=row, column=2, value=certs.get(key, "N/A"))
        row += 1
    row += 1
    
    # Additional
    ws.cell(row=row, column=1, value="ADDITIONAL INFORMATION").font = section_font
    row += 1
    additional = data.get("additional", {})
    for key, label in [("accessories", "Accessories"), ("spare_parts", "Spare Parts"),
                       ("notes", "Notes")]:
        ws.cell(row=row, column=1, value=label)
        ws.cell(row=row, column=2, value=additional.get(key, "N/A"))
        row += 1
    
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 50
    
    # === ALL SPECS Sheet ===
    ws_specs = wb.create_sheet("All Specifications")
    ws_specs.append(["Parameter", "Value", "Unit"])
    ws_specs['A1'].font = header_font
    ws_specs['A1'].fill = header_fill
    ws_specs['B1'].font = header_font
    ws_specs['B1'].fill = header_fill
    ws_specs['C1'].font = header_font
    ws_specs['C1'].fill = header_fill
    
    for spec in data.get("all_specs", []):
        ws_specs.append([
            spec.get("parameter", ""),
            spec.get("value", ""),
            spec.get("unit", "")
        ])
    
    ws_specs.column_dimensions['A'].width = 30
    ws_specs.column_dimensions['B'].width = 30
    ws_specs.column_dimensions['C'].width = 15
    
    # Save to temp file
    output_path = tempfile.mktemp(suffix=".xlsx")
    wb.save(output_path)
    
    return output_path


@app.post("/api/parse-datasheet")
async def parse_datasheet(file: UploadFile = File(...)):
    """Analyze uploaded equipment datasheet and return extracted data"""
    
    print(f"[APP] /api/parse-datasheet called for file: {file.filename} (Type: {file.content_type})")
    
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
        raise HTTPException(400, "File too large. Maximum size is 20MB.")
    
    # Handle PDF files - convert to images first
    if file.content_type == "application/pdf":
        print("[APP] PDF detected, converting to images...")
        try:
            page_images = convert_pdf_to_images(content)
            print(f"[APP] Converted PDF to {len(page_images)} page(s)")
            # Use first page for datasheet analysis
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
        print("[APP] Calling Claude Vision API for datasheet analysis...")
        extracted_data = analyze_datasheet_with_vision(image_base64, content_type)
        print("[APP] Claude Vision API call complete.")
        
        # Generate Excel report
        excel_path = create_datasheet_excel_report(extracted_data, file.filename)
        print("[APP] Generated Excel report.")
        
        # Read Excel file for response
        with open(excel_path, "rb") as f:
            excel_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # Clean up temp file
        os.unlink(excel_path)
        
        return {
            "success": True,
            "data": extracted_data,
            "excel": excel_base64,
            "filename": f"Datasheet_Extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(500, f"Failed to parse AI response: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")


# RFQ/ITB Extraction Prompt
RFQ_EXTRACTION_PROMPT = """You are an expert procurement and tender document analyzer specializing in RFQs (Request for Quotation), ITBs (Invitation to Bid), and tender documents for oil & gas, EPC, and engineering industries.

CRITICAL: Examine the document VERY CAREFULLY. Extract ALL relevant commercial and technical requirements, deadlines, and scope items.

## Extract These Categories:

### 1. DOCUMENT OVERVIEW
- Document Type: RFQ, ITB, RFP, Tender, EOI, etc.
- Reference Number: Document/tender reference
- Issue Date: When the document was issued
- Issuing Company: The company requesting quotes
- Project Name: Project title or name
- Project Location: Where the work will be performed

### 2. KEY DATES & DEADLINES
- Submission Deadline: When quotes/bids are due (date AND time with timezone)
- Validity Period: How long quotes must remain valid
- Clarification Deadline: Last date to ask questions
- Site Visit Date: If applicable
- Award Date: Expected contract award date
- Delivery/Completion Date: When goods/services are needed

### 3. SCOPE OF WORK
Extract each distinct scope item/line item:
- Item Number: Line item reference
- Description: What is being requested
- Quantity: Amount needed with units
- Specifications: Technical requirements
- Delivery Location: Where to deliver

### 4. TECHNICAL REQUIREMENTS
- Standards: Required codes/standards (API, ASME, ISO, etc.)
- Certifications: Required certificates (ATEX, CE, etc.)
- Material Requirements: Specific material specs
- Testing Requirements: FAT, SAT, inspections
- Documentation: Required documents (MTRs, drawings, manuals)

### 5. COMMERCIAL TERMS
- Payment Terms: Payment conditions
- Incoterms: Delivery terms (FOB, CIF, DDP, etc.)
- Currency: Pricing currency
- Warranty: Warranty requirements
- Liquidated Damages: LD clauses if any
- Insurance: Insurance requirements
- Bond/Guarantee: Bid bond, performance guarantee requirements

### 6. SUBMISSION REQUIREMENTS
- Format: How to submit (email, portal, hardcopy)
- Required Documents: What to include in submission
- Pricing Format: How to structure pricing
- Contact Person: Who to send questions to (name, email, phone)

### 7. EVALUATION CRITERIA
- Selection Method: Lowest price, best value, etc.
- Weighted Criteria: If technical/commercial weights are specified
- Mandatory Requirements: Must-have qualifications

### 8. COMPLIANCE CHECKLIST
Generate a checklist of all requirements the bidder must comply with.

Return your analysis as a JSON object with this exact structure:
{
  "overview": {
    "document_type": "...",
    "reference_number": "...",
    "issue_date": "...",
    "issuing_company": "...",
    "project_name": "...",
    "project_location": "..."
  },
  "key_dates": {
    "submission_deadline": "...",
    "validity_period": "...",
    "clarification_deadline": "...",
    "site_visit": "...",
    "award_date": "...",
    "delivery_date": "..."
  },
  "scope_items": [
    {"item_no": "...", "description": "...", "quantity": "...", "specs": "...", "delivery_location": "..."}
  ],
  "technical_requirements": {
    "standards": ["..."],
    "certifications": ["..."],
    "materials": "...",
    "testing": "...",
    "documentation": ["..."]
  },
  "commercial_terms": {
    "payment_terms": "...",
    "incoterms": "...",
    "currency": "...",
    "warranty": "...",
    "liquidated_damages": "...",
    "insurance": "...",
    "bonds": "..."
  },
  "submission": {
    "format": "...",
    "required_docs": ["..."],
    "pricing_format": "...",
    "contact_name": "...",
    "contact_email": "...",
    "contact_phone": "..."
  },
  "evaluation": {
    "method": "...",
    "criteria": ["..."],
    "mandatory_requirements": ["..."]
  },
  "compliance_checklist": [
    {"requirement": "...", "category": "..."}
  ],
  "summary": "Brief summary of what this RFQ is requesting"
}

If you cannot identify certain fields, use "N/A" or leave empty.
Return ONLY the JSON, no other text."""


def analyze_rfq_with_vision(image_base64: str, content_type: str = "image/png") -> dict:
    """Send RFQ document image to Claude Vision API for analysis"""
    client = get_anthropic_client()
    
    # Determine media type
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
                        "text": RFQ_EXTRACTION_PROMPT
                    }
                ]
            }
        ]
    )
    
    content = response.content[0].text
    print(f"[APP] RFQ analysis response length: {len(content) if content else 0} chars")
    
    if not content or not content.strip():
        raise ValueError("Empty response from AI")
    
    # Clean up response - extract JSON
    content = content.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        parts = content.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("{"):
                content = part
                break
    
    content = content.strip()
    if not content.startswith("{") and "{" in content:
        content = content[content.index("{"):]
    if not content.endswith("}") and "}" in content:
        content = content[:content.rindex("}") + 1]
    
    return json.loads(content)


def analyze_rfq_multipage(page_images: list, content_type: str = "image/png") -> dict:
    """Analyze multi-page RFQ document by combining all pages"""
    client = get_anthropic_client()
    
    # Determine media type
    if "png" in content_type:
        media_type = "image/png"
    else:
        media_type = "image/jpeg"
    
    # Build content array with all page images
    content_array = []
    for i, page_bytes in enumerate(page_images):
        page_base64 = encode_image_to_base64(page_bytes)
        content_array.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": page_base64
            }
        })
        print(f"[APP] Added page {i+1} to RFQ analysis request")
    
    # Add the prompt at the end
    content_array.append({
        "type": "text",
        "text": f"This RFQ/tender document has {len(page_images)} pages. Analyze ALL pages together and extract the complete information.\n\n" + RFQ_EXTRACTION_PROMPT
    })
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        messages=[
            {
                "role": "user",
                "content": content_array
            }
        ]
    )
    
    content = response.content[0].text
    print(f"[APP] RFQ multi-page analysis response length: {len(content) if content else 0} chars")
    
    if not content or not content.strip():
        raise ValueError("Empty response from AI")
    
    # Clean up response - extract JSON
    content = content.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        parts = content.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("{"):
                content = part
                break
    
    content = content.strip()
    if not content.startswith("{") and "{" in content:
        content = content[content.index("{"):]
    if not content.endswith("}") and "}" in content:
        content = content[:content.rindex("}") + 1]
    
    return json.loads(content)


def create_rfq_excel_report(data: dict, filename: str) -> str:
    """Generate Excel report from extracted RFQ data"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    
    wb = Workbook()
    
    # Styles
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    section_font = Font(bold=True, size=12, color="1E40AF")
    date_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # === OVERVIEW Sheet ===
    ws = wb.active
    ws.title = "RFQ Overview"
    
    row = 1
    
    # Document Overview
    ws.cell(row=row, column=1, value="DOCUMENT OVERVIEW").font = section_font
    row += 1
    overview = data.get("overview", {})
    for key, label in [("document_type", "Document Type"), ("reference_number", "Reference Number"),
                       ("issue_date", "Issue Date"), ("issuing_company", "Issuing Company"),
                       ("project_name", "Project Name"), ("project_location", "Project Location")]:
        ws.cell(row=row, column=1, value=label)
        ws.cell(row=row, column=2, value=overview.get(key, "N/A"))
        row += 1
    row += 1
    
    # Key Dates
    ws.cell(row=row, column=1, value="KEY DATES & DEADLINES").font = section_font
    row += 1
    dates = data.get("key_dates", {})
    for key, label in [("submission_deadline", "⚠️ SUBMISSION DEADLINE"), ("validity_period", "Validity Period"),
                       ("clarification_deadline", "Clarification Deadline"), ("site_visit", "Site Visit"),
                       ("award_date", "Expected Award Date"), ("delivery_date", "Delivery/Completion Date")]:
        ws.cell(row=row, column=1, value=label)
        cell = ws.cell(row=row, column=2, value=dates.get(key, "N/A"))
        if "deadline" in key.lower():
            cell.fill = date_fill
        row += 1
    row += 1
    
    # Commercial Terms
    ws.cell(row=row, column=1, value="COMMERCIAL TERMS").font = section_font
    row += 1
    commercial = data.get("commercial_terms", {})
    for key, label in [("payment_terms", "Payment Terms"), ("incoterms", "Incoterms"),
                       ("currency", "Currency"), ("warranty", "Warranty"),
                       ("liquidated_damages", "Liquidated Damages"), ("insurance", "Insurance"),
                       ("bonds", "Bonds/Guarantees")]:
        ws.cell(row=row, column=1, value=label)
        ws.cell(row=row, column=2, value=commercial.get(key, "N/A"))
        row += 1
    row += 1
    
    # Submission Info
    ws.cell(row=row, column=1, value="SUBMISSION REQUIREMENTS").font = section_font
    row += 1
    submission = data.get("submission", {})
    ws.cell(row=row, column=1, value="Format")
    ws.cell(row=row, column=2, value=submission.get("format", "N/A"))
    row += 1
    ws.cell(row=row, column=1, value="Contact Name")
    ws.cell(row=row, column=2, value=submission.get("contact_name", "N/A"))
    row += 1
    ws.cell(row=row, column=1, value="Contact Email")
    ws.cell(row=row, column=2, value=submission.get("contact_email", "N/A"))
    row += 1
    ws.cell(row=row, column=1, value="Contact Phone")
    ws.cell(row=row, column=2, value=submission.get("contact_phone", "N/A"))
    row += 1
    
    # Summary
    row += 1
    ws.cell(row=row, column=1, value="SUMMARY").font = section_font
    row += 1
    ws.cell(row=row, column=1, value=data.get("summary", "N/A"))
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
    
    ws.column_dimensions['A'].width = 28
    ws.column_dimensions['B'].width = 55
    
    # === SCOPE ITEMS Sheet ===
    ws_scope = wb.create_sheet("Scope Items")
    ws_scope.append(["Item No", "Description", "Quantity", "Specifications", "Delivery Location"])
    for col in ['A', 'B', 'C', 'D', 'E']:
        ws_scope[f'{col}1'].font = header_font
        ws_scope[f'{col}1'].fill = header_fill
    
    for item in data.get("scope_items", []):
        ws_scope.append([
            item.get("item_no", ""),
            item.get("description", ""),
            item.get("quantity", ""),
            item.get("specs", ""),
            item.get("delivery_location", "")
        ])
    
    ws_scope.column_dimensions['A'].width = 12
    ws_scope.column_dimensions['B'].width = 45
    ws_scope.column_dimensions['C'].width = 15
    ws_scope.column_dimensions['D'].width = 35
    ws_scope.column_dimensions['E'].width = 25
    
    # === TECHNICAL REQUIREMENTS Sheet ===
    ws_tech = wb.create_sheet("Technical Requirements")
    row = 1
    
    tech = data.get("technical_requirements", {})
    
    ws_tech.cell(row=row, column=1, value="STANDARDS").font = section_font
    row += 1
    for std in tech.get("standards", []):
        ws_tech.cell(row=row, column=1, value="•")
        ws_tech.cell(row=row, column=2, value=std)
        row += 1
    row += 1
    
    ws_tech.cell(row=row, column=1, value="CERTIFICATIONS").font = section_font
    row += 1
    for cert in tech.get("certifications", []):
        ws_tech.cell(row=row, column=1, value="•")
        ws_tech.cell(row=row, column=2, value=cert)
        row += 1
    row += 1
    
    ws_tech.cell(row=row, column=1, value="MATERIALS").font = section_font
    row += 1
    ws_tech.cell(row=row, column=1, value=tech.get("materials", "N/A"))
    row += 2
    
    ws_tech.cell(row=row, column=1, value="TESTING REQUIREMENTS").font = section_font
    row += 1
    ws_tech.cell(row=row, column=1, value=tech.get("testing", "N/A"))
    row += 2
    
    ws_tech.cell(row=row, column=1, value="DOCUMENTATION REQUIRED").font = section_font
    row += 1
    for doc in tech.get("documentation", []):
        ws_tech.cell(row=row, column=1, value="•")
        ws_tech.cell(row=row, column=2, value=doc)
        row += 1
    
    ws_tech.column_dimensions['A'].width = 5
    ws_tech.column_dimensions['B'].width = 60
    
    # === COMPLIANCE CHECKLIST Sheet ===
    ws_check = wb.create_sheet("Compliance Checklist")
    ws_check.append(["✓", "Requirement", "Category"])
    for col in ['A', 'B', 'C']:
        ws_check[f'{col}1'].font = header_font
        ws_check[f'{col}1'].fill = header_fill
    
    for item in data.get("compliance_checklist", []):
        ws_check.append([
            "☐",
            item.get("requirement", ""),
            item.get("category", "")
        ])
    
    ws_check.column_dimensions['A'].width = 5
    ws_check.column_dimensions['B'].width = 60
    ws_check.column_dimensions['C'].width = 20
    
    # Save to temp file
    output_path = tempfile.mktemp(suffix=".xlsx")
    wb.save(output_path)
    
    return output_path


@app.post("/api/parse-rfq")
async def parse_rfq(file: UploadFile = File(...)):
    """Analyze uploaded RFQ/ITB document and return extracted data"""
    
    print(f"[APP] /api/parse-rfq called for file: {file.filename} (Type: {file.content_type})")
    
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
        raise HTTPException(400, "File too large. Maximum size is 20MB.")
    
    # Handle PDF files - for RFQs we want to analyze ALL pages
    if file.content_type == "application/pdf":
        print("[APP] PDF detected, converting to images...")
        try:
            page_images = convert_pdf_to_images(content)
            num_pages = len(page_images)
            print(f"[APP] Converted PDF to {num_pages} page(s)")
            
            # Limit to first 10 pages to avoid token limits
            if num_pages > 10:
                print(f"[APP] Limiting analysis to first 10 pages (document has {num_pages})")
                page_images = page_images[:10]
            
            # For multi-page PDFs, analyze all pages together
            if num_pages > 1:
                print(f"[APP] Analyzing {len(page_images)} pages together...")
                extracted_data = analyze_rfq_multipage(page_images, "image/png")
            else:
                # Single page
                image_base64 = encode_image_to_base64(page_images[0])
                extracted_data = analyze_rfq_with_vision(image_base64, "image/png")
                
        except Exception as e:
            print(f"[APP ERROR] PDF processing failed: {e}")
            raise HTTPException(500, f"Failed to process PDF: {str(e)}")
    else:
        # Single image
        image_base64 = encode_image_to_base64(content)
        print("[APP] Image encoded to base64.")
        extracted_data = analyze_rfq_with_vision(image_base64, file.content_type)
    
    try:
        print("[APP] RFQ analysis complete.")
        
        # Generate Excel report
        excel_path = create_rfq_excel_report(extracted_data, file.filename)
        print("[APP] Generated Excel report.")
        
        # Read Excel file for response
        with open(excel_path, "rb") as f:
            excel_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # Clean up temp file
        os.unlink(excel_path)
        
        return {
            "success": True,
            "data": extracted_data,
            "excel": excel_base64,
            "filename": f"RFQ_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(500, f"Failed to parse AI response: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")


if __name__ == "__main__":
    print("[APP] Running app directly with uvicorn.")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
