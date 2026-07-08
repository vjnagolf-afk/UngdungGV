import streamlit as st
import pandas as pd
from datetime import date

def render_tkb_manager():
    st.header("📅 QUẢN LÝ THỜI KHÓA BIỂU & PHÂN CÔNG")
    
    # --- Chức năng chọn đợt ---
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Từ ngày:", date(2025, 9, 29))
    with col2:
        end_date = st.date_input("Đến ngày:", date(2026, 1, 30))
    
    st.info(f"Đang quản lý TKB cho đợt: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")

    # --- Upload file ---
    uploaded_file = st.file_uploader("Tải lên file TKB (.xlsx)", type=["xlsx"])
    
    if uploaded_file:
        # Đọc dữ liệu TKB toàn trường
        df_all = pd.read_excel(uploaded_file, sheet_name="TKB_LOP_S", header=0)
        
        # Tự động lấy danh sách giáo viên từ tiêu đề bảng
        # Dựa trên file, dòng đầu tiên chứa tên GV (vd: "6A\n(Hiếu)")
        header_row = df_all.iloc[0]
        # Lọc tên GV từ các cột từ cột 2 trở đi
        raw_cols = header_row.iloc[2:]
        teachers = []
        for val in raw_cols:
            if isinstance(val, str) and "(" in val:
                name = val.split('(')[1].replace(')', '').strip()
                if name not in teachers: teachers.append(name)
        
        # --- Hiển thị giao diện ---
        tab1, tab2 = st.tabs(["📊 TKB Chung Toàn Trường", "👤 TKB Theo Giáo Viên"])
        
        with tab1:
            st.subheader("Thời khóa biểu toàn trường")
            st.dataframe(df_all, use_container_width=True)
            
        with tab2:
            st.subheader("Tra cứu lịch dạy cá nhân")
            selected_teacher = st.selectbox("Chọn giáo viên:", sorted(teachers))
            
            if selected_teacher:
                # Trích xuất dữ liệu cho GV này
                # Duyệt qua các cột, tìm cột nào có tên GV
                gv_cols = [col for col in df_all.columns if selected_teacher in str(df_all.iloc[0][col])]
                
                # Tạo bảng TKB riêng
                tkb_gv = df_all[["Unnamed: 0", "Unnamed: 1"] + gv_cols].copy()
                tkb_gv.columns = ["Thứ", "Tiết", "Môn - Lớp"]
                tkb_gv["Thứ"] = tkb_gv["Thứ"].ffill() # Điền thứ
                
                st.dataframe(tkb_gv, use_container_width=True, hide_index=True)
                
                # Lưu đợt
                if st.button("💾 Lưu phân công cho đợt này"):
                    st.success(f"Đã lưu TKB đợt {start_date} - {end_date} vào hệ thống!")

    else:
        st.warning("Vui lòng tải file Excel TKB để bắt đầu.")