import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Thu thập hiện trường", layout="wide")

# Danh sách tài khoản mẫu
users = {
    "use.nguyenvana": {"password": "123456", "role": "Công nhân"},
    "use.tranthib": {"password": "123456", "role": "Công nhân"},
    "npc\\longph": {"password": "admin123", "role": "Quản trị viên"}
}

# Dữ liệu tạm
if "data" not in st.session_state:
    st.session_state.data = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Đăng nhập hệ thống")
    with st.form("login_form"):
        user = st.text_input("Mã USE")
        pwd = st.text_input("Mật khẩu", type="password")
        submit = st.form_submit_button("Đăng nhập")
        if submit:
            if user in users and users[user]["password"] == pwd:
                st.session_state.logged_in = True
                st.session_state.username = user
                st.session_state.role = users[user]["role"]
                st.experimental_rerun()
            else:
                st.error("Sai mã USE hoặc mật khẩu.")
    st.stop()

# Giao diện chính sau đăng nhập
st.title("📋 Ghi nhận hiện trường")
with st.form("form_hientruong"):
    vi_tri = st.text_input("📍 Tên vị trí (VD: Cột 1.1)")
    loai = st.selectbox("🔧 Loại công việc", ["Kiểm tra", "Sửa chữa", "Vệ sinh", "Khác"])
    mo_ta = st.text_area("📝 Mô tả hiện trường")
    lat = st.text_input("🌐 Vĩ độ (Latitude)")
    lon = st.text_input("🌐 Kinh độ (Longitude)")
    anh = st.file_uploader("📷 Chọn ảnh hiện trường", type=["jpg", "jpeg", "png"])
    gui = st.form_submit_button("📤 Gửi dữ liệu")

if gui and vi_tri and lat and lon:
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ten_anh = anh.name if anh else ""
    st.session_state.data.append({
        "USE": st.session_state.username,
        "Thời gian": now,
        "Vị trí": vi_tri,
        "Công việc": loai,
        "Mô tả": mo_ta,
        "Lat": lat,
        "Lon": lon,
        "Ảnh": ten_anh
    })
    st.success("✅ Đã ghi dữ liệu.")

    if anh:
        img = Image.open(anh)
        st.image(img, caption="Ảnh hiện trường", use_container_width=True)

    try:
        m = folium.Map(location=[float(lat), float(lon)], zoom_start=17)
        folium.Marker([float(lat), float(lon)],
                      tooltip=vi_tri,
                      popup=mo_ta).add_to(m)
        st.subheader("🗺️ Vị trí hiện trường trên bản đồ:")
        st_folium(m, height=400, width=700)
    except:
        st.warning("Không thể vẽ bản đồ – tọa độ không hợp lệ.")