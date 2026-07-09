import streamlit as st
import io
from docx import Document

# Hàm hỗ trợ tạo file Word từ nội dung văn bản
def create_word_file(title, content):
    doc = Document()
    doc.add_heading(title, 0)
    doc.add_paragraph(content)
    
    # Lưu file vào bộ nhớ đệm (BytesIO) để Streamlit tải xuống
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def render_stem_section():
    st.markdown("## 🚀 CHỨC NĂNG XÂY DỰNG DỰ ÁN GIÁO DỤC STEM")
    st.markdown("---")
    
    # ---------------------------------------------------------
    # KHỞI TẠO BỘ NHỚ (SESSION STATE) ĐỂ LƯU TRỮ DỮ LIỆU
    # ---------------------------------------------------------
    if "stem_generated_content" not in st.session_state:
        st.session_state.stem_generated_content = ""
    if "stem_saved_projects" not in st.session_state:
        st.session_state.stem_saved_projects = {}  # Dictionary lưu các dự án

    # 1. Thông tin cơ bản
    st.subheader("1. Thông tin chung")
    ten_chu_de = st.text_input("Tên dự án / Chủ đề STEM:", 
                               placeholder="Thiết kế hệ thống tiết kiệm năng lượng sử dụng cảm biến thông minh")
    
    col1, col2 = st.columns(2)
    with col1:
        mon_chu_dao = st.selectbox("Môn học chủ đạo:", ["Khoa học tự nhiên", "Toán học", "Công nghệ", "Tin học"])
        lop_hoc = st.selectbox("Lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"])
    with col2:
        thoi_luong = st.text_input("Thời lượng thực hiện:", placeholder="Ví dụ: 3 Tiết")
    
    # 2. Yêu cầu tích hợp & Phân hóa
    st.subheader("2. Yêu cầu tích hợp & Phân hóa")
    tich_hop_ai_iot = st.checkbox("🔌 Tích hợp ứng dụng AI hoặc Vi điều khiển (Ví dụ: Arduino, ESP8266)")
    tich_hop_hoa_nhap = st.checkbox("🤝 Phân hóa hoạt động và câu hỏi dành cho học sinh khuyết tật (Giáo dục hòa nhập)")
    
    # 3. Tải học liệu nguồn (TÍNH NĂNG MỚI THÊM)
    st.subheader("3. Tài liệu tham khảo (Học liệu nguồn)")
    tai_lieu_nguon = st.file_uploader("Tải lên file bài học, tài liệu tham khảo (PDF, Word, TXT)", accept_multiple_files=True)
    
    st.markdown("---")
    
    # ---------------------------------------------------------
    # XỬ LÝ NÚT BẤM VÀ GỌI AI
    # ---------------------------------------------------------
    if st.button("Kích hoạt AI thiết kế tiến trình STEM", use_container_width=True):
        if not ten_chu_de:
            st.warning("Vui lòng nhập tên chủ đề STEM!")
        else:
            with st.spinner("Hệ thống đang phân tích tài liệu và thiết kế bài dạy..."):
                # GỌI API AI TẠI ĐÂY (Tạm thời giả lập kết quả trả về)
                noi_dung_ai = f"""
                # GIÁO ÁN STEM: {ten_chu_de}
                **Môn học:** {mon_chu_dao} | **Đối tượng:** {lop_hoc} | **Thời lượng:** {thoi_luong}
                
                ## BƯỚC 1: XÁC ĐỊNH VẤN ĐỀ
                Học sinh tìm hiểu về thực trạng lãng phí điện năng...
                
                ## BƯỚC 2: NGHIÊN CỨU KIẾN THỨC NỀN
                Nghiên cứu nguyên lý hoạt động của cảm biến và dòng điện...
                """
                
                # Lưu kết quả AI vào bộ nhớ tạm để hiển thị
                st.session_state.stem_generated_content = noi_dung_ai
                st.success("Tạo kế hoạch bài dạy STEM thành công!")

    # ---------------------------------------------------------
    # KHU VỰC HIỂN THỊ NỘI DUNG VÀ TẢI XUỐNG
    # ---------------------------------------------------------
    if st.session_state.stem_generated_content != "":
        st.markdown("### 📖 KẾT QUẢ THIẾT KẾ")
        
        # Hộp hiển thị nội dung có thanh cuộn
        with st.container(border=True):
            st.markdown(st.session_state.stem_generated_content)
        
        # Các nút thao tác
        col_download, col_save = st.columns(2)
        
        with col_download:
            # Chức năng tải file Word
            docx_file = create_word_file(ten_chu_de, st.session_state.stem_generated_content)
            st.download_button(
                label="📥 Tải giáo án về máy (File Word)",
                data=docx_file,
                file_name=f"Giao_an_STEM_{ten_chu_de}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
            
        with col_save:
            # Chức năng lưu dự án
            if st.button("💾 Lưu dự án vào hệ thống", use_container_width=True):
                st.session_state.stem_saved_projects[ten_chu_de] = st.session_state.stem_generated_content
                st.toast(f"Đã lưu thành công dự án: {ten_chu_de}", icon="✅")

    # ---------------------------------------------------------
    # KHU VỰC QUẢN LÝ DỰ ÁN ĐÃ LƯU (HIỂN THỊ VÀ XÓA)
    # ---------------------------------------------------------
    st.markdown("---")
    st.subheader("📁 QUẢN LÝ DỰ ÁN ĐÃ LƯU")
    
    if len(st.session_state.stem_saved_projects) > 0:
        # Lấy danh sách các dự án đã lưu
        danh_sach_du_an = list(st.session_state.stem_saved_projects.keys())
        
        for ten_da in danh_sach_du_an:
            # Tạo các thanh xổ xuống (expander) cho từng dự án
            with st.expander(f"📌 Dự án: {ten_da}"):
                st.markdown(st.session_state.stem_saved_projects[ten_da])
                
                # Nút xóa dự án
                if st.button("🗑️ Xóa dự án này", key=f"btn_del_{ten_da}"):
                    del st.session_state.stem_saved_projects[ten_da]
                    # Rerun lại trang để cập nhật giao diện ngay lập tức
                    st.rerun()
    else:
        st.info("Chưa có dự án nào được lưu.")
