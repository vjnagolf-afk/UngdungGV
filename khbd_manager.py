import streamlit as st
import docx  
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import re
from pypdf import PdfReader

# --- HÀM TRÍCH XUẤT VĂN BẢN VÀ HÌNH ẢNH TỪ FILE NGUỒN ---
def extract_context_from_uploaded_files(uploaded_files):
    combined_text = ""
    extracted_images = [] 
    for file in uploaded_files:
        try:
            if file.name.endswith('.docx'):
                doc = docx.Document(file)
                for paragraph in doc.paragraphs:
                    if paragraph.text: combined_text += paragraph.text + "\n"
                for table in doc.tables:
                    for row in table.rows:
                        text_row = [cell.text for cell in row.cells]
                        combined_text += " | ".join(text_row) + "\n"
                for rel in doc.part.relations.values():
                    if "image" in rel.target_ref:
                        extracted_images.append(rel.target_part.blob)
            elif file.name.endswith('.pdf'):
                reader = PdfReader(file)
                for page in reader.pages:
                    combined_text += (page.extract_text() or "") + "\n"
                    for img_file_object in page.images:
                        extracted_images.append(img_file_object.data)
            elif file.name.endswith('.txt'):
                combined_text += file.read().decode("utf-8") + "\n"
        except Exception as e:
            st.error(f"Lỗi khi xử lý file {file.name}: {str(e)}")
    return combined_text, extracted_images

