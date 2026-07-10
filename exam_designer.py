import streamlit as st
import gspread
from document_processor import read_uploaded_docx, read_uploaded_pdf, export_to_docx_vietnam_standard

# --- (Giữ nguyên toàn bộ hàm sync_exam_to_google_sheet) ---
SPREADSHEET_ID = "1C6642jk_oQ0g9UC2By2qsNxxfQVR0MrZYj52tRdWDlY"
TAB_NAME = "DE_KT"

def sync_exam_to_google_sheet(ten_de, mon, khoi, thoi_gian, noi_dung):
    try:
        creds_dict = None
        priority_keys = ["gspread_credentials", "GSPREAD_CREDENTIALS", "google_sheet_creds", "google_creds", "GOOGLE_KEY"]
        for key in priority_keys:
            if key in st.secrets: creds_dict = st.secrets[key]; break
        if creds_dict is None:
            for key in st.secrets.keys():
                node = st.secrets[key]
                if hasattr(node, "get") or isinstance(node, dict):
                    if node.get("type") == "service_account" or "private_key" in node: creds_dict = node; break
        if creds_dict is None: return False
        gc = gspread.service_account_from_dict(creds_dict)
        sh = gc.open_by_key(SPREADSHEET_ID)
        worksheet = sh.worksheet(TAB_NAME)
        if len(worksheet.get_all_values()) == 0:
            worksheet.append_row(["Tên Đề", "Môn Học", "Khối Lớp", "Thời Gian", "Nội Dung Đề Thi"])
        worksheet.append_row([ten_de, mon, khoi, thoi_gian, noi_dung])
        return True
    except: return False

def render_exam_designer_section(run_ai_prompt_safe_func):
    st.markdown("<h3 style='text-align: center; color: blue;'>Sản phẩm tham gia Cuộc thi AI for Life năm 2026, trường THCS Nguyễn Chí Thanh - Phường Tân Lập tỉnh Đắk Lắk</h3>", unsafe_allow_html=True)
    
    # Tabs chính
    tab_tao, tab_thu_muc = st.tabs(["CHỨC NĂNG TẠO ĐỀ KIỂM TRA", "THƯ MỤC LƯU ĐỀ ĐÃ XD"])
    
    with tab_tao:
        # Hàng 1: Menu chính
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.selectbox("MENU MÔN HỌC", ["Khoa học tự nhiên", "Toán", "Vật lý", "Hóa học"])
        with col2: st.selectbox("MENU LỚP", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"])
        with col3: st.selectbox("HÌNH THỨC KT", ["Trắc nghiệm kết hợp tự luận", "100% Trắc nghiệm"])
        with col4: st.text_input("THỜI GIAN", "45 phút")

        # Hàng 2: Nhận thức
        st.markdown("**Tỷ lệ mức độ nhận thức (%):**")
        c_nb, c_th, c_vd, c_vdc = st.columns(4)
        tl_nb = c_nb.number_input("Nhận biết:", value=40, step=10)
        tl_th = c_th.number_input("Thông hiểu:", value=30, step=10)
        tl_vd = c_vd.number_input("Vận dụng:", value=20, step=10)
        tl_vdc = c_vdc.number_input("Vận dụng cao:", value=10, step=10)

        # Hàng 3: Tên đề và File
        c_name, c_file1, c_file2 = st.columns([2, 1, 1])
        with c_name: st.text_input("Tên bài kiểm tra / Đề số:", "Kiểm tra đánh giá giữa kì I")
        with c_file1: st.file_uploader("Tải Đề Cương (.docx, .pdf):")
        with c_file2: st.file_uploader("Tải Đề mẫu ma trận (.docx):")

        st.divider()

        # PHẦN TRẮC NGHIỆM & TỰ LUẬN
        c_tn, c_tl = st.columns(2)
        
        with c_tn:
            st.markdown("### TRẮC NGHIỆM | 4.0 | Điểm")
            # Căn chỉnh 2 cột cho nhãn và input
            for label, key in [("Số câu nhiều lựa chọn", "nlc"), ("Số câu đúng/sai", "ds"), ("Số câu điền khuyết", "dk"), ("Số câu trả lời ngắn", "tln")]:
                cl1, cl2, cl3 = st.columns([2, 1, 1])
                cl1.write(f"**{label}:**")
                cl2.number_input(f"sl_{key}", label_visibility="collapsed")
                cl3.number_input(f"diem_{key}", label_visibility="collapsed")
                st.write("---") # Đường kẻ giữa các dòng

        with c_tl:
            # Logic: Số câu TL tự sinh
            sc_tl = st.number_input("TỰ LUẬN", value=4)
            st.text_input("6.0", value="6.0", disabled=True)
            st.write("Điểm")
            
            for i in range(int(sc_tl)):
                cl1, cl2, cl3 = st.columns([2, 1, 1])
                cl1.write(f"**Câu {i+1}:**")
                cl2.number_input(f"tl_{i}", label_visibility="collapsed", value=2.0 if i<3 else 1.0)
                cl3.write("điểm")

        st.markdown("**Yêu cầu khác:**")
        st.text_area("Ví dụ: ...", label_visibility="collapsed")
        
        if st.button("🔴 Tự động khởi tạo ma trận và đề thi", type="primary", use_container_width=True):
             # [Giữ nguyên logic sinh đề, xuất Word, đồng bộ Sheet cũ của bạn tại đây]
             pass
             pass

    with tab_thu_muc:
        st.write("📂 Danh sách các đề kiểm tra đã đồng bộ:")
        st.markdown(f"🔗 [Bấm vào đây để mở trực tiếp Google Sheets](https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit)")
