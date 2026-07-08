import streamlit as st
import sqlite3
import pandas as pd
import io
import re

DB_PATH = "teacher_assistant.db"

# --- 1. KHỞI TẠO CẤU TRÚC DỮ LIỆU THÀNH VIÊN VÀ THI ĐUA ĐA NĂM HỌC ---
def setup_org_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tạo bảng danh sách thành viên cố định của tổ
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS org_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT UNIQUE, position TEXT, main_subject TEXT, email TEXT, phone TEXT, note TEXT
    )
    """)
    
    # Tạo bảng lưu thi đua thành tích phân tách có cột năm học (school_year)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS org_emulation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_year TEXT, fullname TEXT, good_lessons INTEGER DEFAULT 0,
        skkn_count INTEGER DEFAULT 0, hsg_count INTEGER DEFAULT 0,
        emulation_title TEXT DEFAULT 'Lao động tiên tiến',
        UNIQUE(school_year, fullname)
    )
    """)
    
    # Tự động nạp dữ liệu gốc 9 thầy cô THCS Nguyễn Chí Thanh (Nếu hệ thống trống)
    cursor.execute("SELECT COUNT(*) FROM org_members")
    if cursor.fetchone()[0] == 0:
        danh_sach_goc = [
            ("Lê Hồng Dưỡng", "Tổ trưởng", "KHTN (Vật lý) - CN", "vjnagolf@gmail.com", "0984331778", ""),
            ("Nguyễn Thị Huyền Trang", "Tổ viên", "KHTN (Vật lý) - CN", "nthtrangnct@gmail.com", "", ""),
            ("Lý Nguyễn Thu Nhi", "Tổ viên", "KHTN (Vật lý) - CN", "nthtrangnct@gmail.com", "", ""),
            ("Lê Hùng Cường", "Tổ viên", "KHTN (Vật lý) - CN", "nthtrangnct@gmail.com", "", ""),
            ("Khương Thị Thúy Vân", "Tổ viên", "KHTN (Sinh)", "nthtrangnct@gmail.com", "", ""),
            ("Trần Xuân Hạnh", "Tổ viên", "GDTC", "nthtrangnct@gmail.com", "", ""),
            ("Trương Vĩnh Văn", "Tổ viên", "KHTN (Sinh) - GDTC", "nthtrangnct@gmail.com", "", ""),
            ("Phạm Xuân Thọ", "Tổ viên", "KHTN (Sinh) - GDTC", "nthtrangnct@gmail.com", "", ""),
            ("Phạm Thùy Ngoan", "Tổ viên", "KHTN (Hóa)", "", "", "")
        ]
        for row in danh_sach_goc:
            cursor.execute("INSERT OR IGNORE INTO org_members (fullname, position, main_subject, email, phone, note) VALUES (?, ?, ?, ?, ?, ?)", row)
            
    conn.commit()
    conn.close()
