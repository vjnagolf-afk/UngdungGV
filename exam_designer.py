# exam_designer.py
import streamlit as st
from document_processor import read_uploaded_docx, read_uploaded_pdf, export_to_docx_vietnam_standard

def render_exam_designer_section(run_ai_prompt_safe_func):
    """Giao diện phân hệ thiết kế đề kiểm tra chuẩn theo sơ đồ hàng cột cũ"""
    
    if "ket_qua_de" not in st.session_state: st.session_state["ket_qua_de"] = ""
    if "model_dung" not in st.session_state: st.session_state["model_dung"] = ""

    # --- HÀNG TÁC NGHIỆP: TẠO ĐỀ & THƯ MỤC ---
    tab_tao_de, tab_thu_muc = st.tabs(["🔴 CHỨC NĂNG TẠO ĐỀ KIỂM TRA AI", "🗂️ THƯ MỤC ĐỀ ĐÃ XÂY DỰNG"])
    
    with tab_tao_de:
        # CẤU TRÚC HÀNG 1: CẤU HÌNH CHUNG & TẢI TÀI LIỆU
        col_left_h1, col_right_h1 = st.columns([1.1, 1.0])
        
        with col_left_h1:
            hinh_thuc = st.selectbox("Hình thức đề:", ["Trắc nghiệm kết hợp tự luận", "100% Trắc nghiệm", "100% Tự luận"])
            mon_hoc = st.text_input("Môn học:", value="Khoa học tự nhiên")
            khoi_lop = st.selectbox("Khối lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Khối 10", "Khối 11", "Khối 12"], index=2)
            thoi_gian = st.text_input("Thời gian:", value="45 phút")
            school = st.text_input("Tên trường hành chính:", value="TRƯỜNG THCS NGUYỄN CHÍ THANH")
            
        with col_right_h1:
            st.markdown("**TẢI TÀI LIỆU LÊN (Giới hạn kiến thức / Đề cương):**")
            file_mau = st.file_uploader("Upload (Giới hạn file .pdf, .docx):", type=["docx", "pdf"], label_visibility="collapsed")
            
            noi_dung_mau = ""
            if file_mau:
                if file_mau.name.endswith(".docx"):
                    noi_dung_mau = read_uploaded_docx(file_mau)
                else:
                    noi_dung_mau = read_uploaded_pdf(file_mau)
                st.success(f"✅ Đã tải cấu trúc tài liệu: {file_mau.name}")
            else:
                st.caption("Chưa có dữ liệu nào được tải lên hệ thống.")

        st.markdown("---")

        # CẤU TRÚC HÀNG 2: PHÂN VÙNG TRẮC NGHIỆM & TỰ LUẬN (HAI CỘT SONG SONG)
        col_tn, col_tl = st.columns([1.1, 1.0])
        
        with col_tn:
            st.markdown("<h4 style='text-align: center; background-color: #FFE4E6; color: #991B1B; padding: 5px; border-radius: 4px;'>PHẦN TRẮC NGHIỆM</h4>", unsafe_allow_html=True)
            
            col_tn_l, col_tn_r = st.columns(2)
            with col_tn_l:
                st.write("") # Căn lề hàng
                st.markdown("**Tổng số câu TNKQ:**")
                sc_nhieu_lua_chon = st.number_input("Số câu nhiều lựa chọn:", min_value=0, max_value=50, value=12)
                sc_dung_sai = st.number_input("Số câu đúng sai:", min_value=0, max_value=50, value=2)
                sc_dien_khuyết = st.number_input("Số câu điền khuyết:", min_value=0, max_value=50, value=0)
                sc_tra_loi_ngan = st.number_input("Số câu trả lời ngắn:", min_value=0, max_value=50, value=0)
            with col_tn_r:
                st.write("")
                tong_diem_tn = st.number_input("Tổng điểm TN:", value=4.00, step=0.25)
                d_nhieu_lua_chon = st.number_input("Tổng điểm dòng này:", value=3.00, step=0.25, key="d_nlc")
                d_dung_sai = st.number_input("Tổng điểm dòng này:", value=1.00, step=0.25, key="d_ds")
                d_dien_khuyết = st.number_input("Tổng điểm dòng này:", value=0.00, step=0.25, key="d_dk")
                d_tra_loi_ngan = st.number_input("Tổng điểm dòng này:", value=0.00, step=0.25, key="d_tln")
                
            tong_cau_tn = sc_nhieu_lua_chon + sc_dung_sai + sc_dien_khuyết + sc_tra_loi_ngan

        with col_tl:
            st.markdown("<h4 style='text-align: center; background-color: #DCFCE7; color: #166534; padding: 5px; border-radius: 4px;'>PHẦN TỰ LUẬN</h4>", unsafe_allow_html=True)
            
            col_tl_l, col_tl_r = st.columns(2)
            with col_tl_l:
                st.write("")
                sc_tu_luan = st.number_input("TỔNG SỐ CÂU TỰ LUẬN:", min_value=0, max_value=20, value=3)
            with col_tl_r:
                st.write("")
                tong_diem_tl = st.number_input("ĐIỂM TỔNG:", value=6.00, step=0.25)
            
            # Tự động sinh danh sách nhập điểm từng câu tự luận theo số lượng người dùng chọn
            st.markdown("Chỉ định điểm chi tiết từng câu:")
            diem_chi_tiet_tl = []
            for i in range(int(sc_tu_luan)):
                diem_cau = st.number_input(f"Câu {i+1}:", min_value=0.0, max_value=10.0, value=2.0 if i < 3 else 1.0, step=0.5, key=f"tl_c_{i}")
                diem_chi_tiet_tl.append((i+1, diem_cau))

        st.markdown("---")

        # CẤU TRÚC HÀNG 3: TỶ LỆ MỨC ĐỘ NHẬN THỨC VÀ NÚT BẤM KHỞI TẠO
        st.markdown("**Tỷ lệ mức độ nhận thức (%):**")
        col_nb, col_th, col_vd, col_vdc = st.columns(4)
        with col_nb:
            tl_nhan_biet = st.number_input("Nhận biết:", min_value=0, max_value=100, value=40, step=10)
        with col_th:
            tl_thong_hieu = st.number_input("Thông hiểu:", min_value=0, max_value=100, value=30, step=10)
        with col_vd:
            tl_van_dung = st.number_input("Vận dụng:", min_value=0, max_value=100, value=20, step=10)
        with col_vdc:
            tl_vd_cao = st.number_input("Vận dụng cao:", min_value=0, max_value=100, value=10, step=10)

        yeu_cau_khac = st.text_area("Nhập yêu cầu khác (Tùy chọn):", placeholder="Ví dụ: Đề thi có chứa 1 câu hỏi thực tế về đồ thị hàm số bậc nhất...")

        # HÀNG NÚT LỆNH ĐIỀU KHIỂN
        col_btn_l, col_btn_r = st.columns([1.5, 1.0])
        with col_btn_l:
            nut_sinh_de = st.button("🔴 Tự động khởi tạo ma trận và đề thi", type="primary", use_container_width=True)
        with col_btn_r:
            st.checkbox("Yêu cầu bám sát kiến thức trong GIÁO TRÌNH, tài liệu", value=True)

        # XỬ LÝ KHI CLICK NÚT SINH ĐỀ CHI TIẾT THEO CẤU HÌNH GIAO DIỆN CHUẨN
        if nut_sinh_de:
            if int(tl_nhan_biet + tl_thong_hieu + tl_van_dung + tl_vd_cao) != 100:
                st.error("⚠️ Tổng tỷ lệ mức độ nhận thức phải bằng 100%!")
            else:
                with st.spinner("🧠 Hệ thống đang xử lý dữ liệu và thiết lập đề thi..."):
                    # Gom toàn bộ tham số người dùng nhập từ giao diện hàng cột thành Prompt chuyên gia
                    chuỗi_điểm_tl = ", ".join([f"Câu {c_id} ({d}đ)" for c_id, d in diem_chi_tiet_tl])
                    prompt_vi_mo = f"""
                    Bạn là Chuyên gia Khảo thí và Kiểm định Chất lượng Giáo dục phổ thông. Hãy sinh Đề thi cho môn {mon_hoc} - {khoi_lop} (Thời gian: {thoi_gian}).
                    
                    TÀI LIỆU MA TRẬN NỀN TẢNG (NẾU CÓ):
                    {noi_dung_mau if noi_dung_mau else "Sử dụng phân phối chương trình SGK hiện hành."}
                    
                    QUY ĐỊNH CẤU TRÚC ĐỀ THI ĐÃ THIẾT LẬP TRÊN GIAO DIỆN:
                    - Hình thức đề: {hinh_thuc}
                    - Phần Trắc nghiệm (Tổng {tong_diem_tn} điểm, gồm {tong_cau_tn} câu):
                      + Nhiều lựa chọn: {sc_nhieu_lua_chon} câu (Chiếm {d_nhieu_lua_chon}đ)
                      + Đúng sai: {sc_dung_sai} câu (Chiếm {d_dung_sai}đ)
                      + Điền khuyết: {sc_dien_khuyết} câu (Chiếm {d_dien_khuyết}đ)
                      + Trả lời ngắn: {sc_tra_loi_ngan} câu (Chiếm {d_tra_loi_ngan}đ)
                    - Phần Tự luận (Tổng {tong_diem_tl} điểm, gồm {sc_tu_luan} câu): Định biên chi tiết: {chuỗi_điểm_tl}
                    - Tỷ lệ nhận thức yêu cầu: Nhận biết {tl_nhan_biet}%, Thông hiểu {tl_thong_hieu}%, Vận dụng {tl_van_dung}%, Vận dụng cao {tl_vd_cao}%.
                    - Yêu cầu bổ sung: {yeu_cau_khac}
                    
                    QUY ĐỊNH ĐỊNH DẠNG ĐỀ (BẮT BUỘC):
                    1. CÔNG THỨC TOÁN HỌC: Tất cả phân số, biểu thức, số mũ, biến số phải đặt gọn trong cặp ký tự $...$ hoặc $$. Ví dụ: $y = f(x)$, $\\frac{{a}}{{b}}$.
                    2. XUỐNG DÒNG PHƯƠNG ÁN: Các phương án trắc nghiệm A., B., C., D. bắt buộc viết tách dòng, mỗi đáp án nằm độc lập trên một hàng mới.
                    """
                    
                    ket_qua, model_thuc_te = run_ai_prompt_safe_func(prompt_vi_mo)
                    st.session_state["ket_qua_de"] = ket_qua
                    st.session_state["model_dung"] = model_thuc_te

        # HIỂN THỊ KẾT QUẢ KHI CÓ DỮ LIỆU
        if st.session_state["ket_qua_de"]:
            st.info(f"🤖 Đề thi được xây dựng thành công bằng mô hình: `{st.session_state['model_dung']}`")
            st.markdown("### 📝 Xem trước nội dung đề thi:")
            st.markdown(st.session_state["ket_qua_de"])
            
            data_word = export_to_docx_vietnam_standard(st.session_state["ket_qua_de"], ten_de, school_name=school)
            st.download_button(
                label="📥 Tải tệp Đề kiểm tra Word (.docx) bản chuẩn hành chính",
                data=data_word,
                file_name=f"De_Kiem_Tra_{khoi_lop.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
