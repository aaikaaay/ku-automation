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


RFQ_EXTRACTION_PROMPT = """You are an expert tender/RFQ analyst for oil & gas, EPC, and industrial projects.

Analyze the uploaded RFQ/ITB/tender document and extract ALL relevant information.

Return a JSON object with these sections:

{
  "overview": {
    "document_type": "RFQ/ITB/Tender/Quote Request/etc.",
    "reference_number": "Document reference or tender number",
    "issuing_company": "Company issuing the RFQ",
    "project_name": "Project name if mentioned",
    "project_location": "Site/location"
  },
  "key_dates": {
    "submission_deadline": "Final submission date/time",
    "validity_period": "Quote validity required",
    "clarification_deadline": "Last date for questions",
    "site_visit": "Site visit date if applicable",
    "award_date": "Expected award date",
    "delivery_date": "Required delivery date"
  },
  "scope_items": [
    {
      "item_no": "1",
      "description": "Item description",
      "quantity": "Qty with unit",
      "specifications": "Key specs if mentioned"
    }
  ],
  "technical_requirements": {
    "standards": ["API 610", "ASME VIII", "etc."],
    "certifications": ["ISO 9001", "ATEX", "etc."],
    "documentation": ["GA drawings", "Test certs", "Manuals", "etc."],
    "special_requirements": ["Any special technical requirements"]
  },
  "commercial_terms": {
    "payment_terms": "Payment conditions",
    "incoterms": "Delivery terms (FOB, CIF, etc.)",
    "currency": "Quotation currency",
    "warranty": "Warranty requirements",
    "liquidated_damages": "LD clause if present",
    "insurance": "Insurance requirements",
    "bonds": "Performance/bid bonds required"
  },
  "compliance_checklist": [
    {"requirement": "Submit in sealed envelope", "category": "Submission"},
    {"requirement": "Include manufacturer datasheets", "category": "Technical"},
    {"requirement": "Provide delivery schedule", "category": "Commercial"}
  ],
  "summary": "Brief 2-3 sentence summary of what this RFQ is for and key points bidders should note."
}

IMPORTANT:
- Extract EVERYTHING you can see - be thorough
- For dates, include time and timezone if specified
- If something is not mentioned, use "N/A"
- For scope items, capture all line items even if details are sparse
- Return ONLY the JSON, no other text"""