# --- HÀM XUẤT FILE WORD (.DOCX) CHUẨN ĐỊNH DẠNG MÀU SẮC, FONT, CỠ CHỮ ---
def export_khbd_to_docx(markdown_content, images_list):
    doc = docx.Document()
    # Định dạng lề trang chuẩn văn bản hành chính Việt Nam
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(1.18)
        section.right_margin = Inches(0.59)

    # Cấu hình màu sắc chuẩn
    MAU_DO = RGBColor(255, 0, 0)
    MAU_XANH_DUONG = RGBColor(0, 51, 153)
    MAU_DEN = RGBColor(0, 0, 0)

    lines = markdown_content.split('\n')
    in_table = False
    table_data = []

    for line in lines:
        clean_line = line.strip().replace('**', '').replace('###', '').replace('##', '').replace('#', '')
        
        # 1. XỬ LÝ BIỂU BẢNG VÀ PHIẾU HỌC TẬP
        if line.strip().startswith('|') and line.strip().endswith('|'):
            if '---|' in line or ':---|' in line: continue
            in_table = True
            cells = [c.strip().replace('**', '') for c in line.split('|')[1:-1]]
            table_data.append(cells)
            continue
        else:
            if in_table and table_data:
                num_rows = len(table_data)
                num_cols = len(table_data[0]) if num_rows > 0 else 0
                if num_cols > 0:
                    word_table = doc.add_table(rows=num_rows, cols=num_cols)
                    word_table.style = 'Table Grid'
                    for r_idx, row in enumerate(table_data):
                        for c_idx, val in enumerate(row):
                            if c_idx < num_cols:
                                cell = word_table.cell(r_idx, c_idx)
                                cell.text = val
                                for p in cell.paragraphs:
                                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                                    for r in p.runs:
                                        r.font.name = 'Times New Roman'
                                        r.font.size = Pt(14)
                                        r.font.color.rgb = MAU_DEN
                in_table = False
                table_data = []

        if not clean_line: continue

        p = doc.add_paragraph()
        # Thừa kế căn lề đều 2 bên cho nội dung thông thường
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        # 2. ĐỊNH DẠNG TIÊU ĐỀ BÀI HỌC (IN HOA ĐẬM, CĂN GIỮA, CHỮ ĐỎ)
        if any(x in clean_line.upper() for x in ["MÔN HỌC:", "LỚP:", "BÀI:", "KẾ HOẠCH BÀI DẠY"]):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(clean_line.upper())
            run.bold = True
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
            run.font.color.rgb = MAU_DO
            
        # 3. ĐỊNH DẠNG ĐỀ MỤC LỚN (IN ĐẬM, CĂN TRÁI, CHỮ XANH DƯƠNG)
        elif re.match(r'^(I|II|III|IV|V|VI)\.', clean_line) or re.match(r'^\d+\.', clean_line):
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(clean_line)
            run.bold = True
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
            run.font.color.rgb = MAU_XANH_DUONG

        # 4. ĐỊNH DẠNG NỘI DUNG THÔNG THƯỜNG (CHỮ ĐEN, CĂN ĐỀU CẢ 2 BÊN)
        else:
            if "[Hình ảnh minh họa]" in line and images_list:
                try:
                    img_stream = io.BytesIO(images_list)
                    doc.add_picture(img_stream, width=Inches(4.5))
                    continue
                except: pass
            
            parts = re.split(r'(\d+)', clean_line)
            for part in parts:
                run = p.add_run(part)
                run.font.name = 'Times New Roman'
                run.font.size = Pt(14)
                run.font.color.rgb = MAU_DEN
                if part.isdigit() and any(x in clean_line for x in ['H2O', 'CO2', 'Fe', 'O2', 'H2SO4', 'N2', 'CH4']):
                    run.font.subscript = True

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()
# --- GIAO DIỆN CHÍNH CỦA PHÂN HỆ ---
def render_khbd_section(run_ai_prompt_safe_func):
    
    tab_xay_dung, tab_luu_khbd = st.tabs(["📝 XÂY DỰNG KẾ HOẠCH BÀI DẠY AI", "🗄️ LƯU KHBD ĐÃ XD"])
    
    if "ket_qua_giao_an" not in st.session_state: st.session_state["ket_qua_giao_an"] = ""
    if "lich_su_khbd" not in st.session_state: st.session_state["lich_su_khbd"] = []
    if "kho_anh_trich_xuat" not in st.session_state: st.session_state["kho_anh_trich_xuat"] = []

    # ==================== THẺ 1: XÂY DỰNG KẾ HOẠCH BÀI DẠY AI ====================
    with tab_xay_dung:
        st.markdown("<h3 style='text-align: center; color: red;'>📖 CHỨC NĂNG XÂY DỰNG KẾ HOẠCH BÀI DẠY TỐI ƯU HÓA CAO</h3>", unsafe_allow_html=True)
        
        ten_bai = st.text_input("Tên bài dạy / Chủ đề:", key="khbd_ten_bai")
        
        col_mon, col_tg, col_lop = st.columns(3)
        with col_mon:
            mon_hoc = st.selectbox("Môn học:", ["Khoa học tự nhiên", "Toán học", "Ngữ văn", "Tiếng Anh", "Lịch sử & Địa lý", "Tin học", "Công nghệ"])
        with col_tg:
            thoi_luong = st.text_input("Thời lượng:", placeholder="Ví dụ: 2 Tiết")
        with col_lop:
            lop = st.text_input("Lớp:", placeholder="Ví dụ: 7A")
            
        tich_hop_ai = st.checkbox("Tích hợp giáo dục AI (Năng lực số và AI)", value=True)
        uati_bam_sat = st.checkbox("Ưu tiên bám sát 100% nội dung tài liệu nguồn tải lên", value=True)
        
        st.markdown("**📁 Hệ thống tải lên học liệu tham khảo đa file (Hỗ trợ nạp cùng lúc nhiều tài liệu):**")
        tai_hoc_lieu = st.file_uploader("Kéo thả tất cả các file tài liệu tại đây", type=["docx", "pdf", "txt"], accept_multiple_files=True, key="hoc_lieu_uploader")
        
        col_btn1, col_blank, col_btn2 = st.columns([2.0, 1.3, 1.7])
        
        st.markdown("**💬 Yêu cầu ràng buộc khác (Để AI làm căn cứ bổ sung khi soạn bài):**")
        yeu_cau_khac = st.text_area("Nhập lưu ý...", placeholder="Ví dụ: Thiết kế bảng biểu so sánh rõ ràng, sử dụng ký tự unicode cho phương trình...", label_visibility="collapsed", height=100)
        
        with col_btn2:
            st.write(""); st.write("")
            nut_chay_ai = st.button("⚡ Khởi tạo kế hoạch bài dạy bằng AI", type="primary", use_container_width=True)
            
        if nut_chay_ai:
            if not ten_bai:
                st.warning("⚠️ Vui lòng nhập Tên bài dạy trước!")
            elif not tai_hoc_lieu:
                st.warning("⚠️ Vui lòng nạp học liệu tham khảo để AI bám sát dữ liệu nguồn!")
            else:
                with st.spinner("🧠 Trợ lý AI đang nghiên cứu kỹ dữ liệu nguồn đa file và tiến hành lập tiến trình bài dạy..."):
                    from khbd_manager import extract_context_from_uploaded_files
                    văn_bản_nguồn, danh_sách_ảnh = extract_context_from_uploaded_files(tai_hoc_lieu)
                    st.session_state["kho_anh_trich_xuat"] = danh_sách_ảnh

                    prompt_yeu_cau = f"""
                    Bạn là Chuyên gia viết giáo án cấp cao bậc THCS/THPT tại Việt Nam. Hãy soạn một Kế hoạch bài dạy cực kỳ chi tiết, đầy đủ chữ theo đúng yêu cầu cấu trúc và định dạng sau.
                    
                    TIÊU ĐỀ BÀI HỌC (Viết in hoa ở đầu giáo án):
                    MÔN HỌC: {mon_hoc.upper()}
                    LỚP: {lop.upper()}
                    BÀI: {ten_bai.upper()} ({thoi_luong})
                    
                    YÊU CẦU CẤU TRÚC PHỤ LỤC IV CÔNG VĂN 5512/BGDĐT:
                    I. MỤC TIÊU (Bắt buộc chia nhỏ thành đúng 4 đề mục con sau):
                       1. Kiến thức
                       2. Năng lực (Bao gồm Năng lực chung và Năng lực đặc thù của môn học)
                       3. Năng lực số và AI (Thiết kế các mục tiêu về việc học sinh biết ứng dụng thiết bị công nghệ và công cụ AI vào bài học)
                       4. Phẩm chất (Chuyển đổi từ mục số 3 cũ thành mục 4)
                    II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU
                    III. TIẾN TRÌNH DẠY HỌC (Thiết kế phân bổ cho tổng số {thoi_luong}. Gồm đủ 4 Hoạt động: Hoạt động 1: Mở đầu; Hoạt động 2: Hình thành kiến thức mới; Hoạt động 3: Luyện tập; Hoạt động 4: Vận dụng).
                       *Mỗi hoạt động phải trình bày đủ 4 mục nhỏ: a) Mục tiêu; b) Nội dung; c) Sản phẩm; d) Tổ chức thực hiện.
                    
                    YÊU CẦU ĐỊNH DẠNG VÀ CÚ PHÁP (Cực kỳ nghiêm ngặt):
                    - BỎ TOÀN BỘ các ký tự dấu sao kép '**' ở đầu và cuối các từ hoặc các mục. Trả về văn bản sạch, không sử dụng định dạng chữ đậm dạng Markdown.
                    - Toàn bộ các nội dung nhỏ, danh sách liệt kê bên trong bài KHÔNG ĐƯỢC DÙNG dấu sao '*' hoặc dấu chấm tròn, mà THỐNG NHẤT sử dụng duy nhất dấu gạch ngang '-' ở đầu dòng.
                    - CÔNG THỨC TOÁN/HÓA HỌC: Trình bày rõ phương trình phản ứng cân bằng (ví dụ: viết rõ chỉ số dạng H2O, CO2, Fe2(SO4)3).
                    - BIỂU BẢNG: Thiết kế phiếu học tập hoặc bảng so sánh bằng ký tự '|' của Markdown.
                    - Bám sát hoàn toàn 100% nội dung kiến thức từ tài liệu nguồn dưới đây.
                    
                    CĂN CỨ BỔ SUNG KHÁC: {yeu_cau_khac}
                    
                    DỮ LIỆU FILE NGUỒN TÀI LIỆU THAM KHẢO:
                    {văn_bản_nguồn}
                    """
                    ket_qua_ai, model_used = run_ai_prompt_safe_func(prompt_yeu_cau)
                    st.session_state["ket_qua_giao_an"] = ket_qua_ai

        with col_btn1:
            st.write(""); st.write("")
            from khbd_manager import export_khbd_to_docx
            docx_data = export_khbd_to_docx(st.session_state["ket_qua_giao_an"], st.session_state["kho_anh_trich_xuat"]) if st.session_state["ket_qua_giao_an"] else b""
            st.download_button(
                label="📥 Tải file Word (.docx) chuẩn về máy",
                data=docx_data,
                file_name=f"KHBD_{ten_bai.replace(' ', '_') if ten_bai else 'BGD_5512'}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                disabled=(st.session_state["ket_qua_giao_an"] == ""),
                use_container_width=True
            )

        st.markdown("**📊 Nội dung bài soạn hiển thị xem trước:**")
        with st.container(border=True):
            if st.session_state["ket_qua_giao_an"]:
                st.markdown(st.session_state["ket_qua_giao_an"])
                if st.button("📥 Lưu vào Thư viện hệ thống", use_container_width=True):
                    if ten_bai:
                        st.session_state["lich_su_khbd"].append({"Tên bài": ten_bai, "Môn": mon_hoc, "Lớp": lop, "Nội dung": st.session_state["ket_qua_giao_an"], "Kho_anh": st.session_state["kho_anh_trich_xuat"]})
                        st.success("✅ Đã lưu giáo án vào Thư viện thành công!")
            else:
                st.caption("Bài soạn sau khi khởi tạo bằng AI sẽ hiển thị tại đây...")

    # ==================== THÈ 2: LƯU TRỮ KẾ HOẠCH BÀI DẠY ĐÃ XD ====================
    with tab_luu_khbd:
        st.markdown("### 🗄️ THƯ VIỆN LƯU TRỮ KẾ HOẠCH BÀI DẠY ĐÃ XÂY DỰNG")
        if not st.session_state["lich_su_khbd"]:
            st.info("Chưa có bài soạn nào được lưu trong phiên này.")
        else:
            for idx, item in enumerate(st.session_state["lich_su_khbd"]):
                col_exp, col_del = st.columns([0.88, 0.12])
                with col_exp:
                    with st.expander(f"📚 {idx+1}. {item['Tên bài']} - Môn: {item['Môn']} (Lớp {item['Lớp']})"):
                        st.markdown(item["Nội dung"])
                        from khbd_manager import export_khbd_to_docx
                        saved_docx = export_khbd_to_docx(item["Nội dung"], item.get("Kho_anh", []))
                        st.download_button(
                            label="📥 Tải lại bản Word (.docx)",
                            data=saved_docx,
                            file_name=f"Luu_tru_{item['Tên bài'].replace(' ', '_')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"dl_saved_docx_{idx}"
                        )
                with col_del:
                    st.write("") 
                    if st.button("🗑️ Xóa bài", key=f"del_khbd_{idx}", use_container_width=True, type="secondary"):
                        st.session_state["lich_su_khbd"].pop(idx)
                        st.success(f"Đã xóa bài số {idx+1}!")
                        st.rerun()
