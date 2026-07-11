import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st

def render_teaching_assistant_section():
    st.title("🌱 Hỗ trợ Giảng dạy")
    
    # Định nghĩa danh sách các tab
    # Nút gỡ lỗi hệ thống (Đã cập nhật cho thư viện google-genai mới)
    if st.button("🛠️ Debug: Xem danh sách Model Gemini đang hỗ trợ"):
        from google import genai
        try:
            # Khởi tạo client lấy key trực tiếp từ secrets
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            st.warning("Các tên model chính xác tài khoản của thầy có thể dùng là:")
            
            models = []
            # Duyệt qua danh sách các model được phép truy cập
            for m in client.models.list():
                models.append(m.name)
            
            st.json(models)
        except Exception as e:
            st.error(f"Lỗi truy xuất: {e}")
