import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

NAVY = RGBColor(15, 23, 42)       # #0F172A
ROYAL_BLUE = RGBColor(30, 58, 138) # #1E3A8A
SLATE = RGBColor(71, 85, 105)      # #475569
TEXT_DARK = RGBColor(30, 41, 59)   # #1E293B
TEAL = RGBColor(13, 148, 136)      # #0D9488
AMBER = RGBColor(217, 119, 6)      # #D97706

def set_cell_background(cell, fill_hex):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_cell_border_left_only(cell, color_hex="1E3A8A", sz="36"):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color_hex}"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

def set_table_borders(table, color_hex="CBD5E1"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{color_hex}"/>'
        f'<w:left w:val="none"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color_hex}"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color_hex}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def init_document():
    doc = docx.Document()
    
    # Page setup: Standard Letter/A4, 0.8 in margins for professional look
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.85)
        s.right_margin = Inches(0.85)
        s.different_first_page_header_footer = True
        
        # Header for subsequent pages
        header = s.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("EventIQ — Complete Project Explanation & Viva Guide  |  Academic Defense")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = SLATE
        
        # Footer
        footer = s.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        frun1 = fp.add_run("Information Retrieval & Ranking Research  •  Department of Computer Science & Engineering")
        frun1.font.name = "Calibri"
        frun1.font.size = Pt(8.5)
        frun1.font.color.rgb = SLATE

    # Base styling
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = TEXT_DARK
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    return doc

