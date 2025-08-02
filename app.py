import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import json
import os

# --- Cấu hình trang ---
st.set_page_config(page_title="Thu thập hiện trường", layout="centered")

# Cấu hình Google Sheets và Google Drive
try:
    raw_secret = st.secrets["gdrive_service_account"]
    GDRIVE_CLIENT_SECRET = json.loads(raw_secret)
except json.JSONDecodeError as e:
    st.error(f"Lỗi giải mã JSON từ secrets: {e}")
    st.stop()
except KeyError:
    st.error("Lỗi: Không tìm thấy key 'gdrive_service_account' trong Streamlit secrets.")
    st.stop()

SPREADSHEET_NAME = 'FieldDataCollection'
WORKSHEET_NAME = 'Sheet1'
SPREADSHEET_AUTH_NAME = 'UserAuth'
WORKSHEET_AUTH_NAME = 'Sheet1'

# Cấu hình email
SENDER_EMAIL = 'your_email@gmail.com'
SENDER_PASSWORD = 'your_password'

@st.cache_resource
def get_all_clients():
    try:
        creds_dict = dict(GDRIVE_CLIENT_SECRET)
        gspread_client = gspread.service_account_from_dict(creds_dict)
        gauth = GoogleAuth()
        gauth.AuthFromDict(creds_dict)
        drive_client = GoogleDrive(gauth)
        return gspread_client, drive_client
    except Exception as e:
        st.error(f"Lỗi kết nối Google API. Vui lòng kiểm tra secret và quyền truy cập. Lỗi chi tiết: {e}")
        return None, None

# Hàm để tải ảnh lên Google Drive và trả về link
def upload_image_to_drive(drive_client, file_obj):
    if not drive_client:
        return None
    try:
        with open(file_obj.name, "wb") as f:
            f.write(file_obj.getbuffer())
        gfile = drive_client.CreateFile({'title': file_obj.name})
        gfile.SetContentFile(file_obj.name)
        gfile.Upload()
        os.remove(file_obj.name)
        return gfile['alternateLink']
    except Exception as e:
        st.error(f"Lỗi tải ảnh lên Google Drive: {e}")
        return None

# Hàm để gửi email (giả lập)
def send_reset_email(to_email, username, password):
    st.info(f"Mật khẩu của bạn là: {password}. Email đã được gửi đến {to_email}")

# Khởi tạo client
gc, drive = get_all_clients()

# --- Giao diện chính ---
st.title("📋 Ứng dụng thu thập thông tin hiện trường")
st.markdown("**Phiên bản mẫu – Mắt Nâu hỗ trợ Đội quản lý Điện lực khu vực Định Hóa**")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if "data" not in st.session_state:
    st.session_state["data"] = []

if not st.session_state['logged_in']:
    st.markdown("### 🔑 Đăng nhập")
    with st.form("login_form"):
        username = st.text_input("👤 USE", placeholder="Nhập tên đăng nhập")
        password = st.text_input("🔒 Mật khẩu", type="password", placeholder="Nhập mật khẩu")
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("✅ Đăng nhập")
        with col2:
            forgot_password_button = st.form_submit_button("❓ Quên mật khẩu")

    if login_button:
        if gc:
            try:
                sh = gc.open(SPREADSHEET_AUTH_NAME)
                worksheet = sh.worksheet(WORKSHEET_AUTH_NAME)
                users = worksheet.get_all_records()
                valid_user = False
                for user_record in users:
                    if user_record['USE'] == username and user_record['Password'] == password:
                        valid_user = True
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.success(f"Chào mừng {username}!")
                        st.experimental_rerun()
                        break
                if not valid_user:
                    st.error("Tên đăng nhập hoặc mật khẩu không đúng.")
            except gspread.exceptions.SpreadsheetNotFound:
                st.error(f"Không tìm thấy Google Sheet xác thực: {SPREADSHEET_AUTH_NAME}")
            except Exception as e:
                st.error(f"Lỗi khi kiểm tra đăng nhập: {e}")

    if forgot_password_button:
        if gc:
            try:
                sh = gc.open(SPREADSHEET_AUTH_NAME)
                worksheet = sh.worksheet(WORKSHEET_AUTH_NAME)
                users = worksheet.get_all_records()
                user_found = False
                for user_record in users:
                    if user_record['USE'] == username:
                        send_reset_email("phamlong666@gmail.com", username, user_record['Password'])
                        user_found = True
                        break
                if not user_found:
                    st.warning("Không tìm thấy tên đăng nhập này.")
            except gspread.exceptions.SpreadsheetNotFound:
                st.error(f"Không tìm thấy Google Sheet xác thực: {SPREADSHEET_AUTH_NAME}")
            except Exception as e:
                st.error(f"Lỗi khi xử lý quên mật khẩu: {e}")

    st.info("Để sử dụng tính năng này, bạn cần tạo một Google Sheet tên là 'UserAuth' với hai cột 'USE' và 'Password'.")

else:
    st.sidebar.markdown(f"**Chào mừng, {st.session_state['username']}!**")
    if st.sidebar.button("Đăng xuất"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.experimental_rerun()

    with st.form("field_form", clear_on_submit=True):
        st.markdown("### 📝 Nhập thông tin")
        col1, col2 = st.columns(2)
        with col1:
            ten_tuyen = st.text_input("🔌 Tên tuyến / TBA")
            nguoi_thuchien = st.text_input("👷 Người thực hiện", value=st.session_state['username'])
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
                image_links = []
                if drive and hinhanh_files:
                    for file in hinhanh_files:
                        link = upload_image_to_drive(drive, file)
                        if link:
                            image_links.append(link)

                record = {
                    "Tên tuyến/TBA": ten_tuyen,
                    "Người thực hiện": nguoi_thuchien,
                    "Thời gian": thoigian.strftime("%d/%m/%Y"),
                    "Loại công việc": loaicv,
                    "Ghi chú": ghichu,
                    "Ảnh": ", ".join(image_links) if image_links else ""
                }

                st.session_state["data"].append(record)
                st.success("✅ Đã ghi nhận thông tin hiện trường!")

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

    if st.session_state["data"]:
        st.markdown("### 📊 Danh sách thông tin đã ghi:")
        df = pd.DataFrame(st.session_state["data"])
        st.dataframe(df, use_container_width=True)
