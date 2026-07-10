import io
import re
import numpy as np
import matplotlib.pyplot as plt
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Pt

GREEK = {
    r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\delta': 'δ', r'\epsilon': 'ε', r'\varepsilon': 'ε',
    r'\zeta': 'ζ', r'\eta': 'η', r'\theta': 'θ', r'\vartheta': 'ϑ', r'\iota': 'ι', r'\kappa': 'κ',
    r'\lambda': 'λ', r'\mu': 'μ', r'\nu': 'ν', r'\xi': 'ξ', r'\pi': 'π',
    r'\rho': 'ρ', r'\sigma': 'σ', r'\tau': 'τ', r'\upsilon': 'υ', r'\phi': 'φ', r'\varphi': 'ϕ',
    r'\chi': 'χ', r'\psi': 'ψ', r'\omega': 'ω',
    r'\Delta': 'Δ', r'\Gamma': 'Γ', r'\Theta': 'Θ', r'\Lambda': 'Λ', r'\Pi': 'Π',
    r'\Sigma': 'Σ', r'\Phi': 'Φ', r'\Psi': 'Ψ', r'\Omega': 'Ω'
}

SYMBOLS = {
    r'\infty': '∞', r'\rightarrow': '→', r'\leftarrow': '←', r'\Rightarrow': '⇒',
    r'\Leftarrow': '⇐', r'\leftrightarrow': '↔', r'\Leftrightarrow': '⇔',
    r'\approx': '≈', r'\neq': '≠', r'\leq': '≤', r'\geq': '≥', r'\times': '×',
    r'\cdot': '·', r'\pm': '±', r'\mp': '∓', r'\circ': '°', r'\partial': '∂',
    r'\nabla': '∇', r'\forall': '∀', r'\exists': '∃', r'\in': '∈', r'\notin': '∉',
    r'\subset': '⊂', r'\supset': '⊃', r'\cup': '∪', r'\cap': '∩', r'\equiv': '≡',
    r'\sim': '∼', r'\propto': '∝', r'\angle': '∠', r'\parallel': '∥', r'\perp': '⊥',
    r'\int': '∫', r'\sum': '∑'
}

TAG_MAP = {
    'Ⓕ': '<m:f>', 'ⓕ': '</m:f>',
    'Ⓝ': '<m:num>', 'ⓝ': '</m:num>',
    'Ⓓ': '<m:den>', 'ⓓ': '</m:den>',
    'Ⓠ': '<m:rad><m:radPr><m:deg m:val=""/></m:radPr>', 'ⓠ': '</m:rad>',
    'Ⓔ': '<m:e>', 'ⓔ': '</m:e>',
    'Ⓑ': '<m:sSub>', 'ⓑ': '</m:sSub>',
    'Ⓟ': '<m:sSup>', 'ⓟ': '</m:sSup>',
    'Ⓩ': '<m:sSubSup>', 'ⓩ': '</m:sSubSup>',
    'Ⓢ': '<m:sub>', 'ⓢ': '</m:sub>',
    'Ⓤ': '<m:sup>', 'ⓤ': '</m:sup>',
    'Ⓧ': '<m:nary><m:naryPr><m:chr m:val="∫"/><m:limLoc m:val="subSup"/></m:naryPr>', 'ⓧ': '</m:nary>',
    'Ⓨ': '<m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr>', 'ⓨ': '</m:nary>',
    'Ⓥ': '<m:acc><m:accPr><m:chr m:val="&#x20D7;"/></m:accPr>', 'ⓥ': '</m:acc>',
    'Ⓜ': '<m:m><m:mPr><m:mcs><m:mc><m:mcPr><m:count m:val="10"/><m:mcJc m:val="c"/></m:mcPr></m:mc></m:mcs></m:mPr>', 'ⓜ': '</m:m>',
    'Ⓡ': '<m:mr>', 'ⓡ': '</m:mr>'
}

