
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tra cứu kết quả thầu thuốc", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("demo_thau_thuoc.csv", sep=",", encoding="utf-8-sig")
    df["tungay_hd"] = pd.to_datetime(df["tungay_hd"], errors="coerce")
    df["denngay_hd"] = pd.to_datetime(df["denngay_hd"], errors="coerce")
    return df

df = load_data()

st.title("📋 Tra cứu kết quả thầu thuốc (Demo)")

with st.expander("🔎 Bộ lọc tìm kiếm"):
    col1, col2, col3 = st.columns(3)
    ten = col1.text_input("Tên thuốc (cột I)")
    hoatchat = col2.text_input("Hoạt chất (cột J)")
    duongdung = col3.text_input("Đường dùng (cột K)")

    col4, col5, col6 = st.columns(3)
    dangbaoche = col4.text_input("Dạng bào chế (cột M)")
    hamluong = col5.text_input("Hàm lượng (cột N)")
    donggoi = col6.text_input("Quy cách đóng gói (cột O)")

    col7, col8, col9 = st.columns(3)
    nhasx = col7.text_input("Nhà sản xuất (cột Q)")
    nuocsx = col8.text_input("Nước sản xuất (cột R)")
    donvitinh = col9.text_input("Đơn vị tính (cột T)")

    col10, col11 = st.columns(2)
    tungay = col10.date_input("Từ ngày (cột AJ)", value=pd.to_datetime("2024-09-01"))
    denngay = col11.date_input("Đến ngày (cột AK)", value=pd.to_datetime("2025-03-31"))

# Lọc dữ liệu theo điều kiện nhập
filtered_df = df.copy()

def text_filter(col, val):
    return filtered_df[col].str.contains(val, case=False, na=False)

if ten:
    filtered_df = filtered_df[text_filter("ten", ten)]
if hoatchat:
    filtered_df = filtered_df[text_filter("hoatchat", hoatchat)]
if duongdung:
    filtered_df = filtered_df[text_filter("duongdung", duongdung)]
if dangbaoche:
    filtered_df = filtered_df[text_filter("dangbaoche", dangbaoche)]
if hamluong:
    filtered_df = filtered_df[text_filter("hamluong", hamluong)]
if donggoi:
    filtered_df = filtered_df[text_filter("donggoi", donggoi)]
if nhasx:
    filtered_df = filtered_df[text_filter("nhasx", nhasx)]
if nuocsx:
    filtered_df = filtered_df[text_filter("nuocsx", nuocsx)]
if donvitinh:
    filtered_df = filtered_df[text_filter("donvitinh", donvitinh)]

# Lọc theo khoảng thời gian
filtered_df = filtered_df[
    (filtered_df["tungay_hd"] >= pd.to_datetime(tungay)) &
    (filtered_df["denngay_hd"] <= pd.to_datetime(denngay))
]

st.success(f"🔍 Có {len(filtered_df)} kết quả được tìm thấy.")

st.dataframe(filtered_df, use_container_width=True)

# Nút tải Excel
import io

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

excel_data = to_excel(filtered_df)

st.download_button(
    label="📥 Tải kết quả ra Excel",
    data=excel_data,
    file_name="ket_qua_thau_thuoc.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

