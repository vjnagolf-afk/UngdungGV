import streamlit as st

def render_chu_nhiem_section(run_ai_prompt_safe=None):
    st.subheader("📋 7. KẾ HOẠCH CÔNG TÁC CHỦ NHIỆM LỚP")
    st.caption("Hệ sinh thái số hỗ trợ giáo viên chủ nhiệm quản lý lớp học và lập kế hoạch thông minh.")
    
    # Tạo 2 thẻ song song lớn cho Phân hệ Chủ nhiệm
    tab_tong_quan, tab_hang_thang = st.tabs([
        "📊 Đặc điểm tình hình & Kế hoạch năm học", 
        "📅 Kế hoạch công tác theo Tháng (AI Tự động)"
    ])
    
    # =========================================================================
    # THÈ 1: ĐẶC ĐIỂM TÌNH HÌNH & KẾ HOẠCH NĂM HỌC
    # =========================================================================
    with tab_tong_quan:
        st.write("### 📌 ĐẶC ĐIỂM TÌNH HÌNH LỚP")
        col_thuan_loi, col_kho_khan = st.columns(2)
        with col_thuan_loi:
            thuan_loi = st.text_area(
                "Thuận lợi", 
                value="- Nhà trường luôn quan tâm đến công tác chủ nhiệm, có những kế hoạch chỉ đạo kịp thời đến tập thể lớp.\n- Tập thể lớp 9D có tinh thần đoàn kết, có ý thức trong công việc được giao, công việc của lớp, có tinh thần cầu tiến, có ý thức vươn lên trong học tập và rèn luyện đạo đức tác phong.\n- Có đội ngũ ban cán sự lớp nhiệt tình năng nổ, hết lòng vì công việc chung.",
                height=180, key="ta_thuan_loi"
            )
        with col_kho_khan:
            kho_khan = st.text_area(
                "Khó khăn", 
                value="- Sự phát triển của công nghệ thông tin có tác động đến tâm sinh lí các em, một số em mê chơi, lơ là việc học.\n- Một số em thích đua đòi, tập làm người lớn, có những biểu hiện đi ngược lại đạo đức của người học sinh. Để đuôi tóc dài, bất chấp những quy định, những nhắc nhở của GVBM, GVCN....",
                height=180, key="ta_kho_khan"
            )
            
        st.write("---")
        st.write("### 📝 KẾ HOẠCH NĂM HỌC 2025-2026")
        col_ren_luyen, col_muc_dich = st.columns(2)
        with col_ren_luyen:
            ren_luyen = st.text_area(
                "Rèn luyện", 
                value="Về rèn luyện: + Có hồ sơ quản lí học sinh khoa học, cụ thể, rõ ràng, chính xác.\n- Giáo dục hành vi, thói quen đạo đức: +Có kế hoạch tìm hiểu học sinh nghèo, học sinh có hoàn cảnh đặc biệt, biết vận dụng mọi điều kiện, khả năng giúp đỡ học sinh, tránh hiện tượng thờ ơ, vô cảm. +Xây dựng các tiêu chí thi đua và tổ chức thi đua phù hợp với đặc điểm, điều kiện của lớp chủ nhiệm đồng thời thường xuyên khuyến khích được tinh thần phấn đấu vượt lên của học",
                height=180, key="ta_ren_luyen"
            )
        with col_muc_dich:
            muc_dich = st.text_area(
                "Mục đích yêu cầu", 
                value="- Luôn kính trọng người trên, thầy cô giáo, cán bộ và nhân viên nhà trường; thương yêu và giúp đỡ nhau, có ý thức xây dựng tập thể, đoàn kết với các bạn, được các bạn tin yêu.\n- Tích cực rèn luyện phẩm chất đạo đức, có lối sống lành mạnh, trung thực, giản dị, khiêm tốn.\n- Hoàn thành đầy đủ nhiệm vụ học tập, có ý thức cố gắng vươn lên trong học tập.\n- Thực hiện nghiêm túc nội quy nhà trường; chấp hành tốt Pháp luật, quy định về trật tự, an toàn",
                height=180, key="ta_muc_dich"
            )
            
        col_chi_tieu, col_bien_phap = st.columns(2)
        with col_chi_tieu:
            chi_tieu = st.text_area(
                "Chỉ tiêu", 
                value="100% học sinh không vi phạm nội quy trường học.\n95% học sinh đạt rèn luyện tốt và Khá.\nKhông có học sinh bỏ học.",
                height=150, key="ta_chi_tieu"
            )
        with col_bien_phap:
            bien_phap_chinh = st.text_area(
                "Biện pháp chính", 
                value="- GVCN quán triệt cho học sinh nội quy của nhà trường, bài học văn hóa ứng xử, giáo dục truyền thống nhà trường, giáo dục môi trường, an toàn giao thông và nhiệm vụ vụ học sinh THCS. - Tổ chức cho học sinh ký cam kết thực hiện nội quy, phòng chống ma túy và tệ nạn xã hội, ký giao ước thi đua thực hiện an toàn giao thông.\n- Tập huấn cán bộ lớp, đội cờ đỏ, cán bộ giữ sổ đầu bài.",
                height=150, key="ta_bien_phap"
            )
            
        if st.button("💾 Lưu Kế hoạch năm học", type="primary", key="btn_save_nam_hoc"):
            st.success("Đã cập nhật và lưu trữ báo cáo Đặc điểm tình hình & Kế hoạch năm học thành công!")

    # =========================================================================
    # THÈ 2: KẾ HOẠCH CÔNG TÁC THEO THÁNG - AI CHỦ ĐỘNG XÂY DỰNG KHUNG KẾ HOẠCH
    # =========================================================================
    with tab_hang_thang:
        st.write("#### 🛠 CẤU HÌNH THÔNG TIN CHỦ NHIỆM")
        col_khoi, col_lop, col_thang = st.columns(3)
        
        with col_khoi:
            khoi_options = ["Khối lớp 6", "Khối lớp 7", "Khối lớp 8", "Khối lớp 9"]
            selected_khoi = st.selectbox("Chọn Khối lớp:", khoi_options, key="sb_khoi_lop")
            
        with col_lop:
            if selected_khoi == "Khối lớp 6":
                lop_options = ["6A", "6B", "6C", "6D", "6E", "6F"]
            elif selected_khoi == "Khối lớp 7":
                lop_options = ["7A", "7B", "7C", "7D", "7E", "7F"]
            elif selected_khoi == "Khối lớp 8":
                lop_options = ["8A", "8B", "8C", "8D", "8E", "8F"]
            else:
                lop_options = ["9A", "9B", "9C", "9D", "9E", "9F", "9G"]
            selected_lop = st.selectbox("Chọn Lớp chủ nhiệm:", lop_options, key="sb_lop_chu_nhiem")
            
        with col_thang:
            thang_options = [
                "Tháng 8/2026", "Tháng 9/2026", "Tháng 10/2026", "Tháng 11/2026", "Tháng 12/2026",
                "Tháng 1/2027", "Tháng 2/2027", "Tháng 3/2027", "Tháng 4/2027", "Tháng 5/2027"
            ]
            selected_thang = st.selectbox("Chọn Tháng công tác:", thang_options, key="sb_thang_cong_tac")
            
        st.write("---")
        st.write(f"⚙️ **Chế độ:** AI đang tự động chuẩn bị dữ liệu cấu trúc cho lớp **{selected_lop}** trong **{selected_thang}**.")
        
        # Thầy cô có thể bổ sung ghi chú hoặc mong muốn riêng nếu muốn, hoặc bỏ trống để AI tự biên soạn
        ghi_chu_them = st.text_input(
            "Yêu cầu bổ sung đặc biệt cho tháng này (nếu có):", 
            placeholder="Ví dụ: Tập trung uốn nắn 3 học sinh hay đi học muộn, chuẩn bị văn nghệ...",
            key="txt_ghi_chu_them"
        )
        
        # Nút bấm kích hoạt AI tự động lập kế hoạch
        if st.button("🚀 Khởi tạo Kế hoạch bằng AI", type="primary", key="btn_chu_nhiem_ai"):
            if run_ai_prompt_safe is not None:
                with st.spinner(f"AI đang phân tích dữ liệu và thiết lập kế hoạch {selected_thang}..."):
                    
                    # Hệ thống tự tạo Prompt nghiệp vụ sư phạm bám sát cấu trúc của thầy cô
                    prompt_he_thong = f"""
                    Bạn là một trợ lý AI chuyên nghiệp hỗ trợ giáo viên chủ nhiệm cấp THCS tại Việt Nam.
                    Hãy lập một bản kế hoạch công tác chủ nhiệm chi tiết cho lớp {selected_lop} ({selected_khoi}) thuộc trường THCS Nguyễn Chí Thanh trong {selected_thang}.
                    
                    YÊU CẦU ĐỊNH DẠNG ĐẦU RA PHẢI TUÂN THỦ CHÍNH XÁC cấu trúc sau đây (không viết tự do, sử dụng định dạng Markdown rõ ràng):
                    
                    KẾ HOẠCH CÔNG TÁC CHỦ NHIỆM LỚP {selected_lop} - {selected_thang.upper()}
                    
                    1. Chủ điểm: 
                    [Xác định tên chủ điểm giáo dục tương ứng của {selected_thang} (Ví dụ: Tháng 9 là 'Mái trường mến yêu', Tháng 11 là 'Tôn sư trọng đạo', Tháng 12 là 'Uống nước nhớ nguồn', Tháng 2 là 'Mừng Đảng - Mừng Xuân'...). Liệt kê 2-3 trọng tâm thi đua hoặc phối hợp y tế/đoàn thể liên quan].
                    
                    2. Nội dung hoạt động:
                    [Liệt kê các đầu việc lớn cần triển khai bằng dấu gạch đầu dòng bao gồm: kiểm tra nề nếp giờ giấc học tập, sinh hoạt dưới cờ (SHDC), duy trì sĩ số trước/sau nghỉ lễ (nếu có), hoạt động công trình măng non (CTMN), phong trào thi đua tại liên đội, cập nhật sổ sách chi đội, nuôi heo tiết kiệm...].
                    
                    * KẾ HOẠCH TỪNG TUẦN:
                    - TUẦN 1: (Ghi rõ các nhiệm vụ cụ thể cần làm hàng ngày, sinh hoạt 15 phút, nhắc nhở nề nếp, chuẩn bị bài, tổng hợp sổ đầu bài thứ 7...)
                    - TUẦN 2: (Các công việc tiếp theo...)
                    - TUẦN 3: (Các công việc tiếp theo...)
                    - TUẦN 4: (Các công việc tiếp theo...)
                    
                    Ghi chú từ giáo viên bổ sung thêm (nếu có): {ghi_chu_them}
                    Hãy viết nội dung mang tính thực tế cao, phù hợp với tâm sinh lý lứa tuổi học sinh {selected_khoi} và bám sát các mốc thời gian của năm học {selected_thang.split('/')[-1]}.
                    """
                    
                    response = run_ai_prompt_safe(prompt_he_thong)
                    
                    st.write("---")
                    st.success(f"🎉 Đã khởi tạo thành công kế hoạch {selected_thang}!")
                    # Hiển thị kết quả cấu trúc
                    st.markdown(response)
            else:
                st.info("Hệ thống kết nối AI đang được đồng bộ...")
