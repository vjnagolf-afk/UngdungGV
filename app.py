import streamlit as st
import io
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import google.generativeai as genai
from pypdf import PdfReader

# 1. CẤU HÌNH TRANG WEB STREAMLIT
st.set_page_config(
    page_title="EduAssist AI - Trợ Lý Giáo Viên", 
    page_icon="📚", 
    layout="wide"
)

# Giao diện tiêu đề chính
st.title("📚 EduAssist AI: Trợ Lý Số Hỗ Trợ Giáo Viên")
st.caption("Sản phẩm tham gia Cuộc thi AI for Life năm 2026 - Phường Tân Lập")
st.markdown("---")

# HÀM CHUYỂN ĐỔI VĂN BẢN THÀNH FILE WORD (.DOCX) ĐỂ TẢI VỀ
def export_to_docx(text_content, title_name, tac_gia="Lê Hồng Dưỡng", don_vi="THCS Nguyễn Chí Thanh"):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(1.18) 
        section.right_margin = Inches(0.59)

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(13)

    if don_vi:
        p_dv = doc.add_paragraph()
        p_dv.add_run(f"ĐƠN VỊ: {don_vi.upper()}").bold = True
        p_dv.paragraph_format.space_after = Pt(0)

    title = doc.add_paragraph()
    title_run = title.add_run(title_name.upper())
    title_run.bold = True
    title_run.font.size = Pt(15)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_before = Pt(12)
    title.paragraph_format.space_after = Pt(12)

    lines = text_content.split('\n')
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
            
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY 
        
        upper_line = cleaned_line.upper()
        if any(keyword in upper_line for keyword in ["KẾ HOẠCH BÀI DẠY", "MÔN HỌC:", "LỚP:", "BÀI HỌC:", "THỜI LƯỢNG:"]):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        if cleaned_line.startswith('#'):
            text = cleaned_line.lstrip('#').strip()
            run = p.add_run(text)
            run.bold = True
            run.font.size = Pt(14)
            if any(keyword in text.upper() for keyword in ["KẾ HOẠCH BÀI DẠY", "MÔN HỌC", "LỚP", "BÀI HỌC", "THỜI LƯỢNG"]):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif '**' in cleaned_line:
            parts = cleaned_line.split('**')
            for i, part in enumerate(parts):
                run = p.add_run(part)
                if i % 2 != 0: 
                    run.bold = True
        else:
            p.add_run(cleaned_line)

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# HÀM ĐỌC FILE WORD (.DOCX) TẢI LÊN
def read_uploaded_docx(uploaded_file):
    try:
        doc = Document(uploaded_file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text)
    except Exception as e:
        st.error(f"Lỗi khi đọc file Word: {e}")
        return ""

# HÀM ĐỌC FILE PDF (.PDF) TẢI LÊN
def read_uploaded_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        full_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
        return "\n".join(full_text)
    except Exception as e:
        st.error(f"Lỗi khi đọc file PDF: {e}")
        return ""


# 2. CẤU HÌNH NHẬP MÃ API KEY TRỰC TIẾP TRÊN GIAO DIỆN BÊN TRÁI
api_key_input = st.sidebar.text_input("Nhập khóa Gemini API Key của bạn (Bắt đầu bằng AQ... hoặc AIza...):", type="password")

if api_key_input:
    # Trở về hàm cấu hình chuẩn của Google để tránh lỗi cú pháp
    genai.configure(api_key=api_key_input)
    st.sidebar.success("🔑 Đã ghi nhận mã API Key của hệ thống!")
else:
    st.sidebar.warning("⚠️ Vui lòng dán mã API Key vào ô trên để kích hoạt.")


# 3. THANH MENU ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR)
st.sidebar.title("Chức năng hệ thống")
chức_năng = st.sidebar.radio(
    "Chọn một công cụ dưới đây:",
    ("1. Thiết kế KHBD thông minh", "2. Tạo ngân hàng câu hỏi")
)

# THÔNG TIN TÁC GIẢ DỰ THI
st.sidebar.markdown("---")
st.sidebar.subheader("✍️ Thông tin dự án")
tac_gia = st.sidebar.text_input("Họ và tên tác giả:", value="Lê Hồng Dưỡng")
don_vi = st.sidebar.text_input("Đơn vị công tác:", value="Trường THCS Nguyễn Chí Thanh")


