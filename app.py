
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Thu thập hiện trường", layout="centered")

st.title("📋 Ứng dụng thu thập thông tin hiện trường")
st.markdown("**Phiên bản mẫu – Mắt Nâu hỗ trợ Đội quản lý Điện lực khu vực Định Hóa**")

# --- Khởi tạo session
if "data" not in st.session_state:
    st.session_state["data"] = []

with st.form("field_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        ten_tuyen = st.text_input("🔌 Tên tuyến / TBA")
        nguoi_thuchien = st.text_input("👷 Người thực hiện")
    with col2:
        thoigian = st.date_input("🗓️ Thời gian ghi nhận", value=datetime.now())
        loaicv = st.selectbox("🔧 Loại công việc", ["Kiểm tra", "Sửa chữa", "Ghi chỉ số", "Khác"])

    ghichu = st.text_area("📝 Ghi chú hiện trường", height=80)
    hinhanh = st.file_uploader("📷 Tải ảnh hiện trường", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    submitted = st.form_submit_button("✅ Ghi nhận thông tin")

    if submitted:
        record = {
            "Tên tuyến/TBA": ten_tuyen,
            "Người thực hiện": nguoi_thuchien,
            "Thời gian": thoigian.strftime("%d/%m/%Y"),
            "Loại công việc": loaicv,
            "Ghi chú": ghichu,
            "Ảnh": [img.name for img in hinhanh] if hinhanh else []
        }
        st.session_state["data"].append(record)
        st.success("✅ Đã ghi nhận thông tin hiện trường!")

# --- Hiển thị dữ liệu đã nhập
if st.session_state["data"]:
    st.markdown("### 📊 Danh sách thông tin đã ghi:")
    df = pd.DataFrame(st.session_state["data"]).drop(columns=["Ảnh"])
    st.dataframe(df, use_container_width=True)

    st.markdown("📸 **Ảnh đính kèm (nếu có):**")
    for i, record in enumerate(st.session_state["data"]):
        if record["Ảnh"]:
            st.markdown(f"**🔹 Bản ghi {i+1} – {record['Tên tuyến/TBA']}**")
            for name in record["Ảnh"]:
                st.write(f"📁 {name}")
