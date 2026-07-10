import streamlit as st

def render_special_ed_section(run_ai_prompt_safe_func):
    st.markdown("<style>.big-text { font-size: 18px !important; }</style>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; color: #154360;'>🌱 XÂY DỰNG KẾ HOẠCH HỖ TRỢ HSKT</h3>", unsafe_allow_html=True)

    if "my_files" not in st.session_state: 
        st.session_state["my_files"] = {}

    tab1, tab2 = st.tabs(["📝 XÂY DỰNG KẾ HOẠCH", "🗂️ QUẢN LÝ HỒ SƠ"])
    
    with tab1:
        c1, c2, c3, c4, c5 = st.columns(5)
        ten_hs = c1.text_input("Họ và tên HS:")
        lop_hs = c2.selectbox("Khối lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Khối 10", "Khối 11", "Khối 12"])
        dang_kt = c3.selectbox("Dạng khuyết tật:", ["Vận động", "Trí tuệ", "Nghe", "Nhìn", "Tự kỷ", "Thần kinh", "Khác"])
        ky_hoc = c4.selectbox("Kế hoạch GDHSKT:", ["Kế hoạch HK I", "Kế hoạch HK II", "Cả Năm"])
        mon_hoc = c5.selectbox("Chọn môn học:", ["Ngữ văn", "Toán", "Tiếng Anh", "KHTN (Lý)", "KHTN (Hóa)", "KHTN (Sinh)", "Tin học", "Nghệ thuật", "HĐTN, hướng nghiệp"])
        
        st.markdown("---")
        for label in ["KH Mẫu", "Thông tin HSKT", "Nội dung học tập HK"]:
            cl, cu, cs = st.columns([1.5, 4, 1])
            cl.markdown(f"**{label}**")
            up = cu.file_uploader("...", key=f"up_{label}", label_visibility="collapsed")
            if cs.button("💾 Lưu", key=f"save_{label}", use_container_width=True) and up:
                st.session_state["my_files"][label] = up
                st.toast(f"Đã lưu: {label}")
            if label in st.session_state["my_files"]:
                cu.caption(f"✅ Đang dùng: {st.session_state['my_files'][label].name}")

        st.markdown("---")
        if st.button("✨ TẠO KẾ HOẠCH HỖ TRỢ HSKT BẰNG AI", type="primary", use_container_width=True):
            prompt = f"Lập KH hỗ trợ HS {ten_hs}, lớp {lop_hs}, dạng {dang_kt}, môn {mon_hoc}, kỳ {ky_hoc}."
            ket_qua, _ = run_ai_prompt_safe_func(prompt)
            st.session_state["ket_qua_hskt"] = ket_qua
            st.markdown(ket_qua)
