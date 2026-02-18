"""
P&ID Parser Demo - KU Automation
Extracts equipment, valves, and line data from P&ID diagrams using AI
Now with Cost Estimation feature!
"""

import os
import json
import base64
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from openai import OpenAI
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

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

# OpenAI client - initialized lazily
_client = None

def get_openai_client():
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(500, "OPENAI_API_KEY not configured")
        _client = OpenAI(api_key=api_key)
    return _client

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
- Type: Category (Vessel, Pump, Heat Exchanger, Coalescer, Filter, Tank, Compressor, etc.)
- Description: Any name or description shown
- Size: Capacity or dimensions if visible

### 2. VALVES
For each valve (gate, globe, ball, check, control, relief, butterfly, plug, needle):
- Tag: Identifier (e.g., XV-101, PV-102, HV-201, or line-based like "BV on 4"-HC-001")
- Type: Gate, Globe, Ball, Check, Control, Relief/PSV, Butterfly, Plug, Needle
- Size: Usually matches the line size (2", 4", 6", etc.)
- Line_Number: Which line it's installed on

### 3. INSTRUMENTS
For each instrument (transmitters, indicators, controllers, switches, analyzers):
- Tag: The ISA tag (e.g., PT-101, FIT-102, LT-201, TIC-301, PSV-001)
- Type: Pressure, Flow, Level, Temperature, Analyzer, etc.
- Function: Transmitter, Indicator, Controller, Switch, Alarm, Element

### 4. LINES/PIPING
For each process line visible:
- Line_Number: Full line designation (e.g., "4"-OC-41-012-N1A1")
- Size: Pipe diameter in inches (first number in line designation)
- Service: Fluid service code (OC=Oil Coalesced, HC=Hydrocarbon, PG=Process Gas, PW=Produced Water, etc.)
- From: Source equipment or off-page reference
- To: Destination equipment or off-page reference

### 5. NOTES
- Design conditions (pressure, temperature)
- Material specifications
- Operating notes
- Any visible text callouts

Return your analysis as a JSON object:
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
  "summary": "Brief description of what this P&ID shows (system/unit name, main function)"
}

IMPORTANT:
- Extract EVERY item you can see - be thorough
- Line sizes are typically 1", 2", 3", 4", 6", 8", 10", 12", 14", 16", 18", 20", 24"
- If uncertain about a value, make your best interpretation rather than omitting
- Return ONLY the JSON, no other text"""


COST_ESTIMATION_PROMPT = """You are an expert cost estimator for oil & gas and process engineering equipment. Based on the extracted P&ID data below, provide budget-level cost estimates for each item.

Use your knowledge of typical market prices for industrial equipment. Consider:
- Equipment type and typical sizing
- Material of construction (assume carbon steel unless specified otherwise)
- Standard industry pricing for oil & gas applications
- Prices should be in USD

EXTRACTED P&ID DATA:
{extracted_data}

Provide cost estimates in this exact JSON format:
{{
  "equipment_costs": [
    {{"tag": "...", "type": "...", "description": "...", "estimated_cost_usd": 0, "cost_basis": "brief explanation"}}
  ],
  "valve_costs": [
    {{"tag": "...", "type": "...", "size": "...", "estimated_cost_usd": 0, "cost_basis": "brief explanation"}}
  ],
  "instrument_costs": [
    {{"tag": "...", "type": "...", "function": "...", "estimated_cost_usd": 0, "cost_basis": "brief explanation"}}
  ],
  "piping_costs": [
    {{"line_number": "...", "size": "...", "estimated_cost_per_meter_usd": 0, "cost_basis": "brief explanation"}}
  ],
  "summary": {{
    "total_equipment": 0,
    "total_valves": 0,
    "total_instruments": 0,
    "total_piping_per_100m": 0,
    "grand_total_estimate": 0,
    "confidence_level": "low/medium/high",
    "assumptions": ["assumption 1", "assumption 2"],
    "exclusions": ["exclusion 1", "exclusion 2"]
  }}
}}

IMPORTANT:
- These are BUDGET estimates only (±30-50% accuracy)
- Exclude installation, engineering, freight costs
- Base on typical 2024-2026 market pricing
- If you cannot estimate, use 0 and explain in cost_basis
- Return ONLY the JSON, no other text."""


def encode_image_to_base64(file_content: bytes) -> str:
    """Convert image bytes to base64 string"""
    return base64.b64encode(file_content).decode('utf-8')


def analyze_pid_with_vision(image_base64: str, content_type: str) -> dict:
    """Send image to OpenAI Vision API for P&ID analysis"""
    
    # Determine media type
    if "png" in content_type:
        media_type = "image/png"
    elif "pdf" in content_type:
        media_type = "application/pdf"
    else:
        media_type = "image/jpeg"
    
    response = get_openai_client().chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PID_EXTRACTION_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{image_base64}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        max_tokens=4096,
        temperature=0.1
    )
    
    # Parse the JSON response
    content = response.choices[0].message.content
    
    # Clean up response (remove markdown code blocks if present)
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()
    
    return json.loads(content)


def estimate_costs(extracted_data: dict) -> dict:
    """Use AI to estimate costs based on extracted P&ID data"""
    
    prompt = COST_ESTIMATION_PROMPT.format(extracted_data=json.dumps(extracted_data, indent=2))
    
    response = get_openai_client().chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=4096,
        temperature=0.2
    )
    
    content = response.choices[0].message.content
    
    # Clean up response
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()
    
    return json.loads(content)


def create_excel_report(data: dict, filename: str, cost_data: Optional[dict] = None) -> str:
    """Generate Excel report from extracted P&ID data with optional cost estimates"""
    
    wb = Workbook()
    
    # Styles
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
    cost_header_fill = PatternFill(start_color="059669", end_color="059669", fill_type="solid")
    currency_font = Font(bold=True, color="059669")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    def style_header(ws, row=1, fill=header_fill):
        for cell in ws[row]:
            cell.font = header_font
            cell.fill = fill
            cell.alignment = Alignment(horizontal='center')
            cell.border = border
    
    def style_data(ws, start_row=2):
        for row in ws.iter_rows(min_row=start_row):
            for cell in row:
                cell.border = border
                cell.alignment = Alignment(horizontal='left')
    
    def format_currency(value):
        try:
            return f"${value:,.0f}"
        except:
            return "$0"
    
    # === EQUIPMENT Sheet ===
    ws_equip = wb.active
    ws_equip.title = "Equipment"
    if cost_data:
        ws_equip.append(["Tag", "Type", "Description", "Size/Capacity", "Est. Cost (USD)", "Cost Basis"])
    else:
        ws_equip.append(["Tag", "Type", "Description", "Size/Capacity"])
    
    equipment_costs = {item.get("tag"): item for item in cost_data.get("equipment_costs", [])} if cost_data else {}
    
    for item in data.get("equipment", []):
        tag = item.get("tag", "")
        row = [tag, item.get("type", ""), item.get("description", ""), item.get("size", "")]
        if cost_data:
            cost_item = equipment_costs.get(tag, {})
            row.extend([cost_item.get("estimated_cost_usd", 0), cost_item.get("cost_basis", "")])
        ws_equip.append(row)
    
    style_header(ws_equip)
    style_data(ws_equip)
    for i, width in enumerate([15, 18, 25, 15, 15, 30] if cost_data else [20, 20, 25, 20]):
        ws_equip.column_dimensions[get_column_letter(i+1)].width = width
    
    # === VALVES Sheet ===
    ws_valves = wb.create_sheet("Valves")
    if cost_data:
        ws_valves.append(["Tag", "Type", "Size", "Line Number", "Est. Cost (USD)", "Cost Basis"])
    else:
        ws_valves.append(["Tag", "Type", "Size", "Line Number"])
    
    valve_costs = {item.get("tag"): item for item in cost_data.get("valve_costs", [])} if cost_data else {}
    
    for item in data.get("valves", []):
        tag = item.get("tag", "")
        row = [tag, item.get("type", ""), item.get("size", ""), item.get("line_number", "")]
        if cost_data:
            cost_item = valve_costs.get(tag, {})
            row.extend([cost_item.get("estimated_cost_usd", 0), cost_item.get("cost_basis", "")])
        ws_valves.append(row)
    
    style_header(ws_valves)
    style_data(ws_valves)
    for i, width in enumerate([15, 15, 10, 18, 15, 30] if cost_data else [18, 18, 10, 18]):
        ws_valves.column_dimensions[get_column_letter(i+1)].width = width
    
    # === INSTRUMENTS Sheet ===
    ws_inst = wb.create_sheet("Instruments")
    if cost_data:
        ws_inst.append(["Tag", "Type", "Function", "Est. Cost (USD)", "Cost Basis"])
    else:
        ws_inst.append(["Tag", "Type", "Function"])
    
    instrument_costs = {item.get("tag"): item for item in cost_data.get("instrument_costs", [])} if cost_data else {}
    
    for item in data.get("instruments", []):
        tag = item.get("tag", "")
        row = [tag, item.get("type", ""), item.get("function", "")]
        if cost_data:
            cost_item = instrument_costs.get(tag, {})
            row.extend([cost_item.get("estimated_cost_usd", 0), cost_item.get("cost_basis", "")])
        ws_inst.append(row)
    
    style_header(ws_inst)
    style_data(ws_inst)
    for i, width in enumerate([15, 15, 18, 15, 30] if cost_data else [20, 20, 20]):
        ws_inst.column_dimensions[get_column_letter(i+1)].width = width
    
    # === LINES Sheet ===
    ws_lines = wb.create_sheet("Lines")
    if cost_data:
        ws_lines.append(["Line Number", "Size", "Service", "From", "To", "Est. Cost/m (USD)", "Cost Basis"])
    else:
        ws_lines.append(["Line Number", "Size", "Service", "From", "To"])
    
    piping_costs = {item.get("line_number"): item for item in cost_data.get("piping_costs", [])} if cost_data else {}
    
    for item in data.get("lines", []):
        line_num = item.get("line_number", "")
        row = [line_num, item.get("size", ""), item.get("service", ""), item.get("from", ""), item.get("to", "")]
        if cost_data:
            cost_item = piping_costs.get(line_num, {})
            row.extend([cost_item.get("estimated_cost_per_meter_usd", 0), cost_item.get("cost_basis", "")])
        ws_lines.append(row)
    
    style_header(ws_lines)
    style_data(ws_lines)
    for i, width in enumerate([22, 10, 15, 15, 15, 15, 30] if cost_data else [22, 10, 15, 15, 15]):
        ws_lines.column_dimensions[get_column_letter(i+1)].width = width
    
    # === COST SUMMARY Sheet (if cost estimation enabled) ===
    if cost_data:
        ws_cost = wb.create_sheet("Cost Summary")
        summary = cost_data.get("summary", {})
        
        ws_cost.append(["BUDGET COST ESTIMATE"])
        ws_cost['A1'].font = Font(bold=True, size=16, color="059669")
        ws_cost.append([])
        ws_cost.append(["Category", "Estimated Cost (USD)"])
        style_header(ws_cost, row=3, fill=cost_header_fill)
        
        ws_cost.append(["Equipment", summary.get("total_equipment", 0)])
        ws_cost.append(["Valves", summary.get("total_valves", 0)])
        ws_cost.append(["Instruments", summary.get("total_instruments", 0)])
        ws_cost.append(["Piping (per 100m)", summary.get("total_piping_per_100m", 0)])
        ws_cost.append([])
        ws_cost.append(["GRAND TOTAL", summary.get("grand_total_estimate", 0)])
        ws_cost['A9'].font = Font(bold=True, size=12)
        ws_cost['B9'].font = Font(bold=True, size=12, color="059669")
        
        ws_cost.append([])
        ws_cost.append(["Confidence Level:", summary.get("confidence_level", "N/A")])
        ws_cost.append([])
        ws_cost.append(["Key Assumptions:"])
        for assumption in summary.get("assumptions", []):
            ws_cost.append(["  •", assumption])
        ws_cost.append([])
        ws_cost.append(["Exclusions:"])
        for exclusion in summary.get("exclusions", []):
            ws_cost.append(["  •", exclusion])
        
        ws_cost.append([])
        ws_cost.append(["DISCLAIMER:"])
        ws_cost.append(["These are BUDGET estimates only with ±30-50% accuracy."])
        ws_cost.append(["For accurate pricing, obtain vendor quotes."])
        
        ws_cost.column_dimensions['A'].width = 25
        ws_cost.column_dimensions['B'].width = 50
        
        style_data(ws_cost, start_row=4)
    
    # === SUMMARY Sheet ===
    ws_summary = wb.create_sheet("Summary")
    ws_summary.append(["P&ID Analysis Summary"])
    ws_summary['A1'].font = Font(bold=True, size=14)
    ws_summary.append([])
    ws_summary.append(["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    ws_summary.append(["Source File:", filename])
    ws_summary.append(["Cost Estimation:", "Included" if cost_data else "Not included"])
    ws_summary.append([])
    ws_summary.append(["Description:", data.get("summary", "N/A")])
    ws_summary.append([])
    ws_summary.append(["Item Counts:"])
    ws_summary.append(["  Equipment:", len(data.get("equipment", []))])
    ws_summary.append(["  Valves:", len(data.get("valves", []))])
    ws_summary.append(["  Instruments:", len(data.get("instruments", []))])
    ws_summary.append(["  Lines:", len(data.get("lines", []))])
    
    if cost_data:
        ws_summary.append([])
        ws_summary.append(["Budget Estimate:", format_currency(cost_data.get("summary", {}).get("grand_total_estimate", 0))])
        ws_summary['B14'].font = currency_font
    
    ws_summary.append([])
    ws_summary.append(["Notes:"])
    for note in data.get("notes", []):
        ws_summary.append(["  -", note])
    
    ws_summary.column_dimensions['A'].width = 18
    ws_summary.column_dimensions['B'].width = 60
    
    # Save to temp file
    output_path = tempfile.mktemp(suffix=".xlsx")
    wb.save(output_path)
    
    return output_path


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main page"""
    html_path = Path(__file__).parent / "static" / "index.html"
    if html_path.exists():
        return FileResponse(str(html_path))
    return HTMLResponse("<h1>P&ID Parser API</h1><p>Use POST /api/analyze to analyze P&ID files.</p>")


@app.post("/api/analyze")
async def analyze_pid(
    file: UploadFile = File(...),
    include_costs: Optional[str] = Form(default="false")
):
    """Analyze uploaded P&ID and return extracted data with optional cost estimates"""
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(400, f"Invalid file type. Allowed: {', '.join(allowed_types)}")
    
    # Read file
    content = await file.read()
    
    # Check file size (max 20MB)
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(400, "File too large. Maximum size is 20MB.")
    
    # Encode to base64
    image_base64 = encode_image_to_base64(content)
    
    try:
        # Analyze with Vision API
        extracted_data = analyze_pid_with_vision(image_base64, file.content_type)
        
        # Cost estimation if requested
        cost_data = None
        if include_costs.lower() == "true":
            cost_data = estimate_costs(extracted_data)
        
        # Generate Excel report
        excel_path = create_excel_report(extracted_data, file.filename, cost_data)
        
        # Read Excel file for response
        with open(excel_path, "rb") as f:
            excel_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # Clean up temp file
        os.unlink(excel_path)
        
        response_data = {
            "success": True,
            "data": extracted_data,
            "excel": excel_base64,
            "filename": f"PID_Extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
        
        if cost_data:
            response_data["costs"] = cost_data
        
        return response_data
        
    except json.JSONDecodeError as e:
        raise HTTPException(500, f"Failed to parse AI response: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "P&ID Parser", "features": ["extraction", "cost_estimation"]}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