DATASHEET_EXTRACTION_PROMPT = """You are an expert equipment datasheet analyzer for industrial equipment.

Analyze the uploaded equipment datasheet and extract ALL specifications into structured data.

Return a JSON object with these sections:

{
  "general": {
    "manufacturer": "Equipment manufacturer/vendor",
    "model": "Model number",
    "tag_number": "Equipment tag if shown",
    "serial_number": "Serial number if shown",
    "equipment_type": "Pump/Valve/Exchanger/Instrument/etc.",
    "service": "Service description or application"
  },
  "operating_conditions": {
    "design_pressure": "Design pressure with unit",
    "operating_pressure": "Operating pressure with unit",
    "design_temperature": "Design temperature with unit",
    "operating_temperature": "Operating temperature with unit",
    "flow_rate": "Flow rate with unit",
    "fluid_medium": "Process fluid or medium"
  },
  "physical": {
    "dimensions": "Overall dimensions (L x W x H)",
    "weight": "Weight (dry/operating)",
    "materials": "Key materials of construction",
    "connections": "Inlet/outlet connections and ratings"
  },
  "performance": {
    "power": "Power requirements/consumption",
    "speed": "RPM or speed",
    "efficiency": "Efficiency if specified",
    "head_dp": "Head or differential pressure",
    "cv_kv": "Cv/Kv for valves"
  },
  "all_specs": [
    {"parameter": "Parameter name", "value": "Value", "unit": "Unit"}
  ],
  "certifications": ["API", "ATEX", "CE", "etc."],
  "notes": ["Any important notes or remarks from the datasheet"],
  "summary": "Brief 2-3 sentence summary of this equipment."
}

IMPORTANT:
- Extract EVERY specification you can see
- Include units for all values
- For "all_specs", capture ALL parameters in a flat list - this is the comprehensive extraction
- If something is not visible, use "N/A"
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


@app.post("/api/parse-rfq")
async def parse_rfq(file: UploadFile = File(...)):
    """Analyze uploaded RFQ/tender document and extract key information"""
    
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
    
    # Determine media type
    if "png" in file.content_type:
        media_type = "image/png"
    elif "pdf" in file.content_type:
        media_type = "application/pdf"
    else:
        media_type = "image/jpeg"
    
    try:
        # Analyze with Vision API
        response = get_openai_client().chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": RFQ_EXTRACTION_PROMPT},
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
        content_text = response.choices[0].message.content
        
        # Clean up response (remove markdown code blocks if present)
        if content_text.startswith("```"):
            content_text = content_text.split("```")[1]
            if content_text.startswith("json"):
                content_text = content_text[4:]
        content_text = content_text.strip()
        
        extracted_data = json.loads(content_text)
        
        # Generate Excel report for RFQ
        excel_path = create_rfq_excel_report(extracted_data, file.filename)
        
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


@app.post("/api/parse-datasheet")
async def parse_datasheet(file: UploadFile = File(...)):
    """Analyze uploaded equipment datasheet and extract specifications"""
    
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
    
    # Determine media type
    if "png" in file.content_type:
        media_type = "image/png"
    elif "pdf" in file.content_type:
        media_type = "application/pdf"
    else:
        media_type = "image/jpeg"
    
    try:
        # Analyze with Vision API
        response = get_openai_client().chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": DATASHEET_EXTRACTION_PROMPT},
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
        content_text = response.choices[0].message.content
        
        # Clean up response (remove markdown code blocks if present)
        if content_text.startswith("```"):
            content_text = content_text.split("```")[1]
            if content_text.startswith("json"):
                content_text = content_text[4:]
        content_text = content_text.strip()
        
        extracted_data = json.loads(content_text)
        
        # Generate Excel report for datasheet
        excel_path = create_datasheet_excel_report(extracted_data, file.filename)
        
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


def create_rfq_excel_report(data: dict, filename: str) -> str:
    """Generate Excel report from extracted RFQ data"""
    
    wb = Workbook()
    
    # Styles
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
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
                cell.alignment = Alignment(horizontal='left', wrap_text=True)
    
    # === OVERVIEW Sheet ===
    ws_overview = wb.active
    ws_overview.title = "Overview"
    ws_overview.append(["Field", "Value"])
    
    overview = data.get("overview", {})
    for field, value in [
        ("Document Type", overview.get("document_type", "N/A")),
        ("Reference Number", overview.get("reference_number", "N/A")),
        ("Issuing Company", overview.get("issuing_company", "N/A")),
        ("Project Name", overview.get("project_name", "N/A")),
        ("Project Location", overview.get("project_location", "N/A"))
    ]:
        ws_overview.append([field, value])
    
    style_header(ws_overview)
    style_data(ws_overview)
    ws_overview.column_dimensions['A'].width = 20
    ws_overview.column_dimensions['B'].width = 50
    
    # === KEY DATES Sheet ===
    ws_dates = wb.create_sheet("Key Dates")
    ws_dates.append(["Milestone", "Date/Period"])
    
    dates = data.get("key_dates", {})
    for field, value in [
        ("⚠️ SUBMISSION DEADLINE", dates.get("submission_deadline", "N/A")),
        ("Validity Period", dates.get("validity_period", "N/A")),
        ("Clarification Deadline", dates.get("clarification_deadline", "N/A")),
        ("Site Visit", dates.get("site_visit", "N/A")),
        ("Award Date", dates.get("award_date", "N/A")),
        ("Delivery Date", dates.get("delivery_date", "N/A"))
    ]:
        ws_dates.append([field, value])
    
    style_header(ws_dates)
    style_data(ws_dates)
    ws_dates.column_dimensions['A'].width = 25
    ws_dates.column_dimensions['B'].width = 40
    
    # === SCOPE ITEMS Sheet ===
    ws_scope = wb.create_sheet("Scope Items")
    ws_scope.append(["Item No", "Description", "Quantity", "Specifications"])
    
    for item in data.get("scope_items", []):
        ws_scope.append([
            item.get("item_no", ""),
            item.get("description", ""),
            item.get("quantity", ""),
            item.get("specifications", "")
        ])
    
    style_header(ws_scope)
    style_data(ws_scope)
    ws_scope.column_dimensions['A'].width = 10
    ws_scope.column_dimensions['B'].width = 40
    ws_scope.column_dimensions['C'].width = 15
    ws_scope.column_dimensions['D'].width = 30
    
    # === TECHNICAL REQUIREMENTS Sheet ===
    ws_tech = wb.create_sheet("Technical")
    ws_tech.append(["Category", "Requirement"])
    
    tech = data.get("technical_requirements", {})
    for std in tech.get("standards", []):
        ws_tech.append(["Standard", std])
    for cert in tech.get("certifications", []):
        ws_tech.append(["Certification", cert])
    for doc in tech.get("documentation", []):
        ws_tech.append(["Documentation", doc])
    for req in tech.get("special_requirements", []):
        ws_tech.append(["Special Requirement", req])
    
    style_header(ws_tech)
    style_data(ws_tech)
    ws_tech.column_dimensions['A'].width = 20
    ws_tech.column_dimensions['B'].width = 50
    
    # === COMMERCIAL TERMS Sheet ===
    ws_comm = wb.create_sheet("Commercial")
    ws_comm.append(["Term", "Value"])
    
    commercial = data.get("commercial_terms", {})
    for field, value in [
        ("Payment Terms", commercial.get("payment_terms", "N/A")),
        ("Incoterms", commercial.get("incoterms", "N/A")),
        ("Currency", commercial.get("currency", "N/A")),
        ("Warranty", commercial.get("warranty", "N/A")),
        ("Liquidated Damages", commercial.get("liquidated_damages", "N/A")),
        ("Insurance", commercial.get("insurance", "N/A")),
        ("Bonds/Guarantees", commercial.get("bonds", "N/A"))
    ]:
        ws_comm.append([field, value])
    
    style_header(ws_comm)
    style_data(ws_comm)
    ws_comm.column_dimensions['A'].width = 20
    ws_comm.column_dimensions['B'].width = 50
    
    # === COMPLIANCE CHECKLIST Sheet ===
    ws_checklist = wb.create_sheet("Checklist")
    ws_checklist.append(["✓", "Category", "Requirement"])
    
    for item in data.get("compliance_checklist", []):
        ws_checklist.append([
            "☐",
            item.get("category", ""),
            item.get("requirement", "")
        ])
    
    style_header(ws_checklist)
    style_data(ws_checklist)
    ws_checklist.column_dimensions['A'].width = 5
    ws_checklist.column_dimensions['B'].width = 15
    ws_checklist.column_dimensions['C'].width = 50
    
    # Save to temp file
    output_path = tempfile.mktemp(suffix=".xlsx")
    wb.save(output_path)
    
    return output_path


def create_datasheet_excel_report(data: dict, filename: str) -> str:
    """Generate Excel report from extracted datasheet data"""
    
    wb = Workbook()
    
    # Styles
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="059669", end_color="059669", fill_type="solid")
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
                cell.alignment = Alignment(horizontal='left', wrap_text=True)
    
    # === GENERAL INFO Sheet ===
    ws_general = wb.active
    ws_general.title = "General Info"
    ws_general.append(["Field", "Value"])
    
    general = data.get("general", {})
    for field, value in [
        ("Manufacturer", general.get("manufacturer", "N/A")),
        ("Model", general.get("model", "N/A")),
        ("Tag Number", general.get("tag_number", "N/A")),
        ("Serial Number", general.get("serial_number", "N/A")),
        ("Equipment Type", general.get("equipment_type", "N/A")),
        ("Service/Application", general.get("service", "N/A"))
    ]:
        ws_general.append([field, value])
    
    style_header(ws_general)
    style_data(ws_general)
    ws_general.column_dimensions['A'].width = 20
    ws_general.column_dimensions['B'].width = 40
    
    # === OPERATING CONDITIONS Sheet ===
    ws_operating = wb.create_sheet("Operating Conditions")
    ws_operating.append(["Parameter", "Value"])
    
    operating = data.get("operating_conditions", {})
    for field, value in [
        ("Design Pressure", operating.get("design_pressure", "N/A")),
        ("Operating Pressure", operating.get("operating_pressure", "N/A")),
        ("Design Temperature", operating.get("design_temperature", "N/A")),
        ("Operating Temperature", operating.get("operating_temperature", "N/A")),
        ("Flow Rate", operating.get("flow_rate", "N/A")),
        ("Fluid/Medium", operating.get("fluid_medium", "N/A"))
    ]:
        ws_operating.append([field, value])
    
    style_header(ws_operating)
    style_data(ws_operating)
    ws_operating.column_dimensions['A'].width = 22
    ws_operating.column_dimensions['B'].width = 35
    
    # === PHYSICAL Sheet ===
    ws_physical = wb.create_sheet("Physical")
    ws_physical.append(["Parameter", "Value"])
    
    physical = data.get("physical", {})
    for field, value in [
        ("Dimensions", physical.get("dimensions", "N/A")),
        ("Weight", physical.get("weight", "N/A")),
        ("Materials", physical.get("materials", "N/A")),
        ("Connections", physical.get("connections", "N/A"))
    ]:
        ws_physical.append([field, value])
    
    style_header(ws_physical)
    style_data(ws_physical)
    ws_physical.column_dimensions['A'].width = 15
    ws_physical.column_dimensions['B'].width = 50
    
    # === PERFORMANCE Sheet ===
    ws_perf = wb.create_sheet("Performance")
    ws_perf.append(["Parameter", "Value"])
    
    perf = data.get("performance", {})
    for field, value in [
        ("Power Requirements", perf.get("power", "N/A")),
        ("Speed/RPM", perf.get("speed", "N/A")),
        ("Efficiency", perf.get("efficiency", "N/A")),
        ("Head/DP", perf.get("head_dp", "N/A")),
        ("Cv/Kv", perf.get("cv_kv", "N/A"))
    ]:
        ws_perf.append([field, value])
    
    style_header(ws_perf)
    style_data(ws_perf)
    ws_perf.column_dimensions['A'].width = 18
    ws_perf.column_dimensions['B'].width = 35
    
    # === ALL SPECS Sheet ===
    ws_specs = wb.create_sheet("All Specifications")
    ws_specs.append(["Parameter", "Value", "Unit"])
    
    for spec in data.get("all_specs", []):
        ws_specs.append([
            spec.get("parameter", ""),
            spec.get("value", ""),
            spec.get("unit", "")
        ])
    
    style_header(ws_specs)
    style_data(ws_specs)
    ws_specs.column_dimensions['A'].width = 30
    ws_specs.column_dimensions['B'].width = 25
    ws_specs.column_dimensions['C'].width = 15
    
    # === SUMMARY Sheet ===
    ws_summary = wb.create_sheet("Summary")
    ws_summary.append(["Datasheet Extraction Summary"])
    ws_summary['A1'].font = Font(bold=True, size=14)
    ws_summary.append([])
    ws_summary.append(["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    ws_summary.append(["Source File:", filename])
    ws_summary.append([])
    ws_summary.append(["Summary:", data.get("summary", "N/A")])
    ws_summary.append([])
    ws_summary.append(["Certifications:"])
    for cert in data.get("certifications", []):
        ws_summary.append(["  •", cert])
    ws_summary.append([])
    ws_summary.append(["Notes:"])
    for note in data.get("notes", []):
        ws_summary.append(["  •", note])
    
    ws_summary.column_dimensions['A'].width = 15
    ws_summary.column_dimensions['B'].width = 60
    
    # Save to temp file
    output_path = tempfile.mktemp(suffix=".xlsx")
    wb.save(output_path)
    
    return output_path


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "KU Automation API", "features": ["pid_parser", "rfq_analyzer", "datasheet_parser", "cost_estimation"]}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
