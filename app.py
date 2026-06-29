import streamlit as st
import google.generativeai as genai
import io
from docx import Document
from docx.shared import Pt, Inches

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

# HÀM CHUYỂN ĐỔI VĂN BẢN THÀNH FILE WORD (.DOCX) CHUYÊN NGHIỆP
def export_to_docx(text_content, title_name, tac_gia="Lê Hồng Dưỡng", don_vi="THCS Nguyễn Chí Thanh"):
    doc = Document()
    
    # Định dạng lề trang chuẩn hành chính (Top, Bottom, Left, Right = 2cm)
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(1.18) 
        section.right_margin = Inches(0.59)

    # Cấu hình font chữ chuẩn Times New Roman
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(13)

    # Nếu có thông tin đơn vị công tác, chèn vào góc trên bên trái
    if don_vi:
        p_dv = doc.add_paragraph()
        p_dv.add_run(f"ĐƠN VỊ: {don_vi.upper()}").bold = True
        p_dv.paragraph_format.space_after = Pt(0)

    # Thêm tiêu đề lớn bài học (Căn giữa)
    title = doc.add_paragraph()
    title_run = title.add_run(title_name.upper())
    title_run.bold = True
    title_run.font.size = Pt(15)
    title.alignment = 1 # Căn giữa
    title.paragraph_format.space_before = Pt(12)
    title.paragraph_format.space_after = Pt(6)

    # Nếu có thông tin tác giả, chèn vào ngay dưới tiêu đề bài học
    if tac_gia:
        p_tg = doc.add_paragraph()
        run_tg = p_tg.add_run(f"Giáo viên thực hiện: {tac_gia}")
        run_tg.italic = True
        p_tg.alignment = 1 # Căn giữa
        p_tg.paragraph_format.space_after = Pt(18)

    # Duyệt từng dòng văn bản từ AI để đưa vào file Word
    lines = text_content.split('\n')
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
            
        p = doc.add_paragraph()
        
        # Xử lý các tiêu đề lớn dạng # hoặc ## hoặc ### từ Markdown
        if cleaned_line.startswith('#'):
            text = cleaned_line.lstrip('#').strip()
            run = p.add_run(text)
            run.bold = True
            run.font.size = Pt(14)
        # Xử lý các dòng có chữ in đậm dạng **văn bản**
        elif '**' in cleaned_line:
            parts = cleaned_line.split('**')
            for i, part in enumerate(parts):
                run = p.add_run(part)
                if i % 2 != 0: 
                    run.bold = True
        else:
            p.add_run(cleaned_line)

    # Lưu file vào bộ nhớ đệm để Streamlit tải về
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# 2. CẤU HÌNH KẾT NỐI API VỚI MẬT KHẨU NGẮN GỌN
MAT_KHAU_KICH_HOAT = "KHTN2026"  
API_KEY_CUA_BAN = "AQ.Ab8RN6Kl5BU49xIqRYVbgD-elWKreXPLWpJyQ0PCZqeu59iLQQ" 

# Hiển thị ô nhập mật khẩu ngắn gọn trên giao diện
mat_khau_nhap = st.sidebar.text_input("Nhập Mật khẩu kích hoạt ứng dụng:", type="password")

client = None
if mat_khau_nhap:
    if mat_khau_nhap == MAT_KHAU_KICH_HOAT:
        try:
            genai.configure(api_key=API_KEY_CUA_BAN)
            client = "CONNECTED" # Biến đánh dấu kết nối thành công
            st.sidebar.success("🔑 Đã kích hoạt ứng dụng thành công!")
        except Exception as e:
            st.sidebar.error(f"Lỗi cấu hình hệ thống: {e}")
    else:
        st.sidebar.error("❌ Mật khẩu kích hoạt không chính xác!")
else:
    st.sidebar.warning("⚠️ Vui lòng nhập mật khẩu ở trên để sử dụng các tính năng AI.")

# 3. THANH MENU ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR)
st.sidebar.title("Chức năng hệ thống")
chức_năng = st.sidebar.radio(
    "Chọn một công cụ dưới đây:",
    ("1. Thiết kế giáo án thông minh", "2. Tạo ngân hàng câu hỏi")
)

# THÔNG TIN TÁC GIẢ CỐ ĐỊNH Ở THANH BÊN
st.sidebar.markdown("---")
st.sidebar.subheader("✍️ Thông tin tác giả dự thi")
tac_gia = st.sidebar.text_input("Họ và tên tác giả:", placeholder="Ví dụ: Nguyễn Văn A")
don_vi = st.sidebar.text_input("Đơn vị công tác:", placeholder="Ví dụ: Trường THCS...")

