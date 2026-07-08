import streamlit as st
import docx  # Dùng để đọc và TẠO mới file Word chuẩn biểu bảng
from docx.shared import Inches
import io
import re
from pypdf import PdfReader

# --- HÀM TRÍCH XUẤT VĂN BẢN VÀ HÌNH ẢNH TỪ FILE NGUỒN ---
def extract_context_from_uploaded_files(uploaded_files):
    combined_text = ""
    extracted_images = [] # Lưu trữ ảnh nhị phân để AI tùy chọn chèn vào giáo án mới
    
    for file in uploaded_files:
        try:
            if file.name.endswith('.docx'):
                doc = docx.Document(file)
                # 1. Đọc văn bản thô và bảng biểu bên trong file nguồn
                for paragraph in doc.paragraphs:
                    if paragraph.text:
                        combined_text += paragraph.text + "\n"
                for table in doc.tables:
                    for row in table.rows:
                        text_row = [cell.text for cell in row.cells]
                        combined_text += " | ".join(text_row) + "\n"
                # 2. Quét trích xuất ảnh đính kèm (nếu có)
                for rel in doc.part.relations.values():
                    if "image" in rel.target_ref:
                        image_data = rel.target_part.blob
                        extracted_images.append(image_data)
                        
            elif file.name.endswith('.pdf'):
                reader = PdfReader(file)
                for page in reader.pages:
                    combined_text += (page.extract_text() or "") + "\n"
                    # Trích xuất ảnh từ trang PDF
                    for img_file_object in page.images:
                        extracted_images.append(img_file_object.data)
                        
            elif file.name.endswith('.txt'):
                combined_text += file.read().decode("utf-8") + "\n"
        except Exception as e:
            st.error(f"Lỗi khi xử lý file {file.name}: {str(e)}")
            
    return combined_text, extracted_images

