import streamlit as st
import pandas as pd

def render_org_section():
    st.subheader("📋 HỆ THỐNG QUẢN LÝ TỔ CHUYÊN MÔN")
    
    # Kiểm tra dữ liệu session
    if "db_thanh_vien" not in st.session_state:
        st.error("Dữ liệu thành viên chưa được khởi tạo.")
        return

    tab1, tab2, tab3 = st.tabs(["👥 Danh sách thành viên", "📊 Phân công giảng dạy", "🏆 Thành tích & Thi đua"])
    
    with tab1:
        st.write("Quản lý danh sách thành viên tổ...")
        st.dataframe(pd.DataFrame(st.session_state["db_thanh_vien"]), use_container_width=True)
        
    with tab2:
        st.write("Quản lý phân công giảng dạy...")
        st.dataframe(pd.DataFrame(st.session_state["db_phan_cong_hien_tai"]), use_container_width=True)
        
    with tab3:
        st.write("Thành tích và thi đua của tổ...")
        st.json(st.session_state["db_thanh_tich_da_nam"])