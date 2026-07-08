import streamlit as st
import pandas as pd

def render_org_section():
    st.subheader("👥 HỆ THỐNG QUẢN LÝ TỔ CHUYÊN MÔN")
    tab1, tab2, tab3 = st.tabs(["👥 Danh sách thành viên", "📊 Phân công giảng dạy", "🏆 Thành tích"])
    with tab1: st.dataframe(pd.DataFrame(st.session_state.get("db_thanh_vien", [])), use_container_width=True)
    with tab2: st.dataframe(pd.DataFrame(st.session_state.get("db_phan_cong_hien_tai", [])), use_container_width=True)
    with tab3: st.json(st.session_state.get("db_thanh_tich_da_nam", {}))

def render_meeting_minutes():
    st.subheader("📝 BIÊN BẢN SINH HOẠT TỔ")
    st.write("Giao diện nhập biên bản sẽ hiển thị ở đây.")
    # Thầy thêm code tạo biên bản tại đây

def render_personal_plan():
    st.subheader("📋 KẾ HOẠCH GIÁO DỤC CÁ NHÂN")
    st.write("Giao diện xây dựng kế hoạch cá nhân sẽ hiển thị ở đây.")
