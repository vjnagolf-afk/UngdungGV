import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json

# Cấu hình
SHEET_ID = '1C6642jk_oQ0g9UC2By2qsNxxfQVR0MrZYj52tRdWDlY' # Hãy đảm bảo ID này đúng

def get_sheet():
    creds_dict = dict(st.secrets["GOOGLE_KEY"])
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    # Dùng sheet1 để tránh lỗi sai tên tab
    return client.open_by_key(SHEET_ID).sheet1

def save_to_sheets(ten_du_an, noi_dung):
    try:
        sheet = get_sheet()
        ngay_luu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([str(ten_du_an), str(noi_dung), str(ngay_luu)])
        return True
    except Exception as e:
        st.error(f"Lỗi lưu: {e}")
        return False

# --- CÁC THẺ GIAO DIỆN ---
def render_tab_1():
    st.markdown("### 💡 Thông tin Sản phẩm")
    st.write("Chào mừng thầy đến với không gian sáng tạo STEM. Đây là nơi quản lý các sản phẩm dự án của thầy.")

def render_tab_2():
    st.success("🛠️ THẺ 2: Soạn KHBD.")
    if "stem_generated_content" not in st.session_state:
        st.session_state.stem_generated_content = ""
    
    ten_du_an = st.text_input("Tên dự án:", key="ten_t2")
    
    if st.button("🚀 KÍCH HOẠT AI BIÊN SOẠN KHBD"):
        # Logic gọi AI của thầy (đây là chỗ để thầy dán hàm gọi AI cũ vào)
        st.session_state.stem_generated_content = "Nội dung kế hoạch bài dạy chi tiết..."
    
    if st.session_state.stem_generated_content:
        st.info("Kết quả từ AI:")
        st.text_area("Nội dung:", value=st.session_state.stem_generated_content, height=200)
        if st.button("💾 LƯU VÀO GOOGLE SHEETS"):
            if save_to_sheets(ten_du_an, st.session_state.stem_generated_content):
                st.toast("Đã lưu thành công lên Sheets!", icon="✅")

def render_tab_3():
    st.markdown("### 📁 KHBD ĐÃ LƯU")
    st.write("Danh sách các kế hoạch bài dạy thầy đã soạn.")

# --- HÀM GỌI CHÍNH ---
def render_stem_section():
    st.markdown("## 🚀 HỆ SINH THÁI GIÁO DỤC STEM")
    tab1, tab2, tab3 = st.tabs(["💡 1. SẢN PHẨM", "🛠️ 2. XÂY DỰNG KHBD", "📁 3. KHBD ĐÃ LƯU"])
    
    with tab1: render_tab_1()
    with tab2: render_tab_2()
    with tab3: render_tab_3()