def add_title_page(doc):
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(80)
    title_p.paragraph_format.space_after = Pt(6)
    r_tag = title_p.add_run("FINAL YEAR ACADEMIC PROJECT  •  CAPSTONE DEFENSE GUIDE")
    r_tag.font.name = "Calibri"
    r_tag.font.size = Pt(10)
    r_tag.font.bold = True
    r_tag.font.color.rgb = ROYAL_BLUE
    
    h_title = doc.add_paragraph()
    h_title.paragraph_format.space_after = Pt(12)
    r_title = h_title.add_run("EventIQ: An Intelligent Event Retrieval and Ranking System")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(26)
    r_title.font.bold = True
    r_title.font.color.rgb = NAVY
    
    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(36)
    r_sub = sub_p.add_run("Complete Project Explanation, Mathematical Theory, Implementation Walkthrough & Exhaustive Viva Voce Preparation Guide")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = SLATE

    meta_table = doc.add_table(rows=7, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.LEFT
    meta_data = [
        ("Domain:", "Information Retrieval (IR), Natural Language Search, Neural Ranking"),
        ("Architectures Evaluated:", "TF-IDF Vector Space, Okapi BM25, MiniLM Semantic, Score Fusion (α=0.70), Intent Re-ranking (λ=0.15)"),
        ("Corpus Scale:", "10,000 Event Documents | 500 Test Queries | 7,500 Graded Relevance Labels"),
        ("Full-Stack Tech Stack:", "PostgreSQL, Python 3.12, FastAPI, Sentence-Transformers, React 19, Vite, Recharts"),
        ("Evaluation Standards:", "TREC Cranfield Pooling, Precision@K, Recall@10, F1, MRR, NDCG@10"),
        ("Target Audience:", "Viva Voce Examiners, University Faculty, Technical Evaluators, Project Lead"),
        ("Document Version:", "3.0 (Post-Hardening Production Release)")
    ]
    for row_idx, (label, val) in enumerate(meta_data):
        c0 = meta_table.cell(row_idx, 0)
        c1 = meta_table.cell(row_idx, 1)
        c0.width = Inches(2.2)
        c1.width = Inches(4.6)
        p0 = c0.paragraphs[0]
        p1 = c1.paragraphs[0]
        p0.paragraph_format.space_after = Pt(4)
        p1.paragraph_format.space_after = Pt(4)
        r0 = p0.add_run(label)
        r0.font.bold = True
        r0.font.size = Pt(10)
        r0.font.color.rgb = ROYAL_BLUE
        r1 = p1.add_run(val)
        r1.font.size = Pt(10)
        set_cell_background(c0, "F8FAFC")
        set_cell_background(c1, "F8FAFC")
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
    set_table_borders(meta_table, "E2E8F0")

    doc.add_page_break()

def add_heading_1(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(18)
    h.paragraph_format.space_after = Pt(8)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(17)
    r.font.bold = True
    r.font.color.rgb = ROYAL_BLUE
    return h

def add_heading_2(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(5)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = NAVY
    return h

def add_heading_3(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(10)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = SLATE
    return h

def add_p(doc, text, bold_prefix=None, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_bold = p.add_run(bold_prefix)
        r_bold.font.bold = True
        r_bold.font.color.rgb = NAVY
    r = p.add_run(text)
    r.font.color.rgb = TEXT_DARK
    return p

def add_bullet(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_bold = p.add_run(bold_prefix)
        r_bold.font.bold = True
        r_bold.font.color.rgb = NAVY
    r = p.add_run(text)
    r.font.color.rgb = TEXT_DARK
    return p

def add_callout(doc, box_title, text_body, box_type="teacher"):
    # box_type: 'teacher' (blue), 'tip' (teal), 'alert' (amber)
    color_map = {
        "teacher": ("1E3A8A", "F0F7FF", ROYAL_BLUE),
        "tip": ("0D9488", "F0FDF4", TEAL),
        "alert": ("D97706", "FFFBEB", AMBER)
    }
    hex_border, hex_bg, title_color = color_map.get(box_type, ("1E3A8A", "F8FAFC", ROYAL_BLUE))
    
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.cell(0, 0)
    c.width = Inches(6.8)
    set_cell_background(c, hex_bg)
    set_cell_margins(c, top=140, bottom=140, left=200, right=200)
    set_cell_border_left_only(c, color_hex=hex_border, sz="36")
    
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(4)
    r_head = p.add_run(f"★  {box_title.upper()}\n")
    r_head.font.bold = True
    r_head.font.size = Pt(9.5)
    r_head.font.color.rgb = title_color
    
    r_body = p.add_run(text_body)
    r_body.font.size = Pt(10)
    r_body.font.color.rgb = TEXT_DARK
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_formula_box(doc, formula_title, formula_latex, variable_explanations):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.cell(0, 0)
    c.width = Inches(6.8)
    set_cell_background(c, "F8FAFC")
    set_cell_margins(c, top=140, bottom=140, left=180, right=180)
    set_cell_border_left_only(c, color_hex="3B82F6", sz="24")
    
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(4)
    r_title = p.add_run(f"FORMULA: {formula_title}\n")
    r_title.font.bold = True
    r_title.font.size = Pt(9.5)
    r_title.font.color.rgb = ROYAL_BLUE
    
    r_form = p.add_run(f"    {formula_latex}\n\n")
    r_form.font.name = "Consolas"
    r_form.font.size = Pt(10.5)
    r_form.font.bold = True
    r_form.font.color.rgb = NAVY
    
    for var, desc in variable_explanations:
        p_var = c.add_paragraph()
        p_var.paragraph_format.space_after = Pt(2)
        r_v = p_var.add_run(f"  • {var}: ")
        r_v.font.bold = True
        r_v.font.size = Pt(9.5)
        r_v.font.color.rgb = SLATE
        r_d = p_var.add_run(desc)
        r_d.font.size = Pt(9.5)
        r_d.font.color.rgb = TEXT_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_table_styled(doc, headers, rows, col_widths=None):
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, "CBD5E1")
    
    # Headers
    for c_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, c_idx)
        if col_widths and c_idx < len(col_widths):
            cell.width = Inches(col_widths[c_idx])
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(h_text)
        r.font.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    # Rows
    for r_idx, row_data in enumerate(rows):
        bg = "FFFFFF" if r_idx % 2 == 0 else "F8FAFC"
        for c_idx, val in enumerate(row_data):
            cell = tbl.cell(r_idx + 1, c_idx)
            if col_widths and c_idx < len(col_widths):
                cell.width = Inches(col_widths[c_idx])
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(str(val))
            r.font.size = Pt(9.5)
            r.font.color.rgb = TEXT_DARK
            
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def add_diagram_box(doc, title, ascii_diagram):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.cell(0, 0)
    c.width = Inches(6.8)
    set_cell_background(c, "F1F5F9")
    set_cell_margins(c, top=120, bottom=120, left=150, right=150)
    set_cell_border_left_only(c, color_hex="0F172A", sz="24")
    
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(4)
    r_t = p.add_run(f"ARCHITECTURE / FLOW DIAGRAM: {title}\n\n")
    r_t.font.bold = True
    r_t.font.size = Pt(9.5)
    r_t.font.color.rgb = ROYAL_BLUE
    
    r_d = p.add_run(ascii_diagram)
    r_d.font.name = "Consolas"
    r_d.font.size = Pt(8.5)
    r_d.font.color.rgb = NAVY
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_code_box(doc, title, code_snippet):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.cell(0, 0)
    c.width = Inches(6.8)
    set_cell_background(c, "F8FAFC")
    set_cell_margins(c, top=100, bottom=100, left=150, right=150)
    set_cell_border_left_only(c, color_hex="475569", sz="20")
    
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(3)
    r_t = p.add_run(f"CODE IMPLEMENTATION: {title}\n")
    r_t.font.bold = True
    r_t.font.size = Pt(9.0)
    r_t.font.color.rgb = SLATE
    
    r_code = p.add_run(code_snippet)
    r_code.font.name = "Consolas"
    r_code.font.size = Pt(8.5)
    r_code.font.color.rgb = NAVY
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
