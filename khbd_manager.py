import streamlit as st
import docx  
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import io
import re
from pypdf import PdfReader
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ================= CẤU HÌNH GOOGLE SHEETS =================
SHEET_ID = '1C6642jk_oQ0g9UC2By2qsNxxfQVR0MrZYj52tRdWDlY' # ID dùng chung của hệ thống

def get_khbd_sheet():
    creds_dict = dict(st.secrets["GOOGLE_KEY"])
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    # Trỏ dữ liệu vào đúng tab KHBD
    return client.open_by_key(SHEET_ID).worksheet("KHBD")

# --- HÀM TRÍCH XUẤT VĂN BẢN VÀ LỌC ẢNH TRÙNG LẶP ---
def extract_context_from_uploaded_files(uploaded_files):
    combined_text = ""
    extracted_images = [] 
    seen_image_sizes = set()
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
                        img_blob = rel.target_part.blob
                        if len(img_blob) not in seen_image_sizes:
                            seen_image_sizes.add(len(img_blob))
                            extracted_images.append(img_blob)
            elif file.name.endswith('.pdf'):
                reader = PdfReader(file)
                for page in reader.pages:
                    combined_text += (page.extract_text() or "") + "\n"
                    for img_file_object in page.images:
                        img_blob = img_file_object.data
                        if len(img_blob) not in seen_image_sizes:
                            seen_image_sizes.add(len(img_blob))
                            extracted_images.append(img_blob)
            elif file.name.endswith('.txt'):
                combined_text += file.read().decode("utf-8") + "\n"
        except Exception as e:
            st.error(f"Lỗi khi xử lý file {file.name}: {str(e)}")
    return combined_text, extracted_images

# --- HÀM SET KHOẢNG CÁCH ĐOẠN 3 - 4.5 PT CHUẨN ---
def set_paragraph_spacing(paragraph, before_pt=3.0, after_pt=4.5):
    p_pr = paragraph._p.get_or_add_pPr()
    spacing = OxmlElement('w:spacing')
    spacing.set(qn('w:before'), str(int(before_pt * 20)))
    spacing.set(qn('w:after'), str(int(after_pt * 20)))
    spacing.set(qn('w:line'), '240')
    spacing.set(qn('w:lineRule'), 'auto')
    p_pr.append(spacing)

# --- HÀM TẠO KHỐI CÔNG THỨC TOÁN ĐỨNG (NHƯ HÌNH MẪU) ---
def add_math_expression(doc, text_line):
    if "[frac:" in text_line or "[root:" in text_line or "v = s / t" in text_line.lower() or "tốc độ =" in text_line.lower():
        p = doc.add_paragraph()
        set_paragraph_spacing(p)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        m_table = doc.add_table(rows=1, cols=3)
        m_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        frac_match = re.search(r'\[frac:\s*([^/]+)/([^\]]+)\]', text_line)
        if frac_match:
            tu, mau = frac_match.group(1).strip(), frac_match.group(2).strip()
            cell = m_table.cell(0, 1)
            cell.text = f"{tu}\n---\n{mau}"
            for para in cell.paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in para.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(14)
                    run.bold = True
            return
            
    p = doc.add_paragraph()
    set_paragraph_spacing(p)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    # Định dạng các mục liệt kê bằng dấu gạch ngang
    if text_line.strip().startswith('-'):
        p.paragraph_format.left_indent = Inches(0.25)
        
    parts = re.split(r'(\d+)', text_line)
    for part in parts:
        run = p.add_run(part)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0, 0, 0)
        if part.isdigit() and any(x in text_line for x in ['H2O', 'CO2', 'Fe', 'O2', 'H2SO4', 'N2', 'CH4']):
            run.font.subscript = True

