import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os

st.set_page_config(page_title="Thu thập hiện trường", layout="centered")
st.title("📋 Ứng dụng thu thập hiện trường")

# Dữ liệu tạm thời
if "data" not in st.session_state:
    st.session_state.data = []

# Danh sách tài khoản mẫu
user_db = {
    "use.nguyenvana": {"password": "123456", "role": "Công nhân"},
    "use.tranthib": {"password": "123456", "role": "Công nhân"},
    "npc\\longph": {"password": "admin123", "role": "Quản trị viên"}
}

# Đăng nhập
with st.expander("🔐 Đăng nhập"):
    username = st.text_input("USE", placeholder="Nhập mã USE")
    password = st.text_input("Mật khẩu", type="password")
    login = st.button("Đăng nhập")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if login:
    user = user_db.get(username)
    if user and user["password"] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = user["role"]
        st.success(f"Đăng nhập thành công: {username}")
    else:
        st.error("Sai USE hoặc mật khẩu.")

# Giao diện chính khi đăng nhập
if st.session_state.logged_in:
    st.subheader("📍 Nhập dữ liệu hiện trường")
    with st.form("form_hientruong"):
        vi_tri = st.text_input("Tên vị trí (VD: Cột 1.1 / TBA ABC)")
        loai_cv = st.selectbox("Loại công việc", ["Kiểm tra", "Sửa chữa", "Vệ sinh", "Khác"])
        mo_ta = st.text_area("Mô tả hiện trường")
        lat = st.text_input("Vĩ độ (Latitude)")
        lon = st.text_input("Kinh độ (Longitude)")
        hinh_anh = st.file_uploader("📷 Chọn ảnh hiện trường", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("📤 Gửi dữ liệu")

        if submitted:
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            record = {
                "USE": st.session_state.username,
                "Thời gian": now,
                "Vị trí": vi_tri,
                "Loại công việc": loai_cv,
                "Mô tả": mo_ta,
                "Vĩ độ": lat,
                "Kinh độ": lon,
                "Tên file ảnh": hinh_anh.name if hinh_anh else ""
            }
            st.session_state.data.append(record)
            st.success("✅ Đã ghi dữ liệu (chưa kết nối Google Sheet)")
            if hinh_anh:
                img = Image.open(hinh_anh)
                st.image(img, caption="Ảnh hiện trường", use_column_width=True)

    st.divider()
    st.subheader("📑 Dữ liệu hiện trường đã nhập")
    df = pd.DataFrame(st.session_state.data)
    st.dataframe(df, use_container_width=True)