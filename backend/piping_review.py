"""
Piping Document Review Module - KU Automation
Generates engineering review comments for piping deliverables

Supports:
- P&IDs (Piping & Instrumentation Diagrams)
- Piping Isometrics
- Piping GA/Layout Drawings
- Line Lists
- Piping Specifications

Generates comments per industry standard format with:
- Comment number
- Drawing/Document reference
- Location (grid, detail, area)
- Technical comment with code reference
- Severity (Hold/Comment/Note)
"""

# Piping review prompts for different document types

PIPING_REVIEW_SYSTEM_PROMPT = """You are a Senior Piping Engineer with 25+ years experience reviewing contractor deliverables for major oil & gas operators. You are meticulous, thorough, and always reference applicable codes and standards.

Your role is to review piping documents and generate professional engineering comments that:
1. Are SPECIFIC - reference exact locations (grid, detail, line number, equipment tag)
2. Are ACTIONABLE - clearly state what needs to change
3. REFERENCE CODES - cite ASME B31.3, project specs, or industry standards
4. Are SEVERITY-RATED - classify each comment appropriately

SEVERITY LEVELS:
- HOLD (🔴): Safety issue, code violation, or fundamental error that MUST be resolved before approval
- COMMENT (🟡): Technical deviation from specs/standards requiring contractor response
- NOTE (🟢): Suggestion, clarification request, or minor observation

COMMON PIPING REVIEW CHECKS:
1. Line numbering consistency (size-service-sequence format)
2. Valve tagging per project standards
3. Instrumentation connection points
4. Pipe support spacing per ASME B31.3 Table 321.1.1
5. Drain and vent provisions
6. Flange ratings vs design pressure
7. Material specifications vs line class
8. Insulation callouts
9. Slope requirements for specific services
10. Tie-in points and isolation requirements
11. Accessibility for maintenance
12. Clash potential with other disciplines
13. P&ID vs Isometric consistency
14. BOM accuracy
15. Weld identification and NDE requirements"""


PID_REVIEW_PROMPT = """Review this P&ID (Piping & Instrumentation Diagram) and generate detailed engineering comments.

PROJECT CONTEXT (if provided):
{project_context}

REVIEW CHECKLIST FOR P&IDs:
1. EQUIPMENT
   - All equipment tagged per project numbering system?
   - Design conditions shown (pressure, temperature)?
   - Nozzle sizes and ratings indicated?
   - Equipment elevations referenced?

2. PIPING
   - Line numbers complete (size-service-area-sequence)?
   - Line class/spec callouts present?
   - All valves tagged (XV, PV, HV, CV, PSV, etc.)?
   - Valve types appropriate for service?
   - Spectacle blinds at isolation points?
   - Drains and vents at low/high points?
   - Slope indicated where required?

3. INSTRUMENTATION
   - All instruments tagged per ISA standards?
   - Control valves have bypass arrangements where required?
   - Safety instrumented functions identified (SIF)?
   - Instrument root valves shown?

4. SAFETY
   - PSV discharge routed correctly (to flare/atmosphere)?
   - Relief device sizing basis referenced?
   - HAZOP recommendations incorporated?
   - Emergency isolation capability?

5. GENERAL
   - Drawing title block complete?
   - Revision history updated?
   - Legend/notes adequate?
   - Reference drawings listed?
   - Hold/approval stamps present?

Generate comments in this JSON format:
{{
    "document_info": {{
        "type": "P&ID",
        "drawing_number": "extracted or 'Not visible'",
        "revision": "extracted or 'Not visible'",
        "title": "extracted or 'Not visible'",
        "area": "extracted or 'Not visible'"
    }},
    "summary": "Brief 2-3 sentence assessment of the document quality and main issues found",
    "statistics": {{
        "equipment_count": 0,
        "valve_count": 0,
        "instrument_count": 0,
        "line_count": 0
    }},
    "comments": [
        {{
            "no": 1,
            "location": "Specific location (e.g., 'Equipment V-101', 'Line 6\"-PW-101', 'Grid B3')",
            "comment": "Detailed technical comment explaining the issue",
            "code_reference": "Applicable code/standard (e.g., 'ASME B31.3 Para 301.3.2', 'Project Spec PS-001')",
            "severity": "HOLD/COMMENT/NOTE",
            "category": "Equipment/Piping/Instrumentation/Safety/Documentation"
        }}
    ],
    "recommendations": [
        "Overall recommendation 1",
        "Overall recommendation 2"
    ],
    "approval_status": "APPROVED/APPROVED WITH COMMENTS/NOT APPROVED/REVISE AND RESUBMIT"
}}

Be thorough - a typical P&ID review generates 10-30 comments. Do not miss obvious issues.
Return ONLY the JSON."""