# --- HÀM XUẤT FILE WORD (.DOCX) CHUẨN ĐỊNH DẠNG TÀI LIỆU MẪU ---
def export_khbd_to_docx(markdown_content, images_list):
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(1.18)
        section.right_margin = Inches(0.59)

    MAU_DO = RGBColor(255, 0, 0)
    MAU_XANH_DUONG = RGBColor(0, 51, 153)
    MAU_DEN = RGBColor(0, 0, 0)

    lines = markdown_content.split('\n')
    in_table = False
    table_data = []
    used_img_idx = 0

    for line in lines:
        # Xóa các ký tự định dạng Markdown thừa cân bằng chuỗi
        clean_line = line.strip().replace('**', '').replace('###', '').replace('##', '').replace('#', '')
        
        # 1. LỌC SẠCH DẤU GẠCH NGANG THỪA Ở ĐẦU ĐỀ MỤC NHỎ
        if re.match(r'^-\s*((\d+\.)|([a-d]\)))', clean_line):
            clean_line = re.sub(r'^-\s*', '', clean_line)

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
                    word_table.alignment = WD_TABLE_ALIGNMENT.CENTER
                    for r_idx, row in enumerate(table_data):
                        for c_idx, val in enumerate(row):
                            if c_idx < num_cols:
                                cell = word_table.cell(r_idx, c_idx)
                                cell.text = val
                                for para in cell.paragraphs:
                                    set_paragraph_spacing(para, 2.0, 3.0)
                                    para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                                    for r in para.runs:
                                        r.font.name = 'Times New Roman'
                                        r.font.size = Pt(14)
                                        r.font.color.rgb = MAU_DEN
                in_table = False
                table_data = []

        if not clean_line: continue

        # Chèn hình ảnh minh họa không trùng lặp
        if "[Hình ảnh minh họa]" in line and images_list:
            if used_img_idx < len(images_list):
                try:
                    p = doc.add_paragraph()
                    set_paragraph_spacing(p)
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    img_stream = io.BytesIO(images_list[used_img_idx])
                    doc.add_picture(img_stream, width=Inches(4.5))
                    used_img_idx += 1
                    continue
                except: pass

        # 2. ĐỊNH DẠNG TIÊU ĐỀ BÀI HỌC VÀ "TIẾT ... " (IN HOA ĐẬM, CĂN GIỮA, CHỮ ĐỎ)
        if any(x in clean_line.upper() for x in ["MÔN HỌC:", "LỚP:", "BÀI:", "KẾ HOẠCH BÀI DẠY", "THỜI LƯỢNG:"]) or re.match(r'^TIẾT\s+\d+', clean_line.upper()):
            p = doc.add_paragraph()
            set_paragraph_spacing(p, 4.0, 4.5)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(clean_line.upper())
            run.bold = True
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
            run.font.color.rgb = MAU_DO

        # 3. ĐỊNH DẠNG "HOẠT ĐỘNG X:" LỚN (IN ĐẬM, CĂN GIỮA, CHỮ XANH DƯƠNG)
        elif re.match(r'^HOẠT\s+ĐỘNG\s+\d+($|[^.\d])', clean_line.upper()) or "HOẠT ĐỘNG 1:" in clean_line.upper() or "HOẠT ĐỘNG 2:" in clean_line.upper() or "HOẠT ĐỘNG 3:" in clean_line.upper() or "HOẠT ĐỘNG 4:" in clean_line.upper():
            p = doc.add_paragraph()
            set_paragraph_spacing(p, 4.0, 4.5)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(clean_line.upper())
            run.bold = True
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
            run.font.color.rgb = MAU_XANH_DUONG

        # 4. ĐỊNH DẠNG "HOẠT ĐỘNG X.Y:" NHỎ (IN ĐẬM, CĂN TRÁI, CHỮ XANH DƯƠNG)
        elif re.match(r'^HOẠT\s+ĐỘNG\s+\d+\.\d+', clean_line.upper()):
            p = doc.add_paragraph()
            set_paragraph_spacing(p, 3.5, 4.0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(clean_line.upper())
            run.bold = True
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
            run.font.color.rgb = MAU_XANH_DUONG

        # 5. ĐỊNH DẠNG CÁC ĐỀ MỤC LỚN I, II, III VÀ 1, 2, 3, 4 (IN ĐẬM, CĂN TRÁI, CHỮ XANH DƯƠNG)
        elif re.match(r'^(I|II|III|IV|V|VI)\.', clean_line) or re.match(r'^\d+\.', clean_line):
            p = doc.add_paragraph()
            set_paragraph_spacing(p, 4.0, 4.5)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(clean_line)
            run.bold = True
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
            run.font.color.rgb = MAU_XANH_DUONG

        # 6. CÁC NỘI DUNG CÒN LẠI (CĂN ĐỀU CẢ 2 BÊN, CHỮ ĐEN)
        else:
            add_math_expression(doc, clean_line)

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
        yeu_cau_khac = st.text_area("Nhập lưu ý...", placeholder="Ví dụ: Giữ nguyên bảng 8.2 về tốc độ của một số phương tiện giao thông...", label_visibility="collapsed", height=100)
        
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
                    văn_bản_nguồn, danh_sách_ảnh = extract_context_from_uploaded_files(tai_hoc_lieu)
                    st.session_state["kho_anh_trich_xuat"] = danh_sách_ảnh

                    prompt_yeu_cau = f"""
                    Bạn là Chuyên gia viết giáo án cấp cao bậc THCS/THPT tại Việt Nam. Hãy soạn một Kế hoạch bài dạy cực kỳ chi tiết, đầy đủ chữ theo đúng yêu cầu cấu trúc và định dạng sau.
                    
                    TIÊU ĐỀ BÀI HỌC (Viết in hoa độc lập):
                    MÔN HỌC: {mon_hoc.upper()}
                    LỚP: {lop.upper()}
                    BÀI: {ten_bai.upper()}
                    (THỜI LƯỢNG: {thoi_luong.upper()})
                    
                    YÊU CẦU CẤU TRÚC PHỤ LỤC IV CÔNG VĂN 5512/BGDĐT:
                    I. MỤC TIÊU (Bắt buộc chia nhỏ thành đúng 4 đề mục con sau, KHÔNG ĐƯỢC THÊM dấu gạch ngang '-' ở trước số thứ tự):
                       1. Kiến thức
                       2. Năng lực (Bao gồm Năng lực chung và Năng lực đặc thù của môn học)
                       3. Năng lực số và AI (Thiết kế chi tiết mục tiêu học sinh ứng dụng thiết bị công nghệ và phần mềm mô phỏng, tra cứu thông tin bằng trợ lý AI)
                       4. Phẩm chất
                    II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU
                    III. TIẾN TRÌNH DẠY HỌC (Phân bổ lộ trình rõ ràng. Nếu chia làm nhiều tiết, bắt đầu bằng dòng chữ viết in hoa độc lập dạng 'TIẾT 1:', 'TIẾT 2:',...).
                       - Tiến trình gồm 4 Hoạt động lớn: 'HOẠT ĐỘNG 1: MỞ ĐẦU (KHỞI ĐỘNG)', 'HOẠT ĐỘNG 2: HÌNH THÀNH KIẾN THỨC MỚI', 'HOẠT ĐỘNG 3: LUYỆN TẬP', 'HOẠT ĐỘNG 4: VẬN DỤNG'.
                       - Nếu có chia các hoạt động nhỏ, đặt tên dạng: 'HOẠT ĐỘNG 1.1: ...', 'HOẠT ĐỘNG 2.1: ...'
                       - Mỗi hoạt động bắt buộc trình bày đủ 4 mục sau và KHÔNG ĐƯỢC THÊM dấu gạch ngang '-' ở trước chữ:
                         a) Mục tiêu:
                         b) Nội dung:
                         c) Sản phẩm:
                         d) Tổ chức thực hiện:
                         * TÍCH HỢP NĂNG LỰC SỐ THỰC TẾ: Trong phần d) Tổ chức thực hiện, viết kịch bản chi tiết giáo viên hướng dẫn học sinh ứng dụng CNTT hoặc dùng AI chatbot giải quyết bài học.
                    
                    YÊU CẦU ĐỊNH DẠNG CÔNG THỨC TOÁN, BIỂU BẢNG VÀ CÚ PHÁP:
                    - TUÂN THỦ TUYỆT ĐỐI BIỂU BẢNG GỐC: Đối với bất kỳ bảng số liệu thực hành hay so sánh nào có sẵn trong tài liệu nguồn, bạn BẮT BUỘC phải sao chép 100% đầy đủ toàn bộ số hàng, số cột và dữ liệu chữ/số bên trong, không được phép viết vắn tắt hay cắt xén thông tin. Thiết kế bảng Markdown bằng ký tự '|'.
                    - BỎ TOÀN BỘ các ký tự dấu sao kép '**' ở đầu và cuối các từ hoặc các mục.
                    - Toàn bộ danh sách nội dung thông thường dùng duy nhất ký tự gạch ngang '-' ở đầu dòng.
                    - CÔNG THỨC TOÁN HỌC KHỐI ĐỨNG: Khi xuất hiện công thức tính tốc độ (v = s/t) hoặc phân số, bạn BẮT BUỘC phải bọc trong thẻ định dạng sau để hệ thống dựng bảng phân số đứng: [frac: tử_số/mẫu_số] (Ví dụ: [frac: Quãng đường đi được/Thời gian đi quãng đường đó] hoặc [frac: s/t]).
                    - HÌNH ẢNH: Tại vị trí lý thuyết phù hợp, ghi một dòng độc lập là "[Hình ảnh minh họa]".
                    
                    CĂN CỨ BỔ SUNG KHÁC: {yeu_cau_khac}
                    
                    DỮ LIỆU FILE NGUỒN TÀI LIỆU THAM KHẢO:
                    {văn_bản_nguồn}
                    """
                    ket_qua_ai, model_used = run_ai_prompt_safe_func(prompt_yeu_cau)
                    st.session_state["ket_qua_giao_an"] = ket_qua_ai

        with col_btn1:
            st.write(""); st.write("")
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
                
                # NÂNG CẤP BỘ LƯU TRỮ KÉP (Local + Cloud)
                col_save_local, col_save_cloud = st.columns(2)
                
                with col_save_local:
                    if st.button("📥 Lưu vào Thư viện hệ thống (Tạm thời)", use_container_width=True):
                        if ten_bai:
                            st.session_state["lich_su_khbd"].append({"Tên bài": ten_bai, "Môn": mon_hoc, "Lớp": lop, "Nội dung": st.session_state["ket_qua_giao_an"], "Kho_anh": st.session_state["kho_anh_trich_xuat"]})
                            st.success("✅ Đã lưu giáo án vào Thư viện tạm thời thành công!")
                
                with col_save_cloud:
                    if st.button("☁️ Lưu lên Đám mây (Google Sheets)", type="primary", use_container_width=True):
                        if ten_bai:
                            try:
                                sheet = get_khbd_sheet()
                                ngay_luu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                # Lưu 5 cột: Tên bài, Môn, Lớp, Nội dung KHBD, Thời gian
                                sheet.append_row([str(ten_bai), str(mon_hoc), str(lop), str(st.session_state["ket_qua_giao_an"]), str(ngay_luu)])
                                st.toast("Đã lưu an toàn lên Google Sheets!", icon="✅")
                                st.success("✅ Đã đồng bộ an toàn lên Google Sheets!")
                            except Exception as e:
                                st.error(f"Lỗi khi lưu lên Đám mây: {e}")

            else:
                st.caption("Bài soạn sau khi khởi tạo bằng AI sẽ hiển thị tại đây...")

    # ==================== THẺ 2: LƯU TRỮ KẾ HOẠCH BÀI DẠY ĐÃ XD ====================
    with tab_luu_khbd:
        st.markdown("### 🗄️ THƯ VIỆN LƯU TRỮ KẾ HOẠCH BÀI DẠY ĐÃ XÂY DỰNG")
        if not st.session_state["lich_su_khbd"]:
            st.info("Chưa có bài soạn nào được lưu trong phiên này.")
        else:
            for idx, item in enumerate(st.session_state["lich_su_khbd"]):
                col_exp, col_del = st.columns([0.88, 0.12])
                with col_exp:
                    with st.expander(f"📚 {idx+1}. {item['Tên bài']} - Lớp {item['Lớp']}"):
                        st.markdown(item["Nội dung"])
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
