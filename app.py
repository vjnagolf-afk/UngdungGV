import streamlit as st
import io
import requests
import json
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

# HÀM CHUYỂN ĐỔI VĂN BẢN THÀNH FILE WORD (.DOCX) ĐỂ TẢI VỀ
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

# HÀM ĐỌC NỘI DUNG TỪ FILE WORD (.DOCX) ĐƯỢC TẢI LÊN ỨNG DỤNG
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


# LỚP GIẢ LẬP GỌI API GEMINI QUA HTTP REQUESTS 
class CustomGeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def create_interaction(self, model, input_text, tools, generation_config):
        url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        
        # Cấu hình lại phần tools định dạng JSON thô chuẩn xác cho Google Search
        api_tools = []
        for t in tools:
            if t.get('type') == 'google_search':
                api_tools.append({'google_search': {}})
                
        payload = {
            "contents": [{"parts": [{"text": input_text}]}],
            "tools": api_tools,
            "generationConfig": {
                "temperature": generation_config.get('temperature', 1),
                "maxOutputTokens": generation_config.get('max_output_tokens', 65536),
                "topP": generation_config.get('top_p', 0.95),
                "thinkingConfig": {
                    "thinkingBudget": 1024 if generation_config.get('thinking_level') == 'high' else 0
                }
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            res_json = response.json()
            # Trích xuất dữ liệu an toàn từ cấu trúc JSON trả về
            try:
                return res_json['candidates'][0]['content']['parts'][0]['text']
            except KeyError:
                raise Exception(f"Không lấy được văn bản. Phản hồi thô từ Google: {res_json}")
        else:
            raise Exception(f"Lỗi từ máy chủ Google ({response.status_code}): {response.text}")


# 2. CẤU HÌNH NHẬP MÃ API KEY TRỰC TIẾP TRÊN GIAO DIỆN BÊN TRÁI
api_key_input = st.sidebar.text_input("Nhập khóa Gemini API Key của bạn (Bắt đầu bằng AQ... hoặc AIza...):", type="password")

client = None
if api_key_input:
    client = CustomGeminiClient(api_key=api_key_input)
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
st.sidebar.subheader("✍️ Thông tin tác giả dự thi")
tac_gia = st.sidebar.text_input("Họ và tên tác giả:", value="Lê Hồng Dưỡng")
don_vi = st.sidebar.text_input("Đơn vị công tác:", value="Trường THCS Nguyễn Chí Thanh")


# CẤU HÌNH THAM SỐ GỐC CỦA THẦY
tools = [{'type': 'google_search'}]
generation_config = {
    'temperature': 1,
    'max_output_tokens': 65536,
    'top_p': 0.95,
    'thinking_level': 'high',
}


# 4. XỬ LÝ LOGIC HIỂN THỊ CHỨC NĂNG
if chức_năng == "1. Thiết kế KHBD thông minh":
    st.header("📋 Công cụ thiết kế Kế hoạch bài dạy (KHBD) thông minh")
    st.info("💡 Hệ thống đã được lập trình để luôn luôn tích hợp sẵn năng lực số và giáo dục trí tuệ nhân tạo (AI) vào tiến trình bài học của thầy.")
    
    col1, col2 = st.columns(2)
    with col1:
        ten_bai = st.text_input("Tên bài học:", placeholder="Ví dụ: Thấu kính")
        lop = st.selectbox("Khối lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"], index=3) # Mặc định chọn Lớp 9
    with col2:
        mon_hoc = st.text_input("Môn học:", value="Khoa học tự nhiên")
        thoi_luong = st.text_input("Thời lượng tiết học:", placeholder="Ví dụ: 1 tiết")
        
    yeu_cau_them = st.text_area("Yêu cầu đặc biệt khác (nếu có):", placeholder="Ví dụ: Tập trung vào thảo luận nhóm và bài tập thực hành...")

    if st.button("🚀 Bắt đầu tạo KHBD"):
        if not client:
            st.error("Vui lòng nhập khóa API Key ở thanh bên trái trước khi thực hiện!")
        elif not ten_bai:
            st.warning("Vui lòng điền tên bài học.")
        else:
            with st.spinner("AI đang thiết lập tiến trình bài dạy, vui lòng đợi..."):
                prompt_giao_an = f"""
                Bạn là một giáo viên THCS và là chuyên gia sư phạm đi đầu trong đổi mới sáng tạo, chuyển đổi số giáo dục tại Việt Nam. Hãy lập một kế hoạch bài dạy (KHBD) hoàn chỉnh cho bài học sau:
                - Tên bài học: {ten_bai}
                - Môn học: {mon_hoc}
                - Khối lớp: {lop}
                - Thời lượng: {thoi_luong}
                - Yêu cầu bổ sung từ giáo viên: {yeu_cau_them}
                
                YÊU CẦU BẮT BUỘC: 
                Trong kế hoạch bài dạy này, bạn PHẢI tích hợp lồng ghép giáo dục năng lực số (sử dụng thiết bị công nghệ, phần mềm mô phỏng, tra cứu số...) và nội dung giáo dục trí tuệ nhân tạo (AI) một cách phù hợp với lứa tuổi học sinh.
                
                Cấu trúc giáo án tuân thủ quy định hành chính chuẩn giáo dục. Trình bày rõ ràng bằng tiếng Việt.
                """
                
                try:
                    # SỬA LỖI: Cập nhật tên định danh chính xác model sang 'models/gemini-1.5-flash-latest'
                    ai_text = client.create_interaction(
                        model='models/gemini-1.5-flash-latest', 
                        input_text=prompt_giao_an,
                        tools=tools,
                        generation_config=generation_config
                    )
                    
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
    st.write("Thầy có thể dán trực tiếp nội dung hoặc đính kèm file bản Word (.docx) chứa tài liệu nguồn bên dưới.")
    
    uploaded_file = st.file_uploader("📥 Đính kèm file Word (.docx) chứa kiến thức nguồn (Tùy chọn):", type=["docx"])
    
    file_content = ""
    if uploaded_file is not None:
        file_content = read_uploaded_docx(uploaded_file)
        if file_content:
            st.success(f"📎 Đã đọc nội dung thành công từ file: {uploaded_file.name}")
            
    tai_lieu = st.text_area(
        "Nội dung/Văn bản kiến thức nguồn:", 
        value=file_content, 
        height=200, 
        placeholder="Dán đoạn văn bản kiến thức hoặc nội dung file Word sẽ tự động xuất hiện ở đây sau khi tải lên..."
    )
    
    col_type, col_num = st.columns(2)
    with col_type:
        loai_cau_hoi = st.radio("Chọn định dạng câu hỏi cần tạo:", ("Câu hỏi Trắc nghiệm", "Câu hỏi Tự luận"))
    with col_num:
        so_luong = st.slider("Số lượng câu hỏi cần tạo:", min_value=1, max_value=20, value=5)
    
    if st.button("⚡ Tạo ngân hàng câu hỏi"):
        if not client:
            st.error("Vui lòng nhập khóa API Key ở thanh bên trái trước khi thực hiện!")
        elif not tai_lieu:
            st.warning("Vui lòng nhập nội dung hoặc đính kèm file Word chứa tài liệu nguồn.")
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
                    # SỬA LỖI: Cập nhật tên định danh chính xác model sang 'models/gemini-1.5-flash-latest'
                    ai_text = client.create_interaction(
                        model='models/gemini-1.5-flash-latest',
                        input_text=prompt_toan_van,
                        tools=tools,
                        generation_config=generation_config
                    )
                    
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
