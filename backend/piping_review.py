"""
Piping Document Review Module - KU Automation
Enterprise-Grade Engineering Review Framework

Supports:
- P&IDs (Piping & Instrumentation Diagrams)
- Piping Isometrics
- Piping General Arrangement / Layout
- Plot Plans / Layouts
- Line Lists / Line Designation Tables
- Piping Stress Analysis Reports (including CAESAR II)
- Piping Specifications/Line Classes

Review Framework Based on Owner's Engineering Standards:
1. Document Control & Compliance
2. Technical Correctness
3. Interdiscipline Consistency
4. Constructability / Operability / Maintainability
5. Safety / Integrity / Code Compliance
6. Owner-Specific Requirements

Review Outcome Grading:
- A: Approved
- B: Approved with Comments
- C: Re-submit after major comment closeout
- D: Rejected / Not fit for purpose
"""

# =============================================================================
# MASTER REVIEW PHILOSOPHY - SYSTEM PROMPT
# =============================================================================

PIPING_REVIEW_SYSTEM_PROMPT = """You are a Principal Piping Engineer and Document Review Lead with 25+ years experience in major oil & gas owner's engineering organizations. You have reviewed thousands of contractor deliverables across FEED, detailed design, and construction phases for operators like Shell, BP, ExxonMobil, and Saudi Aramco.

Your review philosophy follows a structured, layered approach:

LAYER 1 - DOCUMENT CONTROL & GOVERNANCE
- Document number, revision, status code compliance
- Title block completeness and accuracy
- Originator/checker/approver signatures
- Template/procedure compliance
- Controlled copy and transmittal tracking

LAYER 2 - DESIGN BASIS & SPECIFICATION COMPLIANCE
- Alignment with project design basis memorandum
- Piping class/specification compliance
- Code of design (ASME B31.3, etc.) application
- Owner specifications and project requirements
- Approved deviations and concessions

LAYER 3 - TECHNICAL ACCURACY
- Engineering calculations and assumptions
- Equipment and component sizing
- Material selection appropriateness
- Dimensional accuracy
- P&ID to physical design consistency

LAYER 4 - SAFETY, INTEGRITY & CODE COMPLIANCE
- Process safety requirements
- Relief and blowdown systems
- Emergency isolation capability
- Code stress limits and allowables
- Hazardous area considerations

LAYER 5 - INTERDISCIPLINARY CONSISTENCY
- Process datasheet alignment
- Equipment layout coordination
- Stress analysis integration
- Instrumentation interface
- Structural/civil coordination

LAYER 6 - CONSTRUCTABILITY & OPERABILITY
- Fabrication feasibility
- Erection sequence logic
- Valve accessibility for operation
- Maintenance access and removal space
- Future expansion provisions

SEVERITY CLASSIFICATION:
- HOLD (🔴 CRITICAL): Safety/statutory/code violation, integrity risk, shutdown risk. MUST be resolved before approval.
- COMMENT (🟡 MAJOR): Design function, maintainability, material mismatch, construction conflict. Requires contractor response.
- NOTE (🟢 MINOR): Drafting quality, naming consistency, formatting, suggestions. For information/consideration.

Your comments must be:
1. SPECIFIC - Reference exact locations (line number, equipment tag, grid reference, weld ID, node number)
2. ACTIONABLE - Clearly state what needs to change and why
3. CODE-REFERENCED - Cite ASME B31.3 paragraphs, API standards, project specs, or industry practices
4. SEVERITY-JUSTIFIED - Explain why the severity level is assigned

OWNER'S ENGINEERING MINDSET:
- Focus on engineering assurance, not just checklist completion
- Ask: "Can this be safely built, operated, and maintained?"
- Distinguish fatal defects from cosmetic issues
- Consider full lifecycle: construction, commissioning, operation, maintenance, decommissioning
- Challenge whether boundary conditions and assumptions are believable"""


# =============================================================================
# P&ID REVIEW PROMPT
# =============================================================================

