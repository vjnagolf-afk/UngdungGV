import streamlit as st
import io
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from docx import Document
from google import genai

# =========================================================
# CẤU HÌNH GOOGLE SHEETS
# =========================================================
SHEET_ID = 'DÁN_SHEET_ID_CỦA_THẦY_VÀO_ĐÂY'
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name('google_key.json', SCOPE)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet("STEM_Projects")

# =========================================================
# CÁC HÀM XỬ LÝ DỮ LIỆU & WORD
# =========================================================
def create_word_file(title, content):
    doc = Document()
    doc.add_heading(title, 0)
    clean_content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
    clean_content = clean_content.replace('**', '').replace('*', '')
    doc.add_paragraph(clean_content)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# =========================================================
# HÀM RENDER TỪNG THẺ
# =========================================================
def render_tab_1():
    st.info("💡 **THẺ 1 - BỘ LỌC:** Chọn tiêu chí để AI gợi ý dự án STEM.")
    # (Giữ nguyên logic bộ lọc của thầy ở đây...)
    # Nếu cần em sẽ gửi lại chi tiết phần logic này!

def render_tab_2():
    st.success("🛠️ **THẺ 2 - THIẾT KẾ KHBD:** Nhập tên dự án để AI soạn thảo.")
    ten_chu_de_t2 = st.text_input("Tên dự án:", key="ten_t2")
    
    if st.button("🚀 KÍCH HOẠT AI BIÊN SOẠN KHBD"):
        # Gọi Gemini API như đã làm...
        # Lưu vào session_state
        pass

    if st.session_state.stem_generated_content:
        if st.button("💾 LƯU VÀO GOOGLE SHEETS"):
            sheet = get_sheet()
            sheet.append_row([ten_chu_de_t2, st.session_state.stem_generated_content, "2026-07-09"])
            st.toast("Đã lưu vào Google Sheets!", icon="✅")

def render_tab_3():
    st.warning("📁 **THẺ 3 - KHBD ĐÃ LƯU:** Đọc dữ liệu từ Google Sheets.")
    if st.button("🔄 Tải lại danh sách từ Sheets"):
        sheet = get_sheet()
        data = sheet.get_all_records()
        st.session_state.stem_saved_projects = {row['Ten_Du_An']: row['Noi_Dung'] for row in data}
    
    for ten, nd in st.session_state.stem_saved_projects.items():
        with st.expander(f"📌 {ten}"):
            st.markdown(nd)

# =========================================================
# HÀM CHÍNH
# =========================================================
def render_stem_section():
    st.markdown("## 🚀 HỆ SINH THÁI GIÁO DỤC STEM")
    if "stem_saved_projects" not in st.session_state: st.session_state.stem_saved_projects = {}
    
    tab1, tab2, tab3 = st.tabs(["💡 1. SẢN PHẨM", "🛠️ 2. XÂY DỰNG KHBD", "📁 3. KHBD ĐÃ LƯU"])
    with tab1: render_tab_1()
    with tab2: render_tab_2()
    with tab3: render_tab_3()
