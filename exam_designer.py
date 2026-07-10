# exam_designer.py
import streamlit as st
from document_processor import read_uploaded_docx, read_uploaded_pdf, export_to_docx_vietnam_standard

def render_exam_designer_section(run_ai_prompt_safe_func):
    """Giao diện phân hệ thiết kế đề kiểm tra"""
    st.markdown("<h3 style='text-align: center; color: darkblue;'>📝 THIẾT KẾ ĐỀ KIỂM TRA CHUẨN QUY ĐỊNH</h3>", unsafe_allow_html=True)
    
    if "ket_qua_de" not in st.session_state: st.session_state["ket_qua_de"] = ""
    if "model_dung" not in st.session_state: st.session_state["model_dung"] = ""

    st.sidebar.markdown("---")
    st.sidebar.header("📁 CẤU HÌNH FILE MẪU & MA TRẬN")
    file_mau = st.sidebar.file_uploader("Tải lên file Ma trận hoặc Đặc tả mẫu (.docx, .pdf):", type=["docx", "pdf"])
    
    noi_dung_mau = ""
    if file_mau:
        if file_mau.name.endswith(".docx"):
            noi_dung_mau = read_uploaded_docx(file_mau)
        else:
            noi_dung_mau = read_uploaded_pdf(file_mau)
        st.sidebar.success("Đã đọc nội dung cấu trúc file mẫu thành công!")

    if not noi_dung_mau:
        noi_dung_mau = st.sidebar.text_area("Hoặc dán yêu cầu Ma trận & Đặc tả cấu trúc đề vào đây:", 
                                            value="Chương 1: Hàm số (2 câu Nhận biết, 1 câu Thông hiểu)...\nĐáp án trắc nghiệm viết độc lập xuống dòng.")

    col1, col2, col3 = st.columns(3)
    with col1:
        ten_de = st.text_input("Tên bài kiểm tra / Đề số:", value="Đề kiểm tra giữa học kỳ I")
        mon_hoc = st.text_input("Môn học:", value="Toán học")
    with col2:
        khoi_lop = st.text_input("Khối lớp:", value="Khối 12")
        thoi_gian = st.text_input("Thời gian làm bài:", value="90 phút")
    with col3:
        school = st.text_input("Tên trường:", value="TRƯỜNG THCS NGUYỄN CHÍ THANH")

    if st.button("⚡ Tiến hành sinh đề thi tự động bằng AI", type="primary"):
        with st.spinner("🧠 AI đang phân tích ma trận mẫu và tạo đề toán học định dạng LaTeX..."):
            prompt_system = f"""
            Bạn là một chuyên gia ra đề thi học thuật cấp cao tại Việt Nam. 
            Nhiệm vụ của bạn là tạo một Đề kiểm tra môn {mon_hoc} cho {khoi_lop} với chủ đề: {ten_de}.
            
            QUY ĐỊNH BẮT BUỘC VỀ MA TRẬN VÀ CẤU TRÚC:
            Hãy bám sát cấu trúc phân phối, tỷ lệ nhận biết, thông hiểu, vận dụng từ dữ liệu đặc tả mẫu sau đây:
            {noi_dung_mau}
            
            QUY ĐỊNH NGHIÊM NGẶT VỀ ĐỊNH DẠNG:
            1. CÔNG THỨC TOÁN HỌC: Tất cả các biểu thức toán, phân số, số mũ, căn thức, tổng xích-ma, kí hiệu hình học, biến số phải được đặt trong cặp dấu đô-la đơn $...$ hoặc đôi $$. Ví dụ: $A = \\pi r^2$, $(x+a)^n = \\sum_{{k=0}}^{{n}} \\binom{{n}}{{k}} x^k a^{{n-k}}$, $f(x) = \\frac{{n}}{{1!}}$. Tuyệt đối không dùng chữ viết thường tự do.
            2. XUỐNG DÒNG PHƯƠNG ÁN: Các đáp án trắc nghiệm A., B., C., D. BẮT BUỘC mỗi đáp án phải nằm riêng biệt trên một dòng mới. Tuyệt đối không viết gộp trên cùng một hàng.
               Ví dụ:
               Câu 1: Khẳng định nào đúng?
               A. Đồ thị đồng biến
               B. Đồ thị nghịch biến
               C. Hàm số vô nghiệm
               D. Hàm số có 2 nghiệm
            """
            ket_qua, model_thuc_te = run_ai_prompt_safe_func(prompt_system)
            st.session_state["ket_qua_de"] = ket_qua
            st.session_state["model_dung"] = model_thuc_te

    if st.session_state["ket_qua_de"]:
        if "error" in st.session_state["model_dung"] or "❌" in st.session_state["ket_qua_de"]:
            st.error(st.session_state["ket_qua_de"])
        else:
            st.info(f"🤖 Đề thi được tối ưu và khởi tạo thành công bởi mô hình: `{st.session_state['model_dung']}`")
            st.markdown("### 📝 Xem trước đề thi:")
            st.markdown(st.session_state["ket_qua_de"])
            
            data_word = export_to_docx_vietnam_standard(st.session_state["ket_qua_de"], ten_de, school_name=school)
            st.download_button(
                label="📥 Tải tệp Đề kiểm tra Word (.docx) bản chuẩn hành chính",
                data=data_word,
                file_name=f"De_Kiem_Tra_{khoi_lop.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
