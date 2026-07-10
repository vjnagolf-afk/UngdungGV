# exam_designer.py - HOÀN CHỈNH 100% TÍNH NĂNG & GIAO DIỆN PHÁC HỌA
import streamlit as st
import gspread
from document_processor import read_uploaded_docx, read_uploaded_pdf, export_to_docx_vietnam_standard

# Khai báo thông tin cấu hình Google Sheets của bạn
SPREADSHEET_ID = "1C6642jk_oQ0g9UC2By2qsNxxfQVR0MrZYj52tRdWDlY"
TAB_NAME = "DE_KT"

def sync_exam_to_google_sheet(ten_de, mon, khoi, thoi_gian, noi_dung):
    """Tự động tìm kiếm Service Account trong Secrets và đồng bộ kết quả lên Google Sheets"""
    try:
        creds_dict = None
        priority_keys = ["gspread_credentials", "GSPREAD_CREDENTIALS", "google_sheet_creds", "google_creds", "GOOGLE_KEY"]
        for key in priority_keys:
            if key in st.secrets:
                creds_dict = st.secrets[key]
                break
                
        if creds_dict is None:
            for key in st.secrets.keys():
                node = st.secrets[key]
                if hasattr(node, "get") or isinstance(node, dict):
                    if node.get("type") == "service_account" or "private_key" in node:
                        creds_dict = node
                        break
        
        if creds_dict is None:
            return False
            
        gc = gspread.service_account_from_dict(creds_dict)
        sh = gc.open_by_key(SPREADSHEET_ID)
        worksheet = sh.worksheet(TAB_NAME)
        
        if len(worksheet.get_all_values()) == 0:
            worksheet.append_row(["Tên Đề", "Môn Học", "Khối Lớp", "Thời Gian", "Nội Dung Đề Thi"])
            
        worksheet.append_row([ten_de, mon, khoi, thoi_gian, noi_dung])
        return True
    except:
        return False

