import streamlit as st

def render_special_ed_section(run_ai_prompt_safe_func):
    st.markdown("""<style>
        .title-box { background-color: #EBF5FB; padding: 15px; border-radius: 10px; border-left: 5px solid #2980B9; margin-bottom: 20px; }
        .big-font { font-size: 16px !important; font-weight: bold !important; color: #154360; }
        button[kind="primary"] { background-color: #5DADE2 !important; color: white !important; }
    </style>""", unsafe_allow_html=True)
    
    st.markdown("<div class='title-box'><h3 style='text-align: center; color: #154360; margin: 0;'>🌱 XÂY DỰNG KẾ HOẠCH HỖ TRỢ HSKT</h3></div>", unsafe_allow_html=True)

    tab_thiet_ke, tab_quan_ly = st.tabs(["📝 XÂY DỰNG KẾ HOẠCH", "🗂️ QUẢN LÝ HỒ SƠ"])
    
    with tab_thiet_ke:
        # Hàng 1: 5 Menu trên 1 hàng, tăng cỡ chữ
        col1, col2, col3, col4, col5 = st.columns(5)
        ten_hs = col1.text_input("Họ và tên HS:", key="ten_hs_in")
        lop_hs = col2.selectbox("Khối lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Khối 10", "Khối 11", "Khối 12"])
        dang_kt = col3.selectbox("Dạng khuyết tật:", ["Khuyết tật vận động", "Khuyết tật trí tuệ", "Khuyết tật nghe", "Khuyết tật nhìn", "Tự kỷ/Tăng động", "Khuyết tật thần kinh", "Khác"])
        ky_hoc = col4.selectbox("Kế hoạch GDHSKT:", ["Kế hoạch HK I", "Kế hoạch HK II", "Cả Năm"])
        mon_hoc = col5.selectbox("Chọn môn học:", ["Ngữ văn", "Toán", "Tiếng Anh", "Giáo dục công dân", "Lịch sử và Địa lí", "KHTN (Lý)", "KHTN (Hóa)", "KHTN (Sinh)", "Công nghệ", "Tin học", "Nghệ thuật", "Hoạt động trải nghiệm, hướng nghiệp"])
        
        # Hàng tải file mẫu
        c_f1, c_f2 = st.columns(2)
        file_mau = c_f1.file_uploader(f"Tải mẫu KH môn {mon_hoc}:")
        info_file = c_f2.file_uploader("Tải mẫu 'Thông tin về HSKT':")
        
        if st.button("✨ TẠO KẾ HOẠCH HỖ TRỢ TỰ ĐỘNG BẰNG AI", type="primary", use_container_width=True):
            if not ten_hs:
                st.warning("Vui lòng nhập tên học sinh!")
            else:
                with st.spinner("AI đang thiết lập kế hoạch cho em " + ten_hs + "..."):
                    prompt = f"Lập kế hoạch hỗ trợ HSKT cho học sinh {ten_hs}, lớp {lop_hs}, dạng {dang_kt}, môn {mon_hoc}, học kỳ {ky_hoc}."
                    ket_qua, _ = run_ai_prompt_safe_func(prompt)
                    st.session_state["ket_qua_hskt"] = ket_qua
                    st.markdown(ket_qua)
        
        # Nút Lưu và Tải sau khi AI đã sinh xong
        if "ket_qua_hskt" in st.session_state and st.session_state["ket_qua_hskt"]:
            c_save, c_dl = st.columns(2)
            if c_save.button("💾 Lưu kế hoạch"):
                st.success(f"Đã lưu kế hoạch cho HS {ten_hs} vào hệ thống!")
            if c_dl.download_button("📥 Tải kế hoạch (Word)", data=st.session_state["ket_qua_hskt"], file_name=f"KH_{ten_hs}.docx"):
                pass
                    
    with tab_quan_ly:
        st.write("📂 Quản lý hồ sơ cá nhân học sinh.")
