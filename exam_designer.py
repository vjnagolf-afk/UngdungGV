import streamlit as st
import gspread
import sys
import os

# Đường dẫn để gọi bộ lọc và AI
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'teaching_assistant')))
from rag_module.latex_formatter import process_science_formulas
from document_processor import read_uploaded_docx, read_uploaded_pdf, export_to_docx_vietnam_standard
from ai_service import run_ai_prompt_safe

# [CHÈN CÁC HÀM GSPREAD VÀ CẤU HÌNH GOOGLE SHEET VÀO ĐÂY NHƯ CŨ]
# ... (Giữ nguyên phần get_exam_sheet, sync_exam_to_google_sheet...) ...

def render_exam_designer_section(run_ai_prompt_safe_func):
    # PHẦN CSS CỦA THẦY (Giữ nguyên)
    st.markdown("""<style>...[CSS CŨ CỦA THẦY]...</style>""", unsafe_allow_html=True)
    
    # 1. PHẦN GIAO DIỆN CŨ (Thầy dán code cũ vào đây, tôi đã bỏ các dòng tabs)
    # [DÁN CODE GIAO DIỆN CŨ TỪ DÒNG 80 ĐẾN 210 CỦA THẦY]
    
    # 2. XỬ LÝ AI (Đặt ngay sau nút "TỰ ĐỘNG KHỞI TẠO...")
    if 'nut_sinh_de' in locals() and nut_sinh_de:
        with st.spinner("🧠 Đang soạn đề..."):
            ket_qua, model = run_ai_prompt_safe_func(prompt_vi_mo, mo_hinh_uu_tien)
            # --- BỘ LỌC CÔNG THỨC ---
            st.session_state["ket_qua_de"] = process_science_formulas(ket_qua)
            st.session_state["model_dung"] = model
            st.rerun()

    # 3. HIỂN THỊ KẾT QUẢ VÀ NÚT XUẤT (Đặt ngay dưới, không dùng tabs)
    if st.session_state.get("ket_qua_de"):
        st.markdown(st.session_state["ket_qua_de"])
        if st.download_button("📥 Tải bản chuẩn hành chính (.docx)", 
                              data=export_to_docx_vietnam_standard(st.session_state["ket_qua_de"], st.session_state["save_ten_de"]),
                              file_name="De_Thi_Chuan.docx"):
            pass
