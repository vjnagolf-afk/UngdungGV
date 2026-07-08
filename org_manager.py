import streamlit as st
import pandas as pd

def render_org_section():
    st.subheader("📋 HỆ THỐNG QUẢN LÝ VÀ PHÂN CÔNG CHUYÊN MÔN")
    
    # Đảm bảo dữ liệu tồn tại
    if "db_thanh_vien" not in st.session_state:
        st.warning("Dữ liệu tổ chưa sẵn sàng.")
        return

    # Tabs điều hướng
    tab1, tab2, tab3 = st.tabs(["👥 Danh sách thành viên", "📊 Phân công giảng dạy", "🏆 Thành tích & Thi đua"])
    
    with tab1:
        st.dataframe(pd.DataFrame(st.session_state["db_thanh_vien"]), use_container_width=True)
    with tab2:
        st.dataframe(pd.DataFrame(st.session_state.get("db_phan_cong_hien_tai", [])), use_container_width=True)
    with tab3:
        st.json(st.session_state.get("db_thanh_tich_da_nam", {}))