ISOMETRIC_REVIEW_PROMPT = """Review this Piping Isometric Drawing and generate detailed engineering comments.

PROJECT CONTEXT (if provided):
{project_context}

REVIEW CHECKLIST FOR PIPING ISOMETRICS:
1. GENERAL ARRANGEMENT
   - North arrow and orientation correct?
   - Match line references to adjacent isometrics?
   - Equipment nozzle orientations match P&ID/GA?
   - Tie-in points clearly identified?

2. DIMENSIONS & ROUTING
   - All dimensions provided for fabrication?
   - Pipe routing practical and constructable?
   - Adequate clearances for insulation?
   - Supports located at appropriate intervals?
   - Flexibility for thermal expansion?

3. COMPONENTS
   - All fittings specified (elbows, tees, reducers)?
   - Flange ratings match line class?
   - Valve handwheel orientations accessible?
   - Spectacle blinds orientation shown?
   - Orifice flanges orientation (taps up/down)?

4. BILL OF MATERIALS (BOM)
   - All items in BOM match drawing?
   - Material specifications correct per line class?
   - Quantities accurate?
   - Bolt lengths appropriate for flange ratings?
   - Gasket types per service?

5. WELDING & NDE
   - Weld numbers assigned?
   - NDE requirements indicated?
   - PWHT requirements identified?
   - Weld procedures referenced?

6. SUPPORTS
   - Support types appropriate (shoe, guide, anchor)?
   - Support spacing per ASME B31.3?
   - Spring hangers where required?
   - Load data for structural?

7. CONSISTENCY
   - Matches P&ID (routing, components)?
   - Line number matches throughout?
   - Revision matches related documents?

Generate comments in this JSON format:
{{
    "document_info": {{
        "type": "Piping Isometric",
        "drawing_number": "extracted",
        "revision": "extracted",
        "line_number": "extracted",
        "sheet": "X of Y if shown"
    }},
    "summary": "Brief assessment of isometric quality",
    "statistics": {{
        "total_length_approx": "estimated pipe length",
        "fitting_count": 0,
        "valve_count": 0,
        "support_count": 0
    }},
    "comments": [
        {{
            "no": 1,
            "location": "Specific location (e.g., 'Weld W5', 'Flange at V-101', 'Support SP-3')",
            "comment": "Detailed technical comment",
            "code_reference": "Applicable code/standard",
            "severity": "HOLD/COMMENT/NOTE",
            "category": "Dimensions/BOM/Supports/Welding/Routing/Consistency"
        }}
    ],
    "bom_issues": [
        "BOM discrepancy 1 if any"
    ],
    "recommendations": [],
    "approval_status": "APPROVED/APPROVED WITH COMMENTS/NOT APPROVED/REVISE AND RESUBMIT"
}}

Return ONLY the JSON."""


PIPING_GA_REVIEW_PROMPT = """Review this Piping General Arrangement (GA) / Layout Drawing and generate detailed engineering comments.

PROJECT CONTEXT (if provided):
{project_context}

REVIEW CHECKLIST FOR PIPING GA/LAYOUTS:
1. PLOT PLAN COMPLIANCE
   - Pipe rack routing per approved plot plan?
   - Equipment locations match mechanical layout?
   - Access ways and escape routes maintained?
   - Hazardous area boundaries respected?

2. ELEVATIONS & CLEARANCES
   - Minimum headroom maintained (2.1m typical)?
   - Road crossing clearances adequate?
   - Platform access to valves/instruments?
   - Clearance for insulation thickness?
   - Pipe-to-pipe clearances adequate?

3. PIPE RACK
   - Pipe rack loading within structural capacity?
   - Expansion loops/offsets where required?
   - Hot lines on correct side (typically outside)?
   - Future space allocation shown?

4. VALVE ACCESSIBILITY
   - Operating valves within reach (1.0-1.8m)?
   - Handwheel orientation for operation?
   - Chain operators where required?
   - Platform/ladder access for elevated valves?

5. MAINTENANCE ACCESS
   - Valve removal space available?
   - Heat exchanger tube pull space?
   - Pump suction strainer access?
   - In-line instrument removal space?

6. SAFETY
   - PSV discharge routing clear?
   - Emergency isolation valves accessible?
   - Fire hydrant/monitor coverage?
   - Escape route clearances?

7. COORDINATION
   - Clashes with structural steel?
   - Clashes with electrical cable trays?
   - Clashes with HVAC ducts?
   - Underground vs aboveground transitions?

Generate comments in JSON format:
{{
    "document_info": {{
        "type": "Piping GA/Layout",
        "drawing_number": "extracted",
        "revision": "extracted",
        "area": "extracted",
        "elevation": "if shown"
    }},
    "summary": "Brief assessment",
    "comments": [
        {{
            "no": 1,
            "location": "Grid reference or area",
            "comment": "Detailed technical comment",
            "code_reference": "Applicable standard",
            "severity": "HOLD/COMMENT/NOTE",
            "category": "Clearance/Access/Safety/Coordination/Routing"
        }}
    ],
    "clash_potential": [
        "Potential clash area 1"
    ],
    "recommendations": [],
    "approval_status": "APPROVED/APPROVED WITH COMMENTS/NOT APPROVED/REVISE AND RESUBMIT"
}}

Return ONLY the JSON."""


