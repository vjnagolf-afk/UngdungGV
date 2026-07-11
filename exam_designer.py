# =====================================================================
# PHẦN 1: CẤU HÌNH THƯ VIỆN & GOOGLE SHEETS TRÊN EXAM_DESIGNER.PY
# =====================================================================
import streamlit as st
import gspread
from document_processor import read_uploaded_docx, read_uploaded_pdf, export_to_docx_vietnam_standard

# Khai báo cấu hình Google Sheets của hệ thống
SPREADSHEET_ID = "1C6642jk_oQ0g9UC2By2qsNxxfQVR0MrZYj52tRdWDlY"
TAB_NAME = "DE_KT"

def get_exam_sheet():
    """Hàm kết nối và xác thực tài khoản dịch vụ Google Sheets an toàn"""
    try:
        creds_dict = None
        priority_keys = ["gspread_credentials", "GSPREAD_CREDENTIALS", "google_sheet_creds", "google_creds", "GOOGLE_KEY"]
        
        # Tìm thông tin xác thực ưu tiên trong Streamlit secrets
        for key in priority_keys:
            if key in st.secrets:
                creds_dict = st.secrets[key]
                break
                
        # Tìm kiếm dự phòng nếu không khớp từ khóa ưu tiên
        if creds_dict is None:
            for key in st.secrets.keys():
                node = st.secrets[key]
                if hasattr(node, "get") or isinstance(node, dict):
                    if node.get("type") == "service_account" or "private_key" in node:
                        creds_dict = node
                        break
        
        if creds_dict is None:
            return None
            
        gc = gspread.service_account_from_dict(creds_dict)
        sh = gc.open_by_key(SPREADSHEET_ID)
        return sh.worksheet(TAB_NAME)
    except Exception:
        return None

def sync_exam_to_google_sheet(ten_de, mon, khoi, thoi_gian, noi_dung):
    """Đồng bộ nội dung đề thi mới tạo lên bảng tính"""
    sheet = get_exam_sheet()
    if sheet:
        try:
            if len(sheet.get_all_values()) == 0:
                sheet.append_row(["Tên Đề", "Môn Học", "Khối Lớp", "Thời Gian", "Nội Dung Đề Thi"])
            sheet.append_row([ten_de, mon, khoi, thoi_gian, noi_dung])
            return True
        except Exception:
            return False
    return False

def get_all_exams_from_sheet():
    """Tải toàn bộ cơ sở dữ liệu danh sách đề thi đã lưu trữ"""
    sheet = get_exam_sheet()
    return sheet.get_all_records() if sheet else []

def delete_exam_from_sheet(row_index):
    """Xóa hàng đề thi được chọn dựa trên chỉ số index thực tế"""
    sheet = get_exam_sheet()
    if sheet:
        try:
            # +2 vì dòng 1 là tiêu đề (header) và index Google Sheet bắt đầu từ 1
            sheet.delete_rows(row_index + 2)
            return True
        except Exception:
            return False
    return False
