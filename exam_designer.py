# exam_designer.py
import streamlit as st
import io
import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pypdf import PdfReader
import matplotlib.pyplot as plt
import numpy as np

def read_uploaded_docx(uploaded_file):
    try:
        doc = Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])
    except: return "Lỗi đọc file Word"

def read_uploaded_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    except: return "Lỗi đọc file PDF"

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
        ax.text(0.5, 0.5, f"[Không thể vẽ đồ thị: Sai cú pháp toán học]", ha='center', va='center', color='red')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    plt.close(fig)
    return buf

def export_to_docx_vietnam_standard(text_content, title_name, school_name="TRƯỜNG THCS NGUYỄN CHÍ THANH", group_name="TỔ KHOA HỌC TỰ NHIÊN - GDTC"):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(1.18)
        section.right_margin = Inches(0.59)
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(14)
    
    admin_table = doc.add_table(rows=1, cols=2)
    admin_table.autofit = False
    admin_table.columns[0].width = Inches(3.2)
    admin_table.columns[1].width = Inches(3.8)
    
    cell_l = admin_table.rows[0].cells[0]
    p_left = cell_l.paragraphs[0]
    p_left.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_left.add_run(f"{school_name.upper()}\n").bold = True
    p_left.add_run(f"{group_name.upper()}\n").bold = True
    p_left.add_run("Số: ..... /BB-TCM").font.size = Pt(11)
    
    cell_r = admin_table.rows[0].cells[1]
    p_right = cell_r.paragraphs[0]
    p_right.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_right.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n").bold = True
    p_right.add_run("Độc lập - Tự do - Hạnh phúc\n").bold = True
    p_right.add_run("***************").font.size = Pt(11)
    
    doc.add_paragraph()
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.add_run(title_name.upper()).bold = True
    
    in_table = False
    table_data = []
    
    def process_runs(paragraph, text):
        bold_parts = text.split('**')
        for i, b_part in enumerate(bold_parts):
            is_bold = (i % 2 != 0)
            sub_sup_parts = re.split(r'(<sub>.*?</sub>|<sup>.*?</sup>)', b_part)
            for part in sub_sup_parts:
                if not part: continue
                if part.startswith('<sub>') and part.endswith('</sub>'):
                    run = paragraph.add_run(part[5:-6]) 
                    run.bold = is_bold
                    run.font.subscript = True 
                elif part.startswith('<sup>') and part.endswith('</sup>'):
                    run = paragraph.add_run(part[5:-6]) 
                    run.bold = is_bold
                    run.font.superscript = True 
                else:
                    run = paragraph.add_run(part)
                    run.bold = is_bold

    def build_table():
        if not table_data: return
        cols = len(table_data[0])
        table = doc.add_table(rows=len(table_data), cols=cols)
        table.style = 'Table Grid'
        for r_idx, row in enumerate(table_data):
            for c_idx, cell_val in enumerate(row):
                if c_idx < cols:
                    cell = table.cell(r_idx, c_idx)
                    p = cell.paragraphs[0]
                    p.text = "" 
                    process_runs(p, cell_val.strip())
        doc.add_paragraph() 
        
    for line in text_content.split('\n'):
        cleaned_line = line.strip()
        if cleaned_line.startswith('|') and cleaned_line.endswith('|'):
            in_table = True
            row_data = [cell.strip() for cell in cleaned_line.split('|')[1:-1]]
            if all(re.match(r'^[-: ]+$', cell) for cell in row_data): continue
            table_data.append(row_data)
            continue
        if in_table:
            build_table()
            in_table = False
            table_data = []
        if not cleaned_line: continue
        if '[GRAPH:' in cleaned_line:
            match = re.search(r'\[GRAPH:\s*(.+?)\]', cleaned_line)
            if match:
                eq = match.group(1)
                img_stream = generate_plot_stream(eq)
                doc.add_picture(img_stream, width=Inches(3.5))
                last_paragraph = doc.paragraphs[-1]
                last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                continue 
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if cleaned_line.startswith('#'):
            process_runs(p, cleaned_line.replace('#', '').strip())
            for run in p.runs: run.bold = True
        else:
            process_runs(p, cleaned_line)
    if in_table: build_table()
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()
def render_exam_designer_section(api_key_input, run_ai_prompt_safe_func):
    st.markdown("""
    <style>
    .header-pink { background-color: #FCE4EC; color: #880E4F; padding: 10px; text-align: center; font-weight: bold; font-size: 16px; border-radius: 4px; margin-bottom: 15px;}
    .header-green { background-color: #E8F5E9; color: #1B5E20; padding: 10px; text-align: center; font-weight: bold; font-size: 16px; border-radius: 4px; margin-bottom: 15px;}
    .footer-red { color: #D32F2F; font-weight: bold; font-style: italic; font-size: 14px; text-align: center; margin-top: 30px; padding-top: 10px; border-top: 1px solid #ccc;}
    div[data-testid="stNumberInput"] label { display: none !important; } 
    div[data-testid="stTextInput"] label { display: none !important; } 
    div[data-testid="stSelectbox"] label { display: none !important; }
    div[data-testid="stTabs"] button { font-size: 22px !important; font-weight: 800 !important; color: #1E3A8A !important; }
    div[data-testid="stTabs"] button[aria-selected="true"] { color: #E11D48 !important; border-bottom-color: #E11D48 !important; }
    </style>
    """, unsafe_allow_html=True)

    if "db_de_kiem_tra" not in st.session_state: st.session_state["db_de_kiem_tra"] = []
    if "current_exam_designer_output" not in st.session_state: st.session_state["current_exam_designer_output"] = ""

    tab_thiet_ke, tab_kho_luu_tru = st.tabs(["📝 CHỨC NĂNG: TẠO ĐỀ KIỂM TRA AI", "📂 THƯ MỤC ĐỀ ĐÃ XÂY DỰNG"])
    
    with tab_thiet_ke:
        col_top1, col_top2 = st.columns([1, 1])
        with col_top1:
            c_lbl, c_sel = st.columns([1, 2])
            c_lbl.markdown("<div style='margin-top: 8px;'>Hình thức đề:</div>", unsafe_allow_html=True)
            hinh_thuc = c_sel.selectbox("Hinh_thuc", ["Trắc nghiệm kết hợp tự luận", "100% Trắc nghiệm", "100% Tự luận"])
            
            c_lbl2, c_txt2 = st.columns([1, 2])
            c_lbl2.markdown("<div style='margin-top: 8px;'>Môn học:</div>", unsafe_allow_html=True)
            mon_de = c_txt2.text_input("Mon", value="Khoa học tự nhiên")
            
            c_lbl3, c_sel3 = st.columns([1, 2])
            c_lbl3.markdown("<div style='margin-top: 8px;'>Khối lớp:</div>", unsafe_allow_html=True)
            khoi_de = c_sel3.selectbox("Khoi", ["Khối 6", "Khối 7", "Khối 8", "Khối 9"], index=1)
            
            c_lbl4, c_txt4 = st.columns([1, 2])
            c_lbl4.markdown("<div style='margin-top: 8px;'>Thời gian làm bài:</div>", unsafe_allow_html=True)
            tg_de = c_txt4.text_input("Thoi_gian", value="45 phút")

            st.markdown("**📂 Đính kèm tài liệu ma trận hoặc nội dung mẫu (Tùy chọn):**")
            tai_lieu_dinh_kem = st.file_uploader("Tải tài liệu nền (.docx, .pdf)", type=["docx", "pdf"], key="file_de_tai_lieu")

        with col_top2:
            # 🌟 KHỞI TẠO BỘ ĐẾM SỐ CÂU THÀNH PHẦN ĐỂ TỰ ĐỘNG TÍNH TOÁN
            st.markdown("**📊 Cấu hình số câu hỏi và ma trận điểm dòng:**")
            
            # --- 1. PHẦN TRẮC NGHIỆM ---
            st.markdown("🔹 **Phần I. Trắc nghiệm nhiều lựa chọn**")
            col_sc1, col_sc2 = st.columns([1, 1])
            num_tn_input = col_sc1.number_input("Số câu TN:", min_value=0, max_value=50, value=12, step=1, key="num_tn_raw")
            # Tự động sinh danh sách nhập điểm từng câu nếu cần, hoặc gán điểm mặc định để cộng dồn lên ô tổng
            pt_tn_calc = num_tn_input * 0.25 # Mặc định 0.25đ/câu hoặc cho nhập trực tiếp
            col_sc2.markdown(f"<div style='margin-top: 6px; padding: 6px; background:#F3F4F6; border-radius:4px; font-weight:bold;'>Tổng điểm TN: {pt_tn_calc}đ</div>", unsafe_allow_html=True)
            
            # --- 2. PHẦN TỰ LUẬN TỰ SINH CÂU THÀNH PHẦN ---
            st.markdown("🔹 **Phần II. Tự luận (Tự động sinh ô điểm con)**")
            num_tl_input = st.number_input("Nhập tổng số câu tự luận:", min_value=0, max_value=20, value=3, step=1, key="num_tl_raw")
            
            # Tự động lập lịch sinh ô điểm con dựa theo số câu nhập vào
            tl_scores = []
            if num_tl_input > 0:
                st.caption("Nhập số điểm chi tiết cho từng câu tự luận phía dưới:")
                # Sinh số lượng cột nằm ngang hoặc hàng dọc tương ứng
                cols_tl = st.columns(min(num_tl_input, 4))
                for i in range(num_tl_input):
                    col_target = cols_tl[i % 4]
                    score_cell = col_target.number_input(f"Câu {i+1} (Điểm):", min_value=0.0, max_value=10.0, value=1.0, step=0.5, key=f"score_tl_sub_{i}")
                    tl_scores.append(score_cell)
            pt_tl_total = sum(tl_scores)
            st.markdown(f"<div style='width:100%; padding: 6px; background:#EEF2F6; border-radius:4px; font-weight:bold; color:#1E3A8A;'>🔥 Tổng điểm Tự luận: {pt_tl_total}đ</div>", unsafe_allow_html=True)

            # --- 3. ĐIỀN KHUYẾT VÀ TRẢ LỜI NGẮN ---
            st.markdown("🔹 **Phần III. Điền khuyết & Trả lời ngắn**")
            col_sub1, col_sub2 = st.columns(2)
            num_khuyet = col_sub1.number_input("Số câu điền khuyết:", min_value=0, max_value=20, value=2, step=1)
            pt_khuyet = col_sub2.number_input("Điểm điền khuyết:", min_value=0.0, max_value=10.0, value=1.0, step=0.25)
            
            num_ngan = col_sub1.number_input("Số câu trả lời ngắn:", min_value=0, max_value=20, value=2, step=1)
            pt_ngan = col_sub2.number_input("Điểm trả lời ngắn:", min_value=0.0, max_value=10.0, value=1.0, step=0.25)
            
            # Tính tổng điểm toàn bộ đề thi để cảnh báo giáo viên nếu vượt quá 10 điểm
            tong_diem_toan_de = pt_tn_calc + pt_tl_total + pt_khuyet + pt_ngan
            st.markdown(f"<div style='margin-top:10px; padding: 8px; background:#FFF1F2; border:1px solid #FECDD3; border-radius:4px; font-weight:800; color:#9F1239; text-align:center; font-size:16px;'>🎯 TỔNG ĐIỂM TOÀN ĐỀ THI: {tong_diem_toan_de} / 10.0 ĐIỂM</div>", unsafe_allow_html=True)

        st.markdown("---")
        col_btn_zone, col_check_zone = st.columns()
        run_exam_ai = col_btn_zone.button("🚀 Tự động tạo ma trận & đề thi", type="primary", use_container_width=True)
        yeu_cau_bam_sat = col_check_zone.checkbox("Yêu cầu bám sát kiến thức trong tài liệu tải lên", value=True)

        st.markdown("##### Tỷ lệ mức độ nhận thức (%):")
        col_mz1, col_mz2, col_mz3, col_mz4 = st.columns(4)
        c_mz1_l, c_mz1_i = col_mz1.columns()
        c_mz1_l.markdown("<div style='margin-top: 8px;'>Nhận biết:</div>", unsafe_allow_html=True)
        mz_nb = c_mz1_i.number_input("mz_nb", min_value=0, max_value=100, value=40, step=5)
        
        c_mz2_l, c_mz2_i = col_mz2.columns()
        c_mz2_l.markdown("<div style='margin-top: 8px;'>Thông hiểu:</div>", unsafe_allow_html=True)
        mz_th = c_mz2_i.number_input("mz_th", min_value=0, max_value=100, value=30, step=5)
        
        c_mz3_l, c_mz3_i = col_mz3.columns()
        c_mz3_l.markdown("<div style='margin-top: 8px;'>Vận dụng:</div>", unsafe_allow_html=True)
        mz_vd = c_mz3_i.number_input("mz_vd", min_value=0, max_value=100, value=20, step=5)
        
        c_mz4_l, c_mz4_i = col_mz4.columns()
        c_mz4_l.markdown("<div style='margin-top: 8px;'>Vận dụng cao:</div>", unsafe_allow_html=True)
        mz_vdc = c_mz4_i.number_input("mz_vdc", min_value=0, max_value=100, value=10, step=5)

        st.markdown("**Nhập yêu cầu khác (Tùy chọn):**")
        st.caption("Yeu_Cau_Khac")
        note_de = st.text_area("Yêu cầu cụ thể", placeholder="Nhập yêu cầu khác....", label_visibility="collapsed", key="note_de_area")

        if run_exam_ai:
            context_text = ""
            if tai_lieu_dinh_kem is not None:
                if tai_lieu_dinh_kem.name.endswith(".docx"): context_text = read_uploaded_docx(tai_lieu_dinh_kem)
                elif tai_lieu_dinh_kem.name.endswith(".pdf"): context_text = read_uploaded_pdf(tai_lieu_dinh_kem)

            prompt_exam = (
                f"Hãy thiết kế một Ma trận đề thi và Đề kiểm tra chi tiết (kèm Đáp án) cho môn: {mon_de}, {khoi_de}, hình thức: {hinh_thuc}, thời gian: {tg_de}.\n"
                f"CẤU TRÚC ĐỀ BẮT BUỘC:\n"
                f"- Trắc nghiệm: {num_tn_input} câu ({pt_tn_calc} điểm)\n"
                f"- Tự luận: Gồm {num_tl_input} câu lớn với tổng số điểm là {pt_tl_total} điểm (Điểm chi tiết từng câu: {', '.join([f'Câu {i+1}: {s}đ' for i, s in enumerate(tl_scores)])})\n"
                f"- Điền khuyết: {num_khuyet} câu ({pt_khuyet} điểm)\n- Trả lời ngắn: {num_ngan} câu ({pt_ngan} điểm)\n"
                f"MA TRẬN MỨC ĐỘ NHẬN THỨC: Nhận biết {mz_nb}%, Thông hiểu {mz_th}%, Vận dụng {mz_vd}%, Vận dụng cao {mz_vdc}%.\n"
                f"Yêu cầu nội dung kiến thức bổ sung: {note_de}.\n"
                f"Tài liệu tham khảo đính kèm:\n{context_text}\n\n"
                f"Trả về kết quả định dạng văn bản Markdown kết hợp kẻ bảng ma trận dạng '|'."
            )

            if run_ai_prompt_safe_func is not None:
                with st.spinner("🚀 Trợ lý AI đang liên kết API Key hệ thống và thiết kế đề thi..."):
                    res_text, status = run_ai_prompt_safe_func(prompt_exam)
                    if status == "error":
                        st.error(f"❌ Lỗi: {res_text}")
                    else:
                        st.session_state["current_exam_designer_output"] = res_text
                        st.session_state["db_de_kiem_tra"].append({
                            "id": f"De_{len(st.session_state['db_de_kiem_tra'])+1}", "mon": mon_de, "khoi": khoi_de, "hinh_thuc": hinh_thuc, "data": res_text
                        })
                        st.success(f"🎉 Khởi tạo thành công bằng mô hình {status}!")
                        st.rerun()
            else:
                st.error("❌ Lỗi luồng: Chưa kết nối được trình điều khiển AI tổng từ file app.py.")

        if st.session_state["current_exam_designer_output"]:
            st.markdown("---")
            st.markdown(st.session_state["current_exam_designer_output"])
            word_exam_data = export_to_docx_vietnam_standard(st.session_state["current_exam_designer_output"], f"ĐỀ KIỂM TRA MÔN {mon_de.upper()} - {khoi_de.upper()}")
            st.download_button(label="📥 Tải file Word (.docx) Đề kiểm tra", data=word_exam_data, file_name=f"De_Kiem_Tra_{mon_de.replace(' ', '_')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

    with tab_kho_luu_tru:
        st.markdown("#### 📂 Các đề kiểm tra đã được AI tự động sinh và lưu trữ")
        if not st.session_state["db_de_kiem_tra"]:
            st.caption("✨ Chưa có đề kiểm tra nào được tạo.")
        else:
            indices_to_delete = []
            for idx, de_info in enumerate(st.session_state["db_de_kiem_tra"]):
                with st.expander(f"📋 Đề môn {de_info['mon']} - {de_info['khoi']} ({de_info['hinh_thuc']})"):
                    st.markdown(de_info['data'])
                    h_col1, h_col2 = st.columns(2)
                    word_hist_data = export_to_docx_vietnam_standard(de_info['data'], f"ĐỀ KIỂM TRA MÔN {de_info['mon'].upper()} - {de_info['khoi'].upper()}")
                    h_col1.download_button(label="📥 Tải file Word", data=word_hist_data, file_name=f"De_{de_info['mon'].replace(' ', '_')}.docx", key=f"dl_ex_w_{idx}", use_container_width=True)
                    if h_col2.button("❌ Xóa đề thi", key=f"del_ex_btn_{idx}", use_container_width=True): indices_to_delete.append(idx)
            if indices_to_delete:
                for index in sorted(indices_to_delete, reverse=True): st.session_state["db_de_kiem_tra"].pop(index)
                st.success("🗑️ Đã xóa đề thi!")
                st.rerun()

    st.markdown("<div class='footer-red'>© Bản quyền thuộc về Tác giả: Lê Hồng Dưỡng | Đơn vị: Trường THCS Nguyễn Chí Thanh - phường Tân Lập - tỉnh Đắk Lắk</div>", unsafe_allow_html=True)
