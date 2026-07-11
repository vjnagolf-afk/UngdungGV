import streamlit as st
import gspread
import sys
import os

# Đường dẫn module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'teaching_assistant')))
from rag_module.latex_formatter import process_science_formulas
from document_processor import read_uploaded_docx, read_uploaded_pdf, export_to_docx_vietnam_standard
from ai_service import run_ai_prompt_safe

# [CHÈN CÁC HÀM GOOGLE SHEET VÀO ĐÂY: get_exam_sheet, sync_exam_to_google_sheet, ...]
# (Thầy giữ nguyên các hàm này như cũ)

def render_exam_designer_section(run_ai_prompt_safe_func):
    # --- PHẦN 1: GIAO DIỆN CŨ (GIỮ NGUYÊN) ---
    # Thầy dán toàn bộ code cũ từ phần st.markdown(CSS...) 
    # cho đến hết phần st.text_area("Yêu cầu khác", ...) vào đây.
    
    # --- PHẦN 2: NÚT BẤM VÀ XỬ LÝ (TÍCH HỢP BỘ LỌC) ---
    # Sau khi thầy đã dán hết phần giao diện ở trên, thầy đặt đoạn code này vào ngay dưới:
    
    if 'nut_sinh_de' in locals() and nut_sinh_de:
        with st.spinner("🧠 Hệ thống đang xử lý..."):
            # Gọi AI
            ket_qua, model_thuc_te = run_ai_prompt_safe_func(prompt_vi_mo, mo_hinh_uu_tien)
            
            # ĐỒNG BỘ: BỘ LỌC CÔNG THỨC Ở ĐÂY (Trước khi lưu vào session_state)
            final_content = process_science_formulas(ket_qua)
            
            st.session_state["ket_qua_de"] = final_content
            st.session_state["model_dung"] = model_thuc_te
            st.rerun()

    # --- PHẦN 3: HIỂN THỊ KẾT QUẢ & XUẤT WORD ---
    if st.session_state.get("ket_qua_de"):
        st.markdown("---")
        st.markdown(st.session_state["ket_qua_de"])
        
        c_save, c_del = st.columns(2)
        with c_save:
            data_word = export_to_docx_vietnam_standard(
                st.session_state["ket_qua_de"], 
                st.session_state.get("save_ten_de", "De_Thi_Chuan"), 
                school_name=st.session_state.get("save_school", "Trường THCS")
            )
            st.download_button("📥 Tải đề Word chuẩn", data_word, "De_Thi_Chuan.docx", use_container_width=True)
        with c_del:
            if st.button("🗑️ Xóa kết quả", use_container_width=True):
                st.session_state["ket_qua_de"] = ""
                st.rerun()

    # --- PHẦN 4: DANH SÁCH LƯU ĐỀ (GIỮ NGUYÊN) ---
    st.markdown("### THƯ MỤC LƯU ĐỀ ĐÃ XD")
    # [Thầy dán lại đoạn code hiển thị danh sách từ Google Sheets cũ ở đây]
