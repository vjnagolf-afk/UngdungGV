# database_manager.py
import sqlite3
import os

DB_PATH = "teacher_assistant.db"

def init_sqlite_database():
    """Khởi tạo cấu trúc các bảng dữ liệu nội bộ nếu chưa tồn tại"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS system_config (key TEXT UNIQUE, value TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS org_members (id INTEGER PRIMARY KEY AUTOINCREMENT, fullname TEXT UNIQUE, position TEXT, main_subject TEXT, email TEXT, phone TEXT, note TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS org_assignments (id INTEGER PRIMARY KEY AUTOINCREMENT, fullname TEXT UNIQUE, subject_class TEXT, homeroom TEXT, concurrent TEXT, total_periods TEXT DEFAULT '0')")
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
# ai_service.py
import streamlit as st
from google import genai
from google.genai import errors

def get_system_api_key():
    """Lấy API Key tổng dự phòng của hệ thống"""
    return st.secrets.get("GEMINI_API_KEY", "")

def run_ai_prompt_safe(prompt_text, preferred_model="3.5 Flash", is_admin_owner=True):
    """
    Trung tâm điều phối gọi API phân luồng bảo mật.
    - Nếu là máy của Admin: Chạy thẳng bằng Key hệ thống.
    - Nếu là máy giáo viên khác: Ép dùng Key cá nhân dán ở Sidebar giao diện.
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
        return "⚠️ Hệ thống chưa được cấu hình API Key. Vui lòng liên hệ Admin hoặc tự cung cấp mã Key cá nhân!", "error"
    
    # Định biên danh mục mã Model ID thương mại chính thức của Google
    model_pool = {
        "3.1 Flash-Lite": ["gemini-2.5-flash"],
        "3.5 Flash": ["gemini-2.5-flash"],
        "3.1 Pro": ["gemini-2.5-pro", "gemini-2.5-flash"],
        "Tư duy mở rộng": ["gemini-2.5-pro", "gemini-2.5-flash"]
    }
    models_to_try = model_pool.get(preferred_model, ["gemini-2.5-flash"])
    
    last_error_message = "Không có thông tin lỗi cụ thể."
    client = genai.Client(api_key=api_key_to_use)
    
    for model_name in models_to_try:
        try:
            config_params = {}
            if preferred_model == "Tư duy mở rộng" and "pro" in model_name:
                config_params["thinking_config"] = {"thinking_budget": 2048}
            
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text,
                config=config_params if config_params else None
            )
            
            if response and response.text:
                return response.text, f"{model_name} ({nguon_key})"
            else:
                continue
                
        except errors.APIError as error:  
            last_error_message = f"Mô hình {model_name} báo lỗi API: {str(error)}"
            if "429" in str(error):
                st.toast("⏳ Mô hình đạt giới hạn hạn mức câu hỏi của ngày. Hệ thống đang lùi dòng máy...", icon="⚠️")
            continue  
        except Exception as e:
            last_error_message = f"Sự cố đường truyền: {str(e)}"
            continue
            
    return f"❌ Lỗi: Không thể phản hồi. Ghi nhận lỗi cuối cùng: {last_error_message}", "error"
# app.py
import streamlit as st
import pandas as pd
import sqlite3
import os

# Nhúng các cấu trúc module con vừa bóc tách
from database_manager import check_if_admin_device, inject_demo_data, DB_PATH
from ai_service import run_ai_prompt_safe

# Nhúng các phân hệ tác nghiệp vệ tinh của bạn
from exam_designer import render_exam_designer_section 
from grade_manager import render_grade_manager_section
from tkb_manager import render_tkb_manager  
from khbd_manager import render_khbd_section  
from danh_gia_manager import render_assessment_section

from org_manager import render_org_section
from bien_ban_manager import render_meeting_minutes
from ke_hoach_ca_nhan_manager import render_personal_plan 
from stem_manager import render_stem_section
from chu_nhiem_manager import render_chu_nhiem_section 

# Khởi chạy quét thiết bị nhận diện Admin ngay khi nạp trang
is_admin_owner = check_if_admin_device()

# Khởi tạo bộ nhớ tạm đồng bộ session
if "db_thanh_vien" not in st.session_state: st.session_state["db_thanh_vien"] = []
if "db_phan_cong_hien_tai" not in st.session_state: st.session_state["db_phan_cong_hien_tai"] = []

st.set_page_config(page_title="HỆ SINH THÁI SỐ GIÁO VIÊN", layout="wide")

# Tiêu đề giao diện chính
st.markdown("<h1 style='text-align: center; color: darkred; font-weight: bold;'>🔰 HỆ SINH THÁI SỐ - HỖ TRỢ GIÁO VIÊN</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #0056b3; font-weight: bold; font-size: 16px;'>Sản phẩm tham gia Cuộc thi AI for Life năm 2026, trường THCS Nguyễn Chí Thanh - Phường Tân Lập tỉnh Đắk Lắk</p>", unsafe_allow_html=True)
st.markdown("---")

# --- MENU ĐIỀU HƯỚNG TỔNG TẠI SIDEBAR ---
st.sidebar.markdown("### MENU HỆ THỐNG")
st.sidebar.caption("CHỌN PHÂN HỆ TÁC NGHIỆP")

