
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Cấu hình
st.set_page_config(page_title="Thu thập hiện trường", layout="centered")
st.title("📋 Ứng dụng thu thập thông tin hiện trường")
st.markdown("**Mắt Nâu – trợ lý AI hỗ trợ Đội quản lý Điện lực khu vực Định Hóa**")

# Tạo thư mục lưu ảnh nếu chưa có
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Khởi tạo dữ liệu phiên
if "records" not in st.session_state:
    st.session_state.records = []

# Form nhập liệu
with st.form("input_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        ten_tuyen = st.text_input("🔌 Tên tuyến / TBA", placeholder="VD: 473-E6.22")
        nguoi_thuchien = st.text_input("👷 Người thực hiện", placeholder="VD: Nguyễn Văn A")
    with col2:
        thoigian = st.date_input("🕒 Thời gian ghi nhận", value=datetime.now())
        loai_cv = st.selectbox("🔧 Loại công việc", ["Kiểm tra", "Sửa chữa", "Ghi chỉ số", "Khác"])

    ghichu = st.text_area("📝 Ghi chú hiện trường", height=80)
    hinhanh = st.file_uploader("📷 Tải ảnh hiện trường", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    submit = st.form_submit_button("✅ Ghi nhận")

    if submit:
        saved_files = []
        for img in hinhanh:
            save_path = os.path.join(UPLOAD_DIR, img.name)
            with open(save_path, "wb") as f:
                f.write(img.read())
            saved_files.append(save_path)

        st.session_state.records.append({
            "Tên tuyến/TBA": ten_tuyen,
            "Người thực hiện": nguoi_thuchien,
            "Thời gian": thoigian.strftime("%d/%m/%Y"),
            "Loại công việc": loai_cv,
            "Ghi chú": ghichu,
            "Ảnh": saved_files
        })

        st.success("✅ Đã ghi nhận thông tin hiện trường.")

# Hiển thị dữ liệu
if st.session_state.records:
    st.markdown("### 📊 Danh sách thông tin đã ghi:")
    df = pd.DataFrame([
        {
            "Tên tuyến/TBA": r["Tên tuyến/TBA"],
            "Người thực hiện": r["Người thực hiện"],
            "Thời gian": r["Thời gian"],
            "Loại công việc": r["Loại công việc"],
            "Ghi chú": r["Ghi chú"]
        }
        for r in st.session_state.records
    ])
    st.dataframe(df, use_container_width=True)

    st.markdown("### 🖼️ Ảnh hiện trường:")
    for idx, r in enumerate(st.session_state.records):
        if r["Ảnh"]:
            st.markdown(f"**📌 Bản ghi {idx+1} – {r['Tên tuyến/TBA']}**")
            for img_path in r["Ảnh"]:
                st.image(img_path, width=300)
