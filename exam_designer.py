import streamlit as st
import gspread
from document_processor import read_uploaded_docx, read_uploaded_pdf, export_to_docx_vietnam_standard

# ================= ĐOẠN 1: CẤU HÌNH & GOOGLE SHEETS =================
SPREADSHEET_ID = "1C6642jk_oQ0g9UC2By2qsNxxfQVR0MrZYj52tRdWDlY"
TAB_NAME = "DE_KT"

# [Các hàm get_exam_sheet, sync_exam_to_google_sheet, get_all_exams_from_sheet, delete_exam_from_sheet giữ nguyên]
# ... (Giữ nguyên các hàm thao tác Google Sheets của thầy) ...

# ================= ĐOẠN 2: GIAO DIỆN CHÍNH =================
def render_exam_designer_section(run_ai_prompt_safe_func):
    
    # 1. GIAO DIỆN CŨ (Giữ nguyên toàn bộ cấu trúc của thầy)
    # [Bao gồm các st.markdown, st.columns, st.number_input, st.text_input, st.file_uploader, st.checkbox của thầy ở đây]
    
    # 2. XỬ LÝ KHI BẤM NÚT "TỰ ĐỘNG KHỞI TẠO..."
    # (Giả sử nút bấm của thầy đã gán vào biến nut_sinh_de)
    if 'nut_sinh_de' in locals() and nut_sinh_de:
        with st.spinner("🧠 AI đang soạn đề..."):
            # Gọi AI
            ket_qua, model_thuc_te = run_ai_prompt_safe_func(prompt_vi_mo, mo_hinh_uu_tien)
            st.session_state["ket_qua_de"] = ket_qua
            st.session_state["model_dung"] = model_thuc_te
            
            # Lưu tự động
            if "⚠️" not in ket_qua and "Lỗi" not in ket_qua:
                sync_exam_to_google_sheet(st.session_state["save_ten_de"], st.session_state["save_mon_hoc"], 
                                          st.session_state["save_khoi_lop"], st.session_state["save_thoi_gian"], ket_qua)
            st.rerun()

    # 3. HIỂN THỊ KẾT QUẢ (Nằm ngay dưới phần giao diện cũ, không thay đổi bố cục)
    if st.session_state.get("ket_qua_de"):
        st.markdown("---")
        st.info(f"🤖 Đề thi được xây dựng thành công: `{st.session_state.get('model_dung', '')}`")
        st.markdown(st.session_state["ket_qua_de"])
        
        # Nút xuất Word & Xóa
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            data_word = export_to_docx_vietnam_standard(
                st.session_state["ket_qua_de"], 
                st.session_state["save_ten_de"], 
                school_name=st.session_state["save_school"]
            )
            st.download_button("📥 Tải bản chuẩn hành chính (.docx)", data_word, 
                               f"De_Kiem_Tra_{st.session_state['save_khoi_lop'].replace(' ', '_')}.docx", use_container_width=True)
        with col_btn2:
            if st.button("🗑️ Xóa kết quả", use_container_width=True):
                st.session_state["ket_qua_de"] = ""
                st.rerun()

    # 4. DANH SÁCH LƯU ĐỀ (Giữ nguyên vị trí cuối cùng của giao diện)
    st.markdown("### THƯ MỤC LƯU ĐỀ ĐÃ XD")
    # [Hiển thị danh sách từ Google Sheet bằng expander của thầy]
