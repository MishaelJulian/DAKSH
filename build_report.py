import os
import shutil
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=100, bottom=100, left=120, right=120):
    """Set cell padding in dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_border(cell, **kwargs):
    """
    Set cell borders.
    kwargs: top, bottom, left, right
    values: dict(sz=4, val='single', color='000000')
    """
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for border_name, border_props in kwargs.items():
        node = OxmlElement(f'w:{border_name}')
        for key, val in border_props.items():
            node.set(qn(f'w:{key}'), str(val))
        tcBorders.append(node)
    tcPr.append(tcBorders)

def build_daksh_report():
    src_file = 'WeeklyReport.docx'
    dst_file = 'DAKSH_Weekly_Reflection_Report.docx'
    shutil.copyfile(src_file, dst_file)
    
    doc = docx.Document(dst_file)
    
    # Page setup
    for sec in doc.sections:
        sec.top_margin = Inches(0.8)
        sec.bottom_margin = Inches(0.8)
        sec.left_margin = Inches(0.85)
        sec.right_margin = Inches(0.85)
        sec.page_width = Inches(8.5)
        sec.page_height = Inches(11.0)
    
    # Extract logo from P0
    p0 = doc.paragraphs[0]
    
    # Clear all other elements from doc body except p0
    body = doc._body._element
    # Keep only the first p element (p0)
    for child in list(body):
        if child != p0._element and child.tag.endswith(('p', 'tbl', 'sectPr')) and not child.tag.endswith('sectPr'):
            body.remove(child)
            
    # Format p0 (Logo)
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p0.paragraph_format.space_before = Pt(0)
    p0.paragraph_format.space_after = Pt(4)
    p0.paragraph_format.line_spacing = 1.0

    # Helper function to add paragraph
    def add_p(text='', font_name='Calibri', size_pt=14, bold=False, italic=False, underline=False, 
              align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2, line_spacing=1.0):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if text:
            run = p.add_run(text)
            run.font.name = font_name
            run.font.size = Pt(size_pt)
            run.bold = bold
            run.italic = italic
            run.underline = underline
        return p

    # University header lines (Calibri matching template)
    add_p('Department of Computer Science and Engineering', 'Calibri', 15, bold=True, space_after=1)
    add_p('School of Engineering and Technology', 'Calibri', 13.5, bold=True, space_after=1)
    add_p('CHRIST (Deemed to be University) - Bangalore', 'Calibri', 13.5, bold=True, space_after=1)
    add_p('Program: Service Learning (CS682)', 'Calibri', 15, bold=True, space_after=1)
    add_p('Year: 2026-27', 'Calibri', 15, bold=True, space_after=4)
    
    # Date line
    p_date = add_p('Date: ________________', 'Calibri', 12, bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=2, space_after=8)
    
    # Report Title
    add_p('Weekly Reflection Report', 'Times New Roman', 15, bold=True, underline=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=16)

    # Student Details
    # Row 1: Julius B Thomas
    p_s1 = doc.add_paragraph()
    p_s1.paragraph_format.space_before = Pt(0)
    p_s1.paragraph_format.space_after = Pt(3)
    p_s1.paragraph_format.line_spacing = 1.15
    r = p_s1.add_run('Name   & Reg.No:  ')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11.5)
    r.bold = True
    r2 = p_s1.add_run('1. Julius B Thomas (2462095)')
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(11.5)

    # Other students indented
    students = [
        '2. Steven Mathew (2462157)',
        '3. Mishael Julian (2462184)',
        '4. Rahul J Prakash (2462133)',
        '5. Abhishan Francis (2462835)'
    ]
    for st in students:
        p_st = doc.add_paragraph()
        p_st.paragraph_format.space_before = Pt(0)
        p_st.paragraph_format.space_after = Pt(3)
        p_st.paragraph_format.line_spacing = 1.15
        p_st.paragraph_format.left_indent = Inches(1.58)
        r = p_st.add_run(st)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11.5)

    # Class
    p_cls = doc.add_paragraph()
    p_cls.paragraph_format.space_before = Pt(4)
    p_cls.paragraph_format.space_after = Pt(4)
    p_cls.paragraph_format.line_spacing = 1.15
    r = p_cls.add_run('Class                       :  ')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11.5)
    r.bold = True
    r2 = p_cls.add_run('5BTCS AIML A')
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(11.5)

    # Title of Project
    p_proj = doc.add_paragraph()
    p_proj.paragraph_format.space_before = Pt(4)
    p_proj.paragraph_format.space_after = Pt(4)
    p_proj.paragraph_format.line_spacing = 1.15
    r = p_proj.add_run('Title of Project       :  ')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11.5)
    r.bold = True
    r2 = p_proj.add_run('DAKSH Judicial Research and Court Case Information Platform')
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(11.5)

    # Community Details
    p_comm = doc.add_paragraph()
    p_comm.paragraph_format.space_before = Pt(4)
    p_comm.paragraph_format.space_after = Pt(6)
    p_comm.paragraph_format.line_spacing = 1.15
    r = p_comm.add_run('Community Details:  ')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11.5)
    r.bold = True
    r2 = p_comm.add_run('DAKSH Society, 63, Palace Road, Vasanthanagar, Bangalore - 560 052\n(Organization Focus: Law, Governance, and Judicial Policy Research)')
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(11.5)

    # Add page break to guarantee clean start of Page 2
    doc.add_page_break()

    # ==================== PAGE 2 ====================
    p_odd = doc.add_paragraph()
    p_odd.paragraph_format.space_before = Pt(0)
    p_odd.paragraph_format.space_after = Pt(4)
    r_odd = p_odd.add_run('ODDSEM:')
    r_odd.font.name = 'Times New Roman'
    r_odd.font.size = Pt(11)
    r_odd.bold = True
    r_odd.underline = True

    # Reflection Table
    # Table data
    headers = ['S.NO.', 'Date', 'Goals and Objectives', 'Methodology', 'Team Work (Individual contribution)']
    
    rows_data = [
        (
            '1',
            'Week 1',
            'Understand DAKSH community requirements and judicial research context.',
            'Studied collaboration objectives with DAKSH; analysed judicial research workflows and identified core information needs for court-case studies.',
            '• Julius: Formulated user requirements and research goals.\n• Steven: Studied eCourts access structure.\n• Mishael: Evaluated scraping feasibility.\n• Rahul: Outlined data validation needs.\n• Abhishan: Planned structured data storage.'
        ),
        (
            '2',
            'Week 2',
            'Study eCourts portal structure and case data hierarchy.',
            'Explored eCourts navigation flows; analysed sections including case details, hearing history, daily status, processes, and orders/judgments.',
            '• Julius: Defined key legal fields for researchers.\n• Steven: Mapped court and case navigation paths.\n• Mishael: Built initial extraction prototypes.\n• Rahul: Analyzed court date attributes & types.\n• Abhishan: Designed schema for case entities.'
        ),
        (
            '3',
            'Week 3',
            'Develop and test automated case data acquisition workflow.',
            'Implemented browser-based automation to extract case records from eCourts, handling query parameters and multi-section case views.',
            '• Julius: Verified legal data scope coverage.\n• Steven: Enhanced navigation logic across courts.\n• Mishael: Automated scraping & extraction pipeline.\n• Rahul: Inspected raw output for missing fields.\n• Abhishan: Structured records for database export.'
        ),
        (
            '4',
            'Week 4',
            'Validate extracted datasets and refine field mappings.',
            'Verified extracted fields against source portal; distinguished distinct date types (hearing, process, order, disposal) and resolved schema redundancies.',
            '• Julius: Reviewed semantic accuracy for research.\n• Steven: Handled edge cases and pagination.\n• Mishael: Refined extraction scripts & field maps.\n• Rahul: Validated date mappings and accuracy.\n• Abhishan: Normalized relational data schema.'
        ),
        (
            '5',
            'Week 5',
            'Plan researcher-facing platform and future analytics scope.',
            'Designed architecture for case search, filtering, and workspace views; discussed future scope for research analytics and NLP assistance.',
            '• Julius: Outlined search/filter criteria for policy.\n• Steven: Defined case detail presentation flow.\n• Mishael: Integrated pipeline export for analysis.\n• Rahul: Established consistency & QA guidelines.\n• Abhishan: Designed case workspace & search UX.'
        )
    ]

    col_widths = [Inches(0.55), Inches(0.75), Inches(1.65), Inches(1.80), Inches(2.05)]
    total_w = sum(col_widths) # 6.8 inches

    table = doc.add_table(rows=len(rows_data) + 1, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'

    # Set table borders and formatting
    # Header row
    hdr_cells = table.rows[0].cells
    for i, h_text in enumerate(headers):
        hdr_cells[i].text = h_text
        hdr_cells[i].width = col_widths[i]
        set_cell_margins(hdr_cells[i], top=70, bottom=70, left=80, right=80)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)
            r.bold = True

    # Body rows
    for r_idx, row_content in enumerate(rows_data):
        row_cells = table.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row_content):
            row_cells[c_idx].text = val
            row_cells[c_idx].width = col_widths[c_idx]
            set_cell_margins(row_cells[c_idx], top=60, bottom=60, left=80, right=80)
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            
            if c_idx in (0, 1):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(8.5)
                
            # If multiple paragraphs were created by text assignment (due to newlines in bullets)
            for extra_p in row_cells[c_idx].paragraphs[1:]:
                extra_p.paragraph_format.space_before = Pt(0)
                extra_p.paragraph_format.space_after = Pt(0)
                extra_p.paragraph_format.line_spacing = 1.05
                extra_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for r in extra_p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(8.5)

    # Signature line
    p_sig_space = doc.add_paragraph()
    p_sig_space.paragraph_format.space_before = Pt(16)
    p_sig_space.paragraph_format.space_after = Pt(0)

    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(0)
    p_sig.paragraph_format.space_after = Pt(0)
    p_sig.paragraph_format.line_spacing = 1.0
    
    r_sig1 = p_sig.add_run('Signature (Team Member)                                              ')
    r_sig1.font.name = 'Times New Roman'
    r_sig1.font.size = Pt(11)
    
    r_sig2 = p_sig.add_run('Signature (Faculty In charge)')
    r_sig2.font.name = 'Times New Roman'
    r_sig2.font.size = Pt(11)

    doc.save(dst_file)
    print('Report successfully built!')

if __name__ == '__main__':
    build_daksh_report()
