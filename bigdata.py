import streamlit as st
import duckdb
import pandas as pd
import io

st.set_page_config(page_title="Tra cứu DuckDB", layout="wide")

@st.cache_resource
def load_duckdb():
    url = "https://raw.githubusercontent.com/dshoangquan-spec/Search-drug-price/main/Danhmuc.csv.gz"
    con = duckdb.connect(database=':memory:')
    con.execute(f"""
        CREATE OR REPLACE TABLE danhmuc AS 
        SELECT 
            *, 
            TRY_CAST(tungay_hd AS TIMESTAMP) AS tungay,
            TRY_CAST(denngay_hd AS TIMESTAMP) AS denngay
        FROM read_csv_auto('{url}', compression='gzip', delim=',', header=True)
    """)
    return con

con = load_duckdb()

st.markdown('<div class="custom-header">TRA CỨU THẦU THUỐC - DUCKDB</div>', unsafe_allow_html=True)

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

# Bộ lọc nâng cao
with st.expander("📂 Bộ lọc nâng cao"):
    duongdung = st.multiselect("🚑 Chọn đường dùng", 
        con.execute("SELECT DISTINCT duongdung FROM danhmuc WHERE duongdung IS NOT NULL").df()["duongdung"].dropna().tolist()
    )
    dangbaoche = st.multiselect("💊 Chọn dạng bào chế", 
        con.execute("SELECT DISTINCT dangbaoche FROM danhmuc WHERE dangbaoche IS NOT NULL").df()["dangbaoche"].dropna().tolist()
    )
    nhasx = st.multiselect("🏭 Nhà sản xuất", 
        con.execute("SELECT DISTINCT nhasx FROM danhmuc WHERE nhasx IS NOT NULL").df()["nhasx"].dropna().tolist()
    )
    nuocsx = st.multiselect("🌍 Nước sản xuất", 
        con.execute("SELECT DISTINCT nuocsx FROM danhmuc WHERE nuocsx IS NOT NULL").df()["nuocsx"].dropna().tolist()
    )
    donvitinh = st.multiselect("📦 Đơn vị tính", 
        con.execute("SELECT DISTINCT donvitinh FROM danhmuc WHERE donvitinh IS NOT NULL").df()["donvitinh"].dropna().tolist()
    )
    tungay = st.date_input("📅 Từ ngày (hiệu lực)", value=pd.to_datetime("2024-09-01"))
    denngay = st.date_input("📅 Đến ngày (hiệu lực)", value=pd.to_datetime("2025-03-31"))

# Tạo câu truy vấn SQL
query = "SELECT * FROM danhmuc WHERE 1=1"

if ten:
    query += f" AND LOWER(ten) LIKE '%{ten.lower()}%'"
if hoatchat:
    query += f" AND LOWER(hoatchat) LIKE '%{hoatchat.lower()}%'"
if duongdung:
    query += f" AND duongdung IN ({','.join([f'\'{d}\'' for d in duongdung])})"
if dangbaoche:
    query += f" AND dangbaoche IN ({','.join([f'\'{d}\'' for d in dangbaoche])})"
if nhasx:
    query += f" AND nhasx IN ({','.join([f'\'{d}\'' for d in nhasx])})"
if nuocsx:
    query += f" AND nuocsx IN ({','.join([f'\'{d}\'' for d in nuocsx])})"
if donvitinh:
    query += f" AND donvitinh IN ({','.join([f'\'{d}\'' for d in donvitinh])})"
if tungay and denngay:
    query += f" AND tungay >= TIMESTAMP '{tungay}' AND tungay <= TIMESTAMP '{denngay}'"

# Thực thi truy vấn
df_result = con.execute(query).df()

st.markdown(f"### ✅ Tìm thấy {len(df_result)} kết quả")

# Thống kê giá
df_result["gia"] = pd.to_numeric(df_result["gia"], errors="coerce")
gia_values = df_result["gia"].dropna()

if not gia_values.empty:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🟢 Giá thấp nhất", f"{gia_values.min():,.0f}")
    col2.metric("🔴 Giá cao nhất", f"{gia_values.max():,.0f}")
    col3.metric("🟡 Giá trung vị", f"{gia_values.median():,.0f}")
    col4.metric("🔵 Giá trung bình", f"{gia_values.mean():,.0f}")

st.dataframe(df_result, use_container_width=True)

# Xuất Excel
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

st.download_button(
    label="📥 Tải kết quả ra Excel",
    data=to_excel(df_result),
    file_name="ket_qua_thau_duckdb.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
