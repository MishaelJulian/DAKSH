import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import os

def create_daksh_16x9_presentation():
    # Load SamplePPT.pptx as base to preserve master layouts, institutional graphics, and fonts
    prs = pptx.Presentation('SamplePPT.pptx')
    
    # Standard PowerPoint 16:9 widescreen dimensions
    # 13.333333 x 7.5 inches
    prs.slide_width = Inches(13.333333)
    prs.slide_height = Inches(7.5)
    
    print(f"Set presentation slide size to 16:9 widescreen: {prs.slide_width.inches:.3f} x {prs.slide_height.inches:.3f} inches")
    
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
    # SLIDE 1: TITLE SLIDE (16:9 Proportional Positioning)
    # -------------------------------------------------------------
    s1 = prs.slides[0]
    
    for shape in s1.shapes:
        if shape.name == 'object 5': # Christ University Logo
            # Reposition logo to top right in 16:9 canvas
            shape.left = Inches(9.2)
            shape.top = Inches(0.85)
            shape.width = Inches(2.9)
            shape.height = Inches(0.98)
            
        elif shape.name == 'object 6': # Main Title Box
            shape.left = Inches(1.8)
            shape.top = Inches(1.65)
            shape.width = Inches(9.7)
            shape.height = Inches(1.6)
            
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
            shape.left = Inches(4.5)
            shape.top = Inches(3.4)
            shape.width = Inches(4.33)
            shape.height = Inches(0.45)
            
            tf = shape.text_frame
            tf.clear()
            p0 = tf.paragraphs[0]
            p0.text = "Community Partner: DAKSH"
            p0.alignment = PP_ALIGN.CENTER
            p0.font.name = "Times New Roman"
            p0.font.size = Pt(19)
            p0.font.bold = True
            p0.font.color.rgb = ROYAL_BLUE
            
        elif shape.name == 'object 8': # Community Location
            shape.left = Inches(1.2)
            shape.top = Inches(4.0)
            shape.width = Inches(3.8)
            shape.height = Inches(1.25)
            
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
            shape.left = Inches(8.3)
            shape.top = Inches(3.95)
            shape.width = Inches(4.1)
            shape.height = Inches(2.2)
            
            tf = shape.text_frame
            tf.clear()
            p0 = tf.paragraphs[0]
            p0.text = "Team Details (5BTCS AIML A):"
            p0.font.name = "Tahoma"
            p0.font.size = Pt(11.5)
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
                pm.font.size = Pt(10)
                pm.font.color.rgb = CHARCOAL
                
            p_cv_title = tf.add_paragraph()
            p_cv_title.text = "Core Values"
            p_cv_title.font.name = "Trebuchet MS"
            p_cv_title.font.size = Pt(9.5)
            p_cv_title.font.bold = True
            p_cv_title.font.color.rgb = ACCENT_GOLD
            
            p_cv1 = tf.add_paragraph()
            p_cv1.text = "Faith in God | Moral Uprightness | Love of Fellow Beings | Social Responsibility"
            p_cv1.font.name = "Tahoma"
            p_cv1.font.size = Pt(8)
            p_cv1.font.color.rgb = WHITE
            
            p_cv2 = tf.add_paragraph()
            p_cv2.text = "Pursuit of Excellence"
            p_cv2.font.name = "Tahoma"
            p_cv2.font.size = Pt(8)
            p_cv2.font.color.rgb = WHITE

        elif shape.name in ['object 2', 'object 3', 'object 4']:
            # Adjust Mission / Vision on bottom left
            shape.top = Inches(5.6)
            shape.left = Inches(1.2)

    print("Slide 1 configured for 16:9.")

    # Helper function to add a standard 16:9 title-only slide
    def add_standard_16x9_slide(title_text):
        s = prs.slides.add_slide(prs.slide_layouts[3])
        if len(s.shapes) > 0 and s.shapes[0].has_text_frame:
            title_shp = s.shapes[0]
            title_shp.left = Inches(1.5)
            title_shp.top = Inches(1.05)
            title_shp.width = Inches(10.333)
            title_shp.height = Inches(0.50)
            
            tf = title_shp.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            p.text = title_text
            p.font.name = "Trebuchet MS"
            p.font.size = Pt(22)
            p.font.bold = True
            p.font.color.rgb = NAVY
            p.alignment = PP_ALIGN.CENTER
        return s

    # Helper function to add a card shape
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

    # Helper function to add structured card with title & bullet points
    def add_info_card(slide, left, top, width, height, card_title, bullets, header_color=ROYAL_BLUE, bg_color=LIGHT_BG, border_color=CARD_BORDER, title_size=13, body_size=10.5):
        box = add_card_box(slide, left, top, width, height, bg_color, border_color)
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.18)
        tf.margin_right = Inches(0.18)
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
                
            p.space_after = Pt(2.5)
            p.level = 0
        return box

    # Helper function to add a badge/pill tag
    def add_badge(slide, left, top, width, height, text, bg_color, text_color):
        tag = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        tag.fill.solid()
        tag.fill.fore_color.rgb = bg_color
        tag.line.fill.background()
        tf = tag.text_frame
        tf.word_wrap = False
        tf.margin_left = Inches(0.06)
        tf.margin_right = Inches(0.06)
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

    # Standard positions for 16:9 widescreen
    CONTENT_LEFT = Inches(1.0)
    CONTENT_TOP = Inches(2.05)
    CONTENT_WIDTH = Inches(11.333)
    CONTENT_HEIGHT = Inches(4.35)
    
    COL2_WIDTH = Inches(5.48)
    COL2_GAP = Inches(0.37)
    
    COL3_WIDTH = Inches(3.55)
    COL3_GAP = Inches(0.34)

    # -------------------------------------------------------------
    # SLIDE 2: UNIVERSITY MISSION & VISION
    # -------------------------------------------------------------
    s2 = add_standard_16x9_slide("UNIVERSITY MISSION & VISION")
    add_badge(s2, CONTENT_LEFT, Inches(1.62), Inches(2.2), Inches(0.32), "INSTITUTIONAL VALUES", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    add_info_card(
        s2, CONTENT_LEFT, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "CHRIST (Deemed to be University) Mission",
        [
            ("Mission Statement", "CHRIST (Deemed to be University) is a nurturing ground for an individual’s holistic development to make effective contribution to the society in a dynamic environment."),
            ("Holistic Formation", "Nurturing intellectual competence, moral integrity, social sensitivity, and leadership skills to address contemporary socio-technical challenges."),
            ("Dynamic Contribution", "Equipping engineering students with cutting-edge technical capabilities to create transformative civic tools and social impact."),
            ("Societal Engagement", "Promoting community-engaged scholarship where students apply academic knowledge directly to public institutions and civil society needs.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=11
    )
    
    add_info_card(
        s2, CONTENT_LEFT + COL2_WIDTH + COL2_GAP, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "University Vision & Core Values",
        [
            ("Institutional Vision", "Excellence and Service — striving for academic rigour, technical excellence, and dedicated public service through technical innovation."),
            ("Faith in God", "Inspiring ethical responsibility and truthfulness in research, data handling, and scientific representation."),
            ("Moral Uprightness", "Ensuring highest standards of data integrity, transparency, and research ethics in judicial information analysis."),
            ("Love of Fellow Beings", "Developing accessible technological tools that enhance public transparency and institutional accessibility."),
            ("Social Responsibility", "Directing software engineering skills toward strengthening open legal data access and justice-sector administration."),
            ("Pursuit of Excellence", "Delivering robust, validated, production-grade software architectures for judicial research.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=11
    )

    # -------------------------------------------------------------
    # SLIDE 3: SERVICE LEARNING & TEAM DETAILS
    # -------------------------------------------------------------
    s3 = add_standard_16x9_slide("SERVICE LEARNING PROJECT & TEAM")
    add_badge(s3, CONTENT_LEFT, Inches(1.62), Inches(2.4), Inches(0.32), "COLLABORATION PROFILE", TAG_GREEN_BG, TAG_GREEN_TEXT)
    
    add_info_card(
        s3, CONTENT_LEFT, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Project Context & Community Partner",
        [
            ("Project Title", "DAKSH — Judicial Research & Court-Case Information Platform"),
            ("Community Partner", "DAKSH (Bengaluru, Karnataka, India)"),
            ("Partner Profile", "A prominent civil society organization dedicated to data-driven judicial research, court administration reform, and empirical legal analysis."),
            ("Service Learning Focus", "Bridging the gap between raw, distributed public court records and empirical researchers by creating a structured data platform."),
            ("Core Objective", "Transforming fragmented eCourts web data into a centralized, searchable research workspace that saves researcher hours and enables longitudinal studies.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )
    
    add_info_card(
        s3, CONTENT_LEFT + COL2_WIDTH + COL2_GAP, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Engineering Team (5BTCS AIML A)",
        [
            ("Mishael Julian (2462184)", "Automated Data Acquisition Layer, Playwright orchestration & browser session lifecycle."),
            ("Steven Mathew (2462157)", "Structured Schema Modeling, Relational Information Storage & Database Architecture."),
            ("Julius Thomas (2462095)", "Pure DOM Parsing Engine, Data Normalization & Multi-Format Exporter."),
            ("Abhishan Francis (2462835)", "Extraction Workflow Coordination, Automated Field Auditing & Parity Verification."),
            ("Rahul Prakash (2462133)", "Researcher UI/UX Design, Search/Filter Engine & Downstream AI Architecture."),
            ("Department", "Department of Computer Science and Engineering, CHRIST (Deemed to be University).")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )

    # -------------------------------------------------------------
    # SLIDE 4: ABSTRACT
    # -------------------------------------------------------------
    s4 = add_standard_16x9_slide("ABSTRACT")
    add_badge(s4, CONTENT_LEFT, Inches(1.62), Inches(2.2), Inches(0.32), "EXECUTIVE SUMMARY", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    add_info_card(
        s4, CONTENT_LEFT, CONTENT_TOP, CONTENT_WIDTH, CONTENT_HEIGHT,
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
    # SLIDE 5: COMMUNITY PROFILE & STAKEHOLDERS
    # -------------------------------------------------------------
    s5 = add_standard_16x9_slide("COMMUNITY PROFILE & STAKEHOLDER CONTEXT")
    add_badge(s5, CONTENT_LEFT, Inches(1.62), Inches(2.5), Inches(0.32), "STAKEHOLDER ANALYSIS", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    add_info_card(
        s5, CONTENT_LEFT, CONTENT_TOP, COL3_WIDTH, CONTENT_HEIGHT,
        "Community Partner",
        [
            ("Organization", "DAKSH (Bengaluru)"),
            ("Domain", "Civil society justice-sector research organization."),
            ("Mission", "Pioneering data-driven insights into court workflows, case pendency, judicial delay, and justice administration."),
            ("Key Requirement", "Reliable, structured datasets containing complete case histories, hearing logs, and disposal details.")
        ],
        header_color=ROYAL_BLUE, title_size=12.5, body_size=10
    )
    
    add_info_card(
        s5, CONTENT_LEFT + COL3_WIDTH + COL3_GAP, CONTENT_TOP, COL3_WIDTH, CONTENT_HEIGHT,
        "Target Researchers & Users",
        [
            ("Judicial Researchers", "Legal empiricists analyzing caseload trends, hearing patterns, and adjournment reasons."),
            ("Policy Analysts", "Scholars evaluating procedural reforms and court system bottlenecks."),
            ("Legal Academics", "Institutions requiring structured, verified datasets for legal research."),
            ("Core Benefit", "Enables researchers to spend time on deep analysis rather than tedious manual record retrieval.")
        ],
        header_color=ROYAL_BLUE, title_size=12.5, body_size=10
    )
    
    add_info_card(
        s5, CONTENT_LEFT + (COL3_WIDTH + COL3_GAP)*2, CONTENT_TOP, COL3_WIDTH, CONTENT_HEIGHT,
        "Ethical & System Boundaries",
        [
            ("Public Data Only", "Operates strictly on publicly accessible eCourts information."),
            ("No Judicial Automation", "System does NOT make judicial rulings or replace judicial discretion."),
            ("No Legal Practitioner Replacement", "Serves purely as an analytical research workspace for researchers."),
            ("Data Fidelity Priority", "Preserves exact public records without synthetic alterations.")
        ],
        header_color=ROYAL_BLUE, title_size=12.5, body_size=10
    )

    # -------------------------------------------------------------
    # SLIDE 6: PROBLEMS FACED BY THE COMMUNITY
    # -------------------------------------------------------------
    s6 = add_standard_16x9_slide("PROBLEMS FACED BY JUDICIAL RESEARCHERS")
    add_badge(s6, CONTENT_LEFT, Inches(1.62), Inches(2.4), Inches(0.32), "RESEARCH BOTTLENECK", TAG_AMBER_BG, TAG_AMBER_TEXT)
    
    add_info_card(
        s6, CONTENT_LEFT, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Portal & Data Disconnection",
        [
            ("Distributed Case Sections", "Crucial case details, hearing logs, process tables, and daily orders are split across multiple disparate web tabs and popups."),
            ("Separate Order Links", "Daily business records and substantive orders must be clicked and inspected individually, requiring dozens of manual clicks per case."),
            ("Lack of Unified View", "No single interface aggregates a case's chronological life cycle into a unified research workspace."),
            ("Session & CAPTCHA Friction", "Repeated manual searches frequently time out or require constant re-entry of CAPTCHAs, halting research momentum.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )
    
    add_info_card(
        s6, CONTENT_LEFT + COL2_WIDTH + COL2_GAP, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Analytical & Scalability Barriers",
        [
            ("No Relational Querying", "eCourts does not support querying across multi-variable parameters (e.g., comparing disposal stages across specific case types)."),
            ("Severe Scalability Limits", "Conducting empirical studies across hundreds or thousands of cases is practically impossible through manual copying."),
            ("Data Inconsistency Risk", "Manual note-taking and copy-pasting lead to human transcription errors, missing fields, and unverified data."),
            ("Loss of Analysis Time", "Over 80% of research time is consumed by basic data collection rather than substantive legal and policy analysis.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )

    # -------------------------------------------------------------
    # SLIDE 7: CONFIRMATION LETTER PLACEHOLDER
    # -------------------------------------------------------------
    s7 = add_standard_16x9_slide("CONFIRMATION LETTER")
    add_badge(s7, CONTENT_LEFT, Inches(1.62), Inches(2.3), Inches(0.32), "OFFICIAL EVIDENCE", TAG_GREEN_BG, TAG_GREEN_TEXT)
    
    box_doc = add_card_box(s7, Inches(2.5), CONTENT_TOP, Inches(8.333), CONTENT_HEIGHT, WHITE, CARD_BORDER)
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
    # SLIDE 8: NEED ANALYSIS
    # -------------------------------------------------------------
    s8 = add_standard_16x9_slide("NEED ANALYSIS")
    add_badge(s8, CONTENT_LEFT, Inches(1.62), Inches(2.2), Inches(0.32), "LOGICAL PROGRESSION", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    steps = [
        ("1. CURRENT STATE", "Researchers navigate individual eCourts portal pages and disparate case tabs manually."),
        ("2. STRUCTURAL CHALLENGE", "Relevant information is highly fragmented across case details, hearings, processes, and orders."),
        ("3. MANUAL BURDEN", "Repetitive manual lookup, note-taking, and copying cause severe human fatigue and transcription error."),
        ("4. SCALABILITY BOTTLENECK", "Empirical legal research cannot scale beyond small sample sizes due to massive labor overhead."),
        ("5. SYSTEMIC NEED", "A centralized, structured, and auditable judicial research information system."),
        ("6. DAKSH SOLUTION", "End-to-end platform: Automated Data Layer + Structured Database + Researcher Workspace.")
    ]
    
    step_h = Inches(0.60)
    for idx, (title_step, desc_step) in enumerate(steps):
        bg = TAG_BLUE_BG if idx == 5 else LIGHT_BG
        brd = ROYAL_BLUE if idx == 5 else CARD_BORDER
        hdr_c = ROYAL_BLUE if idx == 5 else NAVY
        cbox = add_card_box(s8, CONTENT_LEFT, CONTENT_TOP + idx * (step_h + Inches(0.10)), CONTENT_WIDTH, step_h, bg, brd)
        tf = cbox.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.18)
        tf.margin_top = Inches(0.06)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = title_step + " — "
        r1.font.name = "Trebuchet MS"
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r1.font.color.rgb = hdr_c
        
        r2 = p.add_run()
        r2.text = desc_step
        r2.font.name = "Tahoma"
        r2.font.size = Pt(10)
        r2.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 9: IMPACT IF THE PROBLEM REMAINS UNSOLVED
    # -------------------------------------------------------------
    s9 = add_standard_16x9_slide("IMPACT IF THE PROBLEM REMAINS UNSOLVED")
    add_badge(s9, CONTENT_LEFT, Inches(1.62), Inches(2.4), Inches(0.32), "CONSEQUENCE ANALYSIS", TAG_AMBER_BG, TAG_AMBER_TEXT)
    
    add_info_card(
        s9, CONTENT_LEFT, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Research & Institutional Consequences",
        [
            ("Perpetual Manual Inefficiency", "Researchers will continue spending over 80% of project time on routine portal navigation and copy-pasting instead of data analysis."),
            ("Severe Sample Size Limitations", "Judicial studies remain restricted to 20–50 cases, preventing macro-level empirical evaluation of court administration."),
            ("Fragmented Institutional Datasets", "Every research team compiles isolated, ad-hoc spreadsheets without standardized schemas, hindering cross-study comparison."),
            ("Incomplete Historical Context", "Failure to systematically capture daily status transcripts leads to lost procedural insights regarding case adjournments.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )
    
    add_info_card(
        s9, CONTENT_LEFT + COL2_WIDTH + COL2_GAP, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Policy & Civic Consequences",
        [
            ("Delayed Evidence-Based Insights", "Policy think tanks and reform advocates lack aggregated empirical evidence to recommend procedural improvements."),
            ("Barriers to Transparency", "Public court information remains technically public but practically inaccessible for comprehensive empirical auditing."),
            ("Inability to Track Case Lifecycles", "Execution Petitions (EX) and pending decrees cannot be tracked longitudinally across years and court complexes."),
            ("High Opportunity Cost", "Substantial academic funding and researcher effort are wasted on redundant manual data extraction.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )

    # -------------------------------------------------------------
    # SLIDE 10: PROBLEM STATEMENT
    # -------------------------------------------------------------
    s10 = add_standard_16x9_slide("PROBLEM STATEMENT")
    add_badge(s10, CONTENT_LEFT, Inches(1.62), Inches(2.3), Inches(0.32), "CORE FORMULATION", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    box_ps = add_card_box(s10, CONTENT_LEFT, CONTENT_TOP, CONTENT_WIDTH, CONTENT_HEIGHT, WHITE, CARD_BORDER)
    tf_ps = box_ps.text_frame
    tf_ps.word_wrap = True
    tf_ps.margin_left = Inches(0.3)
    tf_ps.margin_right = Inches(0.3)
    tf_ps.margin_top = Inches(0.18)
    
    p0 = tf_ps.paragraphs[0]
    p0.text = "Formal Problem Formulation"
    p0.font.name = "Trebuchet MS"
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = NAVY
    p0.space_after = Pt(8)
    
    p_quote = tf_ps.add_paragraph()
    p_quote.text = "“Judicial researchers investigating court administration and case workflows are severely hindered by the fragmented, multi-page structure of public court portals. The lack of a centralized, structured database and researcher-centric query workspace turns large-scale case analysis into an error-prone, repetitive, and labor-intensive manual endeavor. There is an urgent need for an integrated judicial research platform that systematically acquires, validates, and normalizes public eCourts data into structured records, providing an intuitive workspace for rich search, multidimensional filtering, and downstream analytical exploration.”"
    p_quote.font.name = "Georgia"
    p_quote.font.size = Pt(11.5)
    p_quote.font.italic = True
    p_quote.font.color.rgb = ROYAL_BLUE
    p_quote.space_after = Pt(12)
    
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
        r1.font.size = Pt(10)
        r1.font.bold = True
        r1.font.color.rgb = NAVY
        
        r2 = p_pil.add_run()
        r2.text = pil_d
        r2.font.name = "Tahoma"
        r2.font.size = Pt(10)
        r2.font.color.rgb = CHARCOAL
        p_pil.space_after = Pt(3)

    # -------------------------------------------------------------
    # SLIDE 11: PROJECT OBJECTIVES
    # -------------------------------------------------------------
    s11 = add_standard_16x9_slide("PROJECT OBJECTIVES")
    add_badge(s11, CONTENT_LEFT, Inches(1.62), Inches(2.4), Inches(0.32), "PLATFORM GOALS", TAG_GREEN_BG, TAG_GREEN_TEXT)
    
    objs = [
        ("1. Automated Data Acquisition", "Systematically collect publicly available case records, hearing histories, daily status logs, processes, and orders from the eCourts portal using Playwright automation."),
        ("2. Structured Information Modeling", "Organize extracted case details into normalized, strongly-typed relational records (CNR, registration details, parties, acts, hearings, business transcripts)."),
        ("3. Relational Storage Architecture", "Develop a structured database schema and export pipeline preserving complete case context with zero data loss and full Unicode (Kannada) fidelity."),
        ("4. Intuitive Researcher UI/UX", "Design a centralized web workspace providing multi-parameter search, dynamic court/case-type dropdowns, and tabbed case inspection views."),
        ("5. Elimination of Manual Overhead", "Dramatically reduce repetitive manual lookup time, enabling empirical researchers to focus on data analysis rather than data retrieval."),
        ("6. Foundation for Future AI/ML", "Establish an auditable data foundation capable of supporting future case similarity clustering, pendency trend analytics, and researcher-defined prioritization.")
    ]
    
    card_h11 = Inches(1.28)
    for i, (ot, od) in enumerate(objs):
        col = i % 2
        row = i // 2
        left_pos = CONTENT_LEFT if col == 0 else CONTENT_LEFT + COL2_WIDTH + COL2_GAP
        top_pos = CONTENT_TOP + row * (card_h11 + Inches(0.14))
        
        cbox = add_card_box(s11, left_pos, top_pos, COL2_WIDTH, card_h11, LIGHT_BG, CARD_BORDER)
        tf = cbox.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.14)
        tf.margin_right = Inches(0.14)
        tf.margin_top = Inches(0.06)
        
        p0 = tf.paragraphs[0]
        p0.text = ot
        p0.font.name = "Trebuchet MS"
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = ROYAL_BLUE
        p0.space_after = Pt(2)
        
        p1 = tf.add_paragraph()
        p1.text = od
        p1.font.name = "Tahoma"
        p1.font.size = Pt(9.5)
        p1.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 12: PROPOSED SOLUTION & SYSTEM ARCHITECTURE
    # -------------------------------------------------------------
    s12 = add_standard_16x9_slide("PROPOSED SYSTEM ARCHITECTURE")
    add_badge(s12, CONTENT_LEFT, Inches(1.62), Inches(2.4), Inches(0.32), "MULTI-TIER PLATFORM", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    tiers = [
        ("TIER 1: PUBLIC DATA SOURCE", "Official eCourts Services Portal (District Courts / City Civil Court Complexes)", TAG_AMBER_BG, TAG_AMBER_TEXT),
        ("TIER 2: DATA ACQUISITION LAYER", "Python 3.12 + Playwright Automation | Session Lifecycle & Human-in-the-Loop CAPTCHA", TAG_BLUE_BG, TAG_BLUE_TEXT),
        ("TIER 3: PARSING & VALIDATION", "BeautifulSoup4 DOM Extraction | 100% Zero-Loss Field Audit Suite & Parity Verifier", TAG_GREEN_BG, TAG_GREEN_TEXT),
        ("TIER 4: STRUCTURED STORAGE", "Normalized Data Models | Relational Schema, JSON Records, Consolidated Master CSV/XLSX", TAG_BLUE_BG, TAG_BLUE_TEXT),
        ("TIER 5: DAKSH APPLICATION CORE", "Query Engine, Multi-Parameter Filters, Case Workspace Router & Aggregation APIs", TAG_GREEN_BG, TAG_GREEN_TEXT),
        ("TIER 6: RESEARCHER UI/UX WORKSPACE", "Search Bar, District/Type Dropdowns, Case Details, Hearing History, Daily Status & Orders", TAG_BLUE_BG, TAG_BLUE_TEXT),
        ("TIER 7: FUTURE AI / ML INTELLIGENCE", "Case Clustering, Pendency Trend Analytics & Decision-Support Case Priority Queue [FUTURE]", TAG_PURPLE_BG, TAG_PURPLE_TEXT)
    ]
    
    tier_h = Inches(0.50)
    for i, (t_title, t_sub, bg, txt) in enumerate(tiers):
        tbox = add_card_box(s12, CONTENT_LEFT, CONTENT_TOP + i * (tier_h + Inches(0.08)), CONTENT_WIDTH, tier_h, bg, CARD_BORDER)
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.18)
        tf.margin_top = Inches(0.05)
        
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = t_title + " → "
        r1.font.name = "Trebuchet MS"
        r1.font.size = Pt(10)
        r1.font.bold = True
        r1.font.color.rgb = txt
        
        r2 = p.add_run()
        r2.text = t_sub
        r2.font.name = "Tahoma"
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 13: DATA ACQUISITION LAYER (FOUNDATION)
    # -------------------------------------------------------------
    s13 = add_standard_16x9_slide("DATA ACQUISITION LAYER")
    add_badge(s13, CONTENT_LEFT, Inches(1.62), Inches(2.7), Inches(0.32), "FOUNDATIONAL INGESTION TIER", TAG_GREEN_BG, TAG_GREEN_TEXT)
    
    add_info_card(
        s13, CONTENT_LEFT, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Automated Navigation & Ingestion",
        [
            ("Role in Hierarchy", "Scraping is strictly the data acquisition foundation — not the final research application."),
            ("Target Portal", "eCourts Case Status Portal (Search by Case Type / Complex)."),
            ("State & District Selection", "Automated dropdown selection for Karnataka / BENGALURU City Civil Court Complex."),
            ("Establishment & Case Type", "PRL. CITY CIVIL AND SESSIONS JUDGE / EX – Execution Petition Under Order."),
            ("CAPTCHA Handling", "Clean pause workflow for human-in-the-loop CAPTCHA entry to ensure reliability.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )
    
    add_info_card(
        s13, CONTENT_LEFT + COL2_WIDTH + COL2_GAP, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Deep Section Extraction Workflow",
        [
            ("Case Details", "Filing/Registration numbers, CNR, first hearing, decision date, case status, judge."),
            ("Parties & Advocates", "Complete petitioner and respondent hierarchies with assigned legal counsel."),
            ("Acts & Sections", "Exhaustive extraction of statutory provisions and sections invoked."),
            ("Case History", "Every hearing row: Judge, Business Date, Hearing Date, Purpose of Hearing."),
            ("Orders & Daily Status", "Visits EVERY order hyperlink; extracts complete judicial business transcripts."),
            ("Zero Data Loss Audit", "Automated parity auditor verifies Web DOM == JSON == CSV == XLSX.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )

    # -------------------------------------------------------------
    # SLIDE 14: STRUCTURED DATABASE & INFORMATION MODEL
    # -------------------------------------------------------------
    s14 = add_standard_16x9_slide("STRUCTURED DATABASE & INFORMATION MODEL")
    add_badge(s14, CONTENT_LEFT, Inches(1.62), Inches(2.5), Inches(0.32), "RELATIONAL SCHEMA", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    add_info_card(
        s14, CONTENT_LEFT, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Core Entities & Relational Schema",
        [
            ("CASE Entity (Master)", "CNR Number (PK), Registration No, Filing Date, Decision Date, Status, Nature of Disposal, Court/Judge."),
            ("Parties & Counsel", "1-to-many relationship: Petitioners, Respondents, and Advocates linked to Case ID."),
            ("Acts & Provisions", "Statute names, section numbers, and legal classifications."),
            ("Hearing History", "Chronological table: Business Date, Next Hearing Date, Purpose of Hearing (Notice, Summons, Disposal)."),
            ("Daily Status & Business", "Complete verbatim transcripts of daily orders with disposal remarks."),
            ("Processes & Transfers", "Process ID, Title, Issue Date, Transferring & Receiving Courts.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )
    
    add_info_card(
        s14, CONTENT_LEFT + COL2_WIDTH + COL2_GAP, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Data Integrity & Architectural Benefits",
        [
            ("Relational Querying", "Enables SQL/indexed querying across complex multi-variable judicial parameters."),
            ("Linguistic Preservation", "Full UTF-8 with BOM support preserving English, Kannada, and vernacular notations without corruption."),
            ("Standardized Export Formats", "Provides clean JSON, relational CSVs, and Excel outputs for downstream statistical software."),
            ("Extensible Data Foundation", "Engineered to seamlessly support future API endpoints, web dashboards, and AI analytics models.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )

    # -------------------------------------------------------------
    # SLIDE 15: PROPOSED APPLICATION & RESEARCHER UI/UX
    # -------------------------------------------------------------
    s15 = add_standard_16x9_slide("PROPOSED RESEARCHER UI/UX WORKSPACE")
    add_badge(s15, CONTENT_LEFT, Inches(1.62), Inches(2.7), Inches(0.32), "PROPOSED APPLICATION UI", TAG_AMBER_BG, TAG_AMBER_TEXT)
    
    add_info_card(
        s15, CONTENT_LEFT, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Search & Multi-Parameter Filter Panel",
        [
            ("Global Search Bar", "Direct lookup by CNR Number, Case Number, Party Name, or Advocate Name."),
            ("Dynamic Dropdowns", "Hierarchical selection: State → District → Court Complex → Establishment."),
            ("Case Classification Filters", "Filter by Case Type (EX, OS, CC), Filing Year, Decision Year, and Case Status (Pending/Disposed)."),
            ("Stage & Purpose Filters", "Filter cases by specific hearing purposes (e.g., Summons, Evidence, Arguments, Orders)."),
            ("Interactive Results Grid", "Displays matching cases with summary metrics: duration, hearing count, and last order date.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )
    
    add_info_card(
        s15, CONTENT_LEFT + COL2_WIDTH + COL2_GAP, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Case Information Workspace (Tabbed View)",
        [
            ("Tab 1: Case Overview", "Summary cards showing registration metadata, judge, court complex, and disposal nature."),
            ("Tab 2: Hearing Chronology", "Interactive timeline of all hearing dates, business dates, and recorded hearing purposes."),
            ("Tab 3: Daily Status Transcripts", "Synchronized transcript viewer displaying daily judicial business notes."),
            ("Tab 4: Parties & Advocates", "Structured party hierarchy with legal representation history."),
            ("Tab 5: Orders & Documents", "Centralized repository of all interlocutory and final orders with download options.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )

    # -------------------------------------------------------------
    # SLIDE 16: RESEARCHER USER JOURNEY
    # -------------------------------------------------------------
    s16 = add_standard_16x9_slide("RESEARCHER USER JOURNEY")
    add_badge(s16, CONTENT_LEFT, Inches(1.62), Inches(2.5), Inches(0.32), "END-TO-END WORKFLOW", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    journey_steps = [
        ("1. Open DAKSH Platform", "Researcher accesses the centralized judicial research web application."),
        ("2. Select Search Parameters", "Selects Court Complex (e.g., Bengaluru City Civil), Case Type (EX), and Year range (2010–2023)."),
        ("3. Apply Research Filters", "Applies granular filters by disposal nature, specific statutory act, or pending duration."),
        ("4. Inspect Results Explorer", "Reviews matching case cards displaying case age, total hearings, and latest stage."),
        ("5. Open Case Workspace", "Opens a unified workspace displaying synchronized hearing histories, daily notes, and orders."),
        ("6. Analyze & Export", "Performs cross-case comparison and exports structured datasets (CSV/JSON) for empirical analysis.")
    ]
    
    step_h16 = Inches(0.60)
    for idx, (j_title, j_desc) in enumerate(journey_steps):
        bg = TAG_BLUE_BG if idx % 2 == 0 else LIGHT_BG
        cbox = add_card_box(s16, CONTENT_LEFT, CONTENT_TOP + idx * (step_h16 + Inches(0.10)), CONTENT_WIDTH, step_h16, bg, CARD_BORDER)
        tf = cbox.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.18)
        tf.margin_top = Inches(0.06)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = j_title + " → "
        r1.font.name = "Trebuchet MS"
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r1.font.color.rgb = ROYAL_BLUE
        
        r2 = p.add_run()
        r2.text = j_desc
        r2.font.name = "Tahoma"
        r2.font.size = Pt(10)
        r2.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 17: FUTURE SCOPE: INTELLIGENT JUDICIAL ANALYTICS
    # -------------------------------------------------------------
    s17 = add_standard_16x9_slide("FUTURE SCOPE: INTELLIGENT JUDICIAL ANALYTICS")
    add_badge(s17, CONTENT_LEFT, Inches(1.62), Inches(2.7), Inches(0.32), "FUTURE SCOPE — ROADMAP", TAG_PURPLE_BG, TAG_PURPLE_TEXT)
    
    add_info_card(
        s17, CONTENT_LEFT, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Proposed Analytical Capabilities",
        [
            ("Case Similarity & Clustering", "Unsupervised clustering of cases based on statutory provisions, party configurations, and procedural trajectories."),
            ("Pendency & Duration Modeling", "Statistical modeling of stage duration to identify key bottlenecks in execution petition lifecycles."),
            ("Adjournment Pattern Analysis", "Analyzing frequency and recorded purposes of adjournments to understand trial delay factors."),
            ("Disposal Trend Evaluation", "Longitudinal comparisons of disposal rates across court establishments and case categories.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )
    
    add_info_card(
        s17, CONTENT_LEFT + COL2_WIDTH + COL2_GAP, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Information Retrieval & Assistance",
        [
            ("Semantic Search", "Fast text retrieval across unstructured daily status business logs and order texts."),
            ("Document Classification", "Automated tagging of orders by nature of relief granted (interim vs. final)."),
            ("Research Recommendations", "Surfacing related historical cases with similar procedural trajectories for researcher review."),
            ("Ethical Research Boundary", "Analytical tools are intended strictly for academic and policy research; system does not predict outcomes or replace human judgment.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )

    # -------------------------------------------------------------
    # SLIDE 18: PROPOSED CASE PRIORITIZATION SYSTEM
    # -------------------------------------------------------------
    s18 = add_standard_16x9_slide("PROPOSED CASE PRIORITIZATION SYSTEM")
    add_badge(s18, CONTENT_LEFT, Inches(1.62), Inches(3.0), Inches(0.32), "PROPOSED FUTURE DECISION SUPPORT", TAG_PURPLE_BG, TAG_PURPLE_TEXT)
    
    add_info_card(
        s18, CONTENT_LEFT, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Prioritization Mechanism & Workflow",
        [
            ("Structured Input Data", "Ingests normalized case features: case age, total pending duration, hearing frequency, and stage."),
            ("Researcher-Defined Weights", "Researchers configure scoring criteria (e.g., cases pending > 5 years, repetitive notice stages)."),
            ("Multi-Factor Scoring Engine", "Calculates composite priority index according to transparent, configurable rules."),
            ("Dynamic Case Priority Queue", "Generates prioritized cohorts for focused empirical study and delay analysis."),
            ("Cohort Export", "Enables researchers to export high-priority case subsets for qualitative legal evaluation.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )
    
    add_info_card(
        s18, CONTENT_LEFT + COL2_WIDTH + COL2_GAP, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Critical Framing & Human Governance",
        [
            ("Research Decision Support Only", "Designed solely to help researchers organize, filter, and prioritize large case volumes for academic study."),
            ("NOT an Automated Judicial Decision-Maker", "Does NOT determine which cases a judge must hear or alter court scheduling."),
            ("Transparent & Auditable", "Every priority score is fully traceable to explicit statutory and procedural feature weights."),
            ("Human Oversight Preserved", "Final analysis and interpretation remain completely under authorized human researcher control.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )

    # -------------------------------------------------------------
    # SLIDE 19: FUTURE AI / ML PIPELINE ARCHITECTURE
    # -------------------------------------------------------------
    s19 = add_standard_16x9_slide("FUTURE AI / ML PIPELINE ARCHITECTURE")
    add_badge(s19, CONTENT_LEFT, Inches(1.62), Inches(2.8), Inches(0.32), "FUTURE ARCHITECTURAL DESIGN", TAG_PURPLE_BG, TAG_PURPLE_TEXT)
    
    ai_pipeline = [
        ("1. Structured Database", "Verified, normalized court dataset (Master Case details, Hearing History, Daily Status, Orders)."),
        ("2. Data Preprocessing", "Text cleaning, Unicode tokenization, missing value imputation, and entity normalization."),
        ("3. Feature Engineering", "Extracts procedural metrics: total adjournments, hearing intervals, stage duration, and textual embeddings."),
        ("4. ML & Analytics Models", "Clustering algorithms (K-Means, DBSCAN), similarity search, and rule-based priority scoring."),
        ("5. Case Representations", "Generates multi-dimensional vector embeddings and procedural feature vectors for each case."),
        ("6. Researcher Dashboard", "Delivers interactive visual dashboards, cohort filtering, and empirical analytical reports.")
    ]
    
    step_h19 = Inches(0.60)
    for idx, (p_title, p_desc) in enumerate(ai_pipeline):
        bg = TAG_PURPLE_BG if idx >= 3 else LIGHT_BG
        cbox = add_card_box(s19, CONTENT_LEFT, CONTENT_TOP + idx * (step_h19 + Inches(0.10)), CONTENT_WIDTH, step_h19, bg, CARD_BORDER)
        tf = cbox.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.18)
        tf.margin_top = Inches(0.06)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = p_title + " → "
        r1.font.name = "Trebuchet MS"
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r1.font.color.rgb = ROYAL_BLUE
        
        r2 = p.add_run()
        r2.text = p_desc
        r2.font.name = "Tahoma"
        r2.font.size = Pt(10)
        r2.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 20: SOFTWARE REQUIREMENTS & TECH STACK
    # -------------------------------------------------------------
    s20 = add_standard_16x9_slide("SOFTWARE REQUIREMENTS & TECH STACK")
    add_badge(s20, CONTENT_LEFT, Inches(1.62), Inches(2.4), Inches(0.32), "VERIFIED TECH STACK", TAG_GREEN_BG, TAG_GREEN_TEXT)
    
    add_info_card(
        s20, CONTENT_LEFT, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Automation, Parsing & Storage",
        [
            ("Programming Runtime", "Python 3.12+ (modern asynchronous features and robust typing)."),
            ("Browser Automation", "Playwright with Chromium engine for robust portal navigation and session management."),
            ("HTML & DOM Parsing", "BeautifulSoup4 + lxml parser for fast, accurate structured HTML extraction."),
            ("Data Serialization", "JSON (strongly-typed dataclass schemas in `models.py`)."),
            ("Spreadsheet & Relational Export", "Pandas, OpenPyXL, and UTF-8 with BOM CSV compilation.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )
    
    add_info_card(
        s20, CONTENT_LEFT + COL2_WIDTH + COL2_GAP, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "System Resilience & Quality Assurance",
        [
            ("Logging Architecture", "Python `logging` with timed rotating file handlers (`ecourts_scraper.log`)."),
            ("Fault Tolerance", "Custom exponential backoff retry decorators for network resilience."),
            ("Field Auditing Suite", "Automated zero-loss field validation comparing Web DOM vs. JSON vs. CSV."),
            ("Unit & Integration Testing", "Pytest automated test suites verifying model schemas and exporter consistency.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )

    # -------------------------------------------------------------
    # SLIDE 21: HARDWARE & RUNTIME ENVIRONMENT
    # -------------------------------------------------------------
    s21 = add_standard_16x9_slide("HARDWARE & RUNTIME ENVIRONMENT")
    add_badge(s21, CONTENT_LEFT, Inches(1.62), Inches(2.4), Inches(0.32), "SYSTEM REQUIREMENTS", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    add_info_card(
        s21, CONTENT_LEFT, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Hardware & System Environment",
        [
            ("Architecture Type", "Software-based data pipeline and web application platform."),
            ("Compute Hardware", "Standard laptop or workstation (Intel Core i5 / AMD Ryzen 5 or higher)."),
            ("Memory (RAM)", "8 GB RAM minimum (16 GB recommended for large dataset processing)."),
            ("Storage", "10 GB available SSD storage for case databases, JSON records, and logs."),
            ("Operating System", "Cross-platform compatibility: Windows 11, Linux (Ubuntu 22.04+), macOS.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )
    
    add_info_card(
        s21, CONTENT_LEFT + COL2_WIDTH + COL2_GAP, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Network & Client Environment",
        [
            ("Network Connectivity", "Stable broadband internet connection required for live eCourts portal queries."),
            ("Client Web Browser", "Modern web browser (Google Chrome, Mozilla Firefox, Microsoft Edge)."),
            ("Display Resolution", "1080p FHD (1920x1080) optimized for researcher multi-tab case workspace."),
            ("No Specialized Sensors", "Pure software platform — requires no microcontrollers, cameras, or embedded hardware.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )

    # -------------------------------------------------------------
    # SLIDE 22: DATA INTEGRITY & VALIDATION FRAMEWORK
    # -------------------------------------------------------------
    s22 = add_standard_16x9_slide("DATA INTEGRITY & VALIDATION FRAMEWORK")
    add_badge(s22, CONTENT_LEFT, Inches(1.62), Inches(2.5), Inches(0.32), "QUALITY ASSURANCE", TAG_GREEN_BG, TAG_GREEN_TEXT)
    
    add_info_card(
        s22, CONTENT_LEFT, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Core Integrity Principles",
        [
            ("Guiding Principle", "“Incorrect information is far more harmful than unavailable information.”"),
            ("Source Traceability", "Every database record retains exact CNR and court registration numbers for 100% auditability."),
            ("Cross-Format Parity", "Strict 1-to-1 parity verification: Web DOM row count == JSON entries == CSV rows == Excel rows."),
            ("Explicit Null Handling", "Unpopulated portal fields are explicitly stored as `null` rather than fabricated with synthetic defaults.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )
    
    add_info_card(
        s22, CONTENT_LEFT + COL2_WIDTH + COL2_GAP, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Linguistic & Technical Safeguards",
        [
            ("Unicode / Script Fidelity", "Full preservation of Kannada vernacular text and special legal characters in business notes."),
            ("Anti-Contamination Checks", "Strict case-boundary isolation ensuring orders and history records cannot cross-pollinate between cases."),
            ("Atomicity in Serialization", "Atomic writing routines prevent corrupted partial records during unexpected interruptions."),
            ("Automated Audit Logs", "Every extraction run generates machine-readable audit reports verifying all sections PASS.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )

    # -------------------------------------------------------------
    # SLIDE 23: SERVICE LEARNING VALUE & ACADEMIC OUTCOMES
    # -------------------------------------------------------------
    s23 = add_standard_16x9_slide("SERVICE LEARNING VALUE & ACADEMIC IMPACT")
    add_badge(s23, CONTENT_LEFT, Inches(1.62), Inches(2.6), Inches(0.32), "COMMUNITY ENGAGEMENT", TAG_GREEN_BG, TAG_GREEN_TEXT)
    
    add_info_card(
        s23, CONTENT_LEFT, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Real-World Civic Technology",
        [
            ("Beyond 'Learning Scraping'", "Value lies in engineering a sustainable data pipeline and application that empowers public judicial research."),
            ("Direct Civic Contribution", "Directly assists DAKSH in their mission to analyze court delay, case pendency, and justice administration."),
            ("Open Legal Data Access", "Transforms opaque, multi-step web records into standardized, reusable open datasets for empirical legal scholars."),
            ("Institutional Trust", "Adheres to rigorous academic data integrity, transparency, and ethical handling standards.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )
    
    add_info_card(
        s23, CONTENT_LEFT + COL2_WIDTH + COL2_GAP, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Technical & Professional Learning",
        [
            ("Applied Software Engineering", "Mastered browser automation (Playwright), asynchronous DOM parsing, and robust error recovery."),
            ("Data Modeling & Relational Design", "Architected comprehensive relational schemas capturing complex judicial lifecycles."),
            ("UI/UX for Specialized Domains", "Designed domain-specific researcher workflows, search interfaces, and case workspaces."),
            ("Interdisciplinary Experience", "Bridged computer science and empirical legal research to create meaningful social impact.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )

    # -------------------------------------------------------------
    # SLIDE 24: TECHNICAL EVIDENCE & BENCHMARK VALIDATION
    # -------------------------------------------------------------
    s24 = add_standard_16x9_slide("TECHNICAL EVIDENCE & BENCHMARK VALIDATION")
    add_badge(s24, CONTENT_LEFT, Inches(1.62), Inches(2.5), Inches(0.32), "VERIFIED EXECUTION", TAG_GREEN_BG, TAG_GREEN_TEXT)
    
    add_info_card(
        s24, CONTENT_LEFT, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT,
        "Validated Benchmark Dataset (2010 EX Cases)",
        [
            ("Live Portal Execution", "Successfully navigated Karnataka eCourts portal for Bengaluru City Civil Court Complex."),
            ("Benchmark Scope", "Complete extraction of the first 20 disposed Executive Petition (EX) cases from 2010."),
            ("100% Field Capture", "Extracted all case details, party hierarchies, acts/sections, hearing histories, and business orders."),
            ("Validated Outputs", "Generated `Consolidated_Executive_Petitions_2023_FINAL.csv`, `cases.json`, and supporting relation CSVs."),
            ("Automated Audit Pass", "Audit suite verified 0 missing fields across all sections and perfect row-count parity.")
        ],
        header_color=ROYAL_BLUE, title_size=13.5, body_size=10.5
    )
    
    if os.path.exists("Ecourts Navigating.jpeg"):
        img_box = add_card_box(s24, CONTENT_LEFT + COL2_WIDTH + COL2_GAP, CONTENT_TOP, COL2_WIDTH, CONTENT_HEIGHT, WHITE, CARD_BORDER)
        s24.shapes.add_picture("Ecourts Navigating.jpeg", CONTENT_LEFT + COL2_WIDTH + COL2_GAP + Inches(0.15), CONTENT_TOP + Inches(0.15), Inches(5.18), Inches(2.35))
        
        tb = s24.shapes.add_textbox(CONTENT_LEFT + COL2_WIDTH + COL2_GAP + Inches(0.15), CONTENT_TOP + Inches(2.6), Inches(5.18), Inches(1.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        p0.text = "Technical Evidence: eCourts Navigation Pipeline"
        p0.font.name = "Trebuchet MS"
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = NAVY
        
        p1 = tf.add_paragraph()
        p1.text = "Automated case-type search configuration, dynamic establishment selection, and Playwright session management on official Karnataka eCourts portal."
        p1.font.name = "Tahoma"
        p1.font.size = Pt(9.5)
        p1.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 25: CURRENT IMPLEMENTATION STATUS
    # -------------------------------------------------------------
    s25 = add_standard_16x9_slide("CURRENT IMPLEMENTATION STATUS")
    add_badge(s25, CONTENT_LEFT, Inches(1.62), Inches(2.5), Inches(0.32), "PROJECT MILESTONES", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    add_info_card(
        s25, CONTENT_LEFT, CONTENT_TOP, COL3_WIDTH, CONTENT_HEIGHT,
        "Completed & Validated\n[CURRENT SYSTEM]",
        [
            ("Playwright Automation", "Dynamic portal navigation, search execution & human-in-the-loop CAPTCHA."),
            ("Multi-Section Parser", "Exhaustive extraction of case metadata, parties, acts, hearings & orders."),
            ("Daily Status Extraction", "Automated opening and scraping of every order hyperlink and business text."),
            ("Zero-Loss Auditor", "Automated field-by-field audit suite confirming 100% capture fidelity."),
            ("Benchmark Dataset", "Gold-standard 2010 Bengaluru City Civil Court EX dataset produced.")
        ],
        header_color=TAG_GREEN_TEXT, bg_color=TAG_GREEN_BG, border_color=TAG_GREEN_TEXT, title_size=12, body_size=9.5
    )
    
    add_info_card(
        s25, CONTENT_LEFT + COL3_WIDTH + COL3_GAP, CONTENT_TOP, COL3_WIDTH, CONTENT_HEIGHT,
        "Currently In Development\n[PROPOSED APP]",
        [
            ("Relational DB Modeling", "Structuring PostgreSQL / SQLite schema for high-speed indexed search."),
            ("Researcher UI/UX", "Designing intuitive frontend with multi-parameter filter dropdowns and case tabs."),
            ("Consolidated Exporter", "Scaling extraction pipelines from 2010 benchmark to 2023–2025 datasets."),
            ("Case Workspace Prototyping", "Building synchronized timeline viewer for hearing logs and daily orders.")
        ],
        header_color=TAG_BLUE_TEXT, bg_color=TAG_BLUE_BG, border_color=TAG_BLUE_TEXT, title_size=12, body_size=9.5
    )
    
    add_info_card(
        s25, CONTENT_LEFT + (COL3_WIDTH + COL3_GAP)*2, CONTENT_TOP, COL3_WIDTH, CONTENT_HEIGHT,
        "Future Scope\n[ROADMAP]",
        [
            ("AI/ML Judicial Analytics", "Case similarity clustering, delay bottleneck detection, and trend modeling."),
            ("Priority Queue Mechanism", "Configurable decision-support scoring for researcher cohort prioritization."),
            ("Semantic Search Engine", "Vector embeddings for full-text querying across judicial business notes."),
            ("Multi-Court Expansion", "Scaling pipeline across South Indian district and High Court portals.")
        ],
        header_color=TAG_PURPLE_TEXT, bg_color=TAG_PURPLE_BG, border_color=TAG_PURPLE_TEXT, title_size=12, body_size=9.5
    )

    # -------------------------------------------------------------
    # SLIDE 26: STRATEGIC PROJECT ROADMAP
    # -------------------------------------------------------------
    s26 = add_standard_16x9_slide("STRATEGIC PROJECT ROADMAP")
    add_badge(s26, CONTENT_LEFT, Inches(1.62), Inches(2.3), Inches(0.32), "DEVELOPMENT PHASES", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    roadmap_phases = [
        ("PHASE 1: DATA ACQUISITION FOUNDATION", "Automated eCourts extraction, Playwright session management, benchmark dataset creation.", "COMPLETED", TAG_GREEN_BG, TAG_GREEN_TEXT),
        ("PHASE 2: STRUCTURED DATABASE MODELING", "Relational schema engineering, zero-loss field auditing, and multi-format dataset compilation.", "IN PROGRESS", TAG_BLUE_BG, TAG_BLUE_TEXT),
        ("PHASE 3: RESEARCHER UI/UX WORKSPACE", "Intuitive search bar, dynamic court dropdowns, tabbed case viewer, and CSV/JSON export.", "IN PROGRESS", TAG_BLUE_BG, TAG_BLUE_TEXT),
        ("PHASE 4: MULTI-DISTRICT SCALING", "Expanding ingestion pipeline from 2010 benchmark to 2023–2025 across multiple court complexes.", "PLANNED", TAG_AMBER_BG, TAG_AMBER_TEXT),
        ("PHASE 5: AI / ML JUDICIAL ANALYTICS", "Unsupervised case clustering, pendency trend analysis, and statutory pattern discovery.", "FUTURE SCOPE", TAG_PURPLE_BG, TAG_PURPLE_TEXT),
        ("PHASE 6: DECISION-SUPPORT PRIORITIZATION", "Researcher-defined case priority scoring and empirical cohort organization queues.", "FUTURE SCOPE", TAG_PURPLE_BG, TAG_PURPLE_TEXT)
    ]
    
    step_h26 = Inches(0.60)
    for idx, (p_title, p_desc, p_badge, b_bg, b_txt) in enumerate(roadmap_phases):
        cbox = add_card_box(s26, CONTENT_LEFT, CONTENT_TOP + idx * (step_h26 + Inches(0.10)), CONTENT_WIDTH, step_h26, LIGHT_BG, CARD_BORDER)
        tf = cbox.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.18)
        tf.margin_top = Inches(0.06)
        p = tf.paragraphs[0]
        
        r1 = p.add_run()
        r1.text = p_title + "  [" + p_badge + "] — "
        r1.font.name = "Trebuchet MS"
        r1.font.size = Pt(10)
        r1.font.bold = True
        r1.font.color.rgb = b_txt
        
        r2 = p.add_run()
        r2.text = p_desc
        r2.font.name = "Tahoma"
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 27: CONCLUSION
    # -------------------------------------------------------------
    s27 = add_standard_16x9_slide("CONCLUSION")
    add_badge(s27, CONTENT_LEFT, Inches(1.62), Inches(2.2), Inches(0.32), "PROJECT SYNTHESIS", TAG_BLUE_BG, TAG_BLUE_TEXT)
    
    box_c = add_card_box(s27, CONTENT_LEFT, CONTENT_TOP, CONTENT_WIDTH, CONTENT_HEIGHT, WHITE, CARD_BORDER)
    tf_c = box_c.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = Inches(0.3)
    tf_c.margin_right = Inches(0.3)
    tf_c.margin_top = Inches(0.18)
    
    p0 = tf_c.paragraphs[0]
    p0.text = "Transforming Court Information into Empirical Judicial Intelligence"
    p0.font.name = "Trebuchet MS"
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = NAVY
    p0.space_after = Pt(8)
    
    p_main = tf_c.add_paragraph()
    p_main.text = "“DAKSH is not merely a web scraper; it is an integrated judicial research technology platform designed to resolve the severe data fragmentation of public court portals. By establishing a validated data acquisition layer, a normalized relational database, and an intuitive researcher-centric workspace, the system empowers empirical researchers to focus on analysis rather than repetitive manual extraction. As the platform evolves toward advanced analytics and intelligent prioritization support, it creates a sustainable technological bridge for evidence-based justice sector reforms.”"
    p_main.font.name = "Georgia"
    p_main.font.size = Pt(11.5)
    p_main.font.italic = True
    p_main.font.color.rgb = ROYAL_BLUE
    p_main.space_after = Pt(12)
    
    takeaways = [
        ("Data Acquisition Foundation", "Automated Playwright ingestion provides a robust, zero-loss technical foundation."),
        ("Centralized Platform Vision", "Transforms scattered HTML pages into a centralized, searchable, tabbed case workspace."),
        ("Academic & Civic Impact", "Directly empowers DAKSH and empirical legal scholars with auditable, high-quality judicial data.")
    ]
    for tk_t, tk_d in takeaways:
        pt = tf_c.add_paragraph()
        r1 = pt.add_run()
        r1.text = "• " + tk_t + ": "
        r1.font.name = "Tahoma"
        r1.font.size = Pt(10)
        r1.font.bold = True
        r1.font.color.rgb = NAVY
        
        r2 = pt.add_run()
        r2.text = tk_d
        r2.font.name = "Tahoma"
        r2.font.size = Pt(10)
        r2.font.color.rgb = CHARCOAL
        pt.space_after = Pt(3)

    # -------------------------------------------------------------
    # SLIDE 28: THANK YOU (16:9 Widescreen)
    # -------------------------------------------------------------
    s28 = prs.slides.add_slide(prs.slide_layouts[0])
    for shape in s28.shapes:
        if shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            if shape.name == 'Title 1':
                shape.left = Inches(1.5)
                shape.top = Inches(2.0)
                shape.width = Inches(10.333)
                shape.height = Inches(1.5)
                
                p0 = tf.paragraphs[0]
                p0.text = "THANK YOU"
                p0.font.name = "Times New Roman"
                p0.font.size = Pt(40)
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
                shape.left = Inches(1.5)
                shape.top = Inches(3.8)
                shape.width = Inches(10.333)
                shape.height = Inches(2.2)
                
                p0 = tf.paragraphs[0]
                p0.text = "Questions & Discussion"
                p0.font.name = "Trebuchet MS"
                p0.font.size = Pt(16)
                p0.font.bold = True
                p0.font.color.rgb = NAVY
                p0.alignment = PP_ALIGN.CENTER
                
                p1 = tf.add_paragraph()
                p1.text = "Service Learning Project in Collaboration with DAKSH, Bengaluru"
                p1.font.name = "Tahoma"
                p1.font.size = Pt(12)
                p1.font.color.rgb = CHARCOAL
                p1.alignment = PP_ALIGN.CENTER
                
                p2 = tf.add_paragraph()
                p2.text = "Team: Mishael Julian | Steven Mathew | Julius Thomas | Abhishan Francis | Rahul Prakash (5BTCS AIML A)"
                p2.font.name = "Tahoma"
                p2.font.size = Pt(11)
                p2.font.bold = True
                p2.font.color.rgb = ROYAL_BLUE
                p2.alignment = PP_ALIGN.CENTER
                
                p3 = tf.add_paragraph()
                p3.text = "Department of Computer Science and Engineering | CHRIST (Deemed to be University), Bengaluru"
                p3.font.name = "Tahoma"
                p3.font.size = Pt(10)
                p3.font.color.rgb = MUTED_GRAY
                p3.alignment = PP_ALIGN.CENTER

    output_path = "DAKSH_Service_Learning_Presentation_16x9.pptx"
    prs.save(output_path)
    print(f"Successfully generated {output_path} with {len(prs.slides)} slides in 16:9 widescreen!")

if __name__ == "__main__":
    create_daksh_16x9_presentation()
