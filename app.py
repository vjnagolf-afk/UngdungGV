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


# LỚP GIẢ LẬP CLIENT GỌI API GEMINI DIRECT
class CustomGeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def create_interaction(self, model, input_text, tools, generation_config):
        # SỬA LỖI: URL truyền trực tiếp model truyền vào đã bao gồm tiền tố models/
        url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={self.api_key}"
        
        headers = {'Content-Type': 'application/json'}
        
        # Chuyển đổi cấu hình tools sang định dạng JSON API tương thích
        api_tools = []
        for t in tools:
            if t.get('type') == 'google_search':
                api_tools.append({'google_search': {}})
                
        # Thiết lập dữ liệu payload gửi lên Google
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
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            raise Exception(f"Lỗi từ máy chủ Google ({response.status_code}): {response.text}")


# 2. CẤU HÌNH NHẬP MÃ API KEY TRỰC TIẾP TRÊN GIAO DIỆN
api_key_input = st.sidebar.text_input("Nhập khóa Gemini API Key của bạn (Dán mã AQ...):", type="password")

client = None
if api_key_input:
    client = CustomGeminiClient(api_key=api_key_input)
    st.sidebar.success("🔑 Đã cấu hình hệ thống thành công!")
else:
    st.sidebar.warning("⚠️ Vui lòng dán toàn bộ mã API Key vào ô trên để sử dụng.")


# 3. THANH MENU ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR)
st.sidebar.title("Chức năng hệ thống")
chức_năng = st.sidebar.radio(
    "Choose a tool bên dưới:",
    ("1. Design KHBD information", "2. Tạo câu hỏi ngân hàng")
)

# THÔNG TIN TÁC GIẢ CỐ ĐỊNH Ở THANH BÊN
st.sidebar.markdown("---")
st.sidebar.subheader("✍️ Thông tin dự án")
tac_gia = st
