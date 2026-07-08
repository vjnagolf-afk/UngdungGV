import streamlit as st
import docx  # Dùng để đọc file Word
from pypdf import PdfReader  # Dùng để đọc file PDF

# --- HÀM TRÍCH XUẤT VĂN BẢN TỪ FILE TẢI LÊN ---
def extract_text_from_files(uploaded_files):
    combined_text = ""
    for file in uploaded_files:
        try:
            if file.name.endswith('.docx'):
                doc = docx.Document(file)
                fullText = [para.text for para in doc.paragraphs]
                combined_text += f"\n--- NỘI DUNG TỪ FILE: {file.name} ---\n" + "\n".join(fullText)
            elif file.name.endswith('.pdf'):
                reader = PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                combined_text += f"\n--- NỘI DUNG TỪ FILE: {file.name} ---\n" + text
            elif file.name.endswith('.txt'):
                combined_text += f"\n--- NỘI DUNG TỪ FILE: {file.name} ---\n" + file.read().decode("utf-8")
        except Exception as e:
            st.error(f"Lỗi khi đọc file {file.name}: {str(e)}")
    return combined_text

# --- GIAO DIỆN CHÍNH CỦA PHÂN HỆ ---
def render_khbd_section(run_ai_prompt_safe_func):
    
    # 1. KHỞI TẠO 2 THẺ (TABS) NGANG THEO YÊU CẦU MỚI
    tab_xay_dung, tab_luu_khbd = st.tabs(["📝 XÂY DỰNG KẾ HOẠCH BÀI DẠY AI", "🗄️ LƯU KHBD ĐÃ XD"])
    
    # Khởi tạo vùng chứa nội dung giáo án trong bộ nhớ tạm nếu chưa có
    if "ket_qua_giao_an" not in st.session_state:
        st.session_state["ket_qua_giao_an"] = ""
    if "lich_su_khbd" not in st.session_state:
        st.session_state["lich_su_khbd"] = []

    # ==================== THẺ 1: XÂY DỰNG KẾ HOẠCH BÀI DẠY AI ====================
    with tab_xay_dung:
        st.markdown("<h3 style='text-align: center; color: red;'>📖 CHỨC NĂNG XÂY DỰNG KẾ HOẠCH BÀI DẠY AI THEO MẪU KHÁCH</h3>", unsafe_allow_html=True)
        
        # --- DÒNG 1: NHẬP TÊN BÀI DẠY ---
        ten_bai = st.text_input("Tên bài dạy / Chủ đề:", key="khbd_ten_bai")
        
        # --- DÒNG 2: MÔN HỌC, THỜI LƯỢNG, LỚP ---
        col_mon, col_tg, col_lop = st.columns(3)
        with col_mon:
            mon_hoc = st.selectbox("Môn học:", ["Khoa học tự nhiên", "Toán học", "Ngữ văn", "Tiếng Anh", "Lịch sử & Địa lý", "Tin học", "Công nghệ"])
        with col_tg:
            thoi_luong = st.text_input("Thời lượng:", placeholder="Ví dụ: 3 tiết")
        with col_lop:
            lop = st.text_input("Lớp:", placeholder="Ví dụ: 6A")
            
        # --- DÒNG 3: CÁC TÙY CHỌN CHECKBOX ---
        tich_hop_ai = st.checkbox("Tích hợp giáo dục AI (Năng lực số và AI)", value=True)
        uati_bam_sat = st.checkbox("Ưu tiên bám sát 100% tài liệu tải lên", value=True)
        
        # --- DÒNG 4: KHU VỰC CÁC NÚT BẤM VÀ TẢI FILE ---
        col_f1, col_f2, col_blank, col_btn1, col_btn2 = st.columns([1.2, 1.2, 1, 1.2, 1.4])
        
        with col_f1:
            st.caption("📁 Tải file học liệu tham khảo:")
            tai_hoc_lieu = st.file_uploader("Upload học liệu", type=["docx", "pdf", "txt"], accept_multiple_files=True, label_visibility="collapsed")
        with col_f2:
            st.caption("📄 Tải giáo án mẫu:")
            tai_giao_an_mau = st.file_uploader("Upload giáo án mẫu", type=["docx", "pdf", "txt"], label_visibility="collapsed")
            st.caption("Chưa chọn mẫu" if not tai_giao_an_mau else f"✅ Mẫu: {tai_giao_an_mau.name}")
            
        with col_btn1:
            st.write("") # Tạo khoảng cách dòng
            st.write("") 
            # Nút xuất file nhanh về máy tính cá nhân
            st.download_button(
                label="💾 Tải file KHBD về máy",
                data=st.session_state["ket_qua_giao_an"],
                file_name=f"KHBD_{ten_bai.replace(' ', '_') if ten_bai else 'Chua_dat_ten'}.txt",
                mime="text/plain",
                disabled=(st.session_state["ket_qua_giao_an"] == ""),
                use_container_width=True
            )
        with col_btn2:
            st.write("") # Tạo khoảng cách dòng
            st.write("")
            nut_chay_ai = st.button("⚡ Khởi tạo giáo án bằng AI", type="primary", use_container_width=True)

        # --- DÒNG 5: Ô CHÁT YÊU CẦU RÀNG BUỘC KHÁC THAY THẾ CHO KHUNG HIỂN THỊ CŨ ---
        st.markdown("**💬 Yêu cầu ràng buộc khác (Để AI làm căn cứ bổ sung khi soạn bài):**")
        yeu_cau_khac = st.text_area(
            "Nhập các lưu ý đặc biệt hoặc phương pháp dạy học cụ thể muốn AI áp dụng...",
            placeholder="Ví dụ: Sử dụng kỹ thuật mảnh ghép ở hoạt động 2, bổ sung thêm bài tập trắc nghiệm phân hóa ở hoạt động luyện tập...",
            label_visibility="collapsed",
            height=100
        )

        # --- DÒNG 6: KHU VỰC HIỂN THỊ NỘI DUNG GIÁO ÁN XEM TRƯỚC ---
        st.markdown("**📊 Nội dung giáo án hiển thị xem trước:**")
        with st.container(border=True):
            if st.session_state["ket_qua_giao_an"]:
                st.markdown(st.session_state["ket_qua_giao_an"])
                
                # Thêm nút bấm phụ trợ để lưu nhanh kết quả sang Thẻ 2
                if st.button("📥 Lưu bài soạn này vào Thư viện hệ thống"):
                    if ten_bai:
                        st.session_state["lich_su_khbd"].append({
                            "Tên bài": ten_bai,
                            "Môn": mon_hoc,
                            "Lớp": lop,
                            "Nội dung": st.session_state["ket_qua_giao_an"]
                        })
                        st.success("✅ Đã lưu giáo án vào danh sách lưu trữ! Hãy qua thẻ 'LƯU KHBD ĐÃ XD' để kiểm tra.")
                    else:
                        st.error("Vui lòng nhập tên bài để có thông tin lưu trữ.")
            else:
                st.caption("Nội dung bài soạn sau khi khởi tạo bằng AI sẽ hiển thị tại đây...")

    # ==================== THẺ 2: LƯU TRỮ KẾ HOẠCH BÀI DẠY ĐÃ XD ====================
    with tab_luu_khbd:
        st.markdown("### 🗄️ THƯ VIỆN LƯU TRỮ KẾ HOẠCH BÀI DẠY ĐÃ XÂY DỰNG")
        st.write("Nơi lưu trữ các kế hoạch bài dạy đã tạo trong phiên làm việc để giáo viên quản lý và xem lại nhanh.")
        
        if not st.session_state["lich_su_khbd"]:
            st.info("Chưa có bài soạn nào được lưu. Sau khi tạo giáo án thành công ở Thẻ 1, hãy bấm nút 'Lưu bài soạn này vào Thư viện hệ thống'.")
        else:
            # Hiển thị danh sách các bài đã lưu theo cấu trúc rút gọn hình hộp Expander
            for idx, item in enumerate(st.session_state["lich_su_khbd"]):
                with st.expander(f"📚 {idx+1}. {item['Tên bài']} - Môn: {item['Môn']} (Lớp {item['Lớp']})"):
                    st.markdown(item["Nội dung"])
                    st.download_button(
                        label="📥 Tải bản sao đính kèm (.txt)",
                        data=item["Nội dung"],
                        file_name=f"Luu_tru_{item['Tên bài'].replace(' ', '_')}.txt",
                        mime="text/plain",
                        key=f"dl_saved_{idx}"
                    )

    # --- XỬ LÝ LOGIC KHI BẤM NÚT KHỞI TẠO GIÁO ÁN BẰNG AI ---
    if nut_chay_ai:
        if not ten_bai:
            st.warning("⚠️ Vui lòng nhập Tên bài dạy / Chủ đề trước khi khởi tạo!")
        else:
            with st.spinner("🧠 Trợ lý AI đang đọc kỹ các file nguồn và tiến hành lập tiến trình bài dạy..."):
                
                # Trích xuất văn bản từ học liệu tham khảo (nếu có tải lên)
                nguon_van_ban = ""
                if tai_hoc_lieu:
                    nguon_van_ban = extract_text_from_files(tai_hoc_lieu)
                
                # Trích xuất dữ liệu từ giáo án mẫu (nếu có tải lên)
                mau_giao_an_text = ""
                if tai_giao_an_mau:
                    mau_giao_an_text = extract_text_from_files([tai_giao_an_mau])

                # Xây dựng câu lệnh Prompt thông minh, tích hợp ô Yêu cầu khác
                prompt_yeu_cau = f"""
                Bạn là một chuyên gia giáo dục cao cấp tại Việt Nam. Nhiệm vụ của bạn là biên soạn Kế hoạch bài dạy (Giáo án) chi tiết.
                
                THÔNG TIN BÀI DẠY:
                - Tên bài dạy / Chủ đề: {ten_bai}
                - Môn học: {mon_hoc}
                - Thời lượng: {thoi_luong} (Yêu cầu phân chia nội dung và tiến trình khít và bám sát chính xác thời lượng này).
                - Khối lớp: {lop}
                
                YÊU CẦU BẮT BUỘC KHI SOẠN BÀI:
                1. BỐ CỤC BÀI SOẠN: Phải tuân thủ chuẩn chỉnh, chính xác theo cấu trúc PHỤ LỤC IV CÔNG VĂN 5512/BGDĐT bao gồm:
                   I. MỤC TIÊU (Kiến thức; Năng lực; Phẩm chất).
                   II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU.
                   III. TIẾN TRÌNH DẠY HỌC (Gồm đầy đủ 4 hoạt động: 1. Mở đầu/Xác định vấn đề; 2. Hình thành kiến thức mới; 3. Luyện tập; 4. Vận dụng). Mỗi hoạt động bắt buộc có đủ: Mục tiêu, Nội dung, Sản phẩm, Tổ chức thực hiện.
                2. { 'TÍCH HỢP NĂNG LỰC SỐ VÀ AI: Ở phần Mục tiêu (Năng lực) và trong các bước Tổ chức thực hiện ở mục Tiến trình dạy học, phải lồng ghép chi tiết các hoạt động yêu cầu học sinh sử dụng thiết bị số, ứng dụng công nghệ thông tin hoặc khai thác các công cụ trí tuệ nhân tạo (AI) để giải quyết nhiệm vụ học tập.' if tich_hop_ai else '' }
                3. { 'BÁM SÁT 100% FILE NGUỒN TÀI LIỆU THAM KHẢO: Đọc thật kỹ phần nội dung văn bản trích xuất từ file nguồn đính kèm dưới đây. Không tự ý tạo ra kiến thức nằm ngoài phạm vi tài liệu này cung cấp.' if (uati_bam_sat and nguon_van_ban) else '' }
                4. { f'CĂN CỨ BỔ SUNG TỪ NGƯỜI DÙNG (YÊU CẦU RÀNG BUỘC KHÁC): Hãy áp dụng triệt để yêu cầu bổ sung sau vào tiến trình soạn bài: {yeu_cau_khac}' if yeu_cau_khac else '' }
                
                {f'MẪU THIẾT KẾ GIÁO ÁN THAM KHẢO (Hãy bắt chước phong cách trình bày từ mẫu này): {mau_giao_an_text}' if mau_giao_an_text else ''}
                