# 4. XỬ LÝ LOGIC CHO TỪNG TÍNH NĂNG
if chức_năng == "1. Thiết kế giáo án thông minh":
    st.header("📋 Công cụ thiết kế giáo án tự động")
    st.write("Điền các thông tin cơ bản dưới đây để AI tự động soạn thảo khung giáo án chuẩn.")
    
    col1, col2 = st.columns(2)
    with col1:
        ten_bai = st.text_input("Tên bài học:", placeholder="Ví dụ: Lăng kính")
        lop = st.selectbox("Khối lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"])
    with col2:
        mon_hoc = st.text_input("Môn học:", placeholder="Ví dụ: Khoa học tự nhiên")
        thoi_luong = st.text_input("Thời lượng tiết học:", placeholder="Ví dụ: 2 tiết (90 phút)")
        
    yeu_cau_them = st.text_area("Yêu cầu đặc biệt (nếu có):", placeholder="Ví dụ: Tập trung vào thảo luận nhóm và bài tập thực hành...")

    if st.button("🚀 Bắt đầu tạo giáo án"):
        if not client:
            st.error("Vui lòng nhập mật khẩu chính xác ở thanh bên trái trước khi thực hiện!")
        elif not ten_bai:
            st.warning("Vui lòng điền tên bài học.")
        else:
            with st.spinner("AI đang nghiên cứu và soạn thảo giáo án, vui lòng đợi trong giây lát..."):
                prompt_giao_an = f"""
                Bạn là một giáo viên THCS và là chuyên gia sư phạm hàng đầu tại Việt Nam. Hãy lập một kế hoạch bài dạy (giáo án) hoàn chỉnh cho bài học sau:
                - Tên bài học: {ten_bai}
                - Môn học: {mon_hoc}
                - Khối lớp: {lop}
                - Thời lượng: {thoi_luong}
                - Yêu cầu bổ sung: {yeu_cau_them}
                
                Yêu cầu cấu trúc giáo án phải tuân thủ nghiêm ngặt quy định chuẩn giáo dục gồm các mục:
                I. Mục tiêu bài học (Kiến thức, Năng lực đặc thù Khoa học tự nhiên, Năng lực chung, Phẩm chất)
                II. Thiết bị dạy học và học liệu
                III. Tiến trình dạy học (Gồm 4 hoạt động: Khởi động; Hình thành kiến thức; Luyện tập; Vận dụng). Mỗi hoạt động cần nêu rõ Mục tiêu, Nội dung, Sản phẩm và Tổ chức thực hiện.
                Trình bày rõ ràng bằng tiếng Việt, phân tách các mục bằng tiêu đề rõ ràng.
                """
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt_giao_an)
                    st.success("✨ Đã tạo xong giáo án thành công!")
                    st.markdown(response.text)
                    
                    # Tạo file Word tự động từ kết quả của AI kèm thông tin tác giả, đơn vị
                    docx_data = export_to_docx(response.text, f"Kế hoạch bài dạy: {ten_bai}", tac_gia, don_vi)
                    
                    # Nút bấm tải file Word (.docx) chuyên nghiệp
                    st.download_button(
                        label="📥 Tải giáo án bản Word (.docx)",
                        data=docx_data,
                        file_name=f"Giao_an_{ten_bai.replace(' ', '_')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception as e:
                    st.error(f"Có lỗi xảy ra khi gọi AI: {e}")

elif chức_năng == "2. Tạo ngân hàng câu hỏi":
    st.header("📝 Hệ thống khởi tạo câu hỏi trắc nghiệm")
    st.write("Dán nội dung tài liệu hoặc kiến thức cốt lõi vào ô dưới đây để AI tự động thiết kế bộ câu hỏi.")
    
    tai_lieu = st.text_area("Nội dung/Văn bản kiến thức nguồn:", height=250, placeholder="Dán đoạn văn bản kiến thức vào đây...")
    so_luong = st.slider("Số lượng câu hỏi trắc nghiệm cần tạo:", min_value=3, max_value=20, value=5)
    
    if st.button("⚡ Tạo ngân hàng câu hỏi"):
        if not client:
            st.error("Vui lòng nhập mật khẩu chính xác ở thanh bên trái trước khi thực hiện!")
        elif not tai_lieu:
            st.warning("Vui lòng nhập nội dung tài liệu nguồn.")
        else:
            with st.spinner("AI đang phân tích dữ liệu và thiết lập câu hỏi..."):
                prompt_cau_hoi = f"""
                Dựa trên văn bản tài liệu được cung cấp dưới đây, hãy tạo ra {so_luong} câu hỏi trắc nghiệm.
                Mỗi câu hỏi phải có 4 phương án lựa chọn (A, B, C, D) và chỉ có 1 đáp án đúng duy nhất.
                Các câu hỏi phải phân tách rõ ràng theo các cấp độ nhận thức: Nhận biết, Thông hiểu, Vận dụng.
                Sau danh sách câu hỏi, hãy tạo một phần riêng biệt hiển thị "BẢNG ĐÁP ÁN VÀ GIẢI THÍCH CHI TIẾT" cho từng câu.
                
                Tài liệu nguồn:
                \"\"\"{tai_lieu}\"\"\"
                """
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt_cau_hoi)
                    st.success("✨ Đã tạo xong bộ câu hỏi trắc nghiệm!")
                    st.markdown(response.text)
                    
                    # Tạo file Word tự động cho bộ câu hỏi kèm thông tin tác giả, đơn vị
                    docx_data = export_to_docx(response.text, f"Ngân hàng câu hỏi trắc nghiệm", tac_gia, don_vi)
                    
                    st.download_button(
                        label="📥 Tải bộ câu hỏi bản Word (.docx)",
                        data=docx_data,
                        file_name="Ngan_hang_cau_hoi.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception as e:
                    st.error(f"Có lỗi xảy ra khi gọi AI: {e}")