def convert_latex_to_omml(latex_str):
    latex_str = latex_str.strip().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Chuẩn hóa khoảng trắng gây lỗi của AI
    latex_str = latex_str.replace(r'\dfrac', r'\frac').replace(r'\limits', '')
    latex_str = re.sub(r'\\frac\s*\{\s*', r'\\frac{', latex_str)
    latex_str = re.sub(r'\}\s*\{\s*', r'}{', latex_str)
    latex_str = re.sub(r'_\s*\{\s*', r'_{', latex_str)
    latex_str = re.sub(r'\^\s*\{\s*', r'^{', latex_str)

    for k, v in GREEK.items(): latex_str = latex_str.replace(k, v)
    for k, v in SYMBOLS.items(): latex_str = latex_str.replace(k, v)
    latex_str = re.sub(r'\\(text|mathrm)\{([^{}]*)\}', r'\2', latex_str)

    def repl_matrix(m):
        res = 'Ⓜ'
        for row in m.group(1).split('\\\\'):
            res += 'Ⓡ'
            for col in row.split('&'): res += f'Ⓔ{col.strip()}ⓔ'
            res += 'ⓡ'
        return res + 'ⓜ'
    latex_str = re.sub(r'\\begin\{(?:p|b|v|V)?matrix\}(.*?)\\end\{(?:p|b|v|V)?matrix\}', repl_matrix, latex_str, flags=re.DOTALL)

    chars = r'a-zA-Z0-9_>\]/()ⒻⓕⓃⓝⒹⓓⓆⓠⒺⓔⒷⓑⓅⓟⓈⓢⓊⓤⓍⓧⓎⓨⓋⓥⓂⓜⓇⓡα-ωΑ-Ω∞=+\-.,'
    while True:
        prev = latex_str
        latex_str = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'ⒻⓃ\1ⓝⒹ\2ⓓⓕ', latex_str)
        latex_str = re.sub(r'\\sqrt\{([^{}]+)\}', r'ⓆⒺ\1ⓔⓠ', latex_str)
        latex_str = re.sub(r'\\vec\{([^{}]+)\}', r'ⓋⒺ\1ⓔⓥ', latex_str)
        latex_str = re.sub(r'(∫|∑)_\{([^{}]+)\}\^\{([^{}]+)\}', r'ⓍⒺ\1ⓔⓈ\2ⓢⓊ\3ⓤⓧ', latex_str)
        latex_str = re.sub(rf'([{chars}]+)_\{{([^{{}}]+)\}}\^\{{([^{{}}]+)\}}', r'ⓏⒺ\1ⓔⓈ\2ⓢⓊ\3ⓤⓩ', latex_str)
        latex_str = re.sub(rf'([{chars}]+)\^\{{([^{{}}]+)\}}_\{{([^{{}}]+)\}}', r'ⓏⒺ\1ⓔⓈ\3ⓢⓊ\2ⓤⓩ', latex_str)
        latex_str = re.sub(rf'([{chars}]+)_\{{([^{{}}]+)\}}', r'ⒷⒺ\1ⓔⓈ\2ⓢⓑ', latex_str)
        latex_str = re.sub(rf'([{chars}]+)_([a-zA-Z0-9])', r'ⒷⒺ\1ⓔⓈ\2ⓢⓑ', latex_str)
        latex_str = re.sub(rf'([{chars}]+)\^\{{([^{{}}]+)\}}', r'ⓅⒺ\1ⓔⓊ\2ⓤⓟ', latex_str)
        latex_str = re.sub(rf'([{chars}]+)\^([a-zA-Z0-9])', r'ⓅⒺ\1ⓔⓊ\2ⓤⓟ', latex_str)
        if latex_str == prev: break

    parts = re.split(f'([{"".join(TAG_MAP.keys())}])', latex_str)
    xml = f'<m:oMath {nsdecls("m")}>'
    RPR = '<m:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/><w:sz w:val="28"/><w:szCs w:val="28"/></m:rPr>'
    for p in parts:
        if p in TAG_MAP: xml += TAG_MAP[p]
        elif p.strip() or p == ' ': xml += f'<m:r>{RPR}<m:t>{p}</m:t></m:r>'
    xml += '</m:oMath>'
    
    try:
        return parse_xml(xml)
    except Exception:
        return None

