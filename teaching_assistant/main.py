import streamlit as st
import sys
import os

# Đường dẫn gốc
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def render_teaching_assistant_section():
    st.title("🌱 Hỗ trợ Giảng dạy")
    
    # Định nghĩa các tab chức năng
    import streamlit as st

def render_teaching_assistant_section():
    st.title("🌱 Hỗ trợ Giảng dạy")
    
    # Định nghĩa các tab - Thầy giữ nguyên thứ tự này để không làm thay đổi giao diện
    tabs = st.tabs([
        "Hỏi-Đáp (RAG)", 
        "Ra đề kiểm tra", 
        "Xây dựng KHBD", 
        "Học liệu", 
        "Phân tích"
    ])
    
    # 1. Tab RAG (Hỏi đáp)
    with tabs[0]:
        from teaching_assistant.rag_module.manager import render_rag
        render_rag()
        
    # 2. Tab Ra đề kiểm tra (Gọi trực tiếp file ở thư mục gốc)
    with tabs[1]:
        # Giả sử hàm hiển thị trong exam_designer.py là render_exam_designer_section
        from exam_designer import render_exam_designer_section
        from ai_service import run_ai_prompt_safe
        render_exam_designer_section(run_ai_prompt_safe)
            
    # 3. Tab KHBD (Dành chỗ để thầy gọi module KHBD sau)
    with tabs[2]:
        st.info("Chức năng Xây dựng KHBD đang được hoàn thiện.")

    # 4 & 5. Các tab còn lại thầy giữ nguyên code cũ của thầy vào đây
    with tabs[3]:
        st.write("Quản lý học liệu...")
    with tabs[4]:
        st.write("Phân tích dữ liệu...")
    
    # Liên kết module RAG (đã hoàn thiện)
    with tabs[0]:
        from teaching_assistant.rag_module.manager import render_rag
        render_rag()
        
    # Liên kết module Ra đề (Thầy cần tạo file exam_module/manager.py)
    with tabs[1]:
        # Gọi trực tiếp tệp ở thư mục gốc
        import exam_designer
        exam_designer.render_exam_interface() # Thầy đảm bảo hàm chính trong file exam_designer.py tên là render_exam_interface            
    # Liên kết module KHBD (Thầy cần tạo file lesson_plan_module/manager.py)
    with tabs[2]:
        try:
            from teaching_assistant.lesson_plan_module.manager import render_lesson_plan
            render_lesson_plan()
        except ImportError:
            st.warning("Module KHBD đang được thiết lập. Vui lòng kiểm tra file `lesson_plan_module/manager.py`.")

    # ... các tab khác ...
