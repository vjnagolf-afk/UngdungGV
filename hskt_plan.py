import streamlit as st
from document_processor import read_uploaded_docx, read_uploaded_pdf

def render_special_ed_section(run_ai_prompt_safe_func):
    # CSS: Tăng cỡ chữ tổng thể
    st.markdown("""<style>
        .big-text { font-size: 18px !important; font-weight: bold; }
        .stButton button { font-size: 16px !important; }
        .stSelectbox, .stTextInput { font-size: 16px !important; }
    </style>""", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; color: #154360;'>🌱 XÂY DỰNG KẾ HOẠCH HỖ TRỢ HSKT</h3>", unsafe_allow_html=True)

    # Khởi tạo session state lưu file
    if "files_hskt" not in st.session_state: st.session_state["files_hskt"] = {}

    tab_thiet_ke, tab_quan_ly = st.tabs(["📝 XÂY DỰNG KẾ HOẠCH", "🗂️ QUẢN LÝ HỒ SƠ"])
    
    with tab_thiet_ke:
        # Hàng 1
        c1, c2, c3, c4, c5 = st.columns(5)
        ten_hs = c1.text_input("Họ và tên HS:")
        lop_hs = c2.selectbox("Khối lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Khối 10", "Khối 11", "Khối 12"])
        dang_kt = c3.selectbox("Dạng khuyết tật:", ["Khuyết tật vận động", "Khuyết tật trí tuệ", "Khuyết tật nghe", "Khuyết tật nhìn", "Tự kỷ", "Khuyết tật thần kinh", "Khác"])
        ky_hoc = c4.selectbox("Kế hoạch GDHSKT:", ["Kế hoạch HK I", "Kế hoạch HK II", "Cả Năm"])
        mon_hoc = c5.selectbox("Chọn môn học:", ["Ngữ văn", "Toán", "Tiếng Anh", "Giáo dục công dân", "KHTN (Lý)", "KHTN (Hóa)", "KHTN (Sinh)", "Công nghệ", "Tin học", "Giáo dục thể chất", "Nghệ thuật", "HĐTN, hướng nghiệp"])
        
        # Hàng tải file (3 nút)
        cf1, cf2, cf3 = st.columns(3)
        files = {
            "KH Mẫu": cf1.file_uploader("Tải file KH mẫu:"),
            "Thông tin HSKT": cf2.file_uploader("Thông tin HSKT:"),
            "Nội dung HK": cf3.file_uploader("Tải nội dung học tập trong HK:")
        }
        
        if st.button("💾 Lưu các file đã chọn"):
            for name, f in files.items():
                if f: st.session_state["files_hskt"][name] = f
            st.success("Đã lưu tệp vào hệ thống!")

        if st.button("✨ TẠO KẾ HOẠCH HỖ TRỢ HSKT BẰNG AI", type="primary", use_container_width=True):
            with st.spinner("AI đang phân tích dữ liệu và mẫu..."):
                # Gom nội dung từ file để gửi AI
                file_context = "Có sử dụng file mẫu." if st.session_state["files_hskt"] else "Không dùng file."
                prompt = f"""Lập kế hoạch hỗ trợ HSKT cho em {ten_hs}, {lop_hs}, dạng {dang_kt}.
                Môn: {mon_hoc}, {ky_hoc}.
                Yêu cầu: Bám sát 100% cấu trúc các cột trong file mẫu đã tải lên. Nội dung học tập cần khớp với dữ liệu học tập HK đã cung cấp. 
                Sử dụng thông tin HSKT làm căn cứ chính để cá nhân hóa."""
                ket_qua, _ = run_ai_prompt_safe_func(prompt)
                st.session_state["ket_qua_hskt"] = ket_qua
                st.markdown(ket_qua)
                    
    with tab_quan_ly:
        st.write("📂 Quản lý hồ sơ cá nhân học sinh.")
