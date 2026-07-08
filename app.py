import streamlit as st
import pandas as pd
# Import các module (Đảm bảo file nằm cùng thư mục)
from exam_designer import render_exam_designer_section
from grade_manager import render_grade_manager_section
from org_manager import render_org_section
from tkb_manager import render_tkb_manager

st.set_page_config(page_title="HỆ SINH THÁI SỐ GIÁO VIÊN", layout="wide")

# --- SIDEBAR MENU ---
st.sidebar.title("MENU HỆ THỐNG")
phan_he = st.sidebar.radio("CHỌN PHÂN HỆ TÁC NGHIỆP", ["Trợ lý Giảng dạy (Giáo viên)", "Trợ lý Quản lý (Tổ chuyên môn)"])

if phan_he == "Trợ lý Giảng dạy (Giáo viên)":
    chuc_nang = st.sidebar.selectbox("CHỌN NỘI DUNG", ["1. Thiết kế KHBD", "2. Thiết kế Đề KT", "3. Đánh giá HS", "4. Quản lý điểm (SMAS)", "5. Quản lý TKB"])
    
    if chuc_nang == "1. Thiết kế KHBD": st.write("Đang phát triển...")
    elif chuc_nang == "2. Thiết kế Đề KT": render_exam_designer_section("", None) # Truyền api_key nếu cần
    elif chuc_nang == "3. Đánh giá HS": st.write("Đang phát triển...")
    elif chuc_nang == "4. Quản lý điểm (SMAS)": render_grade_manager_section()
    elif chuc_nang == "5. Quản lý TKB": render_tkb_manager()

else: # Phân hệ Quản lý tổ
    chuc_nang = st.sidebar.selectbox("QUẢN LÝ TỔ CHUYÊN MÔN", ["Hệ thống Tổ chuyên môn", "Thống kê số liệu"])
    
    if chuc_nang == "Hệ thống Tổ chuyên môn":
        render_org_section()
    elif chuc_nang == "Thống kê số liệu":
        st.header("📊 Thống kê số liệu tổ")
        if "db_thanh_vien" in st.session_state:
            df = pd.DataFrame(st.session_state["db_thanh_vien"])
            st.bar_chart(df["Phân môn chính"].value_counts())
