# database_manager.py
import sqlite3
import os

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
    Quét ID session trình duyệt mở link web.
    Máy đầu tiên click vào ứng dụng sẽ được lưu cấu hình làm thiết bị Admin (Chính chủ).
    """
    init_sqlite_database()
    
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        current_session_id = ctx.session_id if ctx else "default_session"
    except:
        current_session_id = "unknown_session"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT value FROM system_config WHERE key = 'admin_session_id'")
    row = cursor.fetchone()
    
    if row is None:
        # Nếu database trống, ghi nhận ID thiết bị của bạn làm Admin vĩnh viễn
        cursor.execute("INSERT INTO system_config (key, value) VALUES ('admin_session_id', ?)", (current_session_id,))
        conn.commit()
        conn.close()
        return True
    else:
        admin_id = row[0]
        conn.close()
        return current_session_id == admin_id

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
