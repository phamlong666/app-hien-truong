
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Cấu hình
st.set_page_config(page_title="Thu thập hiện trường", layout="centered")
st.title("📋 Ứng dụng thu thập thông tin hiện trường")
st.markdown("**Phiên bản có xác thực người dùng – Mắt Nâu hỗ trợ Đội quản lý Điện lực khu vực Định Hóa**")

# Danh sách tài khoản tạm thời (có thể kết nối Google Sheet hoặc DB sau)
users = {
    "npc\\longph": "admin123",
    "cnv01": "123456",
    "cnv02": "123456"
}

# Tạo thư mục lưu ảnh/video nếu chưa có
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Đăng nhập
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    st.subheader("🔐 Đăng nhập")
    username = st.text_input("👤 Tên đăng nhập")
    password = st.text_input("🔑 Mật khẩu", type="password")
    if st.button("🔓 Đăng nhập"):
        if username in users and users[username] == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("✅ Đăng nhập thành công!")
        else:
            st.error("❌ Sai tên đăng nhập hoặc mật khẩu.")
    st.stop()

# Khởi tạo session lưu dữ liệu
if "records" not in st.session_state:
    st.session_state.records = []

# Form nhập liệu
with st.form("form_input", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        ten_tuyen = st.text_input("🔌 Tên ĐZ / TBA", placeholder="VD: 473-E6.22 hoặc TBA Bản Áng")
        nguoi_thuchien = st.text_input("👷‍♂️ Người thực hiện", value=st.session_state.username)
        vitri = st.text_input("📍 Vị trí (tọa độ GPS hoặc địa chỉ)", placeholder="VD: 21.7621, 105.6083 hoặc Xóm Bản Áng")
    with col2:
        ngay = st.date_input("📅 Ngày thực hiện", value=datetime.now())
        gio = st.time_input("⏰ Giờ thực hiện", value=datetime.now().time())
        ghichu = st.text_area("✏️ Ghi chú", height=100)

    media_files = st.file_uploader("📷 Tải ảnh hoặc video hiện trường", type=["jpg", "jpeg", "png", "mp4"], accept_multiple_files=True)
    submit = st.form_submit_button("✅ Ghi nhận thông tin")

    if submit:
        saved_files = []
        for file in media_files:
            save_path = os.path.join(UPLOAD_DIR, file.name)
            with open(save_path, "wb") as f:
                f.write(file.read())
            saved_files.append(save_path)

        thoigian_full = datetime.combine(ngay, gio)
        record = {
            "Tên ĐZ / TBA": ten_tuyen,
            "Người thực hiện": nguoi_thuchien,
            "Vị trí": vitri,
            "Thời gian": thoigian_full.strftime("%d/%m/%Y %H:%M"),
            "Ghi chú": ghichu,
            "Tệp phương tiện": saved_files
        }

        st.session_state.records.append(record)

        # Lưu tạm vào Excel
        df = pd.DataFrame([{
            "Tên ĐZ / TBA": r["Tên ĐZ / TBA"],
            "Người thực hiện": r["Người thực hiện"],
            "Vị trí": r["Vị trí"],
            "Thời gian": r["Thời gian"],
            "Ghi chú": r["Ghi chú"]
        } for r in st.session_state.records])
        df.to_excel("du_lieu_hien_truong.xlsx", index=False)

        st.success("✅ Đã ghi nhận và lưu dữ liệu vào file Excel.")

# Hiển thị dữ liệu đã nhập
if st.session_state.records:
    st.markdown("### 📊 Danh sách thông tin đã ghi nhận:")
    df = pd.DataFrame([{
        "Tên ĐZ / TBA": r["Tên ĐZ / TBA"],
        "Người thực hiện": r["Người thực hiện"],
        "Vị trí": r["Vị trí"],
        "Thời gian": r["Thời gian"],
        "Ghi chú": r["Ghi chú"]
    } for r in st.session_state.records])
    st.dataframe(df, use_container_width=True)

    st.markdown("### 📸 Phương tiện đính kèm:")
    for i, r in enumerate(st.session_state.records):
        if r["Tệp phương tiện"]:
            st.markdown(f"**📝 Bản ghi {i+1}: {r['Tên ĐZ / TBA']}**")
            for file in r["Tệp phương tiện"]:
                if file.lower().endswith((".jpg", ".jpeg", ".png")):
                    st.image(file, width=300)
                elif file.lower().endswith(".mp4"):
                    st.video(file)
