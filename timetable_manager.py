import streamlit as st
import pandas as pd

def render_timetable_section():
    st.header("📅 QUẢN LÝ THỜI KHÓA BIỂU GIÁO VIÊN")
    
    # 1. Tải file TKB
    uploaded_tkb = st.file_uploader("📥 Nhập file TKB (.xlsx)", type=["xlsx"])
    
    if uploaded_tkb:
        # Đọc sheet TKB_GV_S, header=3 như cũ
        df = pd.read_excel(uploaded_tkb, sheet_name="TKB_GV_S", header=3)
        
        # LỌC BỎ CÁC CỘT RÁC: Chỉ lấy cột có tên (không chứa "Unnamed")
        all_cols = df.columns.tolist()
        teacher_names = [c for c in all_cols if "Unnamed" not in str(c) and c not in ["THỨ", "TIẾT"]]
        
        # 2. Chọn giáo viên từ danh sách đã lọc sạch
        selected_teacher = st.selectbox("👤 Chọn giáo viên:", teacher_names)
        
        if selected_teacher:
            # Lọc dữ liệu: Chỉ lấy Thứ, Tiết và cột của giáo viên đó
            # Đảm bảo tên cột khớp chính xác
            tkb_gv = df[["THỨ", "TIẾT", selected_teacher]].copy()
            
            # Đổi tên cột cho dễ nhìn
            tkb_gv.columns = ["Thứ", "Tiết", "Lịch dạy (Lớp - Môn)"]
            
            # Điền "Thứ" cho các tiết trống
            tkb_gv["Thứ"] = tkb_gv["Thứ"].ffill()
            
            # 3. Hiển thị
            st.subheader(f"Lịch dạy của: {selected_teacher}")
            st.dataframe(tkb_gv, use_container_width=True, hide_index=True)
            
            # Nút xuất
            csv = tkb_gv.to_csv(index=False).encode('utf-8')
            st.download_button(f"📤 Tải TKB của {selected_teacher}", csv, f"TKB_{selected_teacher}.csv", "text/csv")
    else:
        st.info("💡 Vui lòng tải file Excel Thời khóa biểu lên.")
