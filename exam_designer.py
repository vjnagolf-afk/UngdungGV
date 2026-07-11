import streamlit as st
import gspread
from document_processor import read_uploaded_docx, read_uploaded_pdf, export_to_docx_vietnam_standard
from rag_module.latex_formatter import process_science_formulas
from ai_service import run_ai_prompt_safe

# [CHÈN CÁC HÀM GET_EXAM_SHEET, SYNC... CỦA THẦY VÀO ĐÂY]

def render_exam_designer_section(run_ai_prompt_safe_func):
    # --- PHẦN GIAO DIỆN CŨ CỦA THẦY ---
    # [DÁN TOÀN BỘ CODE CŨ TỪ PHẦN CSS ĐẾN HẾT CÁC CỘT (COLUMNS) CỦA THẦY VÀO ĐÂY]
    # Lưu ý: Đảm bảo biến 'nut_sinh_de' là kết quả của st.button(...)

    # --- PHẦN TÍCH HỢP LOGIC AI (Đặt ngay sau nút bấm của thầy) ---
    if 'nut_sinh_de' in locals() and nut_sinh_de:
        with st.spinner("🧠 Đang soạn đề..."):
            ket_qua, model = run_ai_prompt_safe_func(prompt_vi_mo, mo_hinh_uu_tien)
            # BỘ LỌC CÔNG THỨC ĐỂ KHÔNG BỊ LỖI
            st.session_state["ket_qua_de"] = process_science_formulas(ket_qua)
            st.session_state["model_dung"] = model
            st.rerun()

    # --- PHẦN HIỂN THỊ KẾT QUẢ ---
    if st.session_state.get("ket_qua_de"):
        st.markdown("---")
        st.markdown(st.session_state["ket_qua_de"])
        
        c1, c2 = st.columns(2)
        with c1:
            data_word = export_to_docx_vietnam_standard(st.session_state["ket_qua_de"], st.session_state["save_ten_de"])
            st.download_button("📥 Tải bản chuẩn (.docx)", data_word, "De_Thi_Chuan.docx", use_container_width=True)
        with c2:
            if st.button("🗑️ Xóa kết quả", use_container_width=True):
                st.session_state["ket_qua_de"] = ""
                st.rerun()

    # --- THƯ MỤC LƯU ĐỀ (Giữ nguyên giao diện cũ của thầy) ---
    st.markdown("### THƯ MỤC LƯU ĐỀ ĐÃ XD")
    # [DÁN CODE HIỂN THỊ DANH SÁCH TỪ GOOGLE SHEET CỦA THẦY]
