import streamlit as st
import pandas as pd
import json

# Import các module (Đảm bảo các file này nằm cùng thư mục)
from exam_designer import render_exam_designer_section
from grade_manager import render_grade_manager_section
from tkb_manager import render_tkb_manager
from org_manager import render_org_section
from khbd_manager import render_khbd_section

# --- CẤU HÌNH BIẾN GLOBAL (Cần thiết cho AI) ---
# Đảm bảo thầy đã định nghĩa api_key_input và run_ai_prompt_safe ở phía trên này
# Nếu chưa có, thầy hãy copy lại phần định nghĩa từ file cũ vào đây
api_key_input = st.secrets.get("GEMINI_API_KEY", "") 
def run_ai_prompt_safe(prompt, api_key): 
    # Hàm này thầy giữ nguyên như cũ
    return "Kết quả demo", "gemini-model"

# Khởi tạo dữ liệu mẫu
if "db_thanh_vien" not in st.session_state: st.session_state["db_thanh_vien"] = []
if "db_phan_cong_hien_tai" not in st.session_state: st.session_state["db_phan_cong_hien_tai"] = []

st.set_page_config(page_title="HỆ SINH THÁI SỐ GIÁO VIÊN", layout="wide")
st.title("📚 HỆ SINH THÁI SỐ - HỖ TRỢ GIÁO VIÊN")

# --- MENU CHÍNH ---
phan_he = st.sidebar.radio("CHỌN PHÂN HỆ TÁC NGHIỆP", ["Trợ lý Giảng dạy (Giáo viên)", "Trợ lý Quản lý (Tổ chuyên môn)"])

if phan_he == "Trợ lý Giảng dạy (Giáo viên)":
    menu = st.sidebar.selectbox("CHỌN NỘI DUNG", 
                                ["1. Thiết kế KHBD", "2. Thiết kế Đề KT", "3. Đánh giá HS", "4. Quản lý điểm (SMAS)", "5. Quản lý TKB"])
    
    # --- KẾT NỐI LOGIC ĐÃ SỬA ---
    if menu == "1. Thiết kế KHBD":
        render_khbd_section(api_key_input, run_ai_prompt_safe)
        
    elif menu == "2. Thiết kế Đề KT":
        render_exam_designer_section("", None) 
        
    elif menu == "3. Đánh giá HS":
        st.header("📋 ĐÁNH GIÁ HỌC SINH")
        st.info("Chức năng đang được cập nhật...")
        
    elif menu == "4. Quản lý điểm (SMAS)":
        render_grade_manager_section()
        
    elif menu == "5. Quản lý TKB":
        render_tkb_manager()

else: # Phân hệ Quản lý tổ
    menu = st.sidebar.selectbox("QUẢN LÝ TỔ CHUYÊN MÔN", 
                                ["1. Hệ thống Quản lý tổ", "2. Biên bản sinh hoạt", "3. Kế hoạch cá nhân", "4. Thống kê số liệu"])
    
    if menu == "1. Hệ thống Quản lý tổ":
        render_org_section()
    elif menu == "2. Biên bản sinh hoạt":
        st.header("📝 BIÊN BẢN SINH HOẠT TỔ")
    elif menu == "3. Kế hoạch cá nhân":
        st.header("📋 KẾ HOẠCH CÁ NHÂN")
    elif menu == "4. Thống kê số liệu":
        st.header("📊 THỐNG KÊ SỐ LIỆU")
        if st.session_state["db_thanh_vien"]:
            df = pd.DataFrame(st.session_state["db_thanh_vien"])
            st.bar_chart(df["Phân môn chính"].value_counts())
        else: st.info("Chưa có dữ liệu thống kê.")
