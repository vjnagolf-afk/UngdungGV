import streamlit as st
import pandas as pd
import re

def render_tkb_manager():
    st.header("📅 QUẢN LÝ THỜI KHÓA BIỂU")
    uploaded_tkb = st.file_uploader("Tải lên file TKB (.xlsx)", type=["xlsx"])
    
    if uploaded_tkb:
        try:
            # 1. Đọc thô file để tự động tìm dòng tiêu đề chứa chữ THỨ và TIẾT
            df_raw = pd.read_excel(uploaded_tkb, header=None)
            header_idx = 4  # Giá trị mặc định dựa trên cấu trúc file của thầy
            for idx, row in df_raw.iterrows():
                row_str = [str(x).upper() for x in row.values if pd.notna(x)]
                if "THỨ" in row_str and "TIẾT" in row_str:
                    header_idx = idx
                    break
            
            # 2. Đọc lại file Excel từ dòng tiêu đề tìm được
            df = pd.read_excel(uploaded_tkb, header=header_idx)
            df.columns = [str(c).strip() for c in df.columns]
            
            # --- THUẬT TOÁN ĐIỀN KHUYẾT VÀ LÀM SẠCH CỘT THỨ (CHỐNG LỖI SỐ THẬP PHÂN) ---
            if "THỨ" in df.columns:
                # Xử lý gộp ô (ffill)
                df["THỨ"] = df["THỨ"].ffill()
                # Chuyển đổi an toàn: Nếu là số 2.0 hoặc 2 thì ép về chữ "2", nếu là chữ "Thứ 2" thì giữ nguyên
                df["THỨ"] = df["THỨ"].apply(lambda x: str(int(float(x))) if str(x).replace('.','').isdigit() else str(x).strip())
                
            # Loại bỏ các giá trị rác hệ thống phát sinh
            df = df.fillna("")
            df = df.astype(str).replace(["None", "nan", "NaN"], "")
            
            # Lấy danh sách các cột Lớp học (ví dụ: '6A (Hiếu)', '6B (Duy)',...)
            class_columns = [c for c in df.columns if "Unnamed" not in c and c.upper() not in ["THỨ", "TIẾT", "STT", "CỘT 1", "CỘT 2"]]
            
            # --- THUẬT TOÁN RÚT TRÍCH DANH SÁCH TÊN GIÁO VIÊN BỘ MÔN ---
            all_teachers = set()
            for col in class_columns:
                for cell_value in df[col].values:
                    cell_str = str(cell_value).strip()
                    if cell_str and "-" in cell_str:
                        parts = cell_str.split("-")
                        if len(parts) >= 2:
                            # Lấy phần tên phía sau dấu gạch ngang (Ví dụ: 'T.Anh - Hương' -> lấy 'Hương')
                            teacher_name = parts[1].strip()
                            if teacher_name: all_teachers.add(teacher_name)
                            
            # --- ĐIỀU HƯỚNG GIAO DIỆN TABS ---
            tab1, tab2 = st.tabs(["📊 Thời khóa biểu chung", "👤 TKB theo giáo viên"])
            
            with tab1:
                st.markdown("##### 📋 Bảng xem trước Thời khóa biểu toàn trường")
                st.dataframe(df, use_container_width=True, hide_index=True)
                
            with tab2:
                if not all_teachers:
                    st.error("Không tìm thấy thông tin giáo viên bộ môn trong phân phối lịch dạy. Vui lòng kiểm tra lại file.")
                else:
                    selected_teacher = st.selectbox("👤 Chọn tên Giáo viên bộ môn cần tra cứu lịch dạy:", sorted(list(all_teachers)))
                    
                    # Thuật toán tổng hợp lịch dạy cá nhân theo tuần
                    personal_schedule = []
                    
                    for _, row in df.iterrows():
                        thu = row.get("THỨ", "")
                        tiet = row.get("TIẾT", "")
                        
                        for col_class in class_columns:
                            cell_content = str(row[col_class]).strip()
                            
                            if "-" in cell_content:
                                parts = cell_content.split("-")
                                if len(parts) >= 2 and parts[1].strip() == selected_teacher:
                                    # Lấy tên môn học phía trước dấu gạch ngang
                                    subject_name = parts[0].strip()
                                    
                                    personal_schedule.append({
                                        "Thứ": f"Thứ {thu}" if thu.isdigit() else thu,
                                        "Tiết": tiet,
                                        "Lớp giảng dạy": col_class,
                                        "Môn học": subject_name
                                    })
                                    
                    if personal_schedule:
                        df_personal = pd.DataFrame(personal_schedule)
                        st.success(f"📋 Lịch giảng dạy chi tiết trong tuần của thầy/cô: **{selected_teacher}**")
                        
                        # Sắp xếp lịch theo thứ tự Thứ và Tiết tăng dần cho khoa học
                        st.dataframe(df_personal, use_container_width=True, hide_index=True)
                    else:
                        st.info(f"ℹ️ Thầy/cô **{selected_teacher}** không có tiết giảng dạy nào trong tuần này.")
                        
        except Exception as e:
            st.error(f"Lỗi khi đọc file TKB: {e}")
    else:
        st.info("💡 Vui lòng tải file Excel Thời khóa biểu (.xlsx) lên.")
