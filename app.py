import streamlit as st
from grade_manager import render_grade_manager_section
from tkb_manager import render_tkb_manager
from org_manager import render_org_section, render_meeting_minutes, render_personal_plan

st.set_page_config(page_title="HỆ SINH THÁI SỐ GIÁO VIÊN", layout="wide")
st.title("📚 HỆ SINH THÁI SỐ - HỖ TRỢ GIÁO VIÊN")

phan_he = st.sidebar.radio("CHỌN PHÂN HỆ", ["Trợ lý Giảng dạy (Giáo viên)", "Trợ lý Quản lý (Tổ chuyên môn)"])

if phan_he == "Trợ lý Giảng dạy (Giáo viên)":
    menu = st.sidebar.selectbox("CHỌN NỘI DUNG", ["1. Thiết kế KHBD", "2. Thiết kế Đề KT", "3. Đánh giá HS", "4. Quản lý điểm (SMAS)", "5. Quản lý TKB"])
    if menu == "4. Quản lý điểm (SMAS)": render_grade_manager_section()
    elif menu == "5. Quản lý TKB": render_tkb_manager()
    else: st.info("Chức năng đang hoàn thiện...")

else: # Phân hệ Quản lý tổ
    menu = st.sidebar.selectbox("QUẢN LÝ TỔ", ["1. Quản lý Thành viên & Phân công", "2. Biên bản sinh hoạt tổ", "3. Kế hoạch giáo dục cá nhân", "4. Thống kê số liệu"])
    
    if menu == "1. Quản lý Thành viên & Phân công": render_org_section()
    elif menu == "2. Biên bản sinh hoạt tổ": render_meeting_minutes()
    elif menu == "3. Kế hoạch giáo dục cá nhân": render_personal_plan()
    elif menu == "4. Thống kê số liệu": st.write("Chức năng thống kê...")