# 4. XỬ LÝ LOGIC HIỂN THỊ CHỨC NĂNG
if chức_năng == "1. Thiết kế KHBD thông minh":
    st.header("📋 Công cụ thiết kế Kế hoạch bài dạy (KHBD) thông minh")
    st.info("💡 Hệ thống đã được lập trình để luôn luôn tích hợp sẵn năng lực số và giáo dục trí tuệ nhân tạo (AI) vào tiến trình bài học của thầy.")
    
    col1, col2 = st.columns(2)
    with col1:
        ten_bai = st.text_input("Tên bài học:", placeholder="Ví dụ: Thấu kính")
        lop = st.selectbox("Khối lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"], index=3)
    with col2:
        mon_hoc = st.text_input("Môn học:", value="Khoa học tự nhiên")
        thoi_luong = st.text_input("Thời lượng tiết học:", placeholder="Ví dụ: 1 tiết")
        
    st.markdown("##### 📁 Tài liệu gợi ý xây dựng KHBD (Ví dụ: File bài học trong Sách giáo khoa, tài liệu hướng dẫn)")
    uploaded_khbd_file = st.file_uploader(
        "Giáo viên có thể tải lên file PDF hoặc file Word chứa nội dung bài học để AI soạn bám sát tài liệu nguồn:", 
        type=["pdf", "docx"],
        key="khbd_uploader"
    )
    
    khbd_source_content = ""
    if uploaded_khbd_file is not None:
        if uploaded_khbd_file.name.endswith('.docx'):
            khbd_source_content = read_uploaded_docx(uploaded_khbd_file)
        elif uploaded_khbd_file.name.endswith('.pdf'):
            khbd_source_content = read_uploaded_pdf(uploaded_khbd_file)
            
        if khbd_source_content:
            st.success(f"📎 Đã trích xuất và đọc tài liệu học liệu thành công: {uploaded_khbd_file.name}")
            
    yeu_cau_them = st.text_area("Yêu cầu đặc biệt khác (nếu có):", placeholder="Ví dụ: Tập trung vào thảo luận nhóm và bài tập thực hành...")

    if st.button("🚀 Bắt đầu tạo KHBD"):
        if not api_key_input:
            st.error("Vui lòng nhập khóa API Key ở thanh bên trái trước khi thực hiện!")
        elif not ten_bai:
            st.warning("Vui lòng điền tên bài học.")
        else:
            with st.spinner("AI đang thiết lập tiến trình bài dạy, vui lòng đợi..."):
                prompt_giao_an = f"""
                Bạn là một giáo viên THCS và là chuyên gia sư phạm Việt Nam. Hãy lập một kế hoạch bài dạy (KHBD) hoàn chỉnh cho bài học sau:
                - Tên bài học: {ten_bai}
                - Môn học: {mon_hoc}
                - Khối lớp: {lop}
                - Thời lượng: {thoi_luong}
                - Yêu cầu bổ sung từ giáo viên: {yeu_cau_them}
                """
                
                if khbd_source_content:
                    prompt_giao_an += f"\n- BẮT BUỘC BÁM SÁT NỘI DUNG TÀI LIỆU/SGK ĐƯỢC CUNG CẤP SAU ĐÂY:\n\"\"\"{khbd_source_content}\"\"\"\n"
                
                prompt_giao_an += """
                YÊU CẦU BẮT BUỘC VỀ ĐỊNH DẠNG VĂN BẢN:
                Đầu văn bản phải ghi rõ các dòng thông tin sau theo cấu trúc (vui lòng viết hoa đúng cụm từ khóa):
                KẾ HOẠCH BÀI DẠY
                MÔN HỌC: [Tên môn học] - [Khối lớp]
                BÀI HỌC: [Tên bài học]
                THỜI LƯỢ lượng]

                YÊU CẦU BẮT BUỘC VỀ NỘI DUNG "TỔ CHỨC THỰC HIỆN":
                Trong các hoạt động học của tiến trình dạy học, tại mục "Tổ chức thực hiện", bạn bắt buộc phải trình bày chi tiết, cụ thể các bước tổ chức hoạt động học cho học sinh từ chuyển giao nhiệm vụ; theo dõi, hướng dẫn, kiểm tra, đánh giá quá trình và kết quả thực hiện nhiệm vụ thông qua sản phẩm học tập bao gồm đủ 4 bước sau:
                1. Chuyển giao nhiệm vụ: Nêu rõ lệnh gọi, câu hỏi, nhiệm vụ cụ thể giao cho học sinh (cá nhân/nhóm).
                2. Thực hiện nhiệm vụ: Mô tả cụ thể hoạt động của học sinh; hoạt động theo dõi, hướng dẫn, trợ giúp và kiểm tra của giáo viên trong quá trình học sinh làm việc.
                3. Báo cáo thảo luận: Mô tả cách thức tổ chức cho học sinh báo cáo kết quả và thảo luận tranh biện.
                4. Kết luận, nhận định: Giáo viên chốt kiến thức, thực hiện kiểm tra, đánh giá quá trình và kết quả thực hiện nhiệm vụ của học sinh thông qua các sản phẩm học tập cụ thể.

                Ngoài ra, hãy luôn tích hợp lồng ghép giáo dục năng lực số và nội dung giáo dục trí tuệ nhân tạo (AI) một cách khéo léo, phù hợp với lứa tuổi học sinh lớp đang chọn. Trình bày rõ ràng bằng tiếng Việt.
                """
                
                try:
                    # FIX TRIỆT ĐỂ: Sử dụng đường dẫn mô hình đầy đủ bao gồm định danh 'models/' 
                    # Điều này giúp các phiên bản API cũ tự động định tuyến chính xác mà không báo lỗi 404
                    model = genai.GenerativeModel('models/gemini-1.5-flash')
                    response = model.generate_content(prompt_giao_an)
                    
                    ai_text = response.text
                    st.success("✨ Đã tạo xong KHBD tích hợp Năng lực số & AI thành công!")
                    st.markdown(ai_text)
                    
                    docx_data = export_to_docx(ai_text, f"KHBD: {ten_bai}", tac_gia, don_vi)
                    
                    st.download_button(
                        label="📥 Tải KHBD bản Word (.docx)",
                        data=docx_data,
                        file_name=f"KHBD_{ten_bai.replace(' ', '_')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception as e:
                    st.error(f"Có lỗi xảy ra khi kết nối máy chủ AI: {e}")

elif chức_năng == "2. Tạo ngân hàng câu hỏi":
    st.header("📝 Hệ thống khởi tạo câu hỏi trắc nghiệm và tự luận")
    st.write("Thầy có thể dán trực tiếp nội dung hoặc đính kèm file bản Word (.docx) hoặc file PDF (.pdf) chứa tài liệu nguồn bên dưới.")
    
    uploaded_file = st.file_uploader("📥 Đính kèm file kiến thức nguồn (Chấp nhận .docx hoặc .pdf):", type=["docx", "pdf"], key="bank_uploader")
    
    file_content = ""
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.docx'):
            file_content = read_uploaded_docx(uploaded_file)
        elif uploaded_file.name.endswith('.pdf'):
            file_content = read_uploaded_pdf(uploaded_file)
            
        if file_content:
            st.success(f"📎 Đã trích xuất nội dung thành công từ file: {uploaded_file.name}")
            
    tai_lieu = st.text_area(
        "Nội dung/Văn bản kiến thức nguồn:", 
        value=file_content, 
        height=200, 
        placeholder="Dán đoạn văn bản kiến thức hoặc nội dung file tải lên sẽ tự động xuất hiện ở đây..."
    )
    
    col_type, col_num = st.columns(2)
    with col_type:
        loai_cau_hoi = st.radio("Chọn định dạng câu hỏi cần tạo:", ("Câu hỏi Trắc nghiệm", "Câu hỏi Tự luận"))
    with col_num:
        so_luong = st.slider("Số lượng câu hỏi cần tạo:", min_value=1, max_value=20, value=5)
    
    if st.button("⚡ Tạo ngân hàng câu hỏi"):
        if not api_key_input:
            st.error("Vui lòng nhập khóa API Key ở thanh bên trái trước khi thực hiện!")
        elif not tai_lieu:
            st.warning("Vui lòng nhập nội dung hoặc đính kèm file tài liệu nguồn.")
        else:
            with st.spinner("AI đang phân tích dữ liệu nguồn và thiết lập bộ câu hỏi..."):
                if loai_cau_hoi == "Câu hỏi Trắc nghiệm":
                    prompt_cau_hoi = f"""
                    Dựa trên văn bản tài liệu được cung cấp dưới đây, hãy tạo ra {so_luong} câu hỏi TRẮC NGHIỆM.
                    Mỗi câu hỏi phải có 4 phương án lựa chọn (A, B, C, D) và chỉ có 1 đáp án đúng duy nhất.
                    Các câu hỏi phải phân tách rõ ràng theo các cấp độ nhận thức: Nhận biết, Thông hiểu, Vận dụng.
                    Sau danh sách câu hỏi, hãy tạo một phần riêng biệt hiển thị "BẢNG ĐÁP ÁN VÀ GIẢI THÍCH CHI TIẾT" cho từng câu.
                    """
                else:
                    prompt_cau_hoi = f"""
                    Dựa trên văn bản tài liệu được cung cấp dưới đây, hãy tạo ra {so_luong} câu hỏi TỰ LUẬN.
                    Sau danh sách câu hỏi, hãy thiết lập mục "HƯỚNG DẪN CHẤM VÀ Ý CHÍNH TRẢ LỜI CHI TIẾT" cho từng câu hỏi tự luận đó.
                    """
                
                prompt_toan_van = f"{prompt_cau_hoi}\n\nTài liệu nguồn:\n\"\"\"{tai_lieu}\"\"\""
                
                try:
                    # Đã đồng bộ thêm tiền tố định tuyến 'models/' vào trước mô hình ngân hàng câu hỏi
                    model = genai.GenerativeModel('models/gemini-1.5-flash')
                    response = model.generate_content(prompt_toan_van)
                    
                    ai_text = response.text
                    st.success(f"✨ Đã tạo xong bộ {loai_cau_hoi.lower()}!")
                    st.markdown(ai_text)
                    
                    docx_data = export_to_docx(ai_text, f"Ngân hàng {loai_cau_hoi.lower()}", tac_gia, don_vi)
                    
                    st.download_button(
                        label=f"📥 Tải bộ {loai_cau_hoi.lower()} bản Word (.docx)",
                        data=docx_data,
                        file_name=f"Ngan_hang_{loai_cau_hoi.replace(' ', '_')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception as e:
                    st.error(f"Có lỗi xảy ra khi kết nối máy chủ AI: {e}")
