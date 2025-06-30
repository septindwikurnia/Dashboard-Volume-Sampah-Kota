import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Sampah Kota", layout="wide")

# Fungsi baca dan bersihkan data
def load_waste_data(file_path, city_name):
    df = pd.read_csv(file_path)
    date_col = next((col for col in df.columns if "date" in col.lower()), None)
    waste_col = next((col for col in df.columns if "waste" in col.lower() or "kg" in col.lower()), None)

    if date_col and waste_col:
        df = df[[date_col, waste_col]]
        df.columns = ["Date", "Waste_kg"]
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Waste_kg"] = pd.to_numeric(df["Waste_kg"], errors="coerce")
        df.dropna(subset=["Date", "Waste_kg"], inplace=True)
        df["City"] = city_name
        return df
    else:
        st.warning(f"⚠️ Kolom tidak ditemukan di {file_path}")
        return pd.DataFrame()

# Load file
df_austin = load_waste_data("open_source_austin_daily_waste_2003_jan_2021_jul.csv", "Austin")
df_ballarat = load_waste_data("open_source_ballarat_daily_waste_2000_jul_2015_mar.csv", "Ballarat")
df = pd.concat([df_austin, df_ballarat], ignore_index=True)

# Sidebar
st.sidebar.title("🔍 Filter Interaktif")
selected_city = st.sidebar.selectbox("Pilih Kota", df["City"].unique())
filtered_df = df[df["City"] == selected_city]

# Judul dan statistik
st.title("📊 Dashboard Volume Sampah Kota")
st.markdown(f"### Kota: **{selected_city}**")

col1, col2, col3 = st.columns(3)
col1.metric("Total Sampah (kg)", f"{filtered_df['Waste_kg'].sum():,.0f}")
col2.metric("Rata-rata Harian (kg)", f"{filtered_df['Waste_kg'].mean():,.2f}")
col3.metric("Jumlah Hari Pencatatan", f"{filtered_df['Date'].nunique()}")

# Tabs visualisasi
tab1, tab2, tab3, tab4 = st.tabs(["📅 Harian", "📆 Bulanan", "📈 Tahunan", "📦 Distribusi"])

with tab1:
    st.subheader("📅 Volume Sampah Harian")
    fig_daily = px.line(filtered_df, x="Date", y="Waste_kg", title="Tren Sampah Harian")
    st.plotly_chart(fig_daily, use_container_width=True)

with tab2:
    st.subheader("📆 Volume Sampah Bulanan")
    monthly = filtered_df.resample("M", on="Date")["Waste_kg"].sum().reset_index()
    fig_monthly = px.bar(monthly, x="Date", y="Waste_kg", title="Total Sampah per Bulan")
    st.plotly_chart(fig_monthly, use_container_width=True)

with tab3:
    st.subheader("📈 Volume Sampah Tahunan")
    yearly = filtered_df.resample("Y", on="Date")["Waste_kg"].sum().reset_index()
    fig_yearly = px.bar(yearly, x="Date", y="Waste_kg", title="Total Sampah per Tahun")
    st.plotly_chart(fig_yearly, use_container_width=True)

with tab4:
    st.subheader("📦 Distribusi Volume Sampah Harian")
    fig_box = px.box(filtered_df, y="Waste_kg", points="all", title="Distribusi Sampah Harian")
    st.plotly_chart(fig_box, use_container_width=True)

# Unduh Data
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")

csv = convert_df(filtered_df)
st.download_button(
    label="📥 Unduh Data CSV",
    data=csv,
    file_name=f"data_sampah_{selected_city}.csv",
    mime="text/csv"
)

# Data mentah dalam expander
with st.expander("🔍 Lihat Data Mentah"):
    st.dataframe(filtered_df.sort_values("Date"))

# Metadata dalam expander
with st.expander("ℹ️ Metadata"):
    st.markdown("""
    - **Sumber Data**: Dataset open source dari kota Austin dan Ballarat.
    - **Rentang Waktu Data**:
        - Austin: 2003 - 2021
        - Ballarat: 2000 - 2015
    - **Kolom**:
        - `Date`: Tanggal pencatatan
        - `Waste_kg`: Volume sampah harian dalam kilogram
    """)
