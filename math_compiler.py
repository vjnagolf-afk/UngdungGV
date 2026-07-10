# math_compiler.py
import io
import re
import numpy as np
import matplotlib.pyplot as plt
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def generate_plot_stream(eq_str):
    fig, ax = plt.subplots(figsize=(5, 3.5))
    x = np.linspace(-10, 10, 400)
    safe_dict = {"x": x, "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan, "sqrt": np.sqrt}
    try:
        eq_str_py = eq_str.replace('^', '**')
        y = eval(eq_str_py, {"__builtins__": {}}, safe_dict)
        if isinstance(y, (int, float)):
            y = np.full_like(x, y)
        ax.plot(x, y, color='#1E40AF', linewidth=2.5)
        ax.axhline(0, color='black', linewidth=1.2)
        ax.axvline(0, color='black', linewidth=1.2)
        ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
        ax.set_ylim([-10, 10])
        ax.set_title(f"Đồ thị: y = {eq_str}", fontsize=10, pad=10)
    except:
        ax.text(0.5, 0.5, f"[Lỗi cú pháp vẽ đồ thị]", ha='center', va='center', color='red')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    plt.close(fig)
    return buf

def build_omml_fraction(num_str, den_str):
    """Tạo cấu trúc XML Math phân số chuẩn của Microsoft Word (m:f)"""
    return (
        f'<m:f>'
        f'<m:num><m:r><m:t>{num_str}</m:t></m:r></m:num>'
        f'<m:den><m:r><m:t>{den_str}</m:t></m:r></m:den>'
        f'</m:f>'
    )

def convert_latex_to_omml(latex_str):
    """Biến đổi mã nguồn LaTeX thành khối Office Math XML chồng tầng hoàn chỉnh"""
    latex_str = latex_str.strip()
    
    # Chuẩn hóa ký hiệu nhân, chia, vô cùng
    latex_str = latex_str.replace(r'\pi', 'π').replace(r'\infty', '∞').replace(r'\times', '×').replace(r'\cdot', '·')
    
    # Khử toàn bộ dấu ngoặc đơn dư thừa mà AI hay tạo quanh phân số
    latex_str = re.sub(r'\(\((.*?)\)/\((.*?)\)\)', r'(\1)/(\2)', latex_str)
    latex_str = re.sub(r'\((.*?)\)/\((.*?)\)', r'(\1)/(\2)', latex_str)

    # Thuật toán quét và dịch phân số dạng \frac{a}{b} hoặc (a)/(b) sang cấu trúc XML hình thái tầng đứng
    # Bước A: Dịch cấu trúc \frac{t}{s}
    frac_pattern = re.compile(r'\\frac\{([^}]+)\}\{([^}]+)\}')
    while frac_pattern.search(latex_str):
        match = frac_pattern.search(latex_str)
        xml_frac = build_omml_fraction(match.group(1), match.group(2))
        latex_str = latex_str.replace(match.group(0), xml_frac)
        
    # Bước B: Dịch cấu trúc chữ thường dạng phân số phẳng (s)/(t) hoặc s/t sang cấu trúc tầng đứng
    plain_frac_pattern = re.compile(r'([a-zA-Z0-9_().+*-]+)/([a-zA-Z0-9_().+*-]+)')
    while plain_frac_pattern.search(latex_str):
        match = plain_frac_pattern.search(latex_str)
        # Bỏ dấu ngoặc đơn bao quanh tử và mẫu nếu có
        num = match.group(1).strip('()')
        den = match.group(2).strip('()')
        # Tránh dịch nhầm đường dẫn hoặc định dạng text không phải toán
        if '<m:f>' in match.group(0): 
            break
        xml_frac = build_omml_fraction(num, den)
        latex_str = latex_str.replace(match.group(0), xml_frac)

    # Chuẩn hóa lũy thừa số mũ
    latex_str = re.sub(r'\^\{([^}]+)\}', r'^\1', latex_str)
    
    # Bao bọc bằng thẻ m:oMath cốt lõi
    omml_xml = f'<m:oMath {nsdecls("m")}>'
    
    # Kiểm tra xem chuỗi đã được dịch sang cấu trúc phân số XML m:f chưa
    if '<m:f>' in latex_str:
        omml_xml += latex_str
    else:
        omml_xml += f'<m:r><m:t>{latex_str}</m:t></m:r>'
        
    omml_xml += '</m:oMath>'
    try:
        return parse_xml(omml_xml)
    except:
        return None

def process_runs_with_math(paragraph, text):
    """Phân tách chuỗi đan xen giữa chữ thường và công thức đô-la để nạp khối văn bản"""
    parts = re.split(r'(\$\$[\s\S]*?\$\$|\$[\s\S]*?\$)', text)
    for part in parts:
        if not part:
            continue
        if part.startswith('$'):
            math_content = part.replace('$$', '').replace('$', '').strip()
            if math_content:
                math_element = convert_latex_to_omml(math_content)
                if math_element is not None:
                    paragraph._p.append(math_element)
                else:
                    run = paragraph.add_run(part)
                    run.font.name = 'Times New Roman'
        else:
            bold_parts = part.split('**')
            for i, b_part in enumerate(bold_parts):
                is_bold = (i % 2 != 0)
                sub_sup_parts = re.split(r'(<sub>.*?</sub>|<sup>.*?</sup>)', b_part)
                for s_part in sub_sup_parts:
                    if not s_part: 
                        continue
                    if s_part.startswith('<sub>') and s_part.endswith('</sub>'):
                        run = paragraph.add_run(s_part[5:-6])
                        run.bold = is_bold
                        run.font.subscript = True
                    elif s_part.startswith('<sup>') and s_part.endswith('</sup>'):
                        run = paragraph.add_run(s_part[5:-6])
                        run.bold = is_bold
                        run.font.superscript = True
                    else:
                        run = paragraph.add_run(s_part)
                        run.bold = is_bold
                        run.font.name = 'Times New Roman'
