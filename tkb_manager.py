import streamlit as st
import pandas as pd

def render_tkb_manager():
    st.header("📅 QUẢN LÝ THỜI KHÓA BIỂU")
    uploaded_tkb = st.file_uploader("Tải lên file TKB (.xlsx)", type=["xlsx"])
    
    if uploaded_tkb:
        df = pd.read_excel(uploaded_tkb, sheet_name="TKB_GV_S", header=3)
        all_cols = df.columns.tolist()
        teachers = [c for c in all_cols if isinstance(c, str) and "Unnamed" not in c and c not in ["THỨ", "TIẾT"]]
        
        tab1, tab2 = st.tabs(["📊 Thời khóa biểu chung", "👤 TKB theo giáo viên"])
        with tab1:
            st.dataframe(df, use_container_width=True)
        with tab2:
            if not teachers:
                st.error("Không thấy tên giáo viên!")
            else:
                selected_teacher = st.selectbox("Chọn giáo viên:", sorted(teachers))
                tkb_gv = df[["THỨ", "TIẾT", selected_teacher]].copy()
                tkb_gv.columns = ["Thứ", "Tiết", "Lịch dạy"]
                tkb_gv["Thứ"] = tkb_gv["Thứ"].ffill()
                st.dataframe(tkb_gv.dropna(subset=["Lịch dạy"]), use_container_width=True, hide_index=True)
    else:
        st.info("💡 Vui lòng tải file Excel TKB.")