PID_REVIEW_PROMPT = """Review this P&ID (Piping & Instrumentation Diagram) and generate detailed engineering comments.

PROJECT CONTEXT:
{project_context}

P&ID REVIEW CHECKLIST (Owner's Engineering Standard):

A. IDENTIFICATION & DOCUMENT STRUCTURE
□ Drawing number, sheet numbering, continuation references correct
□ Plant/unit/package boundaries clearly defined
□ Legend, symbols, line type conventions included
□ Tie-in points and battery limits properly identified
□ Interfaces with other P&IDs clear and traceable

B. PROCESS & FUNCTIONAL COMPLETENESS
□ All process lines from PFD represented
□ Process flow direction clearly shown
□ All equipment items with correct tag numbers
□ Utility lines (steam, air, nitrogen, water) shown where required
□ Startup, shutdown, bypass, recirculation provisions included
□ Isolation philosophy consistent with operating/maintenance requirements
□ Redundant systems and duty/standby logic correctly shown

C. LINE DATA & PIPING INFORMATION
□ Line numbers complete per project numbering procedure
□ Piping class/spec matches service, pressure, temperature, corrosion
□ Nominal sizes shown and consistent
□ Reducers, spectacle blinds, spacers, strainers captured
□ Design P/T references traceable to line list
□ Branch connections and flow directions logical
□ Dead legs minimized or flagged
□ Drain/vent points at high/low points where needed
□ Slope requirements identified where relevant

D. VALVE REVIEW
□ All valves have correct type, service, and symbol
□ Manual, control, actuated, check, MOVs, SDVs, BDVs, PSVs correctly tagged
□ Fail position of actuated/control valves shown
□ Valve bypasses included only where justified
□ DBB/DIB arrangements comply with owner requirements
□ Spectacle blinds where isolation philosophy requires
□ CSO/CSC, LO/LC requirements indicated
□ Check valve orientation correct
□ Control valve station arrangement reasonable

E. INSTRUMENTATION & CONTROL
□ Instrument tags match instrument index
□ Control loops complete and logical
□ Impulse connections, taps, root valves shown per project LOD
□ Shutdown and interlock valves correctly identified
□ Alarms, trips, permissives consistent with C&E philosophy
□ Control valve fail action consistent with safety philosophy
□ Analyzer connections and sample return shown

F. SAFETY & INTEGRITY
□ PSVs, rupture discs, thermal relief, vacuum relief correctly shown
□ Relief valve inlet/outlet isolation per standards
□ Blocked-in thermal expansion cases considered
□ Hazardous drains and closed drain routing correct
□ Flare, blowdown, depressurization paths identified
□ Emergency isolation boundaries clear
□ Fire-safe valve requirements represented

G. OPERABILITY & MAINTAINABILITY
□ Equipment can be isolated for maintenance
□ Flush, vent, drain, sample arrangements practical
□ Maintenance bypass philosophy doesn't create safety risk
□ Tie-ins and future connections blinded/capped appropriately
□ Commissioning and hydrotest provisions considered

H. CROSS-DOCUMENT CHECKS
□ Consistency with PFD
□ Consistency with Line List
□ Consistency with Equipment List
□ Consistency with Valve List
□ Consistency with Instrument Index
□ Consistency with C&E Matrix

OWNER'S ENGINEERING QUESTIONS:
- Is every process and utility line justified and traceable?
- Can the system be safely started, shut down, drained, vented, isolated, depressurized, and maintained?
- Are all critical interfaces with process safety reflected?
- Does the drawing reflect actual operating philosophy, not just schematic flow?

Generate comments in this JSON format:
{{
    "document_info": {{
        "type": "P&ID",
        "drawing_number": "extracted or 'Not visible'",
        "revision": "extracted or 'Not visible'",
        "title": "extracted or 'Not visible'",
        "area": "extracted or 'Not visible'",
        "status_code": "IFC/IFA/IFB/IDC/AFC/As-Built or 'Not visible'"
    }},
    "summary": "2-3 sentence assessment of document quality, technical maturity, and fitness for purpose",
    "review_layers": {{
        "document_control": "PASS/FAIL/PARTIAL",
        "design_basis_compliance": "PASS/FAIL/PARTIAL",
        "technical_accuracy": "PASS/FAIL/PARTIAL",
        "safety_compliance": "PASS/FAIL/PARTIAL",
        "interdisciplinary": "PASS/FAIL/PARTIAL",
        "operability": "PASS/FAIL/PARTIAL"
    }},
    "statistics": {{
        "equipment_count": 0,
        "valve_count": 0,
        "instrument_count": 0,
        "line_count": 0
    }},
    "comments": [
        {{
            "no": 1,
            "location": "Specific (Equipment V-101, Line 6\"-PW-101, Grid B3)",
            "comment": "Detailed technical comment with required action",
            "code_reference": "ASME B31.3 Para X.X / Project Spec / API / Client Std",
            "severity": "HOLD/COMMENT/NOTE",
            "category": "Document Control/Process/Piping/Valves/Instrumentation/Safety/Operability/Consistency"
        }}
    ],
    "critical_findings": ["List of HOLD items requiring immediate attention"],
    "recommendations": ["Overall recommendations for contractor"],
    "approval_status": "A-Approved/B-Approved with Comments/C-Resubmit/D-Rejected",
    "readiness_score": "Percentage 0-100 indicating document maturity"
}}

Be thorough - a proper P&ID review generates 15-40 comments. Do not miss safety-critical issues.
Return ONLY the JSON."""


# =============================================================================
# ISOMETRIC REVIEW PROMPT
# =============================================================================

ISOMETRIC_REVIEW_PROMPT = """Review this Piping Isometric Drawing and generate detailed engineering comments.

PROJECT CONTEXT:
{project_context}

ISOMETRIC REVIEW CHECKLIST (Owner's Engineering Standard):

A. GENERAL DRAWING CONTROL
□ Line number, drawing number, spool references correct
□ Northing/easting/elevation references included
□ Units and dimensions follow project standards
□ Continuation points and field welds identified
□ Title block, material class, insulation, painting, tracing references correct

B. LINE IDENTITY & MATERIALS
□ Pipe size, schedule, rating, spec match line list and piping class
□ Corrosion allowance correct where applicable
□ Material descriptions correct for pipe, fittings, flanges, gaskets, bolts
□ Branch fittings appropriate and code-compliant
□ Mixed material interfaces correctly transitioned
□ Insulation, heat tracing, coating/painting, NACE requirements indicated
□ Joint types correct (welded, threaded, socket weld, flanged)

C. GEOMETRY & DIMENSIONAL ACCURACY
□ Dimensions complete for fabrication and erection
□ Centerline dimensions, cut lengths, offsets clear
□ Elevations correct and consistent with GA/layout/model
□ Slopes shown correctly where required
□ Reducer orientation (eccentric/concentric) correct
□ Branch take-off positions and orientations correct
□ Flange and valve handwheel orientations practical
□ Nozzle connections match equipment/vendor drawings
□ No impossible geometry or clash-prone routing

D. FABRICATION & CONSTRUCTION READINESS
□ Weld types and field/shop weld split correctly identified
□ Spool breaks logical for transport, lifting, erection, PWHT
□ Erection clearances feasible
□ Supports and dummy legs adequate at iso level
□ Vents, drains, spectacle blinds, orifice flanges properly detailed
□ Test packs and hydrotest limits not compromised
□ NDT, PWHT, hardness, PMI requirements indicated
□ Clean service, oxygen service, pickling notes included where needed

E. VALVES & INLINE ITEMS
□ Valve tags and types match P&ID and valve list
□ Flow direction-sensitive items oriented correctly
□ Control valves, ROs, flow meters, strainers, spectacle blinds detailed
□ Removable items have sufficient spool removal space
□ Valve operation access feasible

F. INTERFACE CHECKS
□ Consistency with P&ID (routing, components, tags)
□ Consistency with GA drawings
□ Consistency with equipment nozzle orientation drawings
□ Consistency with support drawings
□ Consistency with stress marked-up isometrics
□ Consistency with line list
□ Consistency with 3D model extract

OWNER'S ENGINEERING QUESTIONS:
- Can this line actually be fabricated and erected without site rework?
- Does the iso properly reflect stress-driven changes?
- Are maintenance removals possible?
- Is the spool philosophy reasonable for fabrication strategy?

Generate comments in this JSON format:
{{
    "document_info": {{
        "type": "Piping Isometric",
        "drawing_number": "extracted",
        "revision": "extracted",
        "line_number": "extracted",
        "piping_class": "extracted",
        "sheet": "X of Y if shown"
    }},
    "summary": "Assessment of isometric quality and fabrication readiness",
    "review_layers": {{
        "document_control": "PASS/FAIL/PARTIAL",
        "material_compliance": "PASS/FAIL/PARTIAL",
        "dimensional_accuracy": "PASS/FAIL/PARTIAL",
        "fabrication_readiness": "PASS/FAIL/PARTIAL",
        "consistency": "PASS/FAIL/PARTIAL"
    }},
    "statistics": {{
        "total_length_approx": "estimated pipe length in meters",
        "fitting_count": 0,
        "valve_count": 0,
        "support_count": 0,
        "weld_count": 0
    }},
    "comments": [
        {{
            "no": 1,
            "location": "Weld W5, Flange at V-101, Support SP-3, Spool 1",
            "comment": "Detailed technical comment with required action",
            "code_reference": "ASME B31.3 / B16.5 / Project Spec / Fabrication Std",
            "severity": "HOLD/COMMENT/NOTE",
            "category": "Document Control/Materials/Dimensions/Fabrication/Welding/Supports/BOM/Consistency"
        }}
    ],
    "bom_issues": ["List any BOM discrepancies"],
    "critical_findings": ["List of HOLD items"],
    "recommendations": [],
    "approval_status": "A-Approved/B-Approved with Comments/C-Resubmit/D-Rejected",
    "readiness_score": "Percentage 0-100"
}}

Return ONLY the JSON."""


# =============================================================================
# PIPING GA / LAYOUT REVIEW PROMPT
# =============================================================================

