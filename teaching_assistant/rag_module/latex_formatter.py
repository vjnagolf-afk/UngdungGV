import re

def process_science_formulas(raw_text: str) -> str:
    """
    Module trung gian nâng cao: Quét sạch các lỗi xuống dòng vô lý trong biểu thức toán,
    giúp các phân thức, dấu phép tính (=, -, +, \text) đứng liền mạch trên cùng một dòng.
    """
    if not raw_text:
        return ""

    text = str(raw_text)

    # 1. Khôi phục các ký tự xuống dòng và tab thô nếu có
    text = text.replace('\\n', '\n').replace('\\t', '\t')

    # 2. ĐẶC TRỊ LỖI BẺ DÒNG ĐẠI SỐ (Xóa xuống dòng xung quanh dấu phép tính và dấu bằng)
    # Loại bỏ các khoảng trắng và dấu xuống dòng đứng trước hoặc sau các dấu toán học cốt lõi
    # Xử lý cho dấu bằng (=)
    text = re.sub(r'\s*\n\s*=\s*\n\s*', r' = ', text)
    text = re.sub(r'=\s*\n\s*', r' = ', text)
    text = re.sub(r'\s*\n\s*=', r' = ', text)
    
    # Xử lý cho dấu trừ (-) và dấu cộng (+) khi nằm giữa các phân số
    text = re.sub(r'\s*\n\s*-\s*\n\s*', r' - ', text)
    text = re.sub(r'-\s*\n\s*', r' - ', text)
    text = re.sub(r'\s*\n\s*-', r' - ', text)
    
    text = re.sub(r'\s*\n\s*\+\s*\n\s*', r' + ', text)
    text = re.sub(r'\+\s*\n\s*', r' + ', text)
    text = re.sub(r'\s*\n\s*\+', r' + ', text)

    # Khử xuống dòng giữa chữ nối và phân số (Ví dụ: "ký hiệu là \n \frac" -> "ký hiệu là \frac")
    text = re.sub(r'(ký hiệu là|với phân thức đối của|cho phân thức)\s*\n\s*', r'\1 ', text)

    # 3. Tự động phát hiện và sửa lỗi OCR dính chữ (ví dụ: fracst -> \frac{s}{t})
    text = re.sub(r'\bfracst\b', r'\\frac{s}{t}', text)
    text = re.sub(r'\bfrac\s*s\s*t\b', r'\\frac{s}{t}', text)

    # 4. Đảm bảo các hàm văn bản tiếng Việt trong LaTeX được bọc qua \text{...} đúng chuẩn
    text = re.sub(r'\\text\s*([^\{][^\$\n]*)', r'\\text{\1}', text)

    # 5. GIẢI PHÁP ĐẶC TRỊ LỖI HIỂN THỊ TRÊN STREAMLIT:
    # Nhân đôi dấu gạch chéo ngược cho các lệnh toán học/khoa học phổ biến để không bị markdown nuốt mất.
    latex_keywords = [
        'frac', 'sqrt', 'alpha', 'beta', 'gamma', 'delta', 'pi', 'mu', 'rho', 'sigma', 'tau', 'omega',
        'times', 'div', 'pm', 'mp', 'le', 'ge', 'leq', 'geq', 'neq', 'approx', 'equiv', 'cdot',
        'text', 'right', 'left', 'sum', 'int', 'partial', 'nabla', 'degree', 'rightarrow', 'longrightarrow'
    ]
    
    for kw in latex_keywords:
        # Biến \keyword thành \\keyword một cách an toàn
        text = re.sub(r'\\(' + kw + r')\b', r'\\\\\1', text)

    return text
