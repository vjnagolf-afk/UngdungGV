import streamlit as st
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

# --- HÀM XUẤT PHÔI WORD KHĐ THEO PHỤ LỤC III BỘ GIÁO DỤC ---
def export_plan_to_docx(teacher_name, subject_name, markdown_content):
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(1.18)
        section.right_margin = Inches(0.59)
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\nĐộc lập - Tự do - Hạnh phúc\n").bold = True
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("\nKẾ HOẠCH GIÁO DỤC CỦA GIÁO VIÊN\n(PHỤ LỤC III CÔNG VĂN 5512/BGDĐT)\n")
    r_title.bold = True
    r_title.font.size = Pt(14)
    r_title.font.color.rgb = RGBColor(255, 0, 0)
    p_info = doc.add_paragraph()
    p_info.add_run(f"Giáo viên thực hiện: {teacher_name}\nMôn học/Hoạt động giáo dục: {subject_name}\n")
    lines = markdown_content.split('\n')
    for line in lines:
        clean_line = line.strip().replace('**', '').replace('###', '').replace('##', '').replace('#', '')
        if not clean_line: continue
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run = p.add_run(clean_line)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        if line.strip().startswith('#') or "I." in clean_line or "II." in clean_line:
            run.bold = True
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()
import streamlit as st
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

# --- HÀM XUẤT PHÔI WORD KHĐ THEO PHỤ LỤC III BỘ GIÁO DỤC ---
def export_plan_to_docx(teacher_name, subject_name, markdown_content):
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(1.18)
        section.right_margin = Inches(0.59)
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\nĐộc lập - Tự do - Hạnh phúc\n").bold = True
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("\nKẾ HOẠCH GIÁO DỤC CỦA GIÁO VIÊN\n(PHỤ LỤC III CÔNG VĂN 5512/BGDĐT)\n")
    r_title.bold = True
    r_title.font.size = Pt(14)
    r_title.font.color.rgb = RGBColor(255, 0, 0)
    p_info = doc.add_paragraph()
    p_info.add_run(f"Giáo viên thực hiện: {teacher_name}\nMôn học/Hoạt động giáo dục: {subject_name}\n")
    lines = markdown_content.split('\n')
    for line in lines:
        clean_line = line.strip().replace('**', '').replace('###', '').replace('##', '').replace('#', '')
        if not clean_line: continue
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run = p.add_run(clean_line)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        if line.strip().startswith('#') or "I." in clean_line or "II." in clean_line:
            run.bold = True
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()
