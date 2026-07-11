import streamlit as st
import sys
import os

# Đường dẫn gốc
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def render_teaching_assistant_section():
    st.title("🌱 Hỗ trợ Giảng dạy")
    
    # Định nghĩa các tab - Giữ nguyên thứ tự để bảo toàn giao diện
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
        
    # 2. Tab Ra đề kiểm tra (Gọi đúng hàm render_exam_designer_section)
    with tabs[1]:
        from exam_designer import render_exam_designer_section
        from ai_service import run_ai_prompt_safe
        # Gọi đúng tên hàm mà file exam_designer.py của thầy đang chứa
        render_exam_designer_section(run_ai_prompt_safe)
            
    # 3. Tab KHBD
    with tabs[2]:
        try:
            from teaching_assistant.lesson_plan_module.manager import render_lesson_plan
            render_lesson_plan()
        except ImportError:
            st.warning("Module KHBD đang được thiết lập.")

    # 4. Tab Học liệu
    with tabs[3]:
        st.write("Quản lý học liệu...")
        
    # 5. Tab Phân tích
    with tabs[4]:
        st.write("Phân tích dữ liệu...")
