import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Cấu hình Google Sheets và Google Drive
# Vui lòng thay thế 'your_service_account_key.json' bằng tên file key của bạn.
# Bạn cần tạo file này từ Google Cloud Console và chia sẻ quyền truy cập Google Sheet cho email của service account đó.
GDRIVE_CLIENT_SECRET = 'your_service_account_key.json'
SPREADSHEET_NAME = 'FieldDataCollection'
WORKSHEET_NAME = 'Sheet1'

# Hàm để xác thực và kết nối đến Google Sheets
@st.cache_resource
def get_gspread_client():
    try:
        # Sử dụng service account để xác thực
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(GDRIVE_CLIENT_SECRET, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Lỗi kết nối Google Sheets: {e}")
        return None

# Hàm để kết nối đến Google Drive (để tải ảnh lên)
@st.cache_resource
def get_drive_client():
    try:
        gauth = GoogleAuth()
        # Xác thực với service account
        gauth.LoadCredentialsFile(GDRIVE_CLIENT_SECRET)
        if gauth.access_token_expired:
            gauth.Refresh()
        drive = GoogleDrive(gauth)
        return drive
    except Exception as e:
        st.error(f"Lỗi kết nối Google Drive: {e}")
        return None

# Hàm để tải ảnh lên Google Drive và trả về link
def upload_image_to_drive(drive_client, file_obj):
    if not drive_client:
        return None
    try:
        # Tạo file trên Google Drive
        gfile = drive_client.CreateFile({'title': file_obj.name})
        gfile.Upload()
        # Trả về link để xem hoặc chia sẻ
        return gfile['alternateLink']
    except Exception as e:
        st.error(f"Lỗi tải ảnh lên Google Drive: {e}")
        return None

# Khởi tạo client
gc = get_gspread_client()
drive = get_drive_client()

# --- Cấu hình trang ---
st.set_page_config(page_title="Thu thập hiện trường", layout="centered")

st.title("📋 Ứng dụng thu thập thông tin hiện trường")
st.markdown("**Phiên bản mẫu – Mắt Nâu hỗ trợ Đội quản lý Điện lực khu vực Định Hóa**")

# --- Khởi tạo session state ---
if "data" not in st.session_state:
    st.session_state["data"] = []

# --- Form nhập liệu ---
with st.form("field_form", clear_on_submit=True):
    st.markdown("### 📝 Nhập thông tin")
    col1, col2 = st.columns(2)
    with col1:
        ten_tuyen = st.text_input("🔌 Tên tuyến / TBA")
        nguoi_thuchien = st.text_input("👷 Người thực hiện")
    with col2:
        thoigian = st.date_input("🗓️ Thời gian ghi nhận", value=datetime.now())
        loaicv = st.selectbox("🔧 Loại công việc", ["Kiểm tra", "Sửa chữa", "Ghi chỉ số", "Khác"])

    ghichu = st.text_area("📝 Ghi chú hiện trường", height=80)
    hinhanh_files = st.file_uploader("📷 Tải ảnh hiện trường", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    submitted = st.form_submit_button("✅ Ghi nhận thông tin")

    if submitted:
        if not ten_tuyen or not nguoi_thuchien:
            st.warning("⚠️ Vui lòng nhập đầy đủ Tên tuyến và Người thực hiện.")
        else:
            # Tải ảnh lên Google Drive và lấy link
            image_links = []
            if drive and hinhanh_files:
                for file in hinhanh_files:
                    link = upload_image_to_drive(drive, file)
                    if link:
                        image_links.append(link)

            # Tạo bản ghi
            record = {
                "Tên tuyến/TBA": ten_tuyen,
                "Người thực hiện": nguoi_thuchien,
                "Thời gian": thoigian.strftime("%d/%m/%Y"),
                "Loại công việc": loaicv,
                "Ghi chú": ghichu,
                "Ảnh": ", ".join(image_links) if image_links else ""
            }

            # Thêm bản ghi vào session state
            st.session_state["data"].append(record)
            st.success("✅ Đã ghi nhận thông tin hiện trường!")

            # Lưu bản ghi vào Google Sheets
            if gc:
                try:
                    sh = gc.open(SPREADSHEET_NAME)
                    worksheet = sh.worksheet(WORKSHEET_NAME)
                    worksheet.append_row(list(record.values()))
                    st.success("✅ Đã lưu dữ liệu vào Google Sheets!")
                except gspread.exceptions.SpreadsheetNotFound:
                    st.error(f"Không tìm thấy Google Sheet có tên: {SPREADSHEET_NAME}")
                except Exception as e:
                    st.error(f"Lỗi khi lưu vào Google Sheets: {e}")

# --- Hiển thị dữ liệu đã nhập ---
if st.session_state["data"]:
    st.markdown("### 📊 Danh sách thông tin đã ghi:")
    df = pd.DataFrame(st.session_state["data"])
    st.dataframe(df, use_container_width=True)