# --- HÀM KHỞI TẠO FILE WORD CHUẨN ĐỊNH DẠNG (KHÔNG LỖI BIỂU BẢNG & CÔNG THỨC) ---
def export_khbd_to_docx(markdown_content, images_list):
    doc = docx.Document()
    # Cấu hình lề trang chuẩn văn bản hành chính Việt Nam (Top, Bottom, Left, Right)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(1.18)
        section.right_margin = Inches(0.59)

    lines = markdown_content.split('\n')
    in_table = False
    table_data = []

    for line in lines:
        # Xử lý tạo BẢNG BIỂU tự động từ ký tự bảng | của Markdown nhằm chống lỗi hiển thị
        if line.strip().startswith('|') and line.strip().endswith('|'):
            if '---|' in line or ':---|' in line: # Bỏ qua dòng kẻ phân cách bảng
                continue
            in_table = True
            cells = [c.strip() for c in line.split('|')[1:-1]]
            table_data.append(cells)
            continue
        else:
            if in_table and table_data:
                # Tiến hành dựng bảng thực tế vào file Word
                num_rows = len(table_data)
                num_cols = len(table_data[0]) if num_rows > 0 else 0
                if num_cols > 0:
                    word_table = doc.add_table(rows=num_rows, cols=num_cols)
                    word_table.style = 'Table Grid' # Đóng khung lưới rõ ràng
                    for r_idx, row in enumerate(table_data):
                        for c_idx, val in enumerate(row):
                            word_table.cell(r_idx, c_idx).text = val
                in_table = False
                table_data = []

        # Xử lý Công thức toán/hóa học thông qua định dạng chữ (Chống lỗi font)
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            title_text = line.lstrip('#').strip()
            doc.add_heading(title_text, level=min(level, 3))
        elif line.strip():
            # Tự động chèn lại các hình ảnh minh họa trích xuất từ file nguồn cũ vào vị trí phù hợp
            if "[Hình ảnh minh họa" in line and images_list:
                try:
                    img_stream = io.BytesIO(images_list[0]) # Lấy ảnh đầu tiên trong kho nạp
                    doc.add_picture(img_stream, width=Inches(4.5))
                except:
                    pass
            else:
                doc.add_paragraph(line)

    # Chuyển đổi file Word thành dòng dữ liệu để Streamlit tải về
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()
# --- GIAO DIỆN CHÍNH CỦA PHÂN HỆ ---
def render_khbd_section(run_ai_prompt_safe_func):
    
    tab_xay_dung, tab_luu_khbd = st.tabs(["📝 XÂY DỰNG KẾ HOẠCH BÀI DẠY AI", "🗄️ LƯU KHBD ĐÃ XD"])
    
    if "ket_qua_giao_an" not in st.session_state:
        st.session_state["ket_qua_giao_an"] = ""
    if "lich_su_khbd" not in st.session_state:
        st.session_state["lich_su_khbd"] = []
    if "kho_anh_trich_xuat" not in st.session_state:
        st.session_state["kho_anh_trich_xuat"] = []

    # ==================== THẺ 1: XÂY DỰNG KẾ HOẠCH BÀI DẠY AI ====================
    with tab_xay_dung:
        st.markdown("<h3 style='text-align: center; color: red;'>📖 CHỨC NĂNG XÂY DỰNG KẾ HOẠCH BÀI DẠY TỐI ƯU HÓA CAO</h3>", unsafe_allow_html=True)
        
        ten_bai = st.text_input("Tên bài dạy / Chủ đề:", key="khbd_ten_bai")
        
        col_mon, col_tg, col_lop = st.columns(3)
        with col_mon:
            mon_hoc = st.selectbox("Môn học:", ["Khoa học tự nhiên", "Toán học", "Ngữ văn", "Tiếng Anh", "Lịch sử & Địa lý", "Tin học", "Công nghệ"])
        with col_tg:
            thoi_luong = st.text_input("Thời lượng:", placeholder="Ví dụ: 3 tiết")
        with col_lop:
            lop = st.text_input("Lớp:", placeholder="Ví dụ: 6A")
            
        tich_hop_ai = st.checkbox("Tích hợp giáo dục AI (Năng lực số và AI)", value=True)
        uati_bam_sat = st.checkbox("Ưu tiên bám sát 100% nội dung tài liệu nguồn tải lên", value=True)
        
        # --- KHU VỰC TẢI LÊN SỐ LƯỢNG LỚN FILE NGUỒN (ĐÃ LƯỢC BỎ MẪU GIÁO ÁN) ---
        st.markdown("**📁 Hệ thống tải lên học liệu tham khảo đa file (Hỗ trợ nạp cùng lúc nhiều tài liệu):**")
        tai_hoc_lieu = st.file_uploader(
            "Kéo thả tất cả các file tài liệu nền tảng tại đây", 
            type=["docx", "pdf", "txt"], 
            accept_multiple_files=True
        )
        
        col_btn1, col_blank, col_btn2 = st.columns([1.5, 2, 1.5])
        with col_btn1:
            # Tạo file Word thực tế trả về cho giáo viên
            docx_data = export_khbd_to_docx(st.session_state["ket_qua_giao_an"], st.session_state["kho_anh_trich_xuat"]) if st.session_state["ket_qua_giao_an"] else b""
            st.download_button(
                label="📥 Tải file Word (.docx) chuẩn biểu bảng",
                data=docx_data,
                file_name=f"KHBD_{ten_bai.replace(' ', '_') if ten_bai else 'BGD_5512'}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                disabled=(st.session_state["ket_qua_giao_an"] == ""),
                use_container_width=True
            )
        with col_btn2:
            nut_chay_ai = st.button("⚡ Khởi tạo kế hoạch bài dạy bằng AI", type="primary", use_container_width=True)

        st.markdown("**💬 Yêu cầu ràng buộc khác (Để AI làm căn cứ bổ sung khi soạn bài):**")
        yeu_cau_khac = st.text_area(
            "Nhập lưu ý...",
            placeholder="Ví dụ: Thiết kế thêm bảng phụ lục so sánh các chất, viết rõ phương trình hóa học cân bằng, sử dụng công thức toán định dạng rõ ràng...",
            label_visibility="collapsed",
            height=80
        )

        st.markdown("**📊 Nội dung bài soạn hiển thị xem trước:**")
        with st.container(border=True):
            if st.session_state["ket_qua_giao_an"]:
                st.markdown(st.session_state["ket_qua_giao_an"])
                if st.button("📥 Lưu vào Thư viện hệ thống"):
                    if ten_bai:
                        st.session_state["lich_su_khbd"].append({"Tên bài": ten_bai, "Môn": mon_hoc, "Lớp": lop, "Nội dung": st.session_state["ket_qua_giao_an"]})
                        st.success("✅ Đã lưu giáo án thành công!")
                        st.rerun()
            else:
                st.caption("Bài soạn sau khi khởi tạo bằng AI sẽ hiển thị tại đây...")

    # ==================== THẺ 2: LƯU TRỮ KẾ HOẠCH BÀI DẠY ĐÃ XD ====================
    with tab_luu_khbd:
        st.markdown("### 🗄️ THƯ VIỆN LƯU TRỮ KẾ HOẠCH BÀI DẠY ĐÃ XÂY DỰNG")
        if not st.session_state["lich_su_khbd"]:
            st.info("Chưa có bài soạn nào được lưu trong phiên này.")
        else:
            for idx, item in enumerate(st.session_state["lich_su_khbd"]):
                with st.expander(f"📚 {idx+1}. {item['Tên bài']} - Lớp {item['Lớp']}"):
                    st.markdown(item["Nội dung"])

    # --- XỬ LÝ SỰ KIỆN KHI BẤM NÚT GỌI GEMINI AI ---
    if nut_chay_ai:
        if not ten_bai:
            st.warning("⚠️ Vui lòng nhập Tên bài dạy trước!")
        elif not tai_hoc_lieu:
            st.warning("⚠️ Vui lòng nạp học liệu tham khảo để AI bám sát dữ liệu nguồn!")
        else:
            with st.spinner("🧠 Trợ lý AI đang nghiên cứu kỹ dữ liệu nguồn đa file và thiết kế bài soạn..."):
                # Gọi hàm bóc tách văn bản và trích xuất ảnh nền
                văn_bản_nguồn, danh_sách_ảnh = extract_context_from_uploaded_files(tai_hoc_lieu)
                st.session_state["kho_anh_trich_xuat"] = danh_sách_ảnh

                # PROMPT KỸ THUẬT ÉP CẤU TRÚC PHỤ LỤC IV CÔNG VĂN 5512
                prompt_yeu_cau = f"""
                Bạn là Chuyên gia viết giáo án cấp cao. Hãy soạn một Kế hoạch bài dạy chi tiết.
                Tên bài: {ten_bai} | Môn: {mon_hoc} | Thời lượng: {thoi_luong} | Lớp: {lop}
                
                YÊU CẦU NỘI DUNG VÀ CẤU TRÚC BẮT BUỘC:
                1. BỐ CỤC: Tuân thủ 100% cấu trúc PHỤ LỤC IV của Công văn 5512/BGDĐT:
                   I. MỤC TIÊU (1. Kiến thức, 2. Năng lực, 3. Phẩm chất)
                   II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU
                   III. TIẾN TRÌNH DẠY HỌC: Chia đều lộ trình cho đủ {thoi_luong}. Gồm 4 Hoạt động: Hoạt động 1: Mở đầu; Hoạt động 2: Hình thành kiến thức mới; Hoạt động 3: Luyện tập; Hoạt động 4: Vận dụng.
                   *Mỗi hoạt động BẮT BUỘC liệt kê đủ 4 mục nhỏ rõ ràng: a) Mục tiêu; b) Nội dung; c) Sản phẩm; d) Tổ chức thực hiện (Giao nhiệm vụ -> Thực hiện -> Báo cáo thảo luận -> Kết luận nhận định).
                
                2. ĐỘ CHÍNH XÁC: 
                   - { 'Bám sát 100% nội dung tài liệu nguồn được cung cấp dưới đây. Trích xuất đúng thuật ngữ, số liệu.' if uati_bam_sat else '' }
                   - CÔNG THỨC TOÁN/HÓA HỌC: Viết rõ ràng các ký hiệu, chỉ số trên/dưới (Ví dụ: H2O, CO2, Fe2(SO4)3 hoặc các phương trình toán học) bằng ký tự chữ Unicode chuẩn, không viết tắt để tránh lỗi font khi chuyển sang Word.
                   - BIỂU BẢNG: Phần nội dung so sánh hoặc phiếu học tập phải được thiết kế dạng bảng Markdown bằng ký tự '|' để hệ thống tự tạo bảng trong file .docx.
                   - { 'HÌNH ẢNH MINH HỌA: Tại các bước hướng dẫn lý thuyết thích hợp, hãy tự động chèn dòng chữ chính xác là "[Hình ảnh minh họa]" để hệ thống kích hoạt chèn ảnh trích xuất từ file gốc.' if danh_sách_ảnh else '' }
                
                3. { 'NĂNG LỰC SỐ VÀ AI: Lồng ghép hoạt động ứng dụng công nghệ, sử dụng thiết bị thông minh hoặc tra cứu thông tin bằng trợ lý AI vào các nhiệm vụ học sinh cần làm.' if tich_hop_ai else '' }
                4. CĂN CỨ BỔ SUNG KHÁC: {yeu_cau_khac}
                
                DỮ LIỆU FILE NGUỒN TÀI LIỆU THAM KHẢO:
                {văn_bản_nguồn}
                """
                
                ket_qua_ai, model_used = run_ai_prompt_safe_func(prompt_yeu_cau)
                st.session_state["ket_qua_giao_an"] = ket_qua_ai
                st.rerun()
