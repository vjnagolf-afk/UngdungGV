import streamlit as st
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

def export_plan_to_docx(teacher_name, subject_name, markdown_content):
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(1.18)
        section.right_margin = Inches(0.59)
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\nĐộc lập - Tự do - Hạnh phúc\n").bold = True
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("\nKẾ HOẠCH GIÁO DỤC CỦA GIÁO VIÊN\n(PHỤ LỤC III CÔNG VĂN 5512/BGDĐT)\n")
    r_title.bold = True
    r_title.font.size = Pt(14)
    r_title.font.color.rgb = RGBColor(255, 0, 0)
    p_info = doc.add_paragraph()
    p_info.add_run(f"Giáo viên thực hiện: {teacher_name}\nMôn học/Hoạt động giáo dục: {subject_name}\n")
    lines = markdown_content.split('\n')
    for line in lines:
        clean_line = line.strip().replace('**', '').replace('###', '').replace('##', '').replace('#', '')
        if not clean_line: continue
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run = p.add_run(clean_line)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        if line.strip().startswith('#') or "I." in clean_line or "II." in clean_line:
            run.bold = True
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()
def render_personal_plan():
    st.markdown("<h3 style='text-align: left; color: #1E3A8A;'>🗓️ TRỢ LÝ XÂY DỰNG KẾ HOẠCH GIÁO DỤC CÁ NHÂN (PHỤ LỤC III)</h3>", unsafe_allow_html=True)
    
    # Tạo hộp chứa cố định đứng im trên màn hình chống lag widget
    container_output = st.empty()
    
    with st.form("form_personal_plan_fixed_final_v6", border=False):
        col_t, col_s = st.columns(2)
        t_name = col_t.text_input("Họ và tên Giáo viên giảng dạy:", placeholder="Ví dụ: Thầy Lê Hồng Dưỡng", key="plan_txt_t_name_v6")
        s_name = col_s.selectbox("Môn học / Phân môn phụ trách:", ["Khoa học tự nhiên (Vật lý)", "Khoa học tự nhiên (Sinh học)", "Khoa học tự nhiên (Hóa học)", "Toán học", "Ngữ văn", "GDTC"], key="plan_sb_s_name_v6")
        col_g, col_w = st.columns(2)
        grade_target = col_g.text_input("Khối lớp phân công dạy:", placeholder="Ví dụ: Khối 7, Khối 8", key="plan_txt_grade_target_v6")
        week_count = col_w.text_input("Tổng số tuần thực hiện kế hoạch:", placeholder="Ví dụ: 35 Tuần", key="plan_txt_week_count_v6")
        st.markdown("**💬 Các tiêu chí đặc thù hoặc lưu ý phân bổ tiết (Nếu có):**")
        note_plan = st.text_area("Yêu cầu bổ sung cho AI:", placeholder="Ví dụ: Phân bổ chi tiết số tiết cho chương Tốc độ ở vật lý 7 học kỳ I...", label_visibility="collapsed", key="plan_ta_note_v6")
        run_ai_plan = st.form_submit_button(" Khởi tạo Kế hoạch bằng AI", type="primary", use_container_width=True)
        
    if run_ai_plan:
        if not t_name or not grade_target:
            st.warning("⚠️ Vui lòng điền Họ tên giáo viên và Khối lớp để AI lập kế hoạch!")
        else:
            with st.spinner("Trợ lý AI đang nghiên cứu khung chương trình giáo dục phổ thông và lập tiến trình phân bổ tiết Phụ lục III..."):
                prompt_plan = f"Hãy soạn thảo một bản Kế hoạch giáo dục của giáo viên (Phụ lục III - Công văn 5512) chi tiết cho giáo viên: {t_name}, môn: {s_name}, khối lớp: {grade_target} trong {week_count}. Cấu trúc gồm mục I. KẾ HOẠCH DẠY HỌC PHÂN PHỐI CHƯƠNG TRÌNH và mục II. CÁC NHIỆM VỤ KHÁC ĐƯỢC GIAO. Văn bản viết chi tiết đầy đủ chữ, chia dòng gạch ngang '-', tuyệt đối không dùng dấu sao kép '**'."
                try:
                    # Kết nối lấy khóa API hệ thống
                    from app import run_ai_prompt_safe
                    api_key_system = st.secrets.get("GEMINI_API_KEY", "")
                    res_plan, _ = run_ai_prompt_safe(prompt_plan, api_key_system)
                    
                    # Đổ trực tiếp văn bản ra màn hình real-time
                    with container_output.container():
                        st.markdown("---")
                        st.markdown("### 📊 Nội dung Kế hoạch Giáo dục sinh bởi AI:")
                        st.write(res_plan)
                        word_plan_data = export_plan_to_docx(t_name, s_name, res_plan)
                        st.download_button(label="📥 Tải file Word (.docx) Phụ lục III chuẩn về máy", data=word_plan_data, file_name=f"Phu_Luc_III_{t_name.replace(' ', '_')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True, key="download_fixed_v6")
                except Exception as e:
                    # Loại bỏ dòng in lỗi {e} hệ thống cũ gây hiểu lầm trùng key
                    st.error("❌ Hiện tại kết nối mô hình Trí tuệ nhân tạo đang bận hoặc cấu hình GEMINI_API_KEY tại mục Secrets trên Streamlit Cloud chưa được kích hoạt. Thầy vui lòng kiểm tra lại khóa API.")
