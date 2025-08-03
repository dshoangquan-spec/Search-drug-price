import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Tra cứu thầu thuốc", layout="wide")

# CSS tuỳ biến giao diện
st.markdown("""
    <style>
        .main {
            background-color: #f9f9f9;
        }
        .block-container {
            padding-top: 2rem;
        }
        .custom-header {
            font-size: 28px;
            font-weight: bold;
            text-align: center;
            color: #000000;
            padding: 10px 0;
        }
        .metric-label {
            font-weight: bold;
            font-size: 16px;
            text-align: center;
            margin-bottom: 4px;
        }
        .metric-box {
            font-weight: 600;
            font-size: 28px !important;
            text-align: center;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 10px;
            background-color: #ffffff;
        }
        .metric-label {
            font-weight: bold;
            font-size: 20px;
            text-align: center;
            margin-bottom: 5px;
        }
        [data-testid="stMetric"] {
            text-align: center;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 10px;
            background-color: #fff;
            font-size: 20px;
            font-weight: bold;
        }
        [data-testid="stMetric"] > div:nth-child(1) {
            font-size: 20px;
        }
        [data-testid="stMetric"] > div:nth-child(2) {
            font-size: 28px;
            color: #000;
        }
        .stTextInput > div > div,
        .stRadio > div {
            border: none !important;
        }
        .st-emotion-cache-1v0mbdj {
            padding: 1rem;
        }
        .st-emotion-cache-1v0mbdj {
            padding: 1rem;
        }

        /* Thu nhỏ tiêu đề h3 như "Tìm thấy X kết quả", "Thống kê giá" */
        h3 {
            font-size: 18px !important;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/dshoangquan-spec/Search-drug-price/main/Danhmuc.csv.gz"
    df = pd.read_csv(url, compression="gzip", encoding="utf-8-sig")
    df["tungay_hd"] = pd.to_datetime(df["tungay_hd"], errors="coerce")
    df["denngay_hd"] = pd.to_datetime(df["denngay_hd"], errors="coerce")
    return df



df = load_data()
st.markdown('<div class="custom-header">TRA CỨU KẾT QUẢ THẦU THUỐC THEO DỮ LIỆU BHYT</div>', unsafe_allow_html=True)

col_left, col_center, col_right = st.columns(3)
with col_left:
    tim_theo = st.radio("", ["Tên thuốc", "Tên hoạt chất"], horizontal=False)
with col_center:
    if tim_theo == "Tên thuốc":
        ten = st.text_input("Nhập tên thuốc")
        hoatchat = ""
    else:
        hoatchat = st.text_input("Nhập tên hoạt chất")
        ten = ""
with col_right:
    st.write("")

st.markdown("**🔍 Kết quả tìm kiếm**")

with st.expander("📂 Bộ lọc nâng cao"):
    df_temp = df.copy()
    if ten:
        df_temp = df_temp[df_temp["ten"].astype(str).str.lower().str.contains(ten.strip().lower())]
    if hoatchat:
        df_temp = df_temp[df_temp["hoatchat"].astype(str).str.lower().str.contains(hoatchat.strip().lower())]

    col1, col2 = st.columns(2)
    duongdung_options = sorted(df["duongdung"].dropna().unique())
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

filtered_df = filtered_df[
    (filtered_df["tungay_hd"] >= pd.to_datetime(tungay)) &
    (filtered_df["denngay_hd"] <= pd.to_datetime(denngay))
]

st.markdown(f"### ✅ Tìm thấy {len(filtered_df)} kết quả")

hidden_cols = ['loai_thau', 'ma_tinh', 'ten_don_vi', 'ma_cskcb', 'ma_gy', 'maduongdung', 'A', 'B', 'D', 'E', 'G', 'L']
move_to_end = ['F', 'C', 'ten_cskcb', 'ten_tinh']
cols = [col for col in filtered_df.columns if col not in hidden_cols + move_to_end] + [col for col in move_to_end if col in filtered_df.columns]
filtered_df = filtered_df[cols]

filtered_df["gia"] = pd.to_numeric(filtered_df["gia"], errors="coerce")
gia_values = filtered_df["gia"].dropna()

if not gia_values.empty:
    min_price = gia_values.min()
    max_price = gia_values.max()
    median_price = gia_values.median()
    avg_price = gia_values.mean()

    st.markdown("### 📊 Thống kê giá")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='metric-label'>🟢 Giá thấp nhất</div>", unsafe_allow_html=True)
        st.metric(label="", value=f"{min_price:,.0f}")

    with col2:
        st.markdown("<div class='metric-label'>🔴 Giá cao nhất</div>", unsafe_allow_html=True)
        st.metric(label="", value=f"{max_price:,.0f}")

    with col3:
        st.markdown("<div class='metric-label'>🟡 Giá trung vị</div>", unsafe_allow_html=True)
        st.metric(label="", value=f"{median_price:,.0f}")

    with col4:
        st.markdown("<div class='metric-label'>🔵 Giá trung bình</div>", unsafe_allow_html=True)
        st.metric(label="", value=f"{avg_price:,.0f}")
else:
    st.warning("Không có dữ liệu giá để thống kê.")

st.dataframe(filtered_df, use_container_width=True)

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
