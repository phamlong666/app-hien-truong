import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

# Cấu hình Google Sheets và Google Drive
# Vui lòng thay thế 'your_service_account_key.json' bằng tên file key của bạn.
# Bạn cần tạo file này từ Google Cloud Console và chia sẻ quyền truy cập Google Sheet cho email của service account đó.
GDRIVE_CLIENT_SECRET = 'sotaygpt-fba5e9b3e6fd.json'
SPREADSHEET_NAME = 'FieldDataCollection'
WORKSHEET_NAME = 'Sheet1'
SPREADSHEET_AUTH_NAME = 'UserAuth'
WORKSHEET_AUTH_NAME = 'Sheet1'

# Cấu hình email
SENDER_EMAIL = 'your_email@gmail.com' # Thay bằng email của bạn
SENDER_PASSWORD = 'your_password' # Thay bằng mật khẩu ứng dụng của bạn

# Hàm để xác thực và kết nối đến cả Google Sheets và Google Drive
@st.cache_resource
def get_all_clients():
    try:
        # Kiểm tra sự tồn tại của file key
        if not os.path.exists(GDRIVE_CLIENT_SECRET):
            st.error(f"Lỗi: Không tìm thấy file '{GDRIVE_CLIENT_SECRET}'. Vui lòng đảm bảo file này nằm trong cùng thư mục với app.py")
            return None, None
            
        # Sử dụng service account để xác thực
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(GDRIVE_CLIENT_SECRET, scope)
        
        # Kết nối đến Google Sheets
        gspread_client = gspread.authorize(creds)
        
        # Kết nối đến Google Drive
        gauth = GoogleAuth()
        gauth.credentials = creds
        drive_client = GoogleDrive(gauth)
        
        return gspread_client, drive_client
    except Exception as e:
        st.error(f"Lỗi kết nối Google API. Vui lòng kiểm tra file '{GDRIVE_CLIENT_SECRET}' và quyền truy cập. Lỗi chi tiết: {e}")
        return None, None

# Hàm để tải ảnh lên Google Drive và trả về link
def upload_image_to_drive(drive_client, file_obj):
    if not drive_client:
        return None
    try:
        # Tạo file trên Google Drive
        gfile = drive_client.CreateFile({'title': file_obj.name})
        gfile.SetContentFile(file_obj)
        gfile.Upload()
        # Trả về link để xem hoặc chia sẻ
        return gfile['alternateLink']
    except Exception as e:
        st.error(f"Lỗi tải ảnh lên Google Drive: {e}")
        return None

# Hàm để gửi email (được làm đơn giản cho mục đích minh họa)
def send_reset_email(to_email, username, password):
    # Đây là một hàm giả lập, bạn cần dùng thư viện như smtplib để gửi email thực tế
    st.info(f"Mật khẩu của bạn là: {password}. Email đã được gửi đến {to_email}")

# Khởi tạo client
gc, drive = get_all_clients()

# --- Cấu hình trang ---
st.set_page_config(page_title="Thu thập hiện trường", layout="centered")
st.title("📋 Ứng dụng thu thập thông tin hiện trường")
st.markdown("**Phiên bản mẫu – Mắt Nâu hỗ trợ Đội quản lý Điện lực khu vực Định Hóa**")

# Khởi tạo session state cho trạng thái đăng nhập
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Khởi tạo session state cho dữ liệu
if "data" not in st.session_state:
    st.session_state["data"] = []

# Màn hình đăng nhập
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
        # Kiểm tra thông tin đăng nhập
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

# Màn hình chính sau khi đăng nhập
else:
    # Hiển thị thông tin người dùng và nút đăng xuất
    st.sidebar.markdown(f"**Chào mừng, {st.session_state['username']}!**")
    if st.sidebar.button("Đăng xuất"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.experimental_rerun()

    # --- Form nhập liệu ---
    with st.form("field_form", clear_on_submit=True):
        st.markdown("### 📝 Nhập thông tin")
        col1, col2 = st.columns(2)
        with col1:
            ten_tuyen = st.text_input("  Tên tuyến / TBA")
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
 