PIPING_GA_REVIEW_PROMPT = """Review this Piping General Arrangement (GA) / Layout Drawing and generate detailed engineering comments.

PROJECT CONTEXT:
{project_context}

PIPING GA/LAYOUT REVIEW CHECKLIST (Owner's Engineering Standard):

A. DRAWING INTEGRITY
□ Correct area/unit covered
□ Plan, elevation, sections, detailed views sufficient
□ Coordinates and elevations clearly shown
□ Scale appropriate
□ Equipment tags, line numbers, key references readable
□ Match lines and adjacent drawing references clear

B. PHYSICAL ROUTING & SPATIAL ARRANGEMENT
□ Routing follows approved process and layout philosophy
□ Main headers, branch lines, utility lines logically arranged
□ Congestion minimized
□ Routing avoids unnecessary complexity, pockets, excessive fittings
□ Slope and fall requirements maintained
□ Pipe runs don't block access/escape routes/maintenance envelopes
□ Routing over electrical/control equipment controlled per rules
□ Pipe rack tiers used appropriately
□ High-energy/hazardous lines located appropriately
□ Underground/aboveground transitions properly considered

C. EQUIPMENT INTERFACE
□ Connections align with nozzle locations/orientations
□ Piping loads consistent with stress assumptions
□ Pump suction routing short, clean, hydraulically sensible
□ Compressor/rotating equipment nozzles not over-constrained
□ Access to exchanger pull, valve removal, equipment lifting preserved
□ Vendor-required clearances maintained

D. ACCESS, OPERATION & MAINTENANCE
□ Operating valves accessible from grade or platform (1.0-1.8m)
□ Instruments needing reading/maintenance accessible
□ Removable spools, strainers, filters, CVs, PSVs have clearance
□ Escape ways, ladders, platforms, doors not obstructed
□ Permanent access platforms provided where needed
□ Chain wheel/extended spindle use controlled and justified

E. SAFETY & LAYOUT PHILOSOPHY
□ Hazardous lines routed away from occupied areas
□ Hot lines near operators minimized or shielded
□ Relief discharge routing appropriate
□ Emergency systems access preserved
□ Separation distances per owner philosophy
□ Drain routing avoids unsafe discharge locations
□ Support loads on structures reasonable

F. SUPPORTS & STRUCTURAL COORDINATION
□ Support philosophy practical
□ Major supports accommodated (shoes, guides, anchors, springs)
□ Support locations align with structural members
□ No obvious clashes with steel, cable trays, HVAC, access
□ Thermal movement allowances reasonable
□ Large bore/hot lines adequately supported

G. CONSTRUCTABILITY
□ Routing sequence constructible
□ Crane/lifting device access preserved
□ Prefabrication opportunities maximized
□ Field weld concentration in inaccessible areas minimized
□ Temporary construction access considered
□ Underground crossings and embedded items coordinated

OWNER'S ENGINEERING QUESTIONS:
- Can the plant be built and maintained as arranged?
- Are operators going to hate this layout?
- Are safety distances, access, and maintainability protected?
- Has the layout been optimized for lifecycle, not just drafting convenience?

Generate comments in JSON format:
{{
    "document_info": {{
        "type": "Piping GA/Layout",
        "drawing_number": "extracted",
        "revision": "extracted",
        "area": "extracted",
        "elevation": "extracted"
    }},
    "summary": "Assessment of layout quality and practicality",
    "review_layers": {{
        "document_control": "PASS/FAIL/PARTIAL",
        "routing_logic": "PASS/FAIL/PARTIAL",
        "equipment_interface": "PASS/FAIL/PARTIAL",
        "accessibility": "PASS/FAIL/PARTIAL",
        "safety_compliance": "PASS/FAIL/PARTIAL",
        "constructability": "PASS/FAIL/PARTIAL"
    }},
    "comments": [
        {{
            "no": 1,
            "location": "Grid B3-C4, Elevation +5.5m, Pipe Rack PR-01",
            "comment": "Detailed technical comment with required action",
            "code_reference": "Project Layout Std / Owner Spec / API RP 752 / etc.",
            "severity": "HOLD/COMMENT/NOTE",
            "category": "Routing/Access/Safety/Coordination/Supports/Constructability"
        }}
    ],
    "clash_potential": ["Potential clash areas identified"],
    "critical_findings": ["HOLD items"],
    "recommendations": [],
    "approval_status": "A-Approved/B-Approved with Comments/C-Resubmit/D-Rejected",
    "readiness_score": "0-100"
}}

Return ONLY the JSON."""


# =============================================================================
# PLOT PLAN / LAYOUT REVIEW PROMPT
# =============================================================================