def render_org_section():
    setup_org_database()
    
    # --- 2. SIDEBAR ĐĂNG NHẬP PHÂN QUYỀN MÃ PIN ADMIN ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔒 CHỌN VAI TRÒ ĐĂNG NHẬP")
    vai_tro = st.sidebar.selectbox("Vai trò", ["Giáo viên bộ môn", "Tổ trưởng chuyên môn (Admin)", "Ban giám hiệu"], label_visibility="collapsed")
    
    is_admin = False
    if vai_tro == "Tổ trưởng chuyên môn (Admin)":
        st.sidebar.caption("Nhập mã pin quản lý Admin:")
        ma_pin = st.sidebar.text_input("Mã PIN", type="password", value="", label_visibility="collapsed")
        if ma_pin == "123456":
            st.sidebar.success("✅ Quyền Admin đã mở.")
            is_admin = True
        elif ma_pin != "":
            st.sidebar.error("❌ Mã PIN không chính xác.")

    st.subheader("📋 HỆ THỐNG QUẢN LÝ VÀ PHÂN CÔNG CHUYÊN MÔN GIẢNG DẠY")
    tab1, tab2, tab3 = st.tabs(["👥 Danh sách thành viên", "📊 Phân công giảng dạy", "🏅 Thành tích & Thi đua"])
    
    # ==================== THẺ 1: DANH SÁCH THÀNH VIÊN TỔ ====================
    with tab1:
        st.markdown("#### 👥 Danh sách thành viên tổ chuyên môn")
        if is_admin:
            with st.expander("➕ BIỂU MẪU THÊM/CẬP NHẬT THÀNH VIÊN"):
                with st.form("form_add_member", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    m_name = c1.text_input("Họ và tên giáo viên:")
                    m_pos = c2.selectbox("Chức vụ:", ["Tổ viên", "Tổ trưởng", "Tổ phó", "Nhóm trưởng"])
                    m_sub = c1.text_input("Phân môn chính:")
                    m_mail = c2.text_input("Email:")
                    m_phone = c1.text_input("Số điện thoại:")
                    m_note = c2.text_input("Ghi chú:")
                    if st.form_submit_button("💾 Lưu nhân sự vĩnh viễn"):
                        if m_name:
                            conn = sqlite3.connect(DB_PATH)
                            cursor = conn.cursor()
                            cursor.execute("INSERT OR REPLACE INTO org_members (fullname, position, main_subject, email, phone, note) VALUES (?, ?, ?, ?, ?, ?)", (m_name.strip(), m_pos, m_sub.strip(), m_mail.strip(), m_phone.strip(), m_note.strip()))
                            conn.commit()
                            conn.close()
                            st.success(f"Đã cập nhật thầy/cô {m_name} vào danh sách tổ!")
                            st.rerun()

        conn = sqlite3.connect(DB_PATH)
        df_members = pd.read_sql_query("SELECT fullname as [Họ và tên], position as [Chức vụ], main_subject as [Phân môn chính], email as [Email], phone as [Số điện thoại], note as [Ghi chú] FROM org_members", conn)
        conn.close()

        if not df_members.empty:
            df_members.insert(0, "STT", range(1, len(df_members) + 1))
            st.dataframe(df_members, use_container_width=True, hide_index=True)
            st.session_state["db_thanh_vien"] = df_members.to_dict(orient="records")
        else:
            st.caption("Chưa có dữ liệu thành viên tổ.")
    # ==================== THẺ 2: SƠ ĐỒ PHÂN CÔNG GIẢNG DẠY CHUẨN 7 CỘT ====================
    with tab2:
        st.markdown("#### 📊 Sơ đồ Phân công giảng dạy của Tổ chuyên môn")
        
        # Đọc dữ liệu thô từ TKB đợt gần nhất có trong hệ thống để tự trích xuất phân công
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT version_name FROM tkb_data ORDER BY id DESC LIMIT 1")
        last_version = cursor.fetchone()
        
        rows_pc = []
        # Lấy danh sách họ tên từ bảng thành viên làm gốc để phân tích
        cursor.execute("SELECT fullname, position FROM org_members")
        all_gv_db = cursor.fetchall()
        
        if last_version:
            v_name = last_version[0]
            df_tkb_raw = pd.read_sql_query("SELECT thu, tiet, lop, noi_dung FROM tkb_data WHERE version_name = ?", conn, params=[v_name])
            
            for idx, (gv_name, chuc_vu) in enumerate(all_gv_db):
                gv_short_name = gv_name.split()[-1] # Lấy tên viết tắt cuối dòng (ví dụ Lê Hồng Dưỡng -> lấy Dưỡng)
                
                # Thuật toán quét và gom các lớp giảng dạy của giáo viên này từ TKB ngầm
                mon_lop_set = set()
                total_tiets = 0
                chu_nhiem = ""
                
                for _, r in df_tkb_raw.iterrows():
                    cell = str(r["noi_dung"]).strip()
                    c_lop = str(r["lop"]).strip()
                    
                    # Kiểm tra GV chủ nhiệm (nằm trong dấu ngoặc ở tiêu đề cột lớp)
                    if gv_short_name in c_lop:
                        chu_nhiem = c_lop.split("(")[0].strip()
                        
                    if "-" in cell:
                        parts = cell.split("-")
                        if len(parts) >= 2 and parts[-1].strip() == gv_short_name:
                            mon_lop_set.add(f"{parts[0].strip()}-{c_lop.split('(')[0].strip()}")
                            total_tiets += 1
                            
                rows_pc.append({
                    "STT": idx + 1,
                    "Họ tên GV": gv_name,
                    "Môn-Lớp": ", ".join(sorted(list(mon_lop_set))) if mon_lop_set else "Chưa xếp lịch",
                    "Chủ nhiệm": chu_nhiem if chu_nhiem else "Không",
                    "Kiêm nhiệm": "Tổ trưởng chuyên môn" if "Tổ trưởng" in chuc_vu else "Không",
                    "Tổng số tiết": f"{total_tiets} Tiết/Tuần"
                })
        else:
            # Nếu chưa nạp TKB, dựng khung bảng mẫu rỗng để giáo viên điền
            for idx, (gv_name, chuc_vu) in enumerate(all_gv_db):
                rows_pc.append({
                    "STT": idx + 1, "Họ tên GV": gv_name, "Môn-Lớp": "", "Chủ nhiệm": "Không",
                    "Kiêm nhiệm": "Tổ trưởng" if "Tổ trưởng" in chuc_vu else "Không", "Tổng số tiết": "0 Tiết"
                })
        conn.close()
        
        df_pc_view = pd.DataFrame(rows_pc)
        st.dataframe(df_pc_view, use_container_width=True, hide_index=True)
    # ==================== THẺ 3: THÀNH TÍCH THI ĐUA ĐA NĂM HỌC (XỔ MENU 2020 - 2035) ====================
    with tab3:
        st.markdown("#### 🏆 Bảng theo dõi Thành tích & Thi đua Tổ chuyên môn")
        
        # 💥 TẠO MENU XỔ XUỐNG CHỌN NĂM HỌC THEO YÊU CẦU ĐỘC LẬP
        years_options = [f"Năm học {y}-{y+1}" for y in range(2020, 2035)]
        selected_year = st.selectbox("Chọn Niên khóa / Năm học tra cứu dữ liệu thi đua:", years_options, index=5) # Mặc định năm học 2025-2026
        
        if is_admin:
            with st.expander(f"🛠️ BIỂU MẪU GHI ĐIỂM THI ĐUA - KHỐI {selected_year.upper()}"):
                conn = sqlite3.connect(DB_PATH)
                df_all_gv = pd.read_sql_query("SELECT fullname FROM org_members", conn)
                conn.close()
                list_names = df_all_gv["fullname"].tolist() if not df_all_gv.empty else []
                
                if not list_names:
                    st.warning("Vui lòng thêm thành viên ở Tab 1 trước.")
                else:
                    with st.form("form_update_emulation_year"):
                        gv_select = st.selectbox("Chọn Giáo viên:", sorted(list_names))
                        col_e1, col_e2, col_e3 = st.columns(3)
                        s_tot = col_e1.number_input("Số tiết dạy xếp loại TỐT:", min_value=0, value=0, step=1)
                        s_skkn = col_e2.number_input("Số Sáng kiến kinh nghiệm (SKKN):", min_value=0, value=0, step=1)
                        s_hsg = col_e3.number_input("Số giải Học sinh giỏi (HSG):", min_value=0, value=0, step=1)
                        danh_hieu = st.selectbox("Danh hiệu thi đua:", ["Lao động tiên tiến", "Chiến sĩ thi đua cơ sở", "Bằng khen cấp Bộ", "Bằng khen cấp Tỉnh", "Giáo viên dạy giỏi cấp Huyện"])
                        
                        if st.form_submit_button(f"💾 Chốt lưu vào sổ thi đua {selected_year}"):
                            conn = sqlite3.connect(DB_PATH)
                            cursor = conn.cursor()
                            cursor.execute("""
                            INSERT OR REPLACE INTO org_emulation (school_year, fullname, good_lessons, skkn_count, hsg_count, emulation_title)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """, (selected_year, gv_select, s_tot, s_skkn, s_hsg, danh_hieu))
                            conn.commit()
                            conn.close()
                            st.success(f"🎉 Đã lưu thành tích năm {selected_year} cho thầy/cô {gv_select}!")
                            st.rerun()

        # Truy vấn kết xuất bảng dữ liệu thi đua lọc khít theo năm học được lựa chọn
        conn = sqlite3.connect(DB_PATH)
        df_emulation = pd.read_sql_query("""
            SELECT fullname as [Họ và tên giáo viên], good_lessons as [Số tiết dạy Tốt], 
                   skkn_count as [Số SKKN đạt duyệt], hsg_count as [Số giải HSG đạt], 
                   emulation_title as [Danh hiệu thi đua]
            FROM org_emulation WHERE school_year = ?
        """, conn, params=[selected_year])
        conn.close()

        if not df_emulation.empty:
            df_emulation.insert(0, "STT", range(1, len(df_emulation) + 1))
            st.dataframe(df_emulation, use_container_width=True, hide_index=True)
            
            output_org = io.BytesIO()
            with pd.ExcelWriter(output_org, engine='openpyxl') as writer:
                df_emulation.to_excel(writer, index=False, sheet_name="Thi_Dua")
            st.download_button(
                label=f"📥 Xuất file báo cáo sổ thi đua {selected_year} (.xlsx)",
                data=output_org.getvalue(), file_name=f"Thi_Dua_{selected_year.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True
            )
        else:
            st.caption(f"ℹ️ Không có dữ liệu thi đua cho **{selected_year}**. Tổ trưởng vui lòng bật quyền Admin để nhập.")

# --- 5. CÁC HÀM QUẢN LÝ VỆ TINH PHỤ TRỢ (Giữ nguyên cho app.py gọi) ---
def render_meeting_minutes():
    st.header("📝 BIÊN BẢN SINH HOẠT TỔ")
    st.write("Giao diện quản lý nội dung các buổi họp chuyên môn định kỳ.")

def render_personal_plan():
    st.header("📅 KẾ HOẠCH GIÁO DỤC CÁ NHÂN")
    st.write("Giao diện lập kế hoạch cá nhân (Phụ lục III - 5512).")
