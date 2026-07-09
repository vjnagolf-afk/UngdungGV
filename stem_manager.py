import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# =========================================================
# CẤU HÌNH GOOGLE SHEETS TỪ SECRETS (KHÔNG DÙNG FILE)
# =========================================================
SHEET_ID = '1C6642jk_oQ0g9UC2By2qsNxxfQVR0MrZYj52tRdWDlY' # Thầy điền lại ID của thầy vào đây nhé

def get_sheet():
    # Chuyển đổi secrets thành dictionary
    creds_dict = dict(st.secrets["GOOGLE_KEY"])
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet("STEM_Projects")

# =========================================================
# HÀM LƯU DỮ LIỆU
# =========================================================
def save_to_sheets(ten_du_an, noi_dung):
    try:
        sheet = get_sheet()
        ngay_luu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Ép kiểu rõ ràng thành chuỗi (string) để gspread không hiểu lầm
        row_data = [str(ten_du_an), str(noi_dung), str(ngay_luu)]
        
        # Ghi dữ liệu
        sheet.append_row(row_data)
        return True
    except Exception as e:
        # Xuất lỗi chi tiết hơn để kiểm tra
        st.error(f"Lỗi lưu Sheets: {type(e).__name__} - {e}")
        return False

# =========================================================
# GIAO DIỆN (ĐÃ KHỞI TẠO BIẾN TRÁNH LỖI ATTRIBUTE)
# =========================================================
def render_tab_2():
    st.success("🛠️ THẺ 2: Soạn KHBD.")
    
    # Khởi tạo biến nếu chưa có
    if "stem_generated_content" not in st.session_state:
        st.session_state.stem_generated_content = ""

    ten_chu_de_t2 = st.text_input("Tên dự án:", key="ten_t2")
    
    if st.button("🚀 KÍCH HOẠT AI BIÊN SOẠN KHBD"):
        # Giả lập kết quả AI
        st.session_state.stem_generated_content = "Nội dung bài dạy về hệ thống chống trộm..."
    
    if st.session_state.stem_generated_content:
        st.markdown(st.session_state.stem_generated_content)
        if st.button("💾 LƯU VÀO GOOGLE SHEETS"):
            if save_to_sheets(ten_chu_de_t2, st.session_state.stem_generated_content):
                st.toast("Đã lưu thành công!", icon="✅")

def render_stem_section():
    st.markdown("## 🚀 HỆ SINH THÁI GIÁO DỤC STEM")
    tab1, tab2, tab3 = st.tabs(["💡 1. SẢN PHẨM", "🛠️ 2. XÂY DỰNG KHBD", "📁 3. KHBD ĐÃ LƯU"])
    with tab2: render_tab_2()
    # Các tab 1, 3 thầy để nguyên như cũ