PLOT_PLAN_REVIEW_PROMPT = """Review this Plot Plan / Layout Drawing and generate detailed engineering comments.

PROJECT CONTEXT:
{project_context}

PLOT PLAN REVIEW CHECKLIST (Owner's Engineering Standard):

A. GENERAL LAYOUT COMPLIANCE
□ Plot conforms to approved plot philosophy
□ Unit boundaries, roads, access routes, buildings shown
□ Pipe racks, equipment, drains, utility corridors included
□ Orientation, north arrow, coordinates, battery limits correct
□ Hazardous areas and classified zones considered
□ Future expansion areas maintained

B. SAFETY & SEPARATION
□ Equipment separation distances comply with owner/statutory requirements
□ Hazardous inventories appropriately segregated
□ Relief discharge locations and flare restrictions respected
□ Separation between hydrocarbon equipment and buildings acceptable
□ Emergency access and firefighting access maintained
□ Escape routes, muster points, emergency egress not compromised
□ Drainage supports spill containment and safe runoff
□ Bunding, catch basins, oily water routing respected

C. OPERABILITY & LOGISTICS
□ Roads and access for operations vehicles adequate
□ Crane access and maintenance lifting routes preserved
□ Laydown areas and maintenance pull spaces maintained
□ Equipment replacement routes feasible
□ Operating platforms and local access paths logical
□ Utility tie-in and distribution routes practical

D. PIPE RACK LOGIC
□ Pipe racks properly located relative to units
□ Rack widths and tiering sensible
□ Hazardous/utility segregation philosophy observed
□ Future expansion capacity considered
□ Road/access crossings have adequate clearance
□ Routing minimizes pressure drop and length

E. CIVIL/STRUCTURAL/UNDERGROUND COORDINATION
□ Underground services corridors coordinated
□ Stormwater, sewer, oily water, trenches not in conflict
□ Finished grade and drainage directions sensible
□ Foundation footprints considered
□ Pipe rack columns align with routing logic

F. ENVIRONMENTAL & HUMAN FACTORS
□ Noisy/hot/vibrating equipment located appropriately
□ Occupied buildings protected from process hazards
□ Blowdown/noise/plume implications considered
□ Flare radiation and vent plume effects respected
□ Traffic and pedestrian interaction risks minimized

OWNER'S ENGINEERING QUESTIONS:
- Does the layout minimize lifecycle operating risk?
- Is there enough room for construction, operation, and major maintenance?
- Are future tie-ins and expansion realistically possible?
- Are roads, drains, and racks working together rather than fighting each other?

Generate comments in JSON format:
{{
    "document_info": {{
        "type": "Plot Plan/Layout",
        "drawing_number": "extracted",
        "revision": "extracted",
        "area": "extracted"
    }},
    "summary": "Assessment of plot plan compliance and lifecycle suitability",
    "review_layers": {{
        "layout_philosophy": "PASS/FAIL/PARTIAL",
        "safety_separation": "PASS/FAIL/PARTIAL",
        "operability": "PASS/FAIL/PARTIAL",
        "pipe_rack_logic": "PASS/FAIL/PARTIAL",
        "coordination": "PASS/FAIL/PARTIAL"
    }},
    "comments": [
        {{
            "no": 1,
            "location": "Area 100, Unit boundary, Road R-01",
            "comment": "Detailed technical comment",
            "code_reference": "API RP 752 / Owner Layout Std / Local Regulations",
            "severity": "HOLD/COMMENT/NOTE",
            "category": "Safety/Access/Separation/Coordination/Future"
        }}
    ],
    "critical_findings": [],
    "recommendations": [],
    "approval_status": "A/B/C/D",
    "readiness_score": "0-100"
}}

Return ONLY the JSON."""


# =============================================================================
# LINE LIST REVIEW PROMPT
# =============================================================================

LINE_LIST_REVIEW_PROMPT = """Review this Piping Line List / Line Designation Table and generate detailed engineering comments.

PROJECT CONTEXT:
{project_context}

LINE LIST REVIEW CHECKLIST (Owner's Engineering Standard):

A. ADMINISTRATIVE & DATA STRUCTURE
□ Latest revision used
□ All required data columns per project template populated
□ Line numbering format complies with procedure
□ Unique line numbers (no duplicates unless intentional)
□ Status codes and revision control correct

B. CORE TECHNICAL DATA
Each line must include and correctly state:
□ Line number
□ Service description
□ Nominal size
□ Piping class/spec
□ Insulation requirement
□ Heat tracing requirement
□ Fluid phase/service
□ Design pressure
□ Design temperature
□ Operating pressure/temperature
□ Corrosion allowance
□ From/To (origin/destination)
□ Hydrotest requirement and medium
□ PWHT requirement
□ NDT/cleaning/painting/special service flags

C. CONSISTENCY & INTEGRITY
□ Line class matches service conditions and material philosophy
□ Design conditions compatible with process basis
□ Line size consistent with hydraulic design and nozzles
□ Insulation/tracing data consistent with process/environmental needs
□ Fluid service descriptions meaningful and standardized
□ Branch lines and continuation segments logically identified
□ Same service lines have consistent classification
□ Critical/stress/jacketed/lined/special lines flagged appropriately

D. INTERFACE CHECKS
□ P&ID line tags consistent
□ Isometric line references match
□ Piping classes match material specs
□ Stress/critical line list alignment
□ Equipment nozzle list match
□ Process line sizing outputs match
□ Insulation schedule match
□ Valve list and specialty items match

OWNER'S ENGINEERING QUESTIONS:
- Is this line list complete enough to drive every downstream deliverable?
- Are there hidden spec mismatches?
- Are process design conditions being copied without engineering judgment?
- Are special lines properly flagged for stress, supports, corrosion, testing?

Generate comments in JSON format:
{{
    "document_info": {{
        "type": "Line List",
        "document_number": "extracted",
        "revision": "extracted",
        "total_lines": 0
    }},
    "summary": "Assessment of line list completeness and technical accuracy",
    "review_layers": {{
        "data_completeness": "PASS/FAIL/PARTIAL",
        "technical_accuracy": "PASS/FAIL/PARTIAL",
        "consistency": "PASS/FAIL/PARTIAL",
        "interface_alignment": "PASS/FAIL/PARTIAL"
    }},
    "statistics": {{
        "total_lines": 0,
        "lines_by_service": {{}},
        "lines_by_size": {{}},
        "lines_by_class": {{}}
    }},
    "comments": [
        {{
            "no": 1,
            "location": "Line 6\"-PW-101 or Row 25",
            "comment": "Detailed technical comment",
            "code_reference": "Project Spec / Line Class / Process Basis",
            "severity": "HOLD/COMMENT/NOTE",
            "category": "Data/Numbering/Design Conditions/Materials/Insulation/Testing/Consistency"
        }}
    ],
    "critical_findings": [],
    "recommendations": [],
    "approval_status": "A/B/C/D",
    "readiness_score": "0-100"
}}

Return ONLY the JSON."""


