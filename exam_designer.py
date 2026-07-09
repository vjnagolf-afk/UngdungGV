import streamlit as st
import io
import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from pypdf import PdfReader
import matplotlib.pyplot as plt
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ================= CẤU HÌNH GOOGLE SHEETS =================
SHEET_ID = '1C6642jk_oQ0g9UC2By2qsNxxfQVR0MrZYj52tRdWDlY'

def get_dekt_sheet():
    creds_dict = dict(st.secrets["GOOGLE_KEY"])
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet("DE_KT")

# --- CÁC HÀM XỬ LÝ VĂN BẢN VÀ ĐỒ THỊ ---
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
        ax.text(0.5, 0.5, f"[Không thể vẽ đồ thị]", ha='center', va='center', color='red')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    plt.close(fig)
    return buf

def export_to_docx_vietnam_standard(text_content, title_name):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(14)
    doc.add_paragraph(title_name.upper()).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(text_content)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- GIAO DIỆN CHÍNH ---
def render_exam_designer_section(api_key_input, run_ai_prompt_safe_func):
    if "cloud_data_dekt" not in st.session_state: st.session_state["cloud_data_dekt"] = []
    if "current_exam_designer_output" not in st.session_state: st.session_state["current_exam_designer_output"] = ""

    tab_thiet_ke, tab_kho_luu_tru = st.tabs(["📝 TẠO ĐỀ KIỂM TRA AI", "☁️ KHO ĐÁM MÂY (GOOGLE SHEETS)"])
    
    with tab_thiet_ke:
        hinh_thuc = st.selectbox("Hình thức đề thi:", ["Trắc nghiệm kết hợp tự luận", "100% Trắc nghiệm", "100% Tự luận"])
        mon_de = st.text_input("Môn học:", value="Khoa học tự nhiên")
        khoi_de = st.selectbox("Khối lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"], index=3)
        thoi_gian_de = st.text_input("Thời gian:", value="45 phút")
        
        uploaded_files = st.file_uploader("Tải tài liệu nền", type=["docx", "pdf", "txt"], accept_multiple_files=True)
        run_exam_ai = st.button("🚀 Tự động tạo ma trận & đề thi", type="primary")
        
        if run_exam_ai:
            combined_context_text = ""
            if uploaded_files:
                for file_node in uploaded_files:
                    if file_node.name.endswith(".docx"): combined_context_text += read_uploaded_docx(file_node) + "\n\n"
                    elif file_node.name.endswith(".pdf"): combined_context_text += read_uploaded_pdf(file_node) + "\n\n"

            prompt_exam = f"Thiết kế đề kiểm tra {mon_de} {khoi_de}. Hình thức: {hinh_thuc}. Dữ liệu tham khảo: {combined_context_text}"
            res_text, status = run_ai_prompt_safe_func(prompt_exam, api_key_input)
            st.session_state["current_exam_designer_output"] = res_text
            st.rerun()

        if st.session_state["current_exam_designer_output"]:
            st.markdown(st.session_state["current_exam_designer_output"])
            
            # NÚT LƯU ĐỒNG BỘ
            if st.button("☁️ Lưu Đồng Bộ Lên Google Sheets", type="primary"):
                try:
                    sheet = get_dekt_sheet()
                    ten_de = f"Đề {mon_de} {khoi_de} - {datetime.now().strftime('%d/%m/%Y')}"
                    sheet.append_row([ten_de, mon_de, hinh_thuc, str(st.session_state["current_exam_designer_output"]), datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                    st.success("✅ Đã đồng bộ an toàn lên Google Sheets!")
                except Exception as e:
                    st.error(f"Lỗi: {e}")

    with tab_kho_luu_tru:
        st.markdown("### 📂 KHO ĐÁM MÂY (GOOGLE SHEETS)")
        if st.button("🔄 Tải dữ liệu từ Google Sheets"):
            st.session_state["cloud_data_dekt"] = get_dekt_sheet().get_all_values()
            
        danh_sach = st.session_state.get("cloud_data_dekt", [])
        for idx, row in enumerate(danh_sach):
            if len(row) >= 4: # Kiểm tra độ dài tránh lỗi IndexError
                with st.expander(f"📋 {row[0]} (Lưu: {row[4]})"):
                    st.markdown(row[3])
                    # Nút tải và nút xóa vĩnh viễn
                    if st.button("🗑️ Xóa vĩnh viễn", key=f"del_{idx}"):
                        get_dekt_sheet().delete_row(idx + 1)
                        st.rerun()
