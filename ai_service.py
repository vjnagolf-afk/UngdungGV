import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

def get_system_api_key():
    """Lấy API Key tổng dự phòng của hệ thống an toàn, chống lỗi KeyError"""
    try:
        # Kiểm tra sự tồn tại của khóa trước khi trích xuất giá trị để tránh vấp KeyError
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
        
        # Quét tìm các tên khóa dự phòng khác nếu có trong secrets
        for key in st.secrets.keys():
            if "GEMINI" in key.upper() or "API_KEY" in key.upper():
                return st.secrets[key]
    except Exception:
        pass
    return ""

def run_ai_prompt_safe(prompt_text, preferred_model="3.5 Flash", is_admin_owner=True):
    """
    Trung tâm điều phối gọi API phân luồng bảo mật tích hợp LangChain.
    - Nếu là máy của Admin: Chạy bằng Key hệ thống.
    - Nếu là máy giáo viên khác: Ép dùng Key cá nhân.
    """
    if is_admin_owner:
        api_key_to_use = get_system_api_key()
        nguon_key = "Tài khoản hệ thống (Chính chủ)"
    else:
        api_key_ca_nhan = st.session_state.get("gv_api_key_input", "").strip()
        if api_key_ca_nhan:
            api_key_to_use = api_key_ca_nhan
            nguon_key = "Tài khoản cá nhân Giáo viên"
        else:
            return "⚠️ Bạn đang truy cập từ thiết bị thành viên. Vui lòng nhập API Key Gemini cá nhân của bạn ở mục '🔑 TRẠNG THÁI TÀI KHOẢN' tại thanh bên trái để kích hoạt quyền ra đề/soạn bài!", "error"
            
    if not api_key_to_use:
        return "⚠️ Hệ thống chưa được cấu hình API Key. Vui lòng liên hệ Admin hoặc tự cung cấp mã Key cá nhân ở mục Trạng thái tài khoản để sử dụng!", "error"
    
    # Định biên danh mục mã Model ID thương mại chính thức của Google
    # Cập nhật danh sách model để tương thích tốt nhất với thời điểm hiện tại
    # Định biên danh mục mã Model ID dựa trên danh sách khả dụng thực tế của tài khoản
    model_pool = {
        "3.1 Flash-Lite": ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite"],
        "3.5 Flash": ["gemini-3.5-flash", "gemini-flash-latest"],
        "3.1 Pro": ["gemini-3.1-pro-preview", "gemini-pro-latest"],
        "Tư duy mở rộng": ["gemini-3.1-pro-preview", "gemini-2.5-pro"]
    }
    models_to_try = model_pool.get(preferred_model, ["gemini-2.5-flash", "gemini-1.5-pro"])
    
    last_error_message = "Không có thông tin lỗi cụ thể."
    
    # Vòng lặp quét lỗi (Fallback Loop) - Tự động đổi model nếu model chính gặp sự cố
    for model_name in models_to_try:
        try:
            # 1. Khởi tạo LLM bằng LangChain (thay thế cho genai.Client cũ)
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=0.3,
                google_api_key=api_key_to_use
            )
            
            # 2. Đóng gói câu hỏi vào định dạng Message của LangChain
            messages = [HumanMessage(content=prompt_text)]
            
            # 3. Gọi mô hình thực thi
            response = llm.invoke(messages)
            
            if response and response.content:
                return response.content, f"{model_name} ({nguon_key})"
            else:
                continue
                
        except Exception as e:
            error_str = str(e)
            last_error_message = f"Mô hình {model_name} báo lỗi API: {error_str}"
            
            # Phân tích thông báo lỗi để hiển thị Toast cảnh báo cho giáo viên
            if "429" in error_str or "quota" in error_str.lower():
                st.toast(f"⏳ {model_name} đạt giới hạn hạn mức. Đang lùi dòng máy...", icon="⚠️")
            elif "503" in error_str or "unavailable" in error_str.lower():
                st.toast(f"⏳ Máy chủ Google đang bận cục bộ. Tự động chuyển dòng dự phòng...", icon="🔄")
            elif "404" in error_str or "not found" in error_str.lower():
                st.toast(f"⚠️ {model_name} không khả dụng. Đang cập nhật kênh khác...", icon="🔄")
                
            continue # Tiếp tục vòng lặp với mô hình dự phòng tiếp theo
            
    return f"❌ Lỗi: Không thể phản hồi từ AI. Ghi nhận lỗi cuối cùng: {last_error_message}", "error"
