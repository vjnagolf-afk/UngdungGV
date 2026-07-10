# math_compiler.py
import io
import re
import numpy as np
import matplotlib.pyplot as plt
from docx.shared import Pt
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def generate_plot_stream(eq_str):
    """Vẽ đồ thị tự động dựa trên hàm số AI cung cấp"""
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

def convert_latex_to_omml(latex_str):
    """Biến đổi mã nguồn LaTeX thành Office Math XML của Word giúp hiển thị phân số, số mũ đẹp"""
    latex_str = latex_str.replace(r'\pi', 'π').replace(r'\infty', '∞').replace(r'\times', '×')
    
    # Chuẩn hóa tổng xích ma
    latex_str = re.sub(r'\\sum_\{([^}]+)\}\^\{([^}]+)\}', r'∑(chạy từ \1 đến \2)', latex_str)
    
    # Chuẩn hóa phân số \frac{}{}
    frac_pattern = re.compile(r'\\frac\{([^}]+)\}\{([^}]+)\}')
    while frac_pattern.search(latex_str):
        latex_str = frac_pattern.sub(r'(\1)/(\2)', latex_str)
        
    # Chuẩn hóa lũy thừa số mũ
    latex_str = re.sub(r'\^\{([^}]+)\}', r'^\1', latex_str)
    
    omml_xml = f'<w:p {nsdecls("w")}><m:oMathPara {nsdecls("m")}><m:oMath><m:r><m:t>{latex_str}</m:t></m:r></m:oMath></m:oMathPara></w:p>'
    try:
        return parse_xml(omml_xml)
    except:
        return None

def process_runs_with_math(paragraph, text):
    """Tách nhỏ đoạn text để nhúng khối toán và định dạng chữ thường đan xen"""
    parts = re.split(r'(\$\$.*?\{}|\$.*?\$)', text)
    for part in parts:
        if part.startswith('$'):
            math_content = part.replace('$$', '').replace('$', '')
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
                    if not s_part: continue
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
