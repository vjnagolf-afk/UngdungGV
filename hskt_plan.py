import streamlit as st

def render_special_ed_section(run_ai_prompt_safe_func):
    # CSS Tối ưu giao diện dịu nhẹ, nút bấm xanh nhạt
    st.markdown("""
        <style>
            .title-box { background-color: #EBF5FB; padding: 15px; border-radius: 10px; border-left: 5px solid #2980B9; margin-bottom: 20px; }
            /* Định dạng nút bấm màu xanh dịu */
            button[kind="primary"] {
                background-color: #5DADE2 !important;
                border: 1px solid #3498DB !important;
                color: white !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""<div class="title-box"><h3 style='text-align: center; color: #154360; margin: 0;'>🌱 HỖ TRỢ XÂY DỰNG KẾ HOẠCH GIÁO DỤC CÁ NHÂN (IEP)</h3></div>""", unsafe_allow_html=True)

    tab_thiet_ke, tab_quan_ly = st.tabs(["📝 XÂY DỰNG KẾ HOẠCH", "🗂️ HỒ SƠ LƯU TRỮ"])
    
    with tab_thiet_ke:
        with st.container(border=True):
            st.markdown("<h5 style='color: #2980B9;'>1. Thông tin học sinh</h5>", unsafe_allow_html=True)
            col_ten, col_lop, col_dang = st.columns([2, 1, 1.5])
            ten_hs = col_ten.text_input("Họ và tên:", placeholder="Nguyễn Văn A")
            lop_hs = col_lop.selectbox("Lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"])
            dang_kt = col_dang.selectbox("Dạng khuyết tật:", ["Khuyết tật học tập", "Khuyết tật trí tuệ", "Tự kỷ", "Khuyết tật vận động", "Khác"])
                
        with st.container(border=True):
            st.markdown("<h5 style='color: #2980B9;'>2. Đánh giá & Mục tiêu</h5>", unsafe_allow_html=True)
            kha_nang = st.text_area("Khả năng hiện tại:", placeholder="- Điểm mạnh: ...\n- Hạn chế: ...", height=100)
            muc_tieu = st.text_area("Mục tiêu học kỳ:", placeholder="- Mục tiêu 1: ...", height=100)

        ho_so_y_te = st.file_uploader("Tải lên Hồ sơ Y tế (Không bắt buộc):", type=["pdf", "docx"])
        
        # Nút bấm mới: Xanh dịu, chữ trắng
        if st.button("✨ TẠO KẾ HOẠCH HỖ TRỢ BẰNG AI", type="primary", use_container_width=True):
            if not ten_hs or not muc_tieu:
                st.warning("Vui lòng nhập họ tên và mục tiêu giáo dục!")
            else:
                with st.spinner("AI đang thiết lập kế hoạch hỗ trợ chuyên biệt..."):
                    prompt = f"Lập kế hoạch giáo dục cá nhân cho HS {ten_hs}, lớp {lop_hs}, dạng {dang_kt}. Khả năng: {kha_nang}. Mục tiêu: {muc_tieu}."
                    # Gọi hàm AI của bạn
                    ket_qua, _ = run_ai_prompt_safe_func(prompt, "3.1 Flash-Lite")
                    st.success("Đã tạo kế hoạch thành công!")
                    st.markdown(ket_qua)
                    
    with tab_quan_ly:
        st.write("📂 Danh sách kế hoạch đã lưu sẽ hiển thị tại đây.")
