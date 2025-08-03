
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Tra cứu thầu thuốc", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("demo_thau_thuoc.csv", sep=",", encoding="utf-8-sig")
    df["tungay_hd"] = pd.to_datetime(df["tungay_hd"], errors="coerce")
    df["denngay_hd"] = pd.to_datetime(df["denngay_hd"], errors="coerce")
    return df

df = load_data()

st.title("💊 Tra cứu kết quả thầu thuốc")

with st.expander("📂 Bộ lọc nâng cao"):
# Lọc trước theo tên hoặc hoạt chất để dùng cho dropdown
    df_temp = df.copy()
    if ten:
        df_temp = df_temp[df_temp["ten"].astype(str).str.lower().str.contains(ten.strip().lower())]
    if hoatchat:
        df_temp = df_temp[df_temp["hoatchat"].astype(str).str.lower().str.contains(hoatchat.strip().lower())]

    col1, col2 = st.columns(2)
    duongdung_options = sorted(df_temp["duongdung"].dropna().unique())
    dangbaoche_options = sorted(df_temp["dangbaoche"].dropna().unique())

    duongdung = col1.multiselect("🚑 Chọn đường dùng", duongdung_options)
    dangbaoche = col2.multiselect("💊 Chọn dạng bào chế", dangbaoche_options)

    col3, col4 = st.columns(2)
    nhasx_options = sorted(df_temp["nhasx"].dropna().unique())
    nuocsx_options = sorted(df_temp["nuocsx"].dropna().unique())

    nhasx = col3.multiselect("🏭 Nhà sản xuất", nhasx_options)
    nuocsx = col4.multiselect("🌍 Nước sản xuất", nuocsx_options)

    col5, col6 = st.columns(2)
    donvitinh_options = sorted(df_temp["donvitinh"].dropna().unique())
    donvitinh = col5.multiselect("📦 Đơn vị tính", donvitinh_options)

    tungay = col6.date_input("📅 Từ ngày (hiệu lực)", value=pd.to_datetime("2024-09-01"))
    denngay = st.date_input("📅 Đến ngày (hiệu lực)", value=pd.to_datetime("2025-03-31"))

# Bắt đầu lọc dữ liệu
filtered_df = df.copy()

def contains_filter(column, keyword):
    keyword = keyword.strip().lower()
    return filtered_df[column].astype(str).str.lower().str.contains(keyword, na=False)

if ten:
    filtered_df = filtered_df[contains_filter("ten", ten)]
if hoatchat:
    filtered_df = filtered_df[contains_filter("hoatchat", hoatchat)]
if duongdung:
    filtered_df = filtered_df[filtered_df["duongdung"].isin(duongdung)]
if dangbaoche:
    filtered_df = filtered_df[filtered_df["dangbaoche"].isin(dangbaoche)]
if nhasx:
    filtered_df = filtered_df[filtered_df["nhasx"].isin(nhasx)]
if nuocsx:
    filtered_df = filtered_df[filtered_df["nuocsx"].isin(nuocsx)]
if donvitinh:
    filtered_df = filtered_df[filtered_df["donvitinh"].isin(donvitinh)]

# Lọc theo thời gian
filtered_df = filtered_df[
    (filtered_df["tungay_hd"] >= pd.to_datetime(tungay)) &
    (filtered_df["denngay_hd"] <= pd.to_datetime(denngay))
]

st.markdown(f"### ✅ Tìm thấy {len(filtered_df)} kết quả")

# Hiển thị bảng
st.dataframe(filtered_df, use_container_width=True)

# Xuất Excel
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