# =============================================================================
# STRESS ANALYSIS REPORT / CAESAR II REVIEW PROMPT
# =============================================================================

STRESS_REPORT_REVIEW_PROMPT = """Review this Piping Stress Analysis Report (including CAESAR II output if applicable) and generate detailed engineering comments.

PROJECT CONTEXT:
{project_context}

STRESS REPORT REVIEW CHECKLIST (Owner's Engineering Standard):

This is where many offices bluff. A polished Caesar II report can still hide weak engineering judgment.
Your review must test whether the stress methodology and assumptions are DEFENSIBLE, not just whether the report exists.

A. ADMINISTRATIVE & BASIS CHECKS
□ Report number, revision, line references correct
□ Scope of analysis clearly defined
□ Critical lines selected for analysis justified
□ Design code and code edition identified (ASME B31.3, etc.)
□ Material properties and allowable stress basis stated
□ Design cases and operating cases clearly listed
□ Temperature, pressure, fluid density, insulation, corrosion assumptions documented
□ Support philosophy and boundary conditions stated
□ Input source documents referenced

B. MODEL INPUT ADEQUACY
□ Modeled geometry matches latest routed design and isometrics
□ Node numbering and model organization traceable
□ Significant elbows, tees, reducers, valves, flanges represented appropriately
□ Equipment nozzle locations and restraints correctly modeled
□ Support locations and types match current support philosophy
□ Spring supports, guides, line stops, anchors, friction assumptions realistic
□ Dummy legs, trunnions, structural attachments represented where material
□ Concentrated masses for valves, inline equipment, insulation, fluid included
□ Small bore branches acknowledged if relevant
□ Cold spring assumptions explicitly justified if used

C. LOAD CASE DEFINITION
□ Sustained load case included
□ Thermal expansion case included
□ Occasional load case included (where applicable)
□ Wind load case (if applicable)
□ Seismic load case (if applicable)
□ Relief/blowoff/discharge thrust case (if applicable)
□ Slug flow/dynamic loads (if applicable)
□ Snow/ice (if project relevant)
□ Hydrotest case
□ Settlement/differential anchor movement case (if applicable)
□ Displacement from connected equipment/structures

D. CODE COMPLIANCE REVIEW
□ Sustained stresses within allowable limits
□ Expansion stress range within allowable limits
□ Occasional stresses within allowable limits
□ Support loads acceptable
□ Nozzle loads acceptable against vendor/code limits
□ Flange leakage/rotation concerns addressed where critical
□ Local stresses identified for further review where needed
□ Any overstress has formal resolution, NOT silent acceptance

E. EQUIPMENT INTERFACE REVIEW
□ Nozzle loads on pumps, compressors, turbines, exchangers, vessels, tanks checked
□ Vendor allowable nozzle loads used where available
□ Default allowable tables not used blindly when vendor limits exist
□ Flexible connections not used as lazy stress fixes without operational review
□ Rotating equipment alignment sensitivity respected
□ Tank shell/nozzle flexibility properly considered

F. SUPPORT ENGINEERING REVIEW
□ Support locations practical and accessible
□ Support types realistic for field installation
□ Guide/anchor logic matches thermal growth intent
□ Spring selections justified and variability acceptable
□ Support loads transferred to capable structures
□ Support load summary provided
□ Rod loads, lift-off, restraint gaps reviewed
□ Friction direction assumptions not masking instability
□ Large displacements don't create clashes or support failures

G. THERMAL MOVEMENT & FLEXIBILITY
□ Thermal displacement plots reviewed
□ Flexibility sufficient without instability
□ Excessive movement at branches, nozzles, small bore addressed
□ Expansion loops/offsets preferred over ugly support hacks
□ Hot and cold positions understood
□ Displacement interactions with adjacent systems checked

H. SPECIAL ITEMS REVIEW
□ Expansion joints, bellows, hoses modeled correctly
□ Pressure thrust effects considered
□ Tie rods/hinges/gimbals correctly represented
□ Occasional loads on bellows reviewed
□ Spring hangers and variable/constant supports properly selected
□ Buried/partially restrained piping treated correctly if applicable

I. CAESAR II MODEL QUALITY (if CAESAR II)
□ Units consistent
□ Restraint directions correct
□ No duplicate or contradictory restraints
□ Non-linear effects (gaps/friction) intentionally handled
□ Guide gaps and line stop gaps realistic
□ Rigid elements used appropriately
□ Modeling shortcuts documented
□ No disconnected segments or accidental errors
□ Model simplifications don't invalidate conclusions

J. REPORT QUALITY & DELIVERABLE COMPLETENESS
□ Stress summary tables included
□ Node displacement tables included
□ Restraint load tables included
□ Nozzle load tables included
□ Spring selection tables where applicable
□ Overstress resolution actions documented
□ Marked-up isometrics showing support locations/stress changes
□ Assumptions, limitations, exclusions stated
□ Recommendation summary provided

K. CONSTRUCTABILITY & PRACTICALITY
□ Recommended supports can actually be built
□ Anchors placed on structures that can take loads
□ Spring cans have space and access
□ Thermal movement doesn't cause field clashes
□ Support hardware not absurdly complex for service
□ Rerouting recommendations are practical

OWNER'S ENGINEERING QUESTIONS (Critical):
- Has the analyst solved the actual piping problem or just made CAESAR II go green?
- Are the boundary conditions believable?
- Are nozzle load checks based on real vendor data?
- Are support recommendations practical?
- Are thermal growth consequences on operations/maintenance understood?
- Have occasional and upset conditions been seriously reviewed?

Generate comments in JSON format:
{{
    "document_info": {{
        "type": "Piping Stress Report",
        "report_number": "extracted",
        "revision": "extracted",
        "line_numbers_covered": ["list of lines"],
        "design_code": "ASME B31.3 / B31.1 / etc.",
        "software": "CAESAR II / AutoPIPE / Other"
    }},
    "summary": "Assessment of stress analysis quality, methodology soundness, and engineering judgment",
    "review_layers": {{
        "basis_documentation": "PASS/FAIL/PARTIAL",
        "model_accuracy": "PASS/FAIL/PARTIAL",
        "load_case_coverage": "PASS/FAIL/PARTIAL",
        "code_compliance": "PASS/FAIL/PARTIAL",
        "equipment_interface": "PASS/FAIL/PARTIAL",
        "support_engineering": "PASS/FAIL/PARTIAL",
        "practical_viability": "PASS/FAIL/PARTIAL"
    }},
    "stress_summary": {{
        "max_sustained_ratio": "actual/allowable",
        "max_expansion_ratio": "actual/allowable",
        "max_occasional_ratio": "actual/allowable",
        "overstress_locations": ["list if any"],
        "critical_nozzles": ["equipment with high loads"]
    }},
    "comments": [
        {{
            "no": 1,
            "location": "Node 150, Line 8\"-HC-101, Nozzle P-101A",
            "comment": "Detailed technical comment on stress/support/nozzle issue",
            "code_reference": "ASME B31.3 Para 302.3.5 / API 610 / Vendor limits",
            "severity": "HOLD/COMMENT/NOTE",
            "category": "Model/Load Cases/Code Compliance/Nozzle Loads/Supports/Flexibility/Practical"
        }}
    ],
    "nozzle_load_issues": ["Equipment where loads exceed vendor allowables"],
    "support_recommendations": ["Support changes required"],
    "critical_findings": ["HOLD items - safety or code violations"],
    "recommendations": [],
    "approval_status": "A-Approved/B-Approved with Comments/C-Resubmit/D-Rejected",
    "readiness_score": "0-100",
    "engineering_judgment_assessment": "Comment on whether analyst has truly solved the problem vs just passing software checks"
}}

This review requires deep engineering judgment. Do not accept overstresses, unrealistic boundary conditions, or missing load cases.
Return ONLY the JSON."""