def apply_unicode_chemistry(text):
    """ Tự động nhận dạng H2O -> H₂O, SO4^2- -> SO₄²⁻ cho văn bản thường (Safe Text) """
    def repl_chem(m):
        elem = m.group(1)
        sub = m.group(2).translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")) if m.group(2) else ""
        sup = m.group(3).translate(str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")) if m.group(3) else ""
        return elem + sub + sup
    ELEMENTS = r"(H|He|Li|Be|B|C|N|O|F|Ne|Na|Mg|Al|Si|P|S|Cl|Ar|K|Ca|Fe|Cu|Zn|Br|Ag|I|Ba|Pt|Au|Hg|Pb)"
    return re.sub(rf'\b({ELEMENTS})([0-9]+)?(?:\^([0-9]*[+-]))?', repl_chem, text)

def process_runs_with_math(paragraph, text):
    text_clean = text.strip()
    # Nhận diện TOÀN BỘ các loại phân tách Toán học LaTeX
    delimiter_pattern = r'(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|\$[\s\S]*?\$)'
    parts = re.split(delimiter_pattern, text_clean)
    
    for part in parts:
        if not part: continue
        
        is_math = False
        math_content = ""
        if part.startswith('$$') and part.endswith('$$'): math_content = part[2:-2].strip(); is_math = True
        elif part.startswith('\\[') and part.endswith('\\]'): math_content = part[2:-2].strip(); is_math = True
        elif part.startswith('\\(') and part.endswith('\\)'): math_content = part[2:-2].strip(); is_math = True
        elif part.startswith('$') and part.endswith('$'): math_content = part[1:-1].strip(); is_math = True

        if is_math and math_content:
            math_element = convert_latex_to_omml(math_content)
            if math_element is not None:
                paragraph._p.append(math_element)
            else:
                # Fallback an toàn nếu XML quá tải
                clean_text = math_content.replace(r'\frac', '').replace('{', '').replace('}', '')
                run = paragraph.add_run(clean_text)
                run.font.name = 'Times New Roman'; run.font.size = Pt(14); run.italic = True
        else:
            # Xử lý text thông thường & Auto-Chem
            chem_part = apply_unicode_chemistry(part)
            bold_parts = chem_part.split('**')
            for i, b_part in enumerate(bold_parts):
                is_bold = (i % 2 != 0)
                sub_sup_parts = re.split(r'(<sub>.*?</sub>|<sup>.*?</sup>)', b_part)
                for s_part in sub_sup_parts:
                    if not s_part: continue
                    run = paragraph.add_run()
                    run.bold = is_bold
                    run.font.name = 'Times New Roman'; run.font.size = Pt(14)
                    if s_part.startswith('<sub>') and s_part.endswith('</sub>'):
                        run.text = s_part[5:-6]
                        run.font.subscript = True
                    elif s_part.startswith('<sup>') and s_part.endswith('</sup>'):
                        run.text = s_part[5:-6]
                        run.font.superscript = True
                    else:
                        run.text = s_part

def generate_plot_stream(eq_str):
    fig, ax = plt.subplots(figsize=(5, 3.5))
    if eq_str.lower().strip() == 'scatter':
        ax.scatter(np.random.rand(50)*10, np.random.rand(50)*10, color='#1E40AF', alpha=0.7)
        ax.set_title("Đồ thị phân tán (Scatter)", fontsize=10, pad=10)
    else:
        x = np.linspace(-10, 10, 400)
        safe_dict = {"x": x, "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan, "log": np.log, "exp": np.exp, "pi": np.pi}
        try:
            eq_py = eq_str.lower().replace('y=', '').replace('y =', '').strip().replace('^', '**')
            eq_py = re.sub(r'(\d)(x)', r'\1*\2', eq_py)
            y = eval(eq_py, {"__builtins__": {}}, safe_dict)
            if isinstance(y, (int, float)): y = np.full_like(x, y)
            ax.plot(x, y, color='#1E40AF', linewidth=2.5)
            ax.axhline(0, color='black', linewidth=1.2)
            ax.axvline(0, color='black', linewidth=1.2)
        except:
            ax.text(0.5, 0.5, f"[Lỗi biểu thức]", ha='center', va='center', color='red')
        ax.set_title(f"Đồ thị: y = {eq_str.replace('y=','')}", fontsize=10, pad=10)

    ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    plt.close(fig)
    return buf
