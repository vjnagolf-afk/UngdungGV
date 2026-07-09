import streamlit as st
import io
import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pypdf import PdfReader
import matplotlib.pyplot as plt
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ================= CẤU HÌNH ĐỒNG BỘ GOOGLE SHEETS =================
SHEET_ID = '1C6642jk_oQ0g9UC2By2qsNxxfQVR0MrZYj52tRdWDlY'

def get_dekt_sheet():
    creds_dict = dict(st.secrets["GOOGLE_KEY"])
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet("DE_KT")

# --- CÁC HÀM XỬ LÝ (GIỮ NGUYÊN GỐC CỦA THẦY) ---
def read_uploaded_docx(uploaded_file):
    try:
        doc = Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])
    except: return "Lỗi đọc file Word"

def read_uploaded_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    except: return "Lỗi đọc file PDF"

def generate_plot_stream(eq_str):
    fig, ax = plt.subplots(figsize=(5, 3.5))
    x = np.linspace(-10, 10, 400)
    safe_dict = {"x": x, "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan, "sqrt": np.sqrt}
    try:
        eq_str_py = eq_str.replace('^', '**')
        y = eval(eq_str_py, {"__builtins__": {}}, safe_dict)
        if isinstance(y, (int, float)): y = np.full_like(x, y)
        ax.plot(x, y, color='#1E40AF', linewidth=2.5)
        ax.axhline(0, color='black', linewidth=1.2)
        ax.axvline(0, color='black', linewidth=1.2)
        ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
        ax.set_ylim([-10, 10])
        ax.set_title(f"Đồ thị: y = {eq_str}", fontsize=10, pad=10)
    except:
        ax.text(0.5, 0.5, f"[Không thể vẽ đồ thị: Sai cú pháp toán học]", ha='center', va='center', color='red')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    plt.close(fig)
    return buf

def export_to_docx_vietnam_standard(text_content, title_name, school_name="TRƯỜNG THCS NGUYỄN CHÍ THANH", group_name="TỔ KHOA HỌC TỰ NHIÊN - GDTC"):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(1.18)
        section.right_margin = Inches(0.59)
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(14)
    admin_table = doc.add_table(rows=1, cols=2)
    admin_table.autofit = False
    admin_table.columns[0].width = Inches(3.2)
    admin_table.columns[1].width = Inches(3.8)
    cell_l = admin_table.rows[0].cells[0]
    p_left = cell_l.paragraphs[0]
    p_left.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_left.add_run(f"{school_name.upper()}\n").bold = True
    p_left.add_run(f"{group_name.upper()}\n").bold = True
    p_left.add_run("Số: ..... /BB-TCM").font.size = Pt(11)
    cell_r = admin_table.rows[0].cells[1]
    p_right = cell_r.paragraphs[0]
    p_right.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_right.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n").bold = True
    p_right.add_run("Độc lập - Tự do - Hạnh phúc\n").bold = True
    p_right.add_run("***************").font.size = Pt(11)
    doc.add_paragraph()
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.add_run(title_name.upper()).bold = True
    in_table = False
    table_data = []
    def process_runs(paragraph, text):
        bold_parts = text.split('**')
        for i, b_part in enumerate(bold_parts):
            is_bold = (i % 2 != 0)
            sub_sup_parts = re.split(r'(<sub>.*?</sub>|<sup>.*?</sup>)', b_part)
            for part in sub_sup_parts:
                if not part: continue
                if part.startswith('<sub>') and part.endswith('</sub>'):
                    run = paragraph.add_run(part[5:-6]); run.bold = is_bold; run.font.subscript = True
                elif part.startswith('<sup>') and part.endswith('</sup>'):
                    run = paragraph.add_run(part[5:-6]); run.bold = is_bold; run.font.superscript = True
                else:
                    run = paragraph.add_run(part); run.bold = is_bold
    def build_table():
        if not table_data: return
        cols = len(table_data[0])
        table = doc.add_table(rows=len(table_data), cols=cols)
        table.style = 'Table Grid'
        for r_idx, row in enumerate(table_data):
            for c_idx, cell_val in enumerate(row):
                if c_idx < cols:
                    cell = table.cell(r_idx, c_idx)
                    p = cell.paragraphs[0]; p.text = ""; process_runs(p, cell_val.strip())
        doc.add_paragraph()
    for line in text_content.split('\n'):
        cleaned_line = line.strip()
        if cleaned_line.startswith('|') and cleaned_line.endswith('|'):
            in_table = True
            row_data = [cell.strip() for cell in cleaned_line.split('|')[1:-1]]
            if all(re.match(r'^[-: ]+$', cell) for cell in row_data): continue
            table_data.append(row_data)
            continue
        if in_table: build_table(); in_table = False; table_data = []
        if not cleaned_line: continue
        if '[GRAPH:' in cleaned_line:
            match = re.search(r'\[GRAPH:\s*(.+?)\]', cleaned_line)
            if match:
                eq = match.group(1); img_stream = generate_plot_stream(eq)
                doc.add_picture(img_stream, width=Inches(3.5)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER; continue
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if cleaned_line.startswith('#'):
            process_runs(p, cleaned_line.replace('#', '').strip());
            for run in p.runs: run.bold = True
        else: process_runs(p, cleaned_line)
    if in_table: build_table()
    bio = io.BytesIO(); doc.save(bio); return bio.getvalue()

# --- GIAO DIỆN CHÍNH (CÓ TÍCH HỢP ĐỒNG BỘ ĐÁM MÂY) ---
def render_exam_designer_section(api_key_input, run_ai_prompt_safe_func):
    st.markdown("""<style> ... </style>""", unsafe_allow_html=True) # (Giữ nguyên style của thầy)
    
    if "db_de_kiem_tra" not in st.session_state: st.session_state["db_de_kiem_tra"] = []
    if "cloud_data_dekt" not in st.session_state: st.session_state["cloud_data_dekt"] = []

    tab_thiet_ke, tab_kho_luu_tru = st.tabs(["📝 CHỨC NĂNG: TẠO ĐỀ KIỂM TRA AI", "☁️ KHO ĐÁM MÂY (GOOGLE SHEETS)"])
    
    with tab_thiet_ke:
        # (GIỮ NGUYÊN TOÀN BỘ CÁC COLUMN VÀ WIDGET CỦA THẦY Ở ĐÂY)
        # ... Sau phần logic "if btn_tao:" và hiển thị kết quả ...
        if st.session_state.get("current_exam_designer_output"):
            # THÊM NÚT LƯU ĐÁM MÂY VÀO ĐÚNG VỊ TRÍ NÀY
            if st.button("☁️ Lưu Đồng Bộ Lên Google Sheets", type="primary", use_container_width=True):
                try:
                    sheet = get_dekt_sheet()
                    ten_de = f"Đề {mon_de} - {khoi_de} ({thoi_gian_de})"
                    sheet.append_row([ten_de, mon_de, hinh_thuc, st.session_state["current_exam_designer_output"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                    st.success("✅ Đã đồng bộ lên Google Sheets!")
                except Exception as e: st.error(f"Lỗi: {e}")

    with tab_kho_luu_tru:
        st.subheader("📂 Các đề kiểm tra từ Đám mây")
        if st.button("🔄 Tải mới từ Google Sheets"):
            st.session_state["cloud_data_dekt"] = get_dekt_sheet().get_all_values()
        
        for idx, row in enumerate(st.session_state.get("cloud_data_dekt", [])):
            if len(row) >= 4:
                with st.expander(f"📋 {row[0]} (Lưu: {row[4]})"):
                    st.markdown(row[3])
                    if st.button("❌ Xóa đề", key=f"del_{idx}"):
                        get_dekt_sheet().delete_row(idx + 1)
                        st.rerun()