# =============================================================================
# GENERAL PIPING REVIEW PROMPT
# =============================================================================

GENERAL_PIPING_REVIEW_PROMPT = """Review this piping document and generate detailed engineering comments.

PROJECT CONTEXT:
{project_context}

First, identify the document type from:
- P&ID (Piping & Instrumentation Diagram)
- Piping Isometric
- Piping GA/Layout
- Plot Plan/Layout
- Line List/Line Designation Table
- Piping Stress Report (CAESAR II, AutoPIPE, etc.)
- Piping Specification/Line Class
- Other piping document

Apply the Owner's Engineering Review Framework:

LAYER 1 - DOCUMENT CONTROL
□ Document number, revision, status code correct
□ Title block complete and accurate
□ Signatures present as required
□ Template/procedure compliance

LAYER 2 - DESIGN BASIS COMPLIANCE
□ Alignment with project design basis
□ Code of design correctly applied
□ Owner specifications followed

LAYER 3 - TECHNICAL ACCURACY
□ Engineering content correct
□ Calculations/assumptions valid
□ Dimensional accuracy

LAYER 4 - SAFETY & CODE COMPLIANCE
□ Process safety requirements met
□ Code stress/rating limits respected
□ Hazardous area considerations

LAYER 5 - INTERDISCIPLINARY CONSISTENCY
□ Alignment with related documents
□ Interface coordination complete

LAYER 6 - CONSTRUCTABILITY & OPERABILITY
□ Can be built as designed
□ Can be operated and maintained

SEVERITY CLASSIFICATION:
- HOLD: Safety/code/integrity issue - MUST resolve
- COMMENT: Technical deviation - requires response
- NOTE: Suggestion/clarification

Generate comments in JSON format:
{{
    "document_info": {{
        "type": "identified document type",
        "drawing_number": "extracted",
        "revision": "extracted",
        "title": "extracted"
    }},
    "summary": "Assessment of document quality and fitness for purpose",
    "review_layers": {{
        "document_control": "PASS/FAIL/PARTIAL",
        "design_basis": "PASS/FAIL/PARTIAL",
        "technical_accuracy": "PASS/FAIL/PARTIAL",
        "safety_compliance": "PASS/FAIL/PARTIAL",
        "consistency": "PASS/FAIL/PARTIAL",
        "operability": "PASS/FAIL/PARTIAL"
    }},
    "comments": [
        {{
            "no": 1,
            "location": "Specific location",
            "comment": "Detailed technical comment with action required",
            "code_reference": "ASME B31.3 / API / Project Spec",
            "severity": "HOLD/COMMENT/NOTE",
            "category": "Category"
        }}
    ],
    "critical_findings": [],
    "recommendations": [],
    "approval_status": "A-Approved/B-Approved with Comments/C-Resubmit/D-Rejected",
    "readiness_score": "0-100"
}}

Be thorough - generate 15-40 comments for proper engineering assurance.
Return ONLY the JSON."""