def render_exam_designer_section(run_ai_prompt_safe_func):
    """Giao diện phân hệ thiết kế đề kiểm tra được căn chỉnh theo phác họa"""
    
    st.markdown("<h4 style='text-align: center; color: blue; font-weight: bold;'>Sản phẩm tham gia Cuộc thi AI for Life năm 2026, trường THCS Nguyễn Chí Thanh - Phường Tân Lập tỉnh Đắk Lắk</h4>", unsafe_allow_html=True)
    
    if "ket_qua_de" not in st.session_state: st.session_state["ket_qua_de"] = ""
    if "model_dung" not in st.session_state: st.session_state["model_dung"] = ""
    
    # Lưu thông tin cấu hình vào session_state
    if "save_ten_de" not in st.session_state: st.session_state["save_ten_de"] = ""
    if "save_school" not in st.session_state: st.session_state["save_school"] = "TRƯỜNG THCS NGUYỄN CHÍ THANH"
    if "save_mon_hoc" not in st.session_state: st.session_state["save_mon_hoc"] = "Khoa học tự nhiên"
    if "save_khoi_lop" not in st.session_state: st.session_state["save_khoi_lop"] = "Lớp 8"
    if "save_thoi_gian" not in st.session_state: st.session_state["save_thoi_gian"] = "45 phút"

    tab_tao_de, tab_thu_muc = st.tabs(["🔴 CHỨC NĂNG TẠO ĐỀ KIỂM TRA", "🗂️ THƯ MỤC LƯU ĐỀ ĐÃ XD"])
    
    with tab_tao_de:
        # --- HÀNG 1: CÁC MENU NGANG ---
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("<p style='color:blue; font-weight:bold; text-align:center; margin-bottom: 2px;'>MENU MÔN HỌC</p>", unsafe_allow_html=True)
            st.session_state["save_mon_hoc"] = st.text_input("Môn học:", value=st.session_state["save_mon_hoc"], label_visibility="collapsed")
        with col2:
            st.markdown("<p style='color:blue; font-weight:bold; text-align:center; margin-bottom: 2px;'>MENU LỚP</p>", unsafe_allow_html=True)
            st.session_state["save_khoi_lop"] = st.selectbox("Khối lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Khối 10", "Khối 11", "Khối 12"], index=2, label_visibility="collapsed")
        with col3:
            st.markdown("<p style='color:blue; font-weight:bold; text-align:center; margin-bottom: 2px;'>HÌNH THỨC KT</p>", unsafe_allow_html=True)
            hinh_thuc = st.selectbox("Hình thức đề:", ["Trắc nghiệm kết hợp tự luận", "100% Trắc nghiệm", "100% Tự luận"], label_visibility="collapsed")
        with col4:
            st.markdown("<p style='color:blue; font-weight:bold; text-align:center; margin-bottom: 2px;'>THỜI GIAN</p>", unsafe_allow_html=True)
            st.session_state["save_thoi_gian"] = st.text_input("Thời gian:", value=st.session_state["save_thoi_gian"], label_visibility="collapsed")

        # --- HÀNG 2: TỶ LỆ NHẬN THỨC ---
        st.markdown("<p style='color:red; font-weight:bold; font-size:16px; margin-top:15px; margin-bottom: 5px;'>Tỷ lệ mức độ nhận thức (%):</p>", unsafe_allow_html=True)
        col_nb, col_th, col_vd, col_vdc = st.columns(4)
        with col_nb:
            tl_nhan_biet = st.number_input("Nhận biết:", min_value=0, max_value=100, value=40, step=10)
        with col_th:
            tl_thong_hieu = st.number_input("Thông hiểu:", min_value=0, max_value=100, value=30, step=10)
        with col_vd:
            tl_van_dung = st.number_input("Vận dụng:", min_value=0, max_value=100, value=20, step=10)
        with col_vdc:
            tl_vd_cao = st.number_input("Vận dụng cao:", min_value=0, max_value=100, value=10, step=10)

        # --- HÀNG 3: TÊN ĐỀ VÀ TẢI FILE ---
        st.markdown("<br>", unsafe_allow_html=True)
        col_name, col_f1, col_f2 = st.columns([2, 1, 1])
        with col_name:
            st.markdown("<p style='color:red; font-weight:bold; margin-bottom: 5px;'>Tên bài kiểm tra / Đề số:</p>", unsafe_allow_html=True)
            st.session_state["save_ten_de"] = st.text_input("Tên bài kiểm tra", value=st.session_state["save_ten_de"], label_visibility="collapsed", placeholder="Ví dụ: Kiểm tra đánh giá giữa kì I")
        with col_f1:
            st.markdown("<p style='color:red; font-style:italic; font-weight:bold; margin-bottom: 5px; text-align:center;'>Tải Đề Cương (.docx, .pdf):</p>", unsafe_allow_html=True)
            file_de_cuong = st.file_uploader("Upload Đề Cương", type=["docx", "pdf"], key="exam_upload_de_cuong_2026", label_visibility="collapsed")
        with col_f2:
            st.markdown("<p style='color:red; font-style:italic; font-weight:bold; margin-bottom: 5px; text-align:center;'>Tải Đề mẫu ma trận (.docx, .pdf):</p>", unsafe_allow_html=True)
            file_ma_tran = st.file_uploader("Upload Ma Trận", type=["docx", "pdf"], key="exam_upload_ma_tran_2026", label_visibility="collapsed")

        # Xử lý đọc file nội dung
        noi_dung_de_cuong = ""
        if file_de_cuong:
            if file_de_cuong.name.endswith(".docx"):
                noi_dung_de_cuong = read_uploaded_docx(file_de_cuong)
            else:
                noi_dung_de_cuong = read_uploaded_pdf(file_de_cuong)
            st.success(f"✅ Đã nạp tài liệu đề cương: {file_de_cuong.name}")
            
        noi_dung_ma_tran = ""
        if file_ma_tran:
            if file_ma_tran.name.endswith(".docx"):
                noi_dung_ma_tran = read_uploaded_docx(file_ma_tran)
            else:
                noi_dung_ma_tran = read_uploaded_pdf(file_ma_tran)
            st.success(f"✅ Đã nạp cấu trúc ma trận: {file_ma_tran.name}")

        st.markdown("<br>", unsafe_allow_html=True)

        # --- HÀNG 4: BỐ CỤC TRẮC NGHIỆM VÀ TỰ LUẬN (TỰ ĐỘNG TÍNH TỔNG) ---
        col_tn, col_space, col_tl = st.columns([1.2, 0.1, 1.2])
        
        with col_tn:
            # Header TN (Khóa tổng điểm bằng st.empty để tính sau)
            header_tn = st.empty()
            
            # Các hàng nhập liệu
            c1, c2, c3, c4 = st.columns([2.5, 1, 1, 0.8])
            c1.markdown("<p style='font-size:14px; font-weight:bold; margin-top:8px;'>Số câu nhiều lựa chọn:</p>", unsafe_allow_html=True)
            sc_nhieu_lua_chon = c2.number_input("sc_nlc", min_value=0, max_value=50, value=12, label_visibility="collapsed")
            d_nhieu_lua_chon = c3.number_input("d_nlc", min_value=0.0, max_value=10.0, value=3.0, step=0.25, label_visibility="collapsed")
            c4.markdown("<p style='font-style:italic; font-size:14px; margin-top:8px;'>điểm</p>", unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns([2.5, 1, 1, 0.8])
            c1.markdown("<p style='font-size:14px; font-weight:bold; margin-top:8px;'>Số câu đúng/sai:</p>", unsafe_allow_html=True)
            sc_dung_sai = c2.number_input("sc_ds", min_value=0, max_value=50, value=2, label_visibility="collapsed")
            d_dung_sai = c3.number_input("d_ds", min_value=0.0, max_value=10.0, value=0.5, step=0.25, label_visibility="collapsed")
            c4.markdown("<p style='font-style:italic; font-size:14px; margin-top:8px;'>điểm</p>", unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns([2.5, 1, 1, 0.8])
            c1.markdown("<p style='font-size:14px; font-weight:bold; margin-top:8px;'>Số câu điền khuyết:</p>", unsafe_allow_html=True)
            sc_dien_khuyết = c2.number_input("sc_dk", min_value=0, max_value=50, value=12, label_visibility="collapsed")
            d_dien_khuyết = c3.number_input("d_dk", min_value=0.0, max_value=10.0, value=3.0, step=0.25, label_visibility="collapsed")
            c4.markdown("<p style='font-style:italic; font-size:14px; margin-top:8px;'>điểm</p>", unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns([2.5, 1, 1, 0.8])
            c1.markdown("<p style='font-size:14px; font-weight:bold; margin-top:8px;'>Số câu trả lời ngắn:</p>", unsafe_allow_html=True)
            sc_tra_loi_ngan = c2.number_input("sc_tln", min_value=0, max_value=50, value=2, label_visibility="collapsed")
            d_tra_loi_ngan = c3.number_input("d_tln", min_value=0.0, max_value=10.0, value=0.5, step=0.25, label_visibility="collapsed")
            c4.markdown("<p style='font-style:italic; font-size:14px; margin-top:8px;'>điểm</p>", unsafe_allow_html=True)
            
            # Tính tổng và điền ngược lên header
            tong_cau_tn = sc_nhieu_lua_chon + sc_dung_sai + sc_dien_khuyết + sc_tra_loi_ngan
            tong_diem_tn = d_nhieu_lua_chon + d_dung_sai + d_dien_khuyết + d_tra_loi_ngan
            
            header_tn.markdown(f"""
            <div style='background-color:#FFF3CD; padding:10px; display:flex; align-items:center; border-radius:3px; margin-bottom:15px;'>
                <span style='color:blue; font-weight:bold; font-size:18px; margin-right:15px;'>TRẮC NGHIỆM</span>
                <div style='border: 1px solid #ffc107; background: white; color: blue; font-weight: bold; font-size:16px; padding: 2px 15px; margin-right:15px;'>{tong_diem_tn}</div>
                <span style='color:blue; font-weight:bold; font-size:16px;'>Điểm</span>
            </div>
            """, unsafe_allow_html=True)

        with col_tl:
            # Header TL tự sinh
            c_h1, c_h2, c_h3, c_h4 = st.columns([1.5, 0.8, 1, 1])
            with c_h1:
                st.markdown("""<div style='background-color:#D5E8D4; padding:10px; height: 100%; border-radius:3px;'><span style='color:blue; font-weight:bold; font-size:18px;'>TỰ LUẬN</span></div>""", unsafe_allow_html=True)
            with c_h2:
                sc_tu_luan = st.number_input("sc_tl", min_value=0, max_value=20, value=4, label_visibility="collapsed")
            with c_h3:
                ph_tong_diem_tl = st.empty() # Chỗ trống để điền tổng điểm TL
            with c_h4:
                st.markdown("""<div style='background-color:#D5E8D4; padding:10px; height: 100%; border-radius:3px;'><span style='color:blue; font-weight:bold; font-size:16px;'>Điểm</span></div>""", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Tự động sinh hàng nhập điểm dựa trên số câu
            diem_chi_tiet_tl = []
            tong_diem_tl = 0.0
            
            for i in range(int(sc_tu_luan)):
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"<p style='font-size:14px; font-weight:bold; text-align:center; margin-top:8px;'>Câu {i+1}.</p>", unsafe_allow_html=True)
                diem_cau = c2.number_input(f"tl_c_{i}", min_value=0.0, max_value=10.0, value=2.5 if i==0 else (1.5 if i==1 else 1.0), step=0.25, label_visibility="collapsed")
                c3.markdown("<p style='font-style:italic; font-size:14px; margin-top:8px;'>điểm</p>", unsafe_allow_html=True)
                diem_chi_tiet_tl.append((i+1, diem_cau))
                tong_diem_tl += diem_cau
                
            # Điền tổng điểm vào ô khóa phía trên
            ph_tong_diem_tl.markdown(f"<div style='border: 1px solid red; padding: 7px; text-align: center; color: red; font-weight: bold; font-size:16px;'>{tong_diem_tl}</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='color:red; font-weight:bold; text-decoration:underline;'>Yêu cầu khác:</p>", unsafe_allow_html=True)
        yeu_cau_khac = st.text_area("Yêu cầu khác (Tùy chọn):", placeholder="Ví dụ: Đề thi có chứa 1 câu hỏi thực tế về đồ thị hàm số bậc nhất...", label_visibility="collapsed")

        # Khối Nút tạo và các Option chạy AI
        col_btn_l, col_btn_r = st.columns([1.5, 1.0])
        with col_btn_l:
            nut_sinh_de = st.button("🔴 Tự động khởi tạo ma trận và đề thi", type="primary", use_container_width=True)
        with col_btn_r:
            mo_hinh_uu_tien = st.selectbox("Mô hình xử lý đề thi:", ["3.1 Flash-Lite", "3.5 Flash", "3.1 Pro", "Tư duy mở rộng"], index=0, label_visibility="collapsed")
            st.checkbox("Yêu cầu bám sát kiến thức trong GIÁO TRÌNH, tài liệu", value=True)

        # ================= LOGIC GỌI AI VÀ EXPORT CŨ (GIỮ NGUYÊN 100%) =================
        if nut_sinh_de:
            if int(tl_nhan_biet + tl_thong_hieu + tl_van_dung + tl_vd_cao) != 100:
                st.error("⚠️ Tổng tỷ lệ mức độ nhận thức phải bằng 100%!")
            else:
                with st.spinner("🧠 Hệ thống đang lập bảng Ma trận, Bản đặc tả và dựng đề thi..."):
                    chuỗi_điểm_tl = ", ".join([f"Câu {c_id} ({d}đ)" for c_id, d in diem_chi_tiet_tl])
                    
                    # 🚀 CẢI TIẾN PROMPT: Ép buộc tuyệt đối cấu trúc xuất ra phải chứa bảng ma trận và đặc tả
                    prompt_vi_mo = f"""
                    Bạn là Chuyên gia Khảo thí và Kiểm định Chất lượng Giáo dục phổ thông tại Việt Nam. 
                    Hãy thiết kế một tài liệu kiểm tra hoàn chỉnh cho môn {st.session_state['save_mon_hoc']} - {st.session_state['save_khoi_lop']} (Thời gian làm bài: {st.session_state['save_thoi_gian']}).
                    
                    CẤU TRÚC ĐẦU RA BẮT BUỘC THEO THỨ TỰ (KHÔNG ĐƯỢC BỎ SÓT):
                    
                    1. KHUNG MA TRẬN ĐỀ KIỂM TRA: Thiết lập dưới dạng bảng Markdown bằng ký tự '|'. Các cột bao gồm: Nội dung kiến thức, Đơn vị kiến thức, Số câu NB, Số câu TH, Số câu VD, Số câu VDC, Tổng số câu, Tỷ lệ (%).
                    2. BẢNG ĐẶC TẢ KỸ THUẬT ĐỀ KIỂM TRA: Thiết lập dưới dạng bảng Markdown bằng ký tự '|'. Các cột bao gồm: Nội dung kiến thức, Đơn vị kiến thức, Mức độ đánh giá, Số câu hỏi theo ma trận.
                    3. NỘI DUNG ĐỀ KIỂM TRA CHI TIẾT:
                        - Hình thức đề: {hinh_thuc}
                        - Phần Trắc nghiệm ({tong_diem_tn} điểm, {tong_cau_tn} câu): {sc_nhieu_lua_chon} câu nhiều lựa chọn, {sc_dung_sai} câu đúng sai.
                        - Phần Tự luận ({tong_diem_tl} điểm): Phân bổ câu {chuỗi_điểm_tl}
                        - Tỷ lệ nhận thức: Nhận biết {tl_nhan_biet}%, Thông hiểu {tl_thong_hieu}%, Vận dụng {tl_van_dung}%, Vận dụng cao {tl_vd_cao}%.
                        - Yêu cầu bổ sung: {yeu_cau_khac}
                    
                    [FILE ĐỀ CƯƠNG KIẾN THỨC GỐC]:
                    {noi_dung_de_cuong if 'noi_dung_de_cuong' in locals() and noi_dung_de_cuong else "Theo phân phối chương trình học chuẩn."}
                    
                    [FILE MA TRẬN ĐỂ BẮT CHƯỚC (NẾU CÓ)]:
                    {noi_dung_ma_tran if 'noi_dung_ma_tran' in locals() and noi_dung_ma_tran else "Tự sinh dựa theo số lượng câu trên giao diện."}
                    
                    QUY ĐỊNH ĐỊNH DẠNG: Công thức toán đặt trong $...$, các đáp án trắc nghiệm A., B., C., D. bắt buộc viết tách dòng độc lập.
                    """
                    ket_qua, model_thuc_te = run_ai_prompt_safe_func(prompt_vi_mo, mo_hinh_uu_tien)
                    st.session_state["ket_qua_de"] = ket_qua
                    st.session_state["model_dung"] = model_thuc_te
                    
                    if "⚠️" not in ket_qua and "Lỗi" not in ket_qua:
                        success = sync_exam_to_google_sheet(
                            st.session_state["save_ten_de"], 
                            st.session_state["save_mon_hoc"], 
                            st.session_state["save_khoi_lop"], 
                            st.session_state["save_thoi_gian"], 
                            ket_qua
                        )
                        if success:
                            st.toast("🎉 Đã lưu trữ và đồng bộ đề thi thành công lên Google Sheet!", icon="🚀")

        if st.session_state["ket_qua_de"]:
            st.info(f"🤖 Đề thi được xây dựng thành công bằng mô hình thực tế: `{st.session_state['model_dung']}`")
            st.markdown("### 📝 Xem trước nội dung đề thi:")
            st.markdown(st.session_state["ket_qua_de"])
            
            data_word = export_to_docx_vietnam_standard(
                st.session_state["ket_qua_de"], 
                st.session_state["save_ten_de"], 
                school_name=st.session_state["save_school"]
            )
            st.download_button(
                label="📥 Tải tệp Đề kiểm tra Word (.docx) bản chuẩn hành chính",
                data=data_word,
                file_name=f"De_Kiem_Tra_{st.session_state['save_khoi_lop'].replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
            
    with tab_thu_muc:
        st.write("📂 Danh sách các đề kiểm tra đã đồng bộ và lưu trữ thành công:")
        st.markdown(f"🔗 [Bấm vào đây để mở trực tiếp Google Sheets quản lý đề thi](https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit)")
