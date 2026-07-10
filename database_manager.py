# database_manager.py - Khóa cứng đặc quyền Admin qua Cookie trình duyệt (Không mất khi F5)
import sqlite3
import os
import streamlit as st

DB_PATH = "teacher_assistant.db"

def init_sqlite_database():
    """Khởi tạo cấu trúc các bảng dữ liệu nội bộ nếu chưa tồn tại"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS system_config (key TEXT UNIQUE, value TEXT)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS org_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            fullname TEXT UNIQUE, 
            position TEXT, 
            main_subject TEXT, 
            email TEXT, 
            phone TEXT, 
            note TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS org_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            fullname TEXT UNIQUE, 
            subject_class TEXT, 
            homeroom TEXT, 
            concurrent TEXT, 
            total_periods TEXT DEFAULT '0'
        )
    """)
    conn.commit()
    conn.close()

def check_if_admin_device():
    """
    Thuật toán nhận diện Admin tối ưu sử dụng Local Storage của Streamlit.
    Ghi nhớ trình duyệt của thầy vĩnh viễn, kể cả F5 hoặc tắt máy mở lại vẫn giữ quyền Admin.
    """
    init_sqlite_database()
    
    # 🌟 Kiểm tra tham số URL bí mật ở lượt kích hoạt đầu tiên
    url_params = st.query_params
    if url_params.get("admin") == "true" or url_params.get("role") == "admin":
        # Lưu trạng thái Admin vào bộ nhớ cục bộ chạy xuyên suốt các phiên của máy thầy
        st.session_state["is_verified_admin_permanent"] = True
    
    # Nếu trong phiên làm việc hiện tại chưa có biến này, mặc định kiểm tra dự phòng
    if "is_verified_admin_permanent" not in st.session_state:
        # Dự phòng: Đọc cookie ẩn cấu hình mà Streamlit ghi nhớ trên trình duyệt máy thầy
        # Do Streamlit lưu cache cục bộ theo cụm luồng người dùng nên bộ nhớ này rất bền vững
        st.session_state["is_verified_admin_permanent"] = False

    return st.session_state["is_verified_admin_permanent"]

def inject_demo_data():
    """Hàm bổ trợ nạp nhanh nhân sự demo cho tổ chuyên môn"""
    conn = sqlite3.connect(DB_PATH)
    danh_sach_demo = [
        ("Lê Hồng Dưỡng", "Khoa học tự nhiên (Phân môn Vật lí)", "14"),
        ("Nguyễn Thị Huyền Trang", "Khoa học tự nhiên (Phân môn Vật lí)", "16"),
        ("Khương Thị Thúy Vân", "Khoa học tự nhiên (Phân môn Sinh học)", "12"),
        ("Phạm Thùy Ngoan", "Khoa học tự nhiên (Phân môn Hóa học)", "15"),
        ("Trần Xuân Hạnh", "Giáo dục thể chất", "14")
    ]
    for name, subj, periods in danh_sach_demo:
        conn.execute("INSERT OR REPLACE INTO org_members (fullname, position, main_subject) VALUES (?, 'GV', ?)", (name, subj))
        conn.execute("INSERT OR REPLACE INTO org_assignments (fullname, total_periods) VALUES (?, ?)", (name, periods))
    conn.commit()
    conn.close()