phan_he = st.sidebar.radio(
    "Chọn phân hệ:",
    ["Trợ lý Giảng dạy (Giáo viên)", "Trợ lý Quản lý (Tổ chuyên môn)"],
    label_visibility="collapsed",
    key="app_main_sidebar_navigation_root_key_2026_v9"
)

# --- KHỐI HIỂN THỊ Ô NHẬP KEY THEO THIẾT BỊ ĐỐI TƯỢNG ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔑 TRẠNG THÁI TÀI KHOẢN")

if is_admin_owner:
    st.sidebar.success("👑 Thiết bị: Chủ dự án (Admin)")
    st.sidebar.caption("Tự động kích hoạt quyền đặc quyền chạy trực tiếp bằng Key hệ thống.")
    st.session_state["gv_api_key_input"] = ""
else:
    st.sidebar.warning("🔒 Thiết bị: Thành viên/Giáo viên")
    st.sidebar.caption("Vui lòng dán API Key cá nhân từ Google AI Studio để mở khóa phân hệ.")
    st.sidebar.text_input("Nhập API Key Gemini của thầy/cô:", type="password", placeholder="AIzaSy...", key="gv_api_key_input")
    if st.session_state["gv_api_key_input"]:
        st.sidebar.success("🟢 Đã nhận diện Key cá nhân.")

# --- KHỐI ĐIỀU HƯỚNG TÁC NGHIỆP CHI TIẾT ---
if phan_he == "Trợ lý Giảng dạy (Giáo viên)":
    st.sidebar.markdown("### 🛠️ CHỨC NĂNG GIÁO VIÊN")
    menu = st.sidebar.selectbox("Nội dung giảng dạy", ["1. Thiết kế KHBD", "2. Thiết kế Đề KT", "3. Đánh giá HS", "4. Quản lý điểm (SMAS)", "5. Quản lý TKB","6. Thiết kế bài dạy STEM","7. Kế hoạch công tác chủ nhiệm lớp"], label_visibility="collapsed", key="menu_gv_selectbox_v9")
    
    if menu == "1. Thiết kế KHBD": 
        render_khbd_section(lambda p, m: run_ai_prompt_safe(p, m, is_admin_owner))
    elif menu == "2. Thiết kế Đề KT": 
        render_exam_designer_section(lambda p, m: run_ai_prompt_safe(p, m, is_admin_owner))
    elif menu == "3. Đánh giá HS": 
        render_assessment_section(lambda p: run_ai_prompt_safe(p, is_admin_owner=is_admin_owner))
    elif menu == "4. Quản lý điểm (SMAS)": 
        render_grade_manager_section()
    elif menu == "5. Quản lý TKB": 
        render_tkb_manager()
    elif menu == "6. Thiết kế bài dạy STEM":
        render_stem_section()
    elif menu == "7. Kế hoạch công tác chủ nhiệm lớp":
        render_chu_nhiem_section(lambda p: run_ai_prompt_safe(p, is_admin_owner=is_admin_owner))

else:  # Phân hệ Quản lý tổ chuyên môn
    st.sidebar.markdown("### 📂 QUẢN LÝ TỔ CHUYÊN MÔN")
    menu = st.sidebar.selectbox("Nội dung quản lý", ["1. Quản lý & Phân công chuyên môn", "2. Biên bản sinh hoạt", "3. Kế hoạch cá nhân", "4. Thống kê số liệu"], label_visibility="collapsed", key="menu_ql_selectbox_v9")
    
    if menu == "1. Quản lý & Phân công chuyên môn": 
        render_org_section()
    elif menu == "2. Biên bản sinh hoạt": 
        render_meeting_minutes(lambda p: run_ai_prompt_safe(p, is_admin_owner=is_admin_owner))
    elif menu == "3. Kế hoạch cá nhân": 
        render_personal_plan(lambda p: run_ai_prompt_safe(p, is_admin_owner=is_admin_owner))
    elif menu == "4. Thống kê số liệu": 
        st.header("📊 THỐNG KÊ SỐ LIỆU TỔ CHUYÊN MÔN")
        
        df_tv = pd.DataFrame()
        if os.path.exists(DB_PATH):
            try:
                conn = sqlite3.connect(DB_PATH)
                query = "SELECT m.fullname as [Họ và tên], m.main_subject as [Phân môn chính], a.total_periods as [Số tiết/Tuần] FROM org_members m LEFT JOIN org_assignments a ON m.fullname = a.fullname"
                df_tv = pd.read_sql_query(query, conn)
                conn.close()
            except Exception as e:
                st.error(f"⚠️ Lỗi kết nối cơ sở dữ liệu nội bộ: {str(e)}")
        
        thuc_te_co_du_lieu = not df_tv.empty and len(df_tv) > 0 and not (df_tv["Phân môn chính"] == "").all()

        if not thuc_te_co_du_lieu:
            st.warning("ℹ️ Hiện tại chưa có dữ liệu giáo viên nào được nhập từ phân hệ '1. Quản lý & Phân công chuyên môn'.")
            if st.button("💡 Nạp nhanh dữ liệu mẫu để thử nghiệm biểu đồ", type="primary", use_container_width=True):
                try:
                    inject_demo_data()
                    st.success("🎉 Đã nạp dữ liệu thử nghiệm trực tiếp vào SQLite!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Không thể nạp dữ liệu mẫu: {str(e)}")
        else:
            st.subheader("📋 Danh sách phân công hiện tại:")
            st.dataframe(df_tv, use_container_width=True)
