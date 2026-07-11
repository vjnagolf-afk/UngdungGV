import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st

def render_teaching_assistant_section():
    st.title("🌱 Hỗ trợ Giảng dạy")
    
    # Định nghĩa danh sách các tab
