import streamlit as st

def render_stem_section():
    st.markdown("## 🚀 CHỨC NĂNG XÂY DỰNG DỰ ÁN GIÁO DỤC STEM")
    st.markdown("---")
    
    # 1. Thông tin cơ bản
    st.subheader("1. Thông tin chung")
    ten_chu_de = st.text_input("Tên dự án / Chủ đề STEM:", 
                               placeholder="Ví dụ: Thiết kế hệ thống tiết kiệm năng lượng thông minh sử dụng cảm biến...")
    
    col1, col2 = st.columns(2)
    with col1:
        mon_chu_dao = st.selectbox("Môn học chủ đạo:", ["Khoa học tự nhiên", "Toán học", "Công nghệ", "Tin học"])
        lop_hoc = st.selectbox("Lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"])
    with col2:
        thoi_luong = st.text_input("Thời lượng thực hiện:", placeholder="Ví dụ: 3 Tiết")
    
    # 2. Tùy chọn chuyên sâu cho bài giảng
    st.subheader("2. Yêu cầu tích hợp & Phân hóa")
    
    tich_hop_ai_iot = st.checkbox("🔌 Tích hợp ứng dụng AI hoặc Vi điều khiển (Ví dụ: Arduino, ESP8266)")
    tich_hop_hoa_nhap = st.checkbox("🤝 Phân hóa hoạt động và câu hỏi dành cho học sinh khuyết tật (Giáo dục hòa nhập)")
    
    st.markdown("---")
    
    # 3. Nút xử lý AI
    if st.button("Kích hoạt AI thiết kế tiến trình STEM", use_container_width=True):
        if not ten_chu_de:
            st.warning("Vui lòng nhập tên chủ đề STEM!")
        else:
            with st.spinner("Hệ thống đang phân tích yêu cầu và thiết kế bài dạy..."):
                # GỌI API GOOGLE GENAI TẠI ĐÂY
                
                st.success("Tạo kế hoạch bài dạy STEM thành công!")
                # In kết quả từ AI ra màn hình