# =============================================================================
# HELPER FUNCTION
# =============================================================================

def get_review_prompt(doc_type: str, project_context: str = "") -> str:
    """Get the appropriate review prompt based on document type"""
    
    prompts = {
        # P&ID variants
        "pid": PID_REVIEW_PROMPT,
        "p&id": PID_REVIEW_PROMPT,
        "p_id": PID_REVIEW_PROMPT,
        "piping_and_instrumentation": PID_REVIEW_PROMPT,
        
        # Isometric variants
        "isometric": ISOMETRIC_REVIEW_PROMPT,
        "iso": ISOMETRIC_REVIEW_PROMPT,
        "piping_isometric": ISOMETRIC_REVIEW_PROMPT,
        "spool": ISOMETRIC_REVIEW_PROMPT,
        
        # GA/Layout variants
        "ga": PIPING_GA_REVIEW_PROMPT,
        "layout": PIPING_GA_REVIEW_PROMPT,
        "general_arrangement": PIPING_GA_REVIEW_PROMPT,
        "piping_layout": PIPING_GA_REVIEW_PROMPT,
        "piping_ga": PIPING_GA_REVIEW_PROMPT,
        
        # Plot Plan variants
        "plot_plan": PLOT_PLAN_REVIEW_PROMPT,
        "plot": PLOT_PLAN_REVIEW_PROMPT,
        "site_layout": PLOT_PLAN_REVIEW_PROMPT,
        "area_layout": PLOT_PLAN_REVIEW_PROMPT,
        
        # Line List variants
        "line_list": LINE_LIST_REVIEW_PROMPT,
        "linelist": LINE_LIST_REVIEW_PROMPT,
        "line_designation": LINE_LIST_REVIEW_PROMPT,
        "ldt": LINE_LIST_REVIEW_PROMPT,
        "line_designation_table": LINE_LIST_REVIEW_PROMPT,
        
        # Stress Report variants
        "stress": STRESS_REPORT_REVIEW_PROMPT,
        "stress_report": STRESS_REPORT_REVIEW_PROMPT,
        "stress_analysis": STRESS_REPORT_REVIEW_PROMPT,
        "caesar": STRESS_REPORT_REVIEW_PROMPT,
        "caesar_ii": STRESS_REPORT_REVIEW_PROMPT,
        "caesarii": STRESS_REPORT_REVIEW_PROMPT,
        "caesar2": STRESS_REPORT_REVIEW_PROMPT,
        "autopipe": STRESS_REPORT_REVIEW_PROMPT,
        "flexibility_analysis": STRESS_REPORT_REVIEW_PROMPT,
        "piping_stress": STRESS_REPORT_REVIEW_PROMPT,
    }
    
    # Normalize doc_type
    doc_type_normalized = doc_type.lower().strip().replace(" ", "_").replace("-", "_")
    
    # Get prompt or use general
    prompt_template = prompts.get(doc_type_normalized, GENERAL_PIPING_REVIEW_PROMPT)
    
    # Insert project context
    context_text = project_context if project_context else "No specific project context provided. Review against general industry standards and ASME B31.3 Process Piping requirements."
    
    return prompt_template.format(project_context=context_text)


def get_document_types():
    """Return list of supported document types for UI"""
    return [
        {"value": "pid", "label": "P&ID (Piping & Instrumentation Diagram)"},
        {"value": "isometric", "label": "Piping Isometric"},
        {"value": "ga", "label": "Piping General Arrangement / Layout"},
        {"value": "plot_plan", "label": "Plot Plan / Site Layout"},
        {"value": "line_list", "label": "Line List / Line Designation Table"},
        {"value": "stress_report", "label": "Piping Stress Analysis Report (CAESAR II)"},
        {"value": "auto", "label": "Auto-detect Document Type"},
    ]
