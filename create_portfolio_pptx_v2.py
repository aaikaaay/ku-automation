#!/usr/bin/env python3
"""
KU Automation Portfolio Presentation Generator v2
Creates a comprehensive, client-ready PowerPoint presentation for BD meeting (July 2026)
19 slides covering full service catalogue + BD opportunity
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
import os

# ─── Brand Colors ────────────────────────────────────────────────────────────
PRIMARY       = RGBColor(79, 70, 229)   # Indigo #4F46E5
PRIMARY_DARK  = RGBColor(49, 46, 129)   # Dark indigo #312E81
ACCENT        = RGBColor(139, 92, 246)  # Purple #8B5CF6
WHITE         = RGBColor(255, 255, 255)
DARK          = RGBColor(17, 24, 39)    # #111827
GRAY          = RGBColor(107, 114, 128) # #6B7280
LIGHT_BG      = RGBColor(249, 250, 251) # #F9FAFB
INDIGO_LIGHT  = RGBColor(238, 242, 255) # soft indigo tint
DARK_CARD     = RGBColor(30, 41, 59)    # dark card bg
DARK_BORDER   = RGBColor(55, 65, 81)    # dark card border
INDIGO_BADGE  = RGBColor(224, 231, 255) # badge bg
GREEN         = RGBColor(22, 163, 74)
RED_SOFT      = RGBColor(248, 113, 113)
AMBER         = RGBColor(251, 191, 36)
ORANGE_SOFT   = RGBColor(251, 146, 60)
LIGHT_ON_DARK = RGBColor(200, 200, 220)  # muted text on dark backgrounds
LINK_ON_DARK  = RGBColor(165, 180, 252)  # hyperlink color on dark backgrounds

# ─── Helpers ─────────────────────────────────────────────────────────────────

def solid(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color

def no_line(shape):
    shape.line.fill.background()

def border(shape, color, width_pt=0.75):
    shape.line.color.rgb = color
    shape.line.width = Pt(width_pt)

def txb(slide, left, top, width, height, text,
        size=12, bold=False, color=None, align=PP_ALIGN.LEFT, italic=False):
    if color is None:
        color = DARK
    tb = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    run = p.runs[0] if p.runs else p.add_run()
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return tb

def section_label(slide, text, x=0.5, y=0.38, color=PRIMARY):
    """Small-caps style section label e.g. '01 — ABOUT US'"""
    txb(slide, x, y, 5, 0.28, text, size=9, bold=True, color=color)

def slide_title(slide, text, x=0.5, y=0.66, color=DARK, size=38):
    txb(slide, x, y, 12, 0.85, text, size=size, bold=True, color=color)

def accent_quote_box(slide, quote_text, x, y, w, h):
    """Left-accent quote box in indigo tint"""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    solid(bg, INDIGO_LIGHT)
    no_line(bg)
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(0.08), Inches(h))
    solid(line, PRIMARY)
    no_line(line)
    txb(slide, x + 0.18, y + 0.1, w - 0.3, h - 0.2, quote_text, size=11, italic=True, color=PRIMARY_DARK)

def rounded_card(slide, x, y, w, h, fill_color, line_color=None):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    solid(card, fill_color)
    if line_color:
        border(card, line_color)
    else:
        no_line(card)
    return card

def dark_bg(slide, prs):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    solid(bg, DARK)
    no_line(bg)

def light_bg(slide, prs):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    solid(bg, LIGHT_BG)
    no_line(bg)

def popular_badge(slide, x, y, bg_color=None, text_color=WHITE, label="MOST POPULAR"):
    if bg_color is None:
        bg_color = PRIMARY
    b = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(1.85), Inches(0.3))
    solid(b, bg_color)
    no_line(b)
    txb(slide, x + 0.05, y + 0.02, 1.75, 0.27, label, size=7, bold=True, color=text_color, align=PP_ALIGN.CENTER)

def txb_link(slide, left, top, width, height, text, url,
             size=12, bold=False, color=None, align=PP_ALIGN.LEFT):
    """Text box with a clickable hyperlink."""
    if color is None:
        color = PRIMARY
    tb = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.underline = True
    run.hyperlink.address = url
    return tb

# ─── Presentation builder ─────────────────────────────────────────────────────

def create_presentation():
    prs = Presentation()
    prs.slide_width  = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 1 — COVER
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)

    bg = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    solid(bg, PRIMARY_DARK); no_line(bg)

    # Subtle gradient strip at top
    strip = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.35))
    solid(strip, PRIMARY); no_line(strip)

    # KU logo — actual image (cover)
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
    if os.path.exists(logo_path):
        sl.shapes.add_picture(logo_path, Inches(5.917), Inches(1.5), Inches(1.5), Inches(1.5))
    else:
        # Fallback text box if logo not found
        logo_bg = rounded_card(sl, 5.9, 1.45, 1.53, 1.53, WHITE)
        txb(sl, 5.9, 1.75, 1.53, 0.85, "KU", size=40, bold=True, color=PRIMARY, align=PP_ALIGN.CENTER)

    # Title block
    txb(sl, 0, 3.25, 13.333, 0.95, "KU Automation",
        size=54, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txb(sl, 0, 4.18, 13.333, 0.55,
        "AI-Powered Owner's Engineering, Automation & Voice",
        size=22, bold=False, color=RGBColor(200, 200, 230), align=PP_ALIGN.CENTER)

    # Purple divider
    div = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(5.2), Inches(4.88), Inches(2.9), Inches(0.055))
    solid(div, ACCENT); no_line(div)

    txb(sl, 0, 5.05, 13.333, 0.4,
        "Corporate Portfolio & Capabilities  —  July 2026",
        size=14, color=RGBColor(180, 180, 210), align=PP_ALIGN.CENTER)

    txb(sl, 0, 7.0, 13.333, 0.35,
        "Confidential  ·  Prepared for Client Meeting  ·  13 July 2026",
        size=9, color=RGBColor(100, 100, 140), align=PP_ALIGN.CENTER)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 2 — ABOUT US
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    section_label(sl, "01 — ABOUT US")
    slide_title(sl, "Who We Are")

    # Founder card (left)
    rounded_card(sl, 0.5, 1.65, 5.9, 3.1, LIGHT_BG)
    txb(sl, 0.85, 1.85, 5.2, 0.4, "Kingsley Uzowulu", size=20, bold=True, color=DARK)
    txb(sl, 0.85, 2.27, 5.2, 0.3, "Founder & Principal Engineer", size=12, bold=False, color=PRIMARY)
    txb(sl, 0.85, 2.62, 5.2, 1.8,
        "Chartered Engineer (CEng MIMechE) with 21+ years of hands-on experience "
        "in oil & gas, EPC projects, and manufacturing across the UK, Europe, and "
        "Middle East. Domain expert in piping, rotating equipment, process safety, "
        "and AI-powered engineering automation.",
        size=10.5, color=GRAY)

    # Credential tags
    for idx, tag_text in enumerate(["CEng  MIMechE", "21+ yrs O&G / EPC", "AI / ML Specialist"]):
        tx = 0.85 + idx * 1.9
        t = rounded_card(sl, tx, 4.35, 1.75, 0.3, INDIGO_BADGE)
        txb(sl, tx + 0.08, 4.37, 1.6, 0.26, tag_text, size=8.5, bold=False, color=PRIMARY)

    # Right column — mission, industries, coverage
    rounded_card(sl, 6.8, 1.65, 6.0, 1.2, LIGHT_BG)
    txb(sl, 7.1, 1.82, 5.5, 0.35, "🎯  Our Mission", size=13, bold=True, color=DARK)
    txb(sl, 7.1, 2.2, 5.5, 0.6,
        "Bridge cutting-edge AI with practical engineering workflows — making "
        "principal-level review and deep automation accessible to every project team.",
        size=10.5, color=GRAY)

    rounded_card(sl, 6.8, 2.98, 6.0, 1.5, LIGHT_BG)
    txb(sl, 7.1, 3.13, 5.5, 0.35, "🏭  Industries Served", size=13, bold=True, color=DARK)
    txb(sl, 7.1, 3.53, 5.5, 0.9,
        "• Oil & Gas (Upstream · Midstream · Downstream)\n"
        "• EPC Contractors & Engineering Consultancies\n"
        "• Chemical, Power Generation & Manufacturing",
        size=10.5, color=GRAY)

    txb(sl, 6.8, 4.62, 6.0, 0.3, "🌍  Geographic Coverage", size=12, bold=True, color=DARK)
    txb(sl, 6.8, 4.97, 6.0, 0.3, "UK  •  Europe  •  Middle East  •  Global Remote", size=11, color=GRAY)

    # Quote box
    accent_quote_box(sl, '"We bridge the gap between cutting-edge AI and practical engineering workflows."',
                     0.5, 5.42, 12.3, 0.88)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 3 — THE PROBLEM  (dark bg)
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    dark_bg(sl, prs)

    section_label(sl, "02 — THE CHALLENGE", color=RGBColor(129, 140, 248))
    slide_title(sl, "The Problem We Solve", color=WHITE)

    # 3 stat cards
    stats = [
        ("60%", "of senior engineer time\nspent on document admin", RED_SOFT),
        ("$400–$800", "typical consultant cost\nper deliverable review", AMBER),
        ("4–6 hrs", "to manually review\na single tech spec", ORANGE_SOFT),
    ]
    for i, (num, desc, col) in enumerate(stats):
        x = 0.5 + i * 4.28
        rounded_card(sl, x, 1.75, 3.95, 1.9, DARK_CARD, DARK_BORDER)
        txb(sl, x + 0.3, 1.95, 3.35, 0.75, num, size=38, bold=True, color=col)
        txb(sl, x + 0.3, 2.75, 3.35, 0.75, desc, size=10.5, color=RGBColor(200, 205, 215))

    # Pain-points panel
    rounded_card(sl, 0.5, 3.88, 12.333, 2.9, DARK_CARD, DARK_BORDER)
    txb(sl, 0.85, 4.08, 10, 0.38, "Common Pain Points We Address", size=15, bold=True, color=WHITE)
    txb(sl, 0.85, 4.58, 5.6, 1.9,
        "✗  Manual document review bottlenecks\n"
        "✗  Inconsistent extraction from drawings\n"
        "✗  Delayed RFQs — losing contracts",
        size=11.5, color=RGBColor(200, 210, 220))
    txb(sl, 6.7, 4.58, 5.6, 1.9,
        "✗  Knowledge trapped in experts' heads\n"
        "✗  Contractor deliverable review backlog\n"
        "✗  Compliance documentation burden",
        size=11.5, color=RGBColor(200, 210, 220))

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 4 — WHAT WE DO — THREE PRODUCT LINES
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    section_label(sl, "03 — WHAT WE DO")
    slide_title(sl, "Three Product Lines")
    txb(sl, 0.5, 1.5, 10, 0.35, "End-to-end AI capabilities — from document review to live voice agents and custom pipelines.", size=12, color=GRAY)

    product_cards = [
        ("🔍", "KU Review Portal",
         "AI Owner's Engineer for 22 deliverable types",
         "LIVE at services.ku-automation.com",
         "22 live reviewers · 5 disciplines · Results in 4 minutes · From $19/review",
         PRIMARY, INDIGO_LIGHT),
        ("☎️", "KU Voice",
         "AI voice agents that handle real inbound & outbound calls",
         "LIVE demo: +1 (740) 265-2849",
         "Sub-second latency · ElevenLabs natural voice · Arabic + English · CRM streaming",
         RGBColor(139, 92, 246), RGBColor(245, 243, 255)),
        ("⚙️", "Bespoke AI Automation",
         "Custom pipelines built to your workflows",
         "P&ID extraction · Datasheet parsers · RFQ analysers · Chatbots",
         "SharePoint · SAP · AVEVA / Hexagon · REST API · Fully tailored",
         RGBColor(16, 185, 129), RGBColor(236, 253, 245)),
    ]
    for i, (icon, title, sub, live, detail, col, bg_col) in enumerate(product_cards):
        x = 0.5 + i * 4.28
        rounded_card(sl, x, 1.95, 3.95, 4.98, bg_col, col)
        txb(sl, x + 0.25, 2.12, 0.65, 0.65, icon, size=28, color=DARK)
        txb(sl, x + 0.25, 2.82, 3.45, 0.42, title, size=16, bold=True, color=DARK)
        txb(sl, x + 0.25, 3.28, 3.45, 0.55, sub, size=10.5, color=GRAY)
        live_tag = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                       Inches(x + 0.25), Inches(3.93), Inches(3.45), Inches(0.28))
        solid(live_tag, col); no_line(live_tag)
        txb(sl, x + 0.3, 3.95, 3.35, 0.24, live, size=8, bold=True, color=WHITE)
        txb(sl, x + 0.25, 4.3, 3.45, 1.45, detail, size=10, color=DARK)

    # Slide 4 — clickable hyperlinks under each product card
    txb_link(sl, 0.75, 6.6, 3.45, 0.35,
             "→ services.ku-automation.com",
             "https://services.ku-automation.com",
             size=9, bold=True, color=PRIMARY)
    txb_link(sl, 5.03, 6.6, 3.45, 0.35,
             "→ Call +1 (740) 265-2849",
             "tel:+17402652849",
             size=9, bold=True, color=RGBColor(139, 92, 246))
    txb_link(sl, 9.31, 6.6, 3.45, 0.35,
             "→ www.ku-automation.com",
             "https://www.ku-automation.com",
             size=9, bold=True, color=RGBColor(16, 185, 129))

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 5 — KU REVIEW PORTAL — OVERVIEW
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    section_label(sl, "04 — KU REVIEW PORTAL")
    slide_title(sl, "KU Review Portal")
    txb(sl, 0.5, 1.5, 12.333, 0.35,
        "Principal-level engineering review, delivered by AI in minutes, not weeks.",
        size=12.5, italic=True, color=PRIMARY)

    # Key stats row
    kstats = [
        ("22", "Live Reviewers", PRIMARY),
        ("5", "Disciplines", ACCENT),
        ("4 min", "Delivery time", GREEN),
        ("From\n$19", "Per review", RGBColor(245, 158, 11)),
        ("$250–$800", "Consultant\nequivalent", RED_SOFT),
    ]
    for i, (val, lab, col) in enumerate(kstats):
        x = 0.5 + i * 2.52
        rounded_card(sl, x, 1.95, 2.35, 1.35, LIGHT_BG)
        txb(sl, x + 0.12, 2.08, 2.1, 0.58, val, size=28, bold=True, color=col, align=PP_ALIGN.CENTER)
        txb(sl, x + 0.12, 2.68, 2.1, 0.52, lab, size=9, color=GRAY, align=PP_ALIGN.CENTER)

    # 4-step flow
    txb(sl, 0.5, 3.48, 5, 0.3, "How It Works — 4-Step Flow", size=13, bold=True, color=DARK)
    steps = [
        ("①", "Upload PDF", "Any deliverable type"),
        ("②", "AI Reviews", "vs codes & standards"),
        ("③", "Report + Excel", "PDF + comment register"),
        ("④", "Free Preview", "5 findings before you pay"),
    ]
    for i, (num, head, sub) in enumerate(steps):
        x = 0.5 + i * 3.2
        rounded_card(sl, x, 3.88, 3.0, 2.72, INDIGO_LIGHT)
        txb(sl, x + 0.18, 4.0, 2.65, 0.52, num, size=26, bold=True, color=PRIMARY, align=PP_ALIGN.CENTER)
        txb(sl, x + 0.15, 4.57, 2.72, 0.38, head, size=13, bold=True, color=DARK, align=PP_ALIGN.CENTER)
        txb(sl, x + 0.15, 4.99, 2.72, 0.52, sub, size=10, color=GRAY, align=PP_ALIGN.CENTER)
        if i < 3:
            arr = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x + 3.05), Inches(5.1), Inches(0.18), Inches(0.1))
            solid(arr, ACCENT); no_line(arr)

    # Slide 5 — link at bottom
    txb_link(sl, 0.5, 6.8, 12.333, 0.38,
             "→ Try live at services.ku-automation.com",
             "https://services.ku-automation.com",
             size=11, bold=True, color=PRIMARY, align=PP_ALIGN.CENTER)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 6 — REVIEW PORTAL — DISCIPLINE COVERAGE
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    section_label(sl, "05 — DISCIPLINE COVERAGE")
    slide_title(sl, "What's Live: 22 Reviewers Across 5 Disciplines")

    disciplines = [
        ("Piping", "11 LIVE", PRIMARY,
         "P&ID · Isometric · Line List · Caesar II Stress · GA Drawing · "
         "Plot Plan · Valve List · PMS · Piping Class Sheet · MTO/BoQ · Pipe Support"),
        ("Process", "4 LIVE", RGBColor(16, 185, 129),
         "P&ID · PFD · Calculations & Sizing · Reports & Philosophies"),
        ("Mechanical", "2 LIVE", RGBColor(245, 158, 11),
         "Pump Datasheet · Compressor Datasheet"),
        ("Civil", "2 LIVE", RGBColor(239, 68, 68),
         "Foundation Drawing · Concrete Structure"),
        ("Structural", "2 LIVE", RGBColor(139, 92, 246),
         "Steel Structure · Pipe Rack"),
    ]

    # 3-top + 2-bottom layout
    positions = [(0.5, 1.72), (4.78, 1.72), (9.06, 1.72),
                 (2.14, 4.35), (7.1, 4.35)]
    w, h = 3.9, 2.4

    for (x, y), (disc, count, col, items) in zip(positions, disciplines):
        rounded_card(sl, x, y, w, h, LIGHT_BG, col)
        txb(sl, x + 0.2, y + 0.12, w - 0.4, 0.35, disc, size=15, bold=True, color=DARK)
        cnt_box = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                      Inches(x + 0.2), Inches(y + 0.52), Inches(1.1), Inches(0.27))
        solid(cnt_box, col); no_line(cnt_box)
        txb(sl, x + 0.23, y + 0.53, 1.05, 0.24, count, size=8.5, bold=True, color=WHITE)
        txb(sl, x + 0.2, y + 0.9, w - 0.4, h - 1.0, items, size=9.5, color=GRAY)

    # Grand total badge
    rounded_card(sl, 5.5, 7.02, 2.33, 0.38, PRIMARY_DARK)
    txb(sl, 5.5, 7.04, 2.33, 0.36, "  22 LIVE REVIEWERS  TOTAL",
        size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    # Slide 6 — link at bottom
    txb_link(sl, 0.5, 6.7, 4.8, 0.32,
             "→ Full catalogue at services.ku-automation.com/services",
             "https://services.ku-automation.com/services",
             size=9, bold=True, color=PRIMARY)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 7 — WHAT EACH REVIEW DELIVERS
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    section_label(sl, "06 — REVIEW ANATOMY")
    slide_title(sl, "What Each Review Delivers")

    # Sample findings card (left)
    rounded_card(sl, 0.5, 1.65, 6.0, 4.25, INDIGO_LIGHT, PRIMARY)
    txb(sl, 0.78, 1.82, 5.45, 0.35, "Sample Output — P&ID Review", size=12, bold=True, color=PRIMARY)
    txb(sl, 0.78, 2.22, 5.45, 0.32, "🔴 11 CRITICAL   🟠 8 MAJOR   🟡 3 MINOR", size=11, bold=True, color=DARK)
    txb(sl, 0.78, 2.6, 5.45, 0.28, "Recommendation D (Reject) — Return for revision", size=10.5, color=DARK)
    txb(sl, 0.78, 2.97, 5.45, 0.28, "21-page PDF report  +  Multi-sheet Excel register", size=10.5, color=GRAY)
    txb(sl, 0.78, 3.32, 5.45, 0.28, "API cost: $0.18  ·  Delivered in: 4 minutes", size=10.5, color=GREEN)

    # Divider line
    div2 = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.78), Inches(3.72), Inches(5.45), Inches(0.04))
    solid(div2, ACCENT); no_line(div2)

    deliverables = [
        "Severity ratings: CRITICAL / MAJOR / MINOR / OBSERVATION",
        "Code references: ASME, API, NACE, ACI, AISC, ISO, IEC, NFPA…",
        "Explicit recommendation (A / B / C / D)",
        "PDF review report — professionally formatted",
        "Excel comment register — multi-sheet, sortable",
        "Free 5-finding preview before you pay",
    ]
    for j, d in enumerate(deliverables):
        txb(sl, 0.88, 3.85 + j * 0.32, 5.25, 0.3, f"✓  {d}", size=10.5, color=DARK)

    # Right panel
    txb(sl, 6.85, 1.65, 6.0, 0.38, "Why This Matters", size=15, bold=True, color=DARK)
    right_bullets = [
        ("🔴", "CRITICAL", "Immediate safety or code violation — must be resolved before approval"),
        ("🟠", "MAJOR", "Significant non-conformance — design or specification conflict"),
        ("🟡", "MINOR", "Deviation noted — low risk but should be addressed"),
        ("🔵", "OBSERVATION", "Advisory note — best-practice suggestion"),
    ]
    for j, (ico, lab, desc) in enumerate(right_bullets):
        y0 = 2.12 + j * 1.25
        rounded_card(sl, 6.85, y0, 5.9, 1.1, LIGHT_BG)
        txb(sl, 7.08, y0 + 0.1, 0.38, 0.38, ico, size=18, color=DARK)
        txb(sl, 7.52, y0 + 0.1, 4.95, 0.35, lab, size=12, bold=True, color=DARK)
        txb(sl, 7.52, y0 + 0.48, 4.95, 0.52, desc, size=10, color=GRAY)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 8 — CODES & STANDARDS
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    section_label(sl, "07 — CODES & STANDARDS")
    slide_title(sl, "Standards We Enforce")
    txb(sl, 0.5, 1.5, 12.333, 0.32, "KU reviewers check against the standards your client expects — not a generic checklist.", size=11.5, italic=True, color=GRAY)

    groups = [
        ("Piping & Mechanical", PRIMARY, RGBColor(224, 231, 255),
         "ASME B31.3 · B31.1 · B16.5 · B16.9 · B16.11 · B16.20 · B16.34\n"
         "API 6D · API 520/521/526 · API 600/602/607\n"
         "API 610 · 617 · 618 · 619 · 670 · 671 · 682 · 692 · ISO 15848"),
        ("Process & Safety", RGBColor(16, 185, 129), RGBColor(209, 250, 229),
         "API RP 14C/14E · API 520/521 · API 752/753 · API RP 754\n"
         "IEC 61508 / 61511 / 62443 · ISA 5.1 · ISA 18.2\n"
         "HAZOP / LOPA / SIL methodology"),
        ("Structural & Civil", RGBColor(245, 158, 11), RGBColor(254, 243, 199),
         "AISC 360 · AISC 341 · ASCE 7 · ACI 318 · ACI 224R · ACI 360R\n"
         "AWS D1.1 · EN 1992-1-1 · EN 1993-1-1 · IBC 2021 · UFC 3-340-02"),
        ("Materials & Corrosion", RGBColor(239, 68, 68), RGBColor(254, 226, 226),
         "NACE MR0175 / ISO 15156 · ASTM G88 · API 941\n"
         "MSS-SP-44 / 58 / 69 / 75 / 97"),
        ("Fire & Layout", RGBColor(168, 85, 247), RGBColor(243, 232, 255),
         "NFPA 30 · NFPA 2 · NFPA 58\n"
         "IP 19 / EI Model Code · OISD 116 · API 2218"),
    ]

    positions_s8 = [(0.5, 1.9), (6.95, 1.9), (0.5, 4.12), (4.72, 4.12), (8.94, 4.12)]
    dims = [(6.1, 1.95), (6.1, 1.95), (3.9, 2.78), (3.9, 2.78), (3.9, 2.78)]

    for (x, y), (w2, h2), (grp, col, bg_col, stds) in zip(positions_s8, dims, groups):
        rounded_card(sl, x, y, w2, h2, bg_col, col)
        txb(sl, x + 0.2, y + 0.12, w2 - 0.4, 0.32, grp, size=12, bold=True, color=DARK)
        txb(sl, x + 0.2, y + 0.52, w2 - 0.4, h2 - 0.65, stds, size=9.5, color=DARK)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 9 — KU VOICE OVERVIEW
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    section_label(sl, "08 — KU VOICE")
    slide_title(sl, "KU Voice — AI That Answers Your Phone")

    txb(sl, 0.5, 1.5, 12.333, 0.32,
        "AI voice agents that handle real inbound & outbound calls — indistinguishable from a trained human agent.",
        size=11.5, italic=True, color=GRAY)

    # Live demo highlight
    demo_card = rounded_card(sl, 0.5, 1.88, 12.333, 1.08, INDIGO_LIGHT, PRIMARY)
    txb(sl, 0.78, 2.0, 12.0, 0.35, "📞  Live Demo Line — Call Now:", size=13, bold=True, color=PRIMARY)
    txb(sl, 0.78, 2.38, 12.0, 0.48,
        "+1 (740) 265-2849  —  Mythos Kouzina, Greek restaurant AI agent (Dubai)",
        size=12.5, color=DARK)

    # Feature cards
    features_v = [
        ("⚡", "Sub-second\nLatency", "Near-instant voice response; no awkward pauses"),
        ("🗣️", "Natural Voice", "ElevenLabs 'Willa' — natural British female voice"),
        ("🌍", "Multilingual", "Arabic + English; handles accents & interruptions"),
        ("📊", "CRM Streaming", "Calls stream live to your CRM or Google Sheets"),
    ]
    for i, (ico, head, desc) in enumerate(features_v):
        x = 0.5 + i * 3.2
        rounded_card(sl, x, 3.1, 3.0, 1.55, LIGHT_BG)
        txb(sl, x + 0.15, 3.2, 0.5, 0.5, ico, size=22, color=DARK)
        txb(sl, x + 0.72, 3.22, 2.1, 0.45, head, size=11.5, bold=True, color=DARK)
        txb(sl, x + 0.15, 3.72, 2.7, 0.85, desc, size=10, color=GRAY)

    # Use cases
    txb(sl, 0.5, 4.78, 4, 0.32, "Use Cases", size=13, bold=True, color=DARK)
    use_cases = [
        "🍽️  Restaurant order-taking",
        "📅  Appointment booking",
        "🎯  Lead qualification",
        "🏢  After-hours reception",
        "👋  Front-desk assistant",
    ]
    for j, uc in enumerate(use_cases):
        col_j = j // 3
        row_j = j % 3
        txb(sl, 0.5 + col_j * 4.0, 5.12 + row_j * 0.38, 3.8, 0.35, uc, size=11, color=DARK)

    # BD stat box
    rounded_card(sl, 8.6, 4.72, 4.5, 2.2, PRIMARY_DARK)
    txb(sl, 8.85, 4.88, 4.1, 0.38, "Market Opportunity", size=13, bold=True, color=WHITE)
    txb(sl, 8.85, 5.32, 4.1, 1.45,
        "The global call-centre outsourcing market exceeds $500B. "
        "AI voice agents are the fastest-growing AI deployment category "
        "in 2026 — with zero marginal cost per additional call.",
        size=10, color=RGBColor(200, 210, 230))

    # Slide 9 — hyperlinks
    txb_link(sl, 0.5, 6.82, 5.5, 0.38,
             "→ CALL LIVE NOW: +1 (740) 265-2849",
             "tel:+17402652849",
             size=12, bold=True, color=PRIMARY)
    txb_link(sl, 6.5, 6.82, 5.5, 0.38,
             "→ www.ku-automation.com",
             "https://www.ku-automation.com",
             size=12, bold=True, color=PRIMARY)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 10 — BESPOKE AI AUTOMATION
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    section_label(sl, "09 — BESPOKE AI AUTOMATION")
    slide_title(sl, "Custom AI Pipelines")
    txb(sl, 0.5, 1.5, 12, 0.32,
        "Beyond the portal — fully custom AI pipelines designed around your existing workflows and systems.",
        size=11.5, color=GRAY, italic=True)

    bespoke_cards = [
        ("📊", "P&ID Data Extraction",
         "Extract equipment, valves, instruments & tags to structured Excel — automated pipeline.",
         "70% time reduction"),
        ("📄", "Datasheet Parser",
         "Parse technical datasheets into structured database records with 85%+ accuracy gain.",
         "85% accuracy gain"),
        ("⚡", "RFQ / Tender Analyser",
         "AI scans tenders, identifies missed line items, flags scope gaps — 3× faster bid response.",
         "3× faster response"),
        ("🤖", "Engineering Chatbot",
         "RAG chatbot trained on your standards, past projects, and SOPs — available 24/7.",
         "24/7 knowledge access"),
        ("🧠", "Knowledge Extraction",
         "Turn 20 years of expert know-how into a queryable, searchable knowledge base.",
         "Capture expert IP"),
        ("🔌", "Custom Integrations",
         "Connect to SharePoint, SAP, AVEVA/Hexagon, or any REST API — bespoke connectors.",
         "Seamless integration"),
    ]

    colors_b = [PRIMARY, RGBColor(16, 185, 129), RGBColor(168, 85, 247),
                RGBColor(6, 182, 212), RGBColor(245, 158, 11), RGBColor(239, 68, 68)]

    for i, (ico, head, desc, result) in enumerate(bespoke_cards):
        row = i // 3; col_i = i % 3
        x = 0.5 + col_i * 4.28
        y = 1.88 + row * 2.5
        rounded_card(sl, x, y, 3.95, 2.28, LIGHT_BG)
        txb(sl, x + 0.18, y + 0.12, 0.55, 0.55, ico, size=24, color=DARK)
        txb(sl, x + 0.18, y + 0.7, 3.55, 0.38, head, size=13, bold=True, color=DARK)
        txb(sl, x + 0.18, y + 1.12, 3.55, 0.72, desc, size=10, color=GRAY)
        txb(sl, x + 0.18, y + 1.88, 3.55, 0.3, result, size=10.5, bold=True, color=colors_b[i])

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 11 — LIVE DEMOS
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    light_bg(sl, prs)
    section_label(sl, "10 — LIVE DEMOS", color=PRIMARY)
    slide_title(sl, "What You Can See Tomorrow", color=DARK)
    txb(sl, 0.5, 1.5, 12, 0.32, "No signup required for the preview — everything below is production-live right now.", size=11.5, color=GRAY)

    demos_list = [
        ("🌐", "services.ku-automation.com",
         "Full marketplace — 22 reviewers browsable by discipline. Upload a P&ID and get a 5-finding free preview in 4 minutes.",
         PRIMARY, "https://services.ku-automation.com"),
        ("📄", "Upload a Real Document",
         "Bring any P&ID, isometric, or datasheet. We'll run a live review and walk through the PDF + Excel output together.",
         RGBColor(16, 185, 129), None),
        ("📞", "+1 (740) 265-2849",
         "Call the KU Voice demo live in the meeting — Mythos Kouzina Greek restaurant AI. Place a real order or ask about the menu.",
         ACCENT, "tel:+17402652849"),
        ("💻", "www.ku-automation.com",
         "Corporate site + 38+ technical blog posts on engineering AI. Shows content authority and pipeline depth.",
         RGBColor(245, 158, 11), "https://www.ku-automation.com"),
        ("📊", "www.ku-automation.com/portfolio-presentation.html",
         "Web version of this deck — interactive HTML for sharing with decision-makers who weren't in the room.",
         RGBColor(239, 68, 68), "https://www.ku-automation.com/portfolio-presentation.html"),
        ("📝", "www.ku-automation.com/blog",
         "38+ engineering AI blog posts — demonstrates domain authority and content depth to technical audiences.",
         RGBColor(20, 184, 166), "https://www.ku-automation.com/blog"),
        ("🎮", "www.ku-automation.com/demos",
         "Interactive demos — live product showcases you can explore without login.",
         RGBColor(168, 85, 247), "https://www.ku-automation.com/demos"),
    ]

    for i, (ico, head, desc, col, url) in enumerate(demos_list):
        y = 1.88 + i * 0.77
        rounded_card(sl, 0.5, y, 12.333, 0.68, WHITE, col)
        txb(sl, 0.75, y + 0.08, 0.42, 0.42, ico, size=18, color=col)
        # Clickable header text when URL is available
        if url:
            txb_link(sl, 1.28, y + 0.06, 4.5, 0.32, head, url,
                     size=12, bold=True, color=col)
        else:
            txb(sl, 1.28, y + 0.06, 4.5, 0.32, head, size=12, bold=True, color=DARK)
        txb(sl, 1.28, y + 0.38, 10.8, 0.3, desc, size=9.5, color=GRAY)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 12 — DEPLOYMENT OPTIONS
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    section_label(sl, "11 — DEPLOYMENT")
    slide_title(sl, "Flexible Deployment Options")

    deployments = [
        ("☁️", "Cloud SaaS", "Fully managed on secure cloud",
         "✓  No IT infrastructure required\n✓  Automatic updates & maintenance\n✓  Web browser access\n✓  API integration available\n✓  99.9% uptime SLA",
         RGBColor(59, 130, 246), RGBColor(219, 234, 254), True),
        ("🔐", "Private Cloud", "Dedicated VPC instance in your region",
         "✓  Dedicated resources\n✓  Data stays in your region\n✓  VPC integration\n✓  Custom security policies\n✓  SSO / SAML support",
         ACCENT, RGBColor(243, 232, 255), False),
        ("🏢", "On-Premise", "Full deployment in your data centre",
         "✓  Complete data control\n✓  Air-gapped option available\n✓  Integrates with existing systems\n✓  Custom hardware specs\n✓  Perpetual licence option",
         GRAY, RGBColor(243, 244, 246), False),
    ]

    for i, (ico, title, sub, feats, col, bg_col, pop) in enumerate(deployments):
        x = 0.5 + i * 4.28
        rounded_card(sl, x, 1.62, 3.95, 4.65, bg_col, col)
        if pop:
            popular_badge(sl, x + 1.05, 1.38, col)
        txb(sl, x + 0.25, 1.78, 0.6, 0.6, ico, size=26, color=DARK)
        txb(sl, x + 0.25, 2.44, 3.45, 0.4, title, size=16, bold=True, color=DARK)
        txb(sl, x + 0.25, 2.88, 3.45, 0.35, sub, size=10, color=GRAY)
        txb(sl, x + 0.25, 3.28, 3.45, 2.8, feats, size=10.5, color=DARK)

    int_row = rounded_card(sl, 0.5, 6.42, 12.333, 0.78, INDIGO_LIGHT)
    txb(sl, 0.82, 6.56, 12.0, 0.5,
        "🔌  Integrations:  SharePoint  ·  SAP  ·  AVEVA / Hexagon  ·  REST API  ·  Custom connectors",
        size=11, color=DARK)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 13 — SECURITY & COMPLIANCE  (dark)
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    dark_bg(sl, prs)
    section_label(sl, "12 — SECURITY & COMPLIANCE", color=RGBColor(129, 140, 248))
    slide_title(sl, "Enterprise-Grade Security", color=WHITE)

    # Two big cards
    rounded_card(sl, 0.5, 1.65, 5.9, 3.38, DARK_CARD, DARK_BORDER)
    txb(sl, 0.82, 1.82, 5.3, 0.38, "🔒  Data Protection", size=15, bold=True, color=WHITE)
    txb(sl, 0.82, 2.28, 5.3, 2.6,
        "✓  AES-256 encryption at rest; TLS 1.3 in transit\n"
        "✓  Tenant-isolated databases — no data co-mingling\n"
        "✓  Configurable no-retention — data deleted post-review\n"
        "✓  Data residency: UK / EU / UAE — your choice\n"
        "✓  Zero-data-retention AI endpoints — not used for training\n"
        "✓  Isolated compute per tenant",
        size=11, color=RGBColor(180, 220, 180))

    rounded_card(sl, 6.8, 1.65, 6.0, 3.38, DARK_CARD, DARK_BORDER)
    txb(sl, 7.08, 1.82, 5.5, 0.38, "👤  Access Control", size=15, bold=True, color=WHITE)
    txb(sl, 7.08, 2.28, 5.5, 2.6,
        "✓  SAML / OAuth 2.0 / Azure AD SSO\n"
        "✓  Role-based permissions — granular control\n"
        "✓  MFA required for all user accounts\n"
        "✓  Full audit logs — complete activity trails\n"
        "✓  IP allowlisting available\n"
        "✓  Configurable session timeouts",
        size=11, color=RGBColor(180, 220, 180))

    # IP/data-handling line
    rounded_card(sl, 0.5, 5.15, 12.333, 0.72, DARK_CARD, DARK_BORDER)
    txb(sl, 0.78, 5.28, 12.0, 0.52,
        "🔑  Your drawings never leave secure infrastructure. AI providers are configured with zero-data-retention "
        "endpoints. You own all inputs and outputs.",
        size=10.5, color=WHITE)

    # Compliance bar
    rounded_card(sl, 0.5, 6.0, 12.333, 0.78, DARK_CARD, DARK_BORDER)
    txb(sl, 0.82, 6.18, 12.0, 0.5,
        "🇬🇧  UK GDPR     🔐  ISO 27001 (in progress)     ☁️  SOC 2 Type II (in progress)"
        "     🇦🇪  UAE PDPL     🏭  API/ISO/ASME Industry Standards",
        size=10.5, color=WHITE)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 14 — SUPPORT & GOVERNANCE
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    section_label(sl, "13 — SUPPORT & GOVERNANCE")
    slide_title(sl, "Support Tiers & SOP Governance")

    tiers = [
        ("Standard", "Included with all plans",
         "✓  Email support (24 hr response)\n✓  Documentation & knowledge base\n✓  Quarterly software updates\n✓  Bug fixes & security patches",
         LIGHT_BG, DARK, None),
        ("Priority", "Recommended for production",
         "✓  4-hour response time\n✓  Phone & video call support\n✓  Dedicated account manager\n✓  Monthly check-in calls\n✓  Priority feature requests",
         INDIGO_LIGHT, DARK, PRIMARY),
        ("Enterprise", "Mission-critical deployments",
         "✓  1-hour response (24/7)\n✓  On-site support available\n✓  Custom SLA agreements\n✓  Dedicated engineering team\n✓  Quarterly business reviews",
         DARK, WHITE, None),
    ]

    for i, (name, desc, feats, bg_col, tc, brd) in enumerate(tiers):
        x = 0.5 + i * 4.28
        rounded_card(sl, x, 1.62, 3.95, 3.62, bg_col, brd)
        txb(sl, x + 0.28, 1.82, 3.4, 0.42, name, size=17, bold=True, color=tc)
        txb(sl, x + 0.28, 2.28, 3.4, 0.32, desc, size=10, color=GRAY if i < 2 else RGBColor(160, 170, 190))
        txb(sl, x + 0.28, 2.72, 3.4, 2.35, feats, size=10.5, color=tc)

    # SOP governance box
    rounded_card(sl, 0.5, 5.42, 12.333, 1.78, INDIGO_LIGHT, PRIMARY)
    txb(sl, 0.78, 5.58, 12.0, 0.35, "📋  SOP Governance — Internal Quality Framework", size=13, bold=True, color=PRIMARY)
    txb(sl, 0.78, 6.0, 12.0, 1.1,
        "8 documented SOPs (SOP-01 to SOP-08) governing: model selection & prompt versioning · data handling "
        "& retention · incident response & escalation · full audit trail · disclosure to end-users · "
        "hallucination detection checks · code-reference validation · change-control for reviewers.",
        size=10.5, color=DARK)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 15 — ENGAGEMENT MODEL
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    light_bg(sl, prs)
    section_label(sl, "14 — ENGAGEMENT MODEL", color=PRIMARY)
    slide_title(sl, "How We Work Together", color=DARK)

    phases = [
        ("1", "Week 1–2",  "Discovery & Assessment",
         "Understand your workflows, review sample deliverables, IT & security assessment"),
        ("2", "Week 3–4",  "Proof of Concept",
         "Configure with your real data; pilot with a live project team; measure results"),
        ("3", "Week 5–8",  "Production Deployment",
         "Full deployment, system integration, user training, go-live sign-off"),
        ("✓", "Ongoing",   "Continuous Support & Scale",
         "Monthly check-ins, model updates, expand to more disciplines or new use cases"),
    ]

    for i, (num, timeframe, title, desc) in enumerate(phases):
        y0 = 1.62 + i * 1.38
        # Circle
        c = sl.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.6), Inches(y0), Inches(0.72), Inches(0.72))
        solid(c, GREEN if num == "✓" else PRIMARY); no_line(c)
        txb(sl, 0.62, y0 + 0.14, 0.68, 0.44, num, size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        # Content row
        rounded_card(sl, 1.55, y0 - 0.05, 11.3, 0.98, WHITE)
        txb(sl, 1.78, y0 + 0.05, 1.85, 0.32, timeframe, size=10.5, bold=True, color=PRIMARY)
        txb(sl, 1.78, y0 + 0.4, 4.5, 0.35, title, size=13, bold=True, color=DARK)
        txb(sl, 6.62, y0 + 0.22, 5.95, 0.55, desc, size=10.5, color=GRAY)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 16 — RESULTS & CASE SNAPSHOTS
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    section_label(sl, "15 — RESULTS & CASE SNAPSHOTS")
    slide_title(sl, "Proven Impact")

    # 4 stat cards
    stats2 = [
        ("70%", "Doc processing\ntime reduction", RGBColor(59, 130, 246)),
        ("85%", "Data accuracy\ngain", RGBColor(16, 185, 129)),
        ("3×", "Faster RFQ\nresponse time", ACCENT),
        ("<4 wk", "Typical ROI\npayback period", RGBColor(245, 158, 11)),
    ]
    for i, (val, lab, col) in enumerate(stats2):
        x = 0.5 + i * 3.2
        rounded_card(sl, x, 1.62, 3.0, 1.62, col)
        txb(sl, x + 0.18, 1.78, 2.65, 0.65, val, size=34, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        txb(sl, x + 0.18, 2.45, 2.65, 0.65, lab, size=9.5, color=RGBColor(240, 240, 255), align=PP_ALIGN.CENTER)

    # Two case snapshots
    cases = [
        ("Case A — P&ID Review (anonymised)",
         "A sour-gas project (anonymised):\n\n"
         "AI flagged NPSH margin 0.3 m below API 610 minimum, 3 missing NACE material "
         "specifications, and 4 relief-routing issues — in 4 minutes.\n\n"
         "Consultant equivalent:  6 hours / ~$400",
         PRIMARY),
        ("Case B — Bulk Isometric Review",
         "50 isometrics reviewed across one week:\n\n"
         "Was: 25–50 engineer-hours (manual)\n"
         "Is now: 4–5 hours with the portal — 90%+ time saving\n\n"
         "95%+ of comments include ASME B31.3 code references. "
         "Standardised severity ratings across all 50 documents.",
         RGBColor(16, 185, 129)),
    ]
    for i, (head, body, col) in enumerate(cases):
        x = 0.5 + i * 6.45
        rounded_card(sl, x, 3.38, 6.18, 3.82, LIGHT_BG, col)
        txb(sl, x + 0.22, 3.55, 5.75, 0.38, head, size=12.5, bold=True, color=col)
        txb(sl, x + 0.22, 4.0, 5.75, 3.0, body, size=10.5, color=DARK)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 17 — INVESTMENT / PRICING
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    light_bg(sl, prs)
    section_label(sl, "16 — INVESTMENT", color=PRIMARY)
    slide_title(sl, "Pricing & Engagement", color=DARK)

    pricing = [
        ("Pay-Per-Review", "Self-serve · no commitment",
         "From $15\nQuick review\n$39 Detailed",
         "✓  No subscription\n✓  Free 5-finding preview\n✓  All 22 disciplines\n✓  Instant delivery\n✓  Best for testing the platform",
         LIGHT_BG, DARK, None, False),
        ("Team Subscription", "Most popular — for active teams",
         "$2,900/mo",
         "✓  Unlimited reviews (5 users)\n✓  Priority processing queue\n✓  All 22 disciplines\n✓  Dedicated account manager\n✓  Monthly reporting",
         PRIMARY, WHITE, None, True),
        ("Enterprise", "Dedicated tenant, custom scope",
         "Custom",
         "✓  Dedicated tenant & SSO\n✓  On-prem or private cloud\n✓  Custom disciplines\n✓  Unlimited seats\n✓  Dedicated SLAs + support",
         DARK, WHITE, None, False),
    ]

    for i, (name, desc, price, feats, bg_col, tc, brd, pop) in enumerate(pricing):
        x = 0.5 + i * 4.28
        rounded_card(sl, x, 1.62, 3.95, 4.62, bg_col, brd)
        if pop:
            popular_badge(sl, x + 1.05, 1.38)
        txb(sl, x + 0.28, 1.82, 3.4, 0.42, name, size=16, bold=True, color=tc)
        txb(sl, x + 0.28, 2.28, 3.4, 0.32, desc, size=10, color=GRAY if i == 0 else RGBColor(180, 195, 230))
        txb(sl, x + 0.28, 2.72, 3.4, 0.72, price, size=22, bold=True, color=tc)
        txb(sl, x + 0.28, 3.52, 3.4, 2.5, feats, size=10.5, color=tc)

    # Bespoke footer
    rounded_card(sl, 0.5, 6.38, 12.333, 0.82, INDIGO_LIGHT, PRIMARY)
    txb(sl, 0.78, 6.52, 12.0, 0.58,
        "⚙️  Bespoke Projects:  Custom AI automation pipelines from £5K pilot to £75K+ annual programmes. "
        "Tailored to your tech stack, data, and delivery schedule.",
        size=11, color=DARK)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 18 — THE BD OPPORTUNITY
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)
    dark_bg(sl, prs)
    section_label(sl, "17 — MARKET OPPORTUNITY", color=RGBColor(129, 140, 248))
    slide_title(sl, "The BD Opportunity in the Middle East", color=WHITE)

    # Market size highlight
    rounded_card(sl, 0.5, 1.6, 12.333, 1.08, DARK_CARD, DARK_BORDER)
    txb(sl, 0.82, 1.72, 12.0, 0.42,
        "Middle East EPC & AI Services Market:  40%+ YoY growth  ·  ~$2B+ addressable  ·  Highly underpenetrated",
        size=13.5, bold=True, color=AMBER)

    # Two columns
    rounded_card(sl, 0.5, 2.85, 5.85, 3.62, DARK_CARD, DARK_BORDER)
    txb(sl, 0.78, 3.02, 5.35, 0.38, "What KU Has Today", size=13.5, bold=True, color=WHITE)
    txb(sl, 0.78, 3.48, 5.35, 2.82,
        "✓  22 productised, live AI reviewers\n"
        "✓  KU Voice — live AI call agent\n"
        "✓  Bespoke automation pipeline capability\n"
        "✓  38+ published engineering AI articles\n"
        "✓  Working SaaS with real paying users\n"
        "✓  Sole channel today: LinkedIn + inbound web",
        size=11, color=RGBColor(200, 210, 230))

    rounded_card(sl, 6.7, 2.85, 6.13, 3.62, DARK_CARD, DARK_BORDER)
    txb(sl, 6.98, 3.02, 5.65, 0.38, "Distribution — Wide Open", size=13.5, bold=True, color=WHITE)
    txb(sl, 6.98, 3.48, 5.65, 2.82,
        "ADNOC  ·  Saudi Aramco  ·  QatarEnergy\n"
        "PDO  ·  KOC  ·  Sonatrach  ·  TAQA  ·  EGA\n\n"
        "Major EPCs:\n"
        "Petrofac  ·  Worley  ·  Wood  ·  TechnipFMC\n"
        "McDermott  ·  L&T  ·  JGC  ·  Chiyoda\n\n"
        "BD partnership = uncapped upside",
        size=11, color=RGBColor(200, 210, 230))

    # Highlight line
    rounded_card(sl, 0.5, 6.6, 12.333, 0.68, PRIMARY)
    txb(sl, 0.78, 6.72, 12.0, 0.45,
        "🤝  KU has the product. The market is ready. The missing piece is feet on the ground.",
        size=12, bold=True, color=WHITE)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 19 — NEXT STEPS + CONTACT
    # ══════════════════════════════════════════════════════════════════════════
    sl = prs.slides.add_slide(blank)

    # Dark-indigo background
    bg = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    solid(bg, PRIMARY_DARK); no_line(bg)
    strip2 = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.35))
    solid(strip2, PRIMARY); no_line(strip2)

    txb(sl, 0, 0.48, 13.333, 0.28, "18 — NEXT STEPS", size=9, bold=True,
        color=RGBColor(165, 180, 252), align=PP_ALIGN.CENTER)
    txb(sl, 0, 0.82, 13.333, 0.78, "Let's Build Something in the Gulf.",
        size=38, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    # 3 step cards
    step_data = [
        ("1", "Discovery Call",      "30-min call to understand\nyour context & priorities"),
        ("2", "Custom Demo",         "Live walk-through with\nyour own documents"),
        ("3", "Proposal",            "Detailed scope, timeline,\nand investment"),
    ]
    for i, (num, head, desc) in enumerate(step_data):
        x = 1.5 + i * 3.62
        rounded_card(sl, x, 1.75, 3.32, 2.15, RGBColor(55, 48, 163))
        # Number circle
        circ = sl.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 1.18), Inches(1.92), Inches(0.95), Inches(0.95))
        solid(circ, PRIMARY); no_line(circ)
        txb(sl, x + 1.22, 2.04, 0.85, 0.62, num, size=22, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        txb(sl, x + 0.18, 3.0, 2.95, 0.35, head, size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        txb(sl, x + 0.18, 3.38, 2.95, 0.45, desc, size=9.5, color=RGBColor(200, 200, 228), align=PP_ALIGN.CENTER)

    # Contact card
    rounded_card(sl, 2.9, 4.05, 7.53, 2.88, WHITE)
    txb(sl, 2.9, 4.18, 7.53, 0.4, "Contact Us", size=18, bold=True, color=DARK, align=PP_ALIGN.CENTER)

    # Non-hyperlinked line
    txb(sl, 3.1, 4.65, 7.12, 0.35,
        "👤  Kingsley Uzowulu  —  Founder & Principal Engineer",
        size=10.5, color=DARK)
    # Hyperlinked contact items
    contact_links = [
        ("📧  contact@ku-automation.com", "mailto:contact@ku-automation.com"),
        ("🌐  www.ku-automation.com", "https://www.ku-automation.com"),
        ("🛍️  services.ku-automation.com", "https://services.ku-automation.com"),
        ("📞  +1 (740) 265-2849", "tel:+17402652849"),
        ("📅  calendly.com/kingsley-uzowulu/30min", "https://calendly.com/kingsley-uzowulu/30min"),
    ]
    for j, (link_text, link_url) in enumerate(contact_links):
        txb_link(sl, 3.1, 5.05 + j * 0.35, 7.12, 0.32, link_text, link_url,
                 size=10.5, bold=False, color=PRIMARY)

    txb(sl, 0, 7.15, 13.333, 0.28,
        "KU Automation  ·  Confidential  ·  July 2026",
        size=8.5, color=RGBColor(100, 100, 150), align=PP_ALIGN.CENTER)


    # --- Logo watermark on all slides except cover (slide index 0) ---
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
    # Slides with dark backgrounds (0-indexed): 0=cover(skip), 2=problem, 12=security,
    # 17=BD opportunity, 18=next steps/contact
    dark_slide_indices = {2, 12, 17, 18}
    if os.path.exists(logo_path):
        for idx, sl_wm in enumerate(prs.slides):
            if idx == 0:
                continue  # Cover already has full-size logo
            if idx in dark_slide_indices:
                # White rounded-rect backdrop for visibility on dark slides
                wm_bg = sl_wm.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    Inches(12.45), Inches(6.80), Inches(0.6), Inches(0.6))
                solid(wm_bg, WHITE)
                border(wm_bg, RGBColor(200, 200, 220), 0.5)
            sl_wm.shapes.add_picture(
                logo_path, Inches(12.5), Inches(6.85), Inches(0.5), Inches(0.5))

    # ─── Save ─────────────────────────────────────────────────────────────────
    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "KU_Automation_Portfolio_v2_Jul2026.pptx"
    )
    prs.save(out_path)
    print(f"✅  Presentation saved: {out_path}")
    return out_path


if __name__ == "__main__":
    create_presentation()
