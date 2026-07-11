import sys
import os
import streamlit as st
import gspread

# 1. Cấu hình đường dẫn
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'teaching_assistant')))

# 2. Import các module xử lý (Bộ lọc & Xuất file)
from rag_module.latex_formatter import process_science_formulas
from document_processor import read_uploaded_docx, read_uploaded_pdf, export_to_docx_vietnam_standard
from ai_service import run_ai_prompt_safe

# [CHÈN CÁC HÀM GSPREAD VÀ CẤU HÌNH CŨ CỦA THẦY VÀO ĐÂY]
# (get_exam_sheet, sync_exam_to_google_sheet, get_all_exams_from_sheet, delete_exam_from_sheet)

def render_exam_designer_section(run_ai_prompt_safe_func):
    # [CHÈN PHẦN CSS VÀ GIAO DIỆN CŨ CỦA THẦY VÀO ĐÂY]
    # (Đoạn style, các col1, col2, col3, col4, các input và checkbox cũ)

    # 3. LƯU KẾT QUẢ AI VÀ XỬ LÝ (Đặt ngay dưới nút "TỰ ĐỘNG KHỞI TẠO...")
    if nut_sinh_de:
        with st.spinner("🧠 AI đang soạn đề..."):
            raw_output, model_name = run_ai_prompt_safe_func(prompt_vi_mo, mo_hinh_uu_tien)
            
            # --- ĐỒNG BỘ BỘ LỌC CÔNG THỨC (CỰC KỲ QUAN TRỌNG) ---
            final_content = process_science_formulas(raw_output)
            st.session_state["ket_qua_de"] = final_content
            st.rerun()

    # 4. HIỂN THỊ KẾT QUẢ VÀ NÚT XUẤT FILE (Không dùng Tab, nằm trực tiếp trong luồng giao diện)
    if st.session_state.get("ket_qua_de"):
        st.markdown("---")
        st.markdown(st.session_state["ket_qua_de"])
        
        col_x, col_y = st.columns(2)
        with col_x:
            # Xuất file Word chuẩn hành chính
            data_word = export_to_docx_vietnam_standard(
                st.session_state["ket_qua_de"], 
                st.session_state.get("save_ten_de", "De_Thi_Chuan"), 
                school_name=st.session_state.get("save_school", "Trường THCS")
            )
            st.download_button("📥 Tải đề Word chuẩn hành chính", data_word, "De_Thi_Chuan.docx", use_container_width=True)
        with col_y:
            if st.button("🗑️ Xóa kết quả", use_container_width=True):
                st.session_state["ket_qua_de"] = ""
                st.rerun()

    # 5. PHẦN THƯ MỤC LƯU ĐỀ ĐÃ XD (Đặt dưới cùng, không nằm trong tab)
    st.markdown("### THƯ MỤC LƯU ĐỀ ĐÃ XD")
    # [CODE HIỂN THỊ DANH SÁCH ĐỀ TỪ GOOGLE SHEET CŨ CỦA THẦY Ở ĐÂY]
