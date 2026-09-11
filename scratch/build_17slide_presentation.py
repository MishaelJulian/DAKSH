import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import os

def create_daksh_17slide_presentation():
    # Load SamplePPT.pptx as base to preserve master layouts, institutional graphics, and fonts
    prs = pptx.Presentation('SamplePPT.pptx')
    
    # Original dimensions: 11.0 x 8.5 inches
    prs.slide_width = Inches(11.0)
    prs.slide_height = Inches(8.5)
    
    print(f"Presentation slide size: {prs.slide_width.inches:.2f} x {prs.slide_height.inches:.2f} inches (Original Template)")
    
    # Color palette
    NAVY = RGBColor(15, 32, 67)          # #0F2043 (Deep primary brand navy)
    ROYAL_BLUE = RGBColor(28, 54, 102)    # #1C3666 (Secondary deep blue)
    ACCENT_GOLD = RGBColor(209, 173, 107) # #D1AD6B (Template Gold/Bronze)
    CHARCOAL = RGBColor(40, 44, 52)       # Main body text
    MUTED_GRAY = RGBColor(100, 110, 125)  # Subtitles / meta text
    LIGHT_BG = RGBColor(246, 248, 252)    # Light container card background
    WHITE = RGBColor(255, 255, 255)       # Pure white
    CARD_BORDER = RGBColor(220, 226, 235) # Subtle card border
    
    TAG_GREEN_BG = RGBColor(232, 245, 233)
    TAG_GREEN_TEXT = RGBColor(46, 125, 50)
    
    TAG_BLUE_BG = RGBColor(227, 242, 253)
    TAG_BLUE_TEXT = RGBColor(21, 101, 192)
    
    TAG_PURPLE_BG = RGBColor(243, 229, 245)
    TAG_PURPLE_TEXT = RGBColor(123, 31, 162)
    
    TAG_AMBER_BG = RGBColor(255, 248, 225)
    TAG_AMBER_TEXT = RGBColor(230, 81, 0)
    
    # Reset slides except slide 1
    slide_count = len(prs.slides)
    for i in range(slide_count - 1, 0, -1):
        rId = prs.slides._sldIdLst[i].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[i]
        
    print(f"Reset slides to {len(prs.slides)} slide.")
    
    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE (Original Template Layout)
    # -------------------------------------------------------------
    s1 = prs.slides[0]
    
    for shape in s1.shapes:
        if shape.name == 'object 6': # Main Title Placeholder
            tf = shape.text_frame
            tf.clear()
            p0 = tf.paragraphs[0]
            p0.text = "SERVICE LEARNING"
            p0.alignment = PP_ALIGN.CENTER
            p0.font.name = "Times New Roman"
            p0.font.size = Pt(20)
            p0.font.bold = False
            p0.font.color.rgb = NAVY
            
            p1 = tf.add_paragraph()
            p1.text = "DAKSH"
            p1.alignment = PP_ALIGN.CENTER
            p1.font.name = "Times New Roman"
            p1.font.size = Pt(36)
            p1.font.bold = True
            p1.font.color.rgb = NAVY
            
            p2 = tf.add_paragraph()
            p2.text = "Judicial Research and Court-Case Information Platform"
            p2.alignment = PP_ALIGN.CENTER
            p2.font.name = "Trebuchet MS"
            p2.font.size = Pt(17)
            p2.font.bold = True
            p2.font.color.rgb = ROYAL_BLUE
            
            p3 = tf.add_paragraph()
            p3.text = "Structured Court Data, Searchable Research & Intelligent Analytics"
            p3.alignment = PP_ALIGN.CENTER
            p3.font.name = "Tahoma"
            p3.font.size = Pt(12)
            p3.font.italic = True
            p3.font.color.rgb = MUTED_GRAY

        elif shape.name == 'object 7': # Community Partner
            tf = shape.text_frame
            tf.clear()
            p0 = tf.paragraphs[0]
            p0.text = "Community Partner: DAKSH"
            p0.alignment = PP_ALIGN.CENTER
            p0.font.name = "Times New Roman"
            p0.font.size = Pt(20)
            p0.font.bold = True
            p0.font.color.rgb = ROYAL_BLUE
            
        elif shape.name == 'object 8': # Community Location
            tf = shape.text_frame
            tf.clear()
            p0 = tf.paragraphs[0]
            p0.text = "Community Organization"
            p0.alignment = PP_ALIGN.CENTER
            p0.font.name = "Tahoma"
            p0.font.size = Pt(13)
            p0.font.bold = True
            p0.font.color.rgb = NAVY
            
            p1 = tf.add_paragraph()
            p1.text = "DAKSH Society"
            p1.alignment = PP_ALIGN.CENTER
            p1.font.name = "Tahoma"
            p1.font.size = Pt(12)
            p1.font.bold = True
            p1.font.color.rgb = ROYAL_BLUE
            
            p2 = tf.add_paragraph()
            p2.text = "Bengaluru, Karnataka, India"
            p2.alignment = PP_ALIGN.CENTER
            p2.font.name = "Tahoma"
            p2.font.size = Pt(11)
            p2.font.color.rgb = CHARCOAL
            
            p3 = tf.add_paragraph()
            p3.text = "Advancing Justice System Reforms & Judicial Research"
            p3.alignment = PP_ALIGN.CENTER
            p3.font.name = "Tahoma"
            p3.font.size = Pt(10)
            p3.font.italic = True
            p3.font.color.rgb = MUTED_GRAY

        elif shape.name == 'object 9': # Team Details
            tf = shape.text_frame
            tf.clear()
            p0 = tf.paragraphs[0]
            p0.text = "Team Details (5BTCS AIML A):"
            p0.font.name = "Tahoma"
            p0.font.size = Pt(12)
            p0.font.bold = True
            p0.font.color.rgb = NAVY
            
            members = [
                "Mishael Julian – 2462184",
                "Steven Mathew – 2462157",
                "Julius Thomas – 2462095",
                "Abhishan Francis – 2462835",
                "Rahul Prakash – 2462133"
            ]
            for m in members:
                pm = tf.add_paragraph()
                pm.text = m
                pm.font.name = "Tahoma"
                pm.font.size = Pt(10.5)
                pm.font.color.rgb = CHARCOAL
                
            p_cv_title = tf.add_paragraph()
            p_cv_title.text = "Core Values"
            p_cv_title.font.name = "Trebuchet MS"
            p_cv_title.font.size = Pt(10)
            p_cv_title.font.bold = True
            p_cv_title.font.color.rgb = ACCENT_GOLD
            
            p_cv1 = tf.add_paragraph()
            p_cv1.text = "Faith in God | Moral Uprightness | Love of Fellow Beings | Social Responsibility"
            p_cv1.font.name = "Tahoma"
            p_cv1.font.size = Pt(8.5)
            p_cv1.font.color.rgb = WHITE
            
            p_cv2 = tf.add_paragraph()
            p_cv2.text = "Pursuit of Excellence"
            p_cv2.font.name = "Tahoma"
            p_cv2.font.size = Pt(8.5)
            p_cv2.font.color.rgb = WHITE

    print("Slide 1 configured.")

    # Helper function to add standard 4:3 slide
    def add_standard_slide(title_text):
        s = prs.slides.add_slide(prs.slide_layouts[3])
        if len(s.shapes) > 0 and s.shapes[0].has_text_frame:
            s.shapes[0].text_frame.text = title_text
            p = s.shapes[0].text_frame.paragraphs[0]
            p.font.name = "Trebuchet MS"
            p.font.size = Pt(22)
            p.font.bold = True
            p.font.color.rgb = NAVY
            p.alignment = PP_ALIGN.CENTER
        return s

    def add_card_box(slide, left, top, width, height, bg_color=LIGHT_BG, border_color=CARD_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(1)
        else:
            shape.line.fill.background()
        return shape

    def add_info_card(slide, left, top, width, height, card_title, bullets, header_color=ROYAL_BLUE, bg_color=LIGHT_BG, border_color=CARD_BORDER, title_size=13, body_size=11):
        box = add_card_box(slide, left, top, width, height, bg_color, border_color)
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.15)
        tf.margin_right = Inches(0.15)
        tf.margin_top = Inches(0.12)
        tf.margin_bottom = Inches(0.12)
        
        p0 = tf.paragraphs[0]
        p0.text = card_title
        p0.font.name = "Trebuchet MS"
        p0.font.size = Pt(title_size)
        p0.font.bold = True
        p0.font.color.rgb = header_color
        p0.space_after = Pt(4)
        
        for idx, item in enumerate(bullets):
            p = tf.add_paragraph()
            if isinstance(item, tuple):
                lead, body = item
                r1 = p.add_run()
                r1.text = lead + ": " if lead else ""
                r1.font.name = "Tahoma"
                r1.font.size = Pt(body_size)
                r1.font.bold = True
                r1.font.color.rgb = CHARCOAL
                
                r2 = p.add_run()
                r2.text = body
                r2.font.name = "Tahoma"
                r2.font.size = Pt(body_size)
                r2.font.bold = False
                r2.font.color.rgb = CHARCOAL
            else:
                r = p.add_run()
                r.text = item
                r.font.name = "Tahoma"
                r.font.size = Pt(body_size)
                r.font.color.rgb = CHARCOAL
                
            p.space_after = Pt(3)
            p.level = 0
        return box

    def add_badge(slide, left, top, width, height, text, bg_color, text_color):
        tag = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        tag.fill.solid()
        tag.fill.fore_color.rgb = bg_color
        tag.line.fill.background()
        tf = tag.text_frame
        tf.word_wrap = False
        tf.margin_left = Inches(0.05)
        tf.margin_right = Inches(0.05)
        tf.margin_top = Inches(0.02)
        tf.margin_bottom = Inches(0.02)
        p = tf.paragraphs[0]
        p.text = text
        p.font.name = "Tahoma"
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = text_color
        p.alignment = PP_ALIGN.CENTER
        return tag

    C_LEFT = Inches(0.6)
    C_TOP = Inches(2.5)
    C_WIDTH = Inches(9.8)
    C_HEIGHT = Inches(4.3)
    COL2_W = Inches(4.75)
    COL2_GAP = Inches(0.3)

    # -------------------------------------------------------------
    # SLIDE 2: ABSTRACT
    # -------------------------------------------------------------
    s2 = add_standard_slide("ABSTRACT")
    add_badge(s2, C_LEFT, Inches(2.05), Inches(2.2), Inches(0.32), "EXECUTIVE SUMMARY", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    add_info_card(
        s2, C_LEFT, C_TOP, C_WIDTH, C_HEIGHT,
        "DAKSH: A Judicial Research and Court-Case Information Platform",
        [
            ("System Overview", "DAKSH is envisioned as an end-to-end judicial research platform that organizes publicly available court-case information into a structured, centralized, and searchable ecosystem. The project directly addresses the friction of repeatedly navigating fragmented court records when conducting empirical case-level research."),
            ("Data Acquisition Foundation", "An automated data acquisition layer powered by Playwright systematically collects case details, party hierarchies, acts/sections, hearing histories, daily status business logs, and final orders/judgments from the eCourts portal."),
            ("Structured Information Storage", "Collected information is normalized into structured database models that preserve complete case lifecycles, full relational linkages, and linguistic fidelity (including Kannada/vernacular scripts) with zero data loss."),
            ("Researcher-Centric Application", "A dedicated web application provides researchers with intuitive multi-parameter filters, dropdowns, full-text case search, and a unified case workspace, eliminating tedious manual record compilation."),
            ("Future Intelligence Roadmap", "The platform establishes a verified foundation for future analytical capabilities, including case similarity clustering, pendency trend analysis, and decision-support case prioritization.")
        ],
        header_color=ROYAL_BLUE, title_size=14, body_size=11
    )

    # -------------------------------------------------------------
    # SLIDE 3: INTRODUCTION TO COMMUNITY & PROBLEMS FACED
    # -------------------------------------------------------------
    s3 = add_standard_slide("COMMUNITY PROFILE & PROBLEMS FACED")
    add_badge(s3, C_LEFT, Inches(2.05), Inches(2.5), Inches(0.32), "STAKEHOLDERS & CONTEXT", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    add_info_card(
        s3, C_LEFT, C_TOP, COL2_W, C_HEIGHT,
        "Community Profile & Stakeholders",
        [
            ("Community Partner", "DAKSH (Bengaluru) — Leading civil society organization researching justice administration and court data transparency."),
            ("Target Users", "Judicial researchers, empirical legal scholars, and policy analysts studying case pendency, delay patterns, and procedural flows."),
            ("Core Benefit", "Enables researchers to spend time analyzing judicial trends rather than manually locating and copying basic records."),
            ("Ethical Boundaries", "Operates strictly on public eCourts data; does NOT make judicial rulings or replace legal counsel.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )
    
    add_info_card(
        s3, C_LEFT + COL2_W + COL2_GAP, C_TOP, COL2_W, C_HEIGHT,
        "Problems Faced by Judicial Researchers",
        [
            ("Data Fragmentation", "Crucial case details, hearing logs, process tables, and daily orders are scattered across multiple disparate web tabs and popups."),
            ("Separate Order Links", "Daily business records and substantive orders must be clicked and inspected individually, requiring dozens of clicks per case."),
            ("Lack of Relational Querying", "eCourts does not support querying across multi-variable parameters (e.g., comparing disposal stages across case types)."),
            ("Scalability Bottleneck", "Manual copy-pasting is error-prone and practically impossible for large-scale empirical studies across hundreds of cases.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )

    # -------------------------------------------------------------
    # SLIDE 4: CONFIRMATION LETTER
    # -------------------------------------------------------------
    s4 = add_standard_slide("CONFIRMATION LETTER")
    add_badge(s4, C_LEFT, Inches(2.05), Inches(2.3), Inches(0.32), "OFFICIAL EVIDENCE", TAG_GREEN_BG, TAG_GREEN_TEXT)
    
    box_doc = add_card_box(s4, Inches(2.2), C_TOP, Inches(6.6), C_HEIGHT, WHITE, CARD_BORDER)
    tf_doc = box_doc.text_frame
    tf_doc.word_wrap = True
    tf_doc.margin_left = Inches(0.4)
    tf_doc.margin_right = Inches(0.4)
    tf_doc.margin_top = Inches(0.4)
    
    p0 = tf_doc.paragraphs[0]
    p0.text = "ORGANIZATIONAL ENGAGEMENT DOCUMENTATION"
    p0.font.name = "Trebuchet MS"
    p0.font.size = Pt(15)
    p0.font.bold = True
    p0.font.color.rgb = NAVY
    p0.alignment = PP_ALIGN.CENTER
    p0.space_after = Pt(10)
    
    p1 = tf_doc.add_paragraph()
    p1.text = "Service Learning Collaboration with DAKSH"
    p1.font.name = "Tahoma"
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = ROYAL_BLUE
    p1.alignment = PP_ALIGN.CENTER
    p1.space_after = Pt(12)
    
    p2 = tf_doc.add_paragraph()
    p2.text = "[ Formal Confirmation Letter / Engagement Certificate — To Be Inserted ]"
    p2.font.name = "Tahoma"
    p2.font.size = Pt(11.5)
    p2.font.italic = True
    p2.font.color.rgb = MUTED_GRAY
    p2.alignment = PP_ALIGN.CENTER
    p2.space_after = Pt(14)
    
    details = [
        "Partner Organization: DAKSH (Bengaluru, Karnataka)",
        "Project Scope: Automated Judicial Data Acquisition & Structured Research Platform",
        "Target Court: Bengaluru City Civil Court Complex (Executive Petitions Benchmark)",
        "Academic Department: Department of Computer Science and Engineering, CHRIST (Deemed to be University)"
    ]
    for d in details:
        pd = tf_doc.add_paragraph()
        pd.text = "• " + d
        pd.font.name = "Tahoma"
        pd.font.size = Pt(10.5)
        pd.font.color.rgb = CHARCOAL
        pd.space_after = Pt(3)

    # -------------------------------------------------------------
    # SLIDE 5: NEED ANALYSIS
    # -------------------------------------------------------------
    s5 = add_standard_slide("NEED ANALYSIS")
    add_badge(s5, C_LEFT, Inches(2.05), Inches(2.2), Inches(0.32), "LOGICAL PROGRESSION", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    steps = [
        ("1. CURRENT STATE", "Researchers navigate individual eCourts portal pages and disparate case tabs manually."),
        ("2. STRUCTURAL CHALLENGE", "Relevant information is highly fragmented across case details, hearings, processes, and orders."),
        ("3. MANUAL BURDEN", "Repetitive manual lookup, note-taking, and copying cause severe human fatigue and transcription error."),
        ("4. SCALABILITY BOTTLENECK", "Empirical legal research cannot scale beyond small sample sizes due to massive labor overhead."),
        ("5. SYSTEMIC NEED", "A centralized, structured, and auditable judicial research information system."),
        ("6. DAKSH SOLUTION", "End-to-end platform: Automated Data Layer + Structured Database + Researcher Workspace.")
    ]
    
    step_h = Inches(0.65)
    for idx, (title_step, desc_step) in enumerate(steps):
        bg = TAG_BLUE_BG if idx == 5 else LIGHT_BG
        brd = ROYAL_BLUE if idx == 5 else CARD_BORDER
        hdr_c = ROYAL_BLUE if idx == 5 else NAVY
        cbox = add_card_box(s5, C_LEFT, Inches(2.45) + idx * (step_h + Inches(0.08)), C_WIDTH, step_h, bg, brd)
        tf = cbox.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.15)
        tf.margin_top = Inches(0.08)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = title_step + " — "
        r1.font.name = "Trebuchet MS"
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = hdr_c
        
        r2 = p.add_run()
        r2.text = desc_step
        r2.font.name = "Tahoma"
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 6: IMPACT IF THE PROBLEM REMAINS UNSOLVED
    # -------------------------------------------------------------
    s6 = add_standard_slide("IMPACT IF THE PROBLEM REMAINS UNSOLVED")
    add_badge(s6, C_LEFT, Inches(2.05), Inches(2.4), Inches(0.32), "CONSEQUENCE ANALYSIS", TAG_AMBER_BG, TAG_AMBER_TEXT)
    
    add_info_card(
        s6, C_LEFT, C_TOP, COL2_W, C_HEIGHT,
        "Research & Institutional Consequences",
        [
            ("Perpetual Manual Inefficiency", "Researchers will continue spending over 80% of project time on routine portal navigation and copy-pasting instead of data analysis."),
            ("Severe Sample Size Limitations", "Judicial studies remain restricted to 20–50 cases, preventing macro-level empirical evaluation of court administration."),
            ("Fragmented Institutional Datasets", "Every research team compiles isolated, ad-hoc spreadsheets without standardized schemas, hindering cross-study comparison."),
            ("Incomplete Historical Context", "Failure to systematically capture daily status transcripts leads to lost procedural insights regarding case adjournments.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=11
    )
    
    add_info_card(
        s6, C_LEFT + COL2_W + COL2_GAP, C_TOP, COL2_W, C_HEIGHT,
        "Policy & Civic Consequences",
        [
            ("Delayed Evidence-Based Insights", "Policy think tanks and reform advocates lack aggregated empirical evidence to recommend procedural improvements."),
            ("Barriers to Transparency", "Public court information remains technically public but practically inaccessible for comprehensive empirical auditing."),
            ("Inability to Track Case Lifecycles", "Execution Petitions (EX) and pending decrees cannot be tracked longitudinally across years and court complexes."),
            ("High Opportunity Cost", "Substantial academic funding and researcher effort are wasted on redundant manual data extraction.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=11
    )

    # -------------------------------------------------------------
    # SLIDE 7: PROBLEM STATEMENT
    # -------------------------------------------------------------
    s7 = add_standard_slide("PROBLEM STATEMENT")
    add_badge(s7, C_LEFT, Inches(2.05), Inches(2.3), Inches(0.32), "CORE FORMULATION", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    box_ps = add_card_box(s7, C_LEFT, C_TOP, C_WIDTH, C_HEIGHT, WHITE, CARD_BORDER)
    tf_ps = box_ps.text_frame
    tf_ps.word_wrap = True
    tf_ps.margin_left = Inches(0.3)
    tf_ps.margin_right = Inches(0.3)
    tf_ps.margin_top = Inches(0.2)
    
    p0 = tf_ps.paragraphs[0]
    p0.text = "Formal Problem Formulation"
    p0.font.name = "Trebuchet MS"
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = NAVY
    p0.space_after = Pt(10)
    
    p_quote = tf_ps.add_paragraph()
    p_quote.text = "“Judicial researchers investigating court administration and case workflows are severely hindered by the fragmented, multi-page structure of public court portals. The lack of a centralized, structured database and researcher-centric query workspace turns large-scale case analysis into an error-prone, repetitive, and labor-intensive manual endeavor. There is an urgent need for an integrated judicial research platform that systematically acquires, validates, and normalizes public eCourts data into structured records, providing an intuitive workspace for rich search, multidimensional filtering, and downstream analytical exploration.”"
    p_quote.font.name = "Georgia"
    p_quote.font.size = Pt(12)
    p_quote.font.italic = True
    p_quote.font.color.rgb = ROYAL_BLUE
    p_quote.space_after = Pt(14)
    
    pillars = [
        ("Data Fragmentation", "Disjointed storage across multiple HTML pages and popups without unified indexing."),
        ("Manual Friction", "High manual overhead for CAPTCHAs, search navigation, and spreadsheet transcription."),
        ("Platform Necessity", "Requirement for an end-to-end system: Ingestion → Normalized Database → Researcher UI/UX.")
    ]
    for pil_t, pil_d in pillars:
        p_pil = tf_ps.add_paragraph()
        r1 = p_pil.add_run()
        r1.text = "• " + pil_t + ": "
        r1.font.name = "Tahoma"
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r1.font.color.rgb = NAVY
        
        r2 = p_pil.add_run()
        r2.text = pil_d
        r2.font.name = "Tahoma"
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = CHARCOAL
        p_pil.space_after = Pt(4)

    # -------------------------------------------------------------
    # SLIDE 8: PROJECT OBJECTIVES
    # -------------------------------------------------------------
    s8 = add_standard_slide("PROJECT OBJECTIVES")
    add_badge(s8, C_LEFT, Inches(2.05), Inches(2.4), Inches(0.32), "PLATFORM GOALS", TAG_GREEN_BG, TAG_GREEN_TEXT)
    
    objs = [
        ("1. Automated Data Acquisition", "Systematically collect publicly available case records, hearing histories, daily status logs, processes, and orders from the eCourts portal using Playwright automation."),
        ("2. Structured Information Modeling", "Organize extracted case details into normalized, strongly-typed relational records (CNR, registration details, parties, acts, hearings, business transcripts)."),
        ("3. Relational Storage Architecture", "Develop a structured database schema and export pipeline preserving complete case context with zero data loss and full Unicode (Kannada) fidelity."),
        ("4. Intuitive Researcher UI/UX", "Design a centralized web workspace providing multi-parameter search, dynamic court/case-type dropdowns, and tabbed case inspection views."),
        ("5. Elimination of Manual Overhead", "Dramatically reduce repetitive manual lookup time, enabling empirical researchers to focus on data analysis rather than data retrieval."),
        ("6. Foundation for Future AI/ML", "Establish an auditable data foundation capable of supporting future case similarity clustering, pendency trend analytics, and researcher-defined prioritization.")
    ]
    
    card_h8 = Inches(1.3)
    for i, (ot, od) in enumerate(objs):
        col = i % 2
        row = i // 2
        left_pos = C_LEFT if col == 0 else C_LEFT + COL2_W + COL2_GAP
        top_pos = C_TOP + row * (card_h8 + Inches(0.12))
        
        cbox = add_card_box(s8, left_pos, top_pos, COL2_W, card_h8, LIGHT_BG, CARD_BORDER)
        tf = cbox.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.12)
        tf.margin_right = Inches(0.12)
        tf.margin_top = Inches(0.08)
        
        p0 = tf.paragraphs[0]
        p0.text = ot
        p0.font.name = "Trebuchet MS"
        p0.font.size = Pt(11.5)
        p0.font.bold = True
        p0.font.color.rgb = ROYAL_BLUE
        p0.space_after = Pt(2)
        
        p1 = tf.add_paragraph()
        p1.text = od
        p1.font.name = "Tahoma"
        p1.font.size = Pt(10)
        p1.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 9: PROPOSED SYSTEM ARCHITECTURE
    # -------------------------------------------------------------
    s9 = add_standard_slide("PROPOSED SYSTEM ARCHITECTURE")
    add_badge(s9, C_LEFT, Inches(2.05), Inches(2.4), Inches(0.32), "MULTI-TIER PLATFORM", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    tiers = [
        ("TIER 1: PUBLIC DATA SOURCE", "Official eCourts Services Portal (District Courts / City Civil Court Complexes)", TAG_AMBER_BG, TAG_AMBER_TEXT),
        ("TIER 2: DATA ACQUISITION LAYER", "Python 3.12 + Playwright Automation | Session Lifecycle & Human-in-the-Loop CAPTCHA", TAG_BLUE_BG, TAG_BLUE_TEXT),
        ("TIER 3: PARSING & VALIDATION", "BeautifulSoup4 DOM Extraction | 100% Zero-Loss Field Audit Suite & Parity Verifier", TAG_GREEN_BG, TAG_GREEN_TEXT),
        ("TIER 4: STRUCTURED STORAGE", "Normalized Data Models | Relational Schema, JSON Records, Consolidated Master CSV/XLSX", TAG_BLUE_BG, TAG_BLUE_TEXT),
        ("TIER 5: DAKSH APPLICATION CORE", "Query Engine, Multi-Parameter Filters, Case Workspace Router & Aggregation APIs", TAG_GREEN_BG, TAG_GREEN_TEXT),
        ("TIER 6: RESEARCHER UI/UX WORKSPACE", "Search Bar, District/Type Dropdowns, Case Details, Hearing History, Daily Status & Orders", TAG_BLUE_BG, TAG_BLUE_TEXT),
        ("TIER 7: FUTURE AI / ML INTELLIGENCE", "Case Clustering, Pendency Trend Analytics & Decision-Support Case Priority Queue [FUTURE]", TAG_PURPLE_BG, TAG_PURPLE_TEXT)
    ]
    
    tier_h = Inches(0.54)
    for i, (t_title, t_sub, bg, txt) in enumerate(tiers):
        tbox = add_card_box(s9, C_LEFT, Inches(2.45) + i * (tier_h + Inches(0.07)), C_WIDTH, tier_h, bg, CARD_BORDER)
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.15)
        tf.margin_top = Inches(0.06)
        
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = t_title + " → "
        r1.font.name = "Trebuchet MS"
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r1.font.color.rgb = txt
        
        r2 = p.add_run()
        r2.text = t_sub
        r2.font.name = "Tahoma"
        r2.font.size = Pt(10)
        r2.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 10: DATA ACQUISITION LAYER (FOUNDATION)
    # -------------------------------------------------------------
    s10 = add_standard_slide("DATA ACQUISITION LAYER")
    add_badge(s10, C_LEFT, Inches(2.05), Inches(2.7), Inches(0.32), "FOUNDATIONAL INGESTION TIER", TAG_GREEN_BG, TAG_GREEN_TEXT)
    
    add_info_card(
        s10, C_LEFT, C_TOP, COL2_W, C_HEIGHT,
        "Automated Navigation & Ingestion",
        [
            ("Role in Hierarchy", "Scraping is strictly the data acquisition foundation — not the final research application."),
            ("Target Portal", "eCourts Case Status Portal (Search by Case Type / Complex)."),
            ("State & District Selection", "Automated dropdown selection for Karnataka / BENGALURU City Civil Court Complex."),
            ("Establishment & Case Type", "PRL. CITY CIVIL AND SESSIONS JUDGE / EX – Execution Petition Under Order."),
            ("CAPTCHA Handling", "Clean pause workflow for human-in-the-loop CAPTCHA entry to ensure reliability.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=11
    )
    
    add_info_card(
        s10, C_LEFT + COL2_W + COL2_GAP, C_TOP, COL2_W, C_HEIGHT,
        "Deep Section Extraction Workflow",
        [
            ("Case Details", "Filing/Registration numbers, CNR, first hearing, decision date, case status, judge."),
            ("Parties & Advocates", "Complete petitioner and respondent hierarchies with assigned legal counsel."),
            ("Acts & Sections", "Exhaustive extraction of statutory provisions and sections invoked."),
            ("Case History", "Every hearing row: Judge, Business Date, Hearing Date, Purpose of Hearing."),
            ("Orders & Daily Status", "Visits EVERY order hyperlink; extracts complete judicial business transcripts."),
            ("Zero Data Loss Audit", "Automated parity auditor verifies Web DOM == JSON == CSV == XLSX.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=11
    )

    # -------------------------------------------------------------
    # SLIDE 11: STRUCTURED DATABASE & INFORMATION MODEL
    # -------------------------------------------------------------
    s11 = add_standard_slide("STRUCTURED DATABASE & INFORMATION MODEL")
    add_badge(s11, C_LEFT, Inches(2.05), Inches(2.5), Inches(0.32), "RELATIONAL SCHEMA", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    add_info_card(
        s11, C_LEFT, C_TOP, COL2_W, C_HEIGHT,
        "Core Entities & Relational Schema",
        [
            ("CASE Entity (Master)", "CNR Number (PK), Registration No, Filing Date, Decision Date, Status, Nature of Disposal, Court/Judge."),
            ("Parties & Counsel", "1-to-many relationship: Petitioners, Respondents, and Advocates linked to Case ID."),
            ("Acts & Provisions", "Statute names, section numbers, and legal classifications."),
            ("Hearing History", "Chronological table: Business Date, Next Hearing Date, Purpose of Hearing (Notice, Summons, Disposal)."),
            ("Daily Status & Business", "Complete verbatim transcripts of daily orders with disposal remarks."),
            ("Processes & Transfers", "Process ID, Title, Issue Date, Transferring & Receiving Courts.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=11
    )
    
    add_info_card(
        s11, C_LEFT + COL2_W + COL2_GAP, C_TOP, COL2_W, C_HEIGHT,
        "Data Integrity & Architectural Benefits",
        [
            ("Relational Querying", "Enables SQL/indexed querying across complex multi-variable judicial parameters."),
            ("Linguistic Preservation", "Full UTF-8 with BOM support preserving English, Kannada, and vernacular notations without corruption."),
            ("Standardized Export Formats", "Provides clean JSON, relational CSVs, and Excel outputs for downstream statistical software."),
            ("Extensible Data Foundation", "Engineered to seamlessly support future API endpoints, web dashboards, and AI analytics models.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=11
    )

    # -------------------------------------------------------------
    # SLIDE 12: PROPOSED APPLICATION & RESEARCHER UI/UX
    # -------------------------------------------------------------
    s12 = add_standard_slide("PROPOSED RESEARCHER UI/UX WORKSPACE")
    add_badge(s12, C_LEFT, Inches(2.05), Inches(2.7), Inches(0.32), "PROPOSED APPLICATION UI", TAG_AMBER_BG, TAG_AMBER_TEXT)
    
    add_info_card(
        s12, C_LEFT, C_TOP, COL2_W, C_HEIGHT,
        "Search & Multi-Parameter Filter Panel",
        [
            ("Global Search Bar", "Direct lookup by CNR Number, Case Number, Party Name, or Advocate Name."),
            ("Dynamic Dropdowns", "Hierarchical selection: State → District → Court Complex → Establishment."),
            ("Case Classification Filters", "Filter by Case Type (EX, OS, CC), Filing Year, Decision Year, and Case Status (Pending/Disposed)."),
            ("Stage & Purpose Filters", "Filter cases by specific hearing purposes (e.g., Summons, Evidence, Arguments, Orders)."),
            ("Interactive Results Grid", "Displays matching cases with summary metrics: duration, hearing count, and last order date.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=11
    )
    
    add_info_card(
        s12, C_LEFT + COL2_W + COL2_GAP, C_TOP, COL2_W, C_HEIGHT,
        "Case Information Workspace (Tabbed View)",
        [
            ("Tab 1: Case Overview", "Summary cards showing registration metadata, judge, court complex, and disposal nature."),
            ("Tab 2: Hearing Chronology", "Interactive timeline of all hearing dates, business dates, and recorded hearing purposes."),
            ("Tab 3: Daily Status Transcripts", "Synchronized transcript viewer displaying daily judicial business notes."),
            ("Tab 4: Parties & Advocates", "Structured party hierarchy with legal representation history."),
            ("Tab 5: Orders & Documents", "Centralized repository of all interlocutory and final orders with download options.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=11
    )

    # -------------------------------------------------------------
    # SLIDE 13: RESEARCHER USER JOURNEY
    # -------------------------------------------------------------
    s13 = add_standard_slide("RESEARCHER USER JOURNEY")
    add_badge(s13, C_LEFT, Inches(2.05), Inches(2.5), Inches(0.32), "END-TO-END WORKFLOW", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    journey_steps = [
        ("1. Open DAKSH Platform", "Researcher accesses the centralized judicial research web application."),
        ("2. Select Search Parameters", "Selects Court Complex (e.g., Bengaluru City Civil), Case Type (EX), and Year range (2010–2023)."),
        ("3. Apply Research Filters", "Applies granular filters by disposal nature, specific statutory act, or pending duration."),
        ("4. Inspect Results Explorer", "Reviews matching case cards displaying case age, total hearings, and latest stage."),
        ("5. Open Case Workspace", "Opens a unified workspace displaying synchronized hearing histories, daily notes, and orders."),
        ("6. Analyze & Export", "Performs cross-case comparison and exports structured datasets (CSV/JSON) for empirical analysis.")
    ]
    
    step_h13 = Inches(0.65)
    for idx, (j_title, j_desc) in enumerate(journey_steps):
        bg = TAG_BLUE_BG if idx % 2 == 0 else LIGHT_BG
        cbox = add_card_box(s13, C_LEFT, Inches(2.45) + idx * (step_h13 + Inches(0.08)), C_WIDTH, step_h13, bg, CARD_BORDER)
        tf = cbox.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.15)
        tf.margin_top = Inches(0.08)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = j_title + " → "
        r1.font.name = "Trebuchet MS"
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = ROYAL_BLUE
        
        r2 = p.add_run()
        r2.text = j_desc
        r2.font.name = "Tahoma"
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 14: FUTURE SCOPE: INTELLIGENT ANALYTICS & PRIORITIZATION
    # -------------------------------------------------------------
    s14 = add_standard_slide("FUTURE SCOPE: ANALYTICS & PRIORITIZATION")
    add_badge(s14, C_LEFT, Inches(2.05), Inches(2.8), Inches(0.32), "FUTURE SCOPE — DECISION SUPPORT", TAG_PURPLE_BG, TAG_PURPLE_TEXT)
    
    add_info_card(
        s14, C_LEFT, C_TOP, COL2_W, C_HEIGHT,
        "AI/ML Judicial Analytics [FUTURE]",
        [
            ("Case Clustering", "Unsupervised grouping of cases by procedural milestones, stage durations, and statutory provisions."),
            ("Pendency & Delay Modeling", "Statistical analysis identifying procedural stages causing prolonged case pendency."),
            ("Adjournment Pattern Detection", "Analyzing hearing intervals and adjournment frequency across case types."),
            ("Semantic Retrieval", "Vector search across unstructured judicial daily status transcripts and order texts.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )
    
    add_info_card(
        s14, C_LEFT + COL2_W + COL2_GAP, C_TOP, COL2_W, C_HEIGHT,
        "Case Prioritization Queue [PROPOSED]",
        [
            ("Decision Support Focus", "Designed to help researchers organize, rank, and filter large case cohorts for empirical study."),
            ("Multi-Factor Scoring", "Configurable weights based on case age, total hearings, stage intervals, and statutory importance."),
            ("Transparent & Auditable", "Every score is fully traceable to explicit features; no black-box predictions."),
            ("Human Governance", "Strictly an academic decision-support tool; does NOT alter court scheduling or judicial rulings.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )

    # -------------------------------------------------------------
    # SLIDE 15: REQUIREMENTS & DATA INTEGRITY
    # -------------------------------------------------------------
    s15 = add_standard_slide("SYSTEM REQUIREMENTS & DATA INTEGRITY")
    add_badge(s15, C_LEFT, Inches(2.05), Inches(2.5), Inches(0.32), "TECHNICAL SPECIFICATIONS", TAG_GREEN_BG, TAG_GREEN_TEXT)
    
    add_info_card(
        s15, C_LEFT, C_TOP, COL2_W, C_HEIGHT,
        "Software & Hardware Requirements",
        [
            ("Programming Runtime", "Python 3.12+ (dataclass schemas, async Playwright, typing)."),
            ("Ingestion & Parsing", "Playwright (Chromium engine) + BeautifulSoup4 + lxml parser."),
            ("Data Serialization", "JSON (schema-validated), CSV (UTF-8 with BOM), OpenPyXL, Pandas."),
            ("Host Compute", "Standard laptop/workstation (Intel i5/Ryzen 5, 8GB RAM, 10GB SSD)."),
            ("Software-Only System", "Requires no microcontrollers, cameras, or embedded hardware sensors.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )
    
    add_info_card(
        s15, C_LEFT + COL2_W + COL2_GAP, C_TOP, COL2_W, C_HEIGHT,
        "Data Integrity & Validation Framework",
        [
            ("Core Principle", "“Incorrect information is far more harmful than unavailable information.”"),
            ("Cross-Format Parity", "Strict 1-to-1 verification: Web DOM row count == JSON entries == CSV rows == Excel rows."),
            ("Explicit Nulls", "Unpopulated portal fields are explicitly stored as `null` without synthetic fabrication."),
            ("Unicode Fidelity", "Full preservation of Kannada vernacular text in daily business records without corruption.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )

    # -------------------------------------------------------------
    # SLIDE 16: TECHNICAL EVIDENCE & IMPLEMENTATION STATUS
    # -------------------------------------------------------------
    s16 = add_standard_slide("TECHNICAL EVIDENCE & CURRENT STATUS")
    add_badge(s16, C_LEFT, Inches(2.05), Inches(2.5), Inches(0.32), "EXECUTION & MILESTONES", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    col3_w = Inches(3.1)
    col3_gap = Inches(0.25)
    
    add_info_card(
        s16, C_LEFT, C_TOP, col3_w, C_HEIGHT,
        "Completed & Validated\n[CURRENT SYSTEM]",
        [
            ("Playwright Automation", "Dynamic portal navigation, search execution & human-in-the-loop CAPTCHA."),
            ("Multi-Section Parser", "Exhaustive extraction of case metadata, parties, acts, hearings & orders."),
            ("Daily Status Extraction", "Automated opening and scraping of every order hyperlink and business text."),
            ("Benchmark Dataset", "Gold-standard 2010 Bengaluru City Civil Court EX dataset produced.")
        ],
        header_color=TAG_GREEN_TEXT, bg_color=TAG_GREEN_BG, border_color=TAG_GREEN_TEXT, title_size=12, body_size=9.5
    )
    
    add_info_card(
        s16, C_LEFT + col3_w + col3_gap, C_TOP, col3_w, C_HEIGHT,
        "In Development\n[PROPOSED APP]",
        [
            ("Relational DB Modeling", "Structuring PostgreSQL / SQLite schema for indexed search."),
            ("Researcher UI/UX", "Designing frontend with multi-parameter filter dropdowns and case tabs."),
            ("Case Workspace Prototyping", "Building synchronized timeline viewer for hearing logs and daily orders."),
            ("Scaling Pipeline", "Scaling extraction from 2010 to 2023–2025 datasets.")
        ],
        header_color=TAG_BLUE_TEXT, bg_color=TAG_BLUE_BG, border_color=TAG_BLUE_TEXT, title_size=12, body_size=9.5
    )
    
    add_info_card(
        s16, C_LEFT + (col3_w + col3_gap)*2, C_TOP, col3_w, C_HEIGHT,
        "Future Scope\n[ROADMAP]",
        [
            ("AI/ML Judicial Analytics", "Case similarity clustering and pendency bottleneck modeling."),
            ("Priority Queue Engine", "Decision-support scoring for researcher cohort prioritization."),
            ("Semantic Search", "Vector embeddings for full-text querying across judicial business notes."),
            ("Multi-Court Expansion", "Scaling pipeline across South Indian district and High Courts.")
        ],
        header_color=TAG_PURPLE_TEXT, bg_color=TAG_PURPLE_BG, border_color=TAG_PURPLE_TEXT, title_size=12, body_size=9.5
    )

    # -------------------------------------------------------------
    # SLIDE 17: STRATEGIC ROADMAP, CONCLUSION & THANK YOU
    # -------------------------------------------------------------
    s17 = prs.slides.add_slide(prs.slide_layouts[0])
    for shape in s17.shapes:
        if shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            if shape.name == 'Title 1':
                p0 = tf.paragraphs[0]
                p0.text = "CONCLUSION & THANK YOU"
                p0.font.name = "Times New Roman"
                p0.font.size = Pt(36)
                p0.font.bold = True
                p0.font.color.rgb = NAVY
                p0.alignment = PP_ALIGN.CENTER
                
                p1 = tf.add_paragraph()
                p1.text = "DAKSH — Judicial Research and Court-Case Information Platform"
                p1.font.name = "Trebuchet MS"
                p1.font.size = Pt(16)
                p1.font.bold = True
                p1.font.color.rgb = ROYAL_BLUE
                p1.alignment = PP_ALIGN.CENTER
            elif shape.name == 'Subtitle 2':
                p0 = tf.paragraphs[0]
                p0.text = "Transforming Court Information into Empirical Judicial Intelligence"
                p0.font.name = "Georgia"
                p0.font.size = Pt(13)
                p0.font.italic = True
                p0.font.color.rgb = NAVY
                p0.alignment = PP_ALIGN.CENTER
                
                p1 = tf.add_paragraph()
                p1.text = "Service Learning Project in Collaboration with DAKSH, Bengaluru"
                p1.font.name = "Tahoma"
                p1.font.size = Pt(11.5)
                p1.font.bold = True
                p1.font.color.rgb = ROYAL_BLUE
                p1.alignment = PP_ALIGN.CENTER
                
                p2 = tf.add_paragraph()
                p2.text = "Team: Mishael Julian | Steven Mathew | Julius Thomas | Abhishan Francis | Rahul Prakash (5BTCS AIML A)"
                p2.font.name = "Tahoma"
                p2.font.size = Pt(10.5)
                p2.font.color.rgb = CHARCOAL
                p2.alignment = PP_ALIGN.CENTER
                
                p3 = tf.add_paragraph()
                p3.text = "Department of Computer Science and Engineering | CHRIST (Deemed to be University), Bengaluru"
                p3.font.name = "Tahoma"
                p3.font.size = Pt(10)
                p3.font.color.rgb = MUTED_GRAY
                p3.alignment = PP_ALIGN.CENTER

    # Save outputs
    output_path = "DAKSH_Service_Learning_Presentation.pptx"
    try:
        prs.save(output_path)
        print(f"Successfully saved {output_path} with {len(prs.slides)} slides!")
    except Exception as e:
        alt_path = "DAKSH_Service_Learning_Presentation_17Slides.pptx"
        prs.save(alt_path)
        print(f"File locked, saved to {alt_path} with {len(prs.slides)} slides!")

if __name__ == "__main__":
    create_daksh_17slide_presentation()