LINE_LIST_REVIEW_PROMPT = """Review this Piping Line List and generate detailed engineering comments.

PROJECT CONTEXT (if provided):
{project_context}

REVIEW CHECKLIST FOR LINE LISTS:
1. LINE NUMBERING
   - Consistent format (size-service-area-seq)?
   - All P&ID lines captured?
   - No duplicate line numbers?

2. DESIGN CONDITIONS
   - Design pressure/temperature logical for service?
   - Operating conditions within design envelope?
   - Pressure class appropriate for conditions?

3. LINE CLASS/SPEC
   - Line class appropriate for service and conditions?
   - Material compatible with fluid?
   - Flange rating adequate for design pressure?

4. SIZING
   - Line sizes appropriate for flow/velocity?
   - Size changes noted and justified?
   - Consistent with P&ID?

5. INSULATION
   - Insulation type appropriate (thermal/personnel protection)?
   - Thickness specified?
   - Heat tracing where required?

6. TESTING
   - Test pressure specified?
   - Test medium appropriate?
   - PWHT requirements identified?

7. PIGGING/CLEANING
   - Piggable lines identified?
   - Cleaning requirements noted?

Generate comments in JSON format:
{{
    "document_info": {{
        "type": "Line List",
        "document_number": "extracted",
        "revision": "extracted",
        "total_lines": 0
    }},
    "summary": "Brief assessment",
    "statistics": {{
        "total_lines": 0,
        "lines_by_service": {{}},
        "lines_by_size": {{}}
    }},
    "comments": [
        {{
            "no": 1,
            "location": "Line number or row reference",
            "comment": "Detailed technical comment",
            "code_reference": "Applicable standard",
            "severity": "HOLD/COMMENT/NOTE",
            "category": "Numbering/Design/Sizing/Material/Insulation"
        }}
    ],
    "recommendations": [],
    "approval_status": "APPROVED/APPROVED WITH COMMENTS/NOT APPROVED/REVISE AND RESUBMIT"
}}

Return ONLY the JSON."""


GENERAL_PIPING_REVIEW_PROMPT = """Review this piping document and generate detailed engineering comments.

First, identify the document type:
- P&ID (Piping & Instrumentation Diagram)
- Piping Isometric
- Piping GA/Layout
- Line List/Line Designation Table
- Piping Specification/Line Class
- Other piping document

PROJECT CONTEXT (if provided):
{project_context}

Then review thoroughly against applicable standards:
- ASME B31.3 Process Piping
- ASME B16 series (flanges, fittings, valves)
- Project specifications
- Industry best practices

Generate specific, actionable comments with code references.

Return JSON format:
{{
    "document_info": {{
        "type": "identified document type",
        "drawing_number": "extracted",
        "revision": "extracted",
        "title": "extracted"
    }},
    "summary": "Brief assessment of document quality and main issues",
    "comments": [
        {{
            "no": 1,
            "location": "Specific location reference",
            "comment": "Detailed technical comment explaining the issue and required action",
            "code_reference": "ASME B31.3 Para X.X.X or Project Spec or N/A",
            "severity": "HOLD/COMMENT/NOTE",
            "category": "Category of issue"
        }}
    ],
    "recommendations": [
        "Overall recommendation"
    ],
    "approval_status": "APPROVED/APPROVED WITH COMMENTS/NOT APPROVED/REVISE AND RESUBMIT"
}}

Be thorough and professional. Generate 10-30 comments for a typical document.
Return ONLY the JSON."""


def get_review_prompt(doc_type: str, project_context: str = "") -> str:
    """Get the appropriate review prompt based on document type"""
    
    prompts = {
        "pid": PID_REVIEW_PROMPT,
        "p&id": PID_REVIEW_PROMPT,
        "isometric": ISOMETRIC_REVIEW_PROMPT,
        "iso": ISOMETRIC_REVIEW_PROMPT,
        "ga": PIPING_GA_REVIEW_PROMPT,
        "layout": PIPING_GA_REVIEW_PROMPT,
        "general_arrangement": PIPING_GA_REVIEW_PROMPT,
        "line_list": LINE_LIST_REVIEW_PROMPT,
        "linelist": LINE_LIST_REVIEW_PROMPT,
        "line_designation": LINE_LIST_REVIEW_PROMPT,
    }
    
    # Get prompt or use general
    prompt_template = prompts.get(doc_type.lower(), GENERAL_PIPING_REVIEW_PROMPT)
    
    # Insert project context
    context_text = project_context if project_context else "No specific project context provided. Review against general industry standards."
    
    return prompt_template.format(project_context=context_text)
