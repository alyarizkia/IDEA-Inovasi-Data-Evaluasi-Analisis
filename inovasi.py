import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import base64
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
import altair as alt
import plotly.express as px
from prophet import Prophet
from prophet.plot import plot_plotly

load_dotenv()  

user = os.getenv("DB_USER")
password = os.getenv("DB_PASS")
host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")
dbname = os.getenv("DB_NAME")

# Buat koneksi engine
engine = create_engine(
    f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
)

# PAGE CONFIG
st.set_page_config(page_title="IDEA", layout="wide")

# Load CSS eksternal
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# SIDEBAR
st.sidebar.image("D:\\magang\\projek akhir\\foto\\logo.svg", caption="IDEA", width=50)
menu = st.sidebar.radio(
    "Navigasi",
    ["🏠 Beranda", "📚 Arsip", "📊 Lensa Inovasi", "🏅 Indeks Inovasi", "🤖 Asisten Cerdas", "🌍 Pemetaan SDGs", "📑 Rekap", "⚙️ Pengaturan"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.image("D:\\magang\\projek akhir\\foto\\ilustrasi-1.png", width="stretch")
st.sidebar.info("Welcome back 👋 Admin Cakep")

# DATA
# ====== INOVASI ======
query_inovasi = """
SELECT 
    i.nama,
    i.tahun,
    i.jenis,
    i.bentuk,
    s.unit_nama AS skpd
FROM public.inovasi i
LEFT JOIN public.master_skpd s
    ON i.skpd_kode = s.unit_id::varchar;
"""
data_inovasi = pd.read_sql(query_inovasi, engine)

mapping_bentuk = {
    "1": "Inovasi tata kelola pemerintahan daerah",
    "2": "Inovasi pelayanan publik",
    "3": "Inovasi Daerah lainnya sesuai dengan Urusan Pemerintahan yang menjadi kewenangan Daerah"
}

data_inovasi["bentuk"] = data_inovasi["bentuk"].replace(mapping_bentuk)


# ====== PENELITIAN ======
query_penelitian = """
SELECT 
    p.judul,
    p.tahun,
    b.nama_bidang,
    p.status
FROM litbang.penelitian p
LEFT JOIN litbang.master_bidang b
    ON p.bidang_id::integer = b.bidang_id;
"""
data_penelitian = pd.read_sql(query_penelitian, engine)

# ====== PERGURUAN TINGGI ======
query_pt = """
SELECT 
    nama_perguruan_tinggi
FROM litbang.perguruan_tinggi;
"""
data_pt = pd.read_sql(query_pt, engine)

# MAIN DASHBOARD
if menu == "🏠 Beranda":
    # Hero Section
    def get_base64_of_bin_file(bin_file):
        with open(bin_file, "rb") as f:
            return base64.b64encode(f.read()).decode()

    img_path = "D:/magang/projek akhir/foto/surabaya-1.jpg"
    img_base64 = get_base64_of_bin_file(img_path)

    logo_path = "D:\\magang\\projek akhir\\foto\\logo.svg"
    logo_base64 = get_base64_of_bin_file(logo_path)

    # Bagian header sistem (di atas container gambar)
    st.markdown(f"""
        <div class="system-header">
            <img src="data:image/svg+xml;base64,{logo_base64}" alt="logo">
            <div class="title">IDEA</div>
        </div>
    """, unsafe_allow_html=True)

    # Ambil count langsung dari DataFrame hasil query
    jumlah_inovasi = data_inovasi.shape[0]         
    jumlah_penelitian = data_penelitian.shape[0]  
    jumlah_pt = data_pt.shape[0]                  
    jumlah_skpd = data_inovasi['skpd'].nunique()  

    # Tampilkan di hero section
    st.markdown(f"""
    <div class="hero-container">
        <img src="data:image/jpg;base64,{img_base64}" class="hero-image">
        <div class="hero-text">Selamat Pagi, Admin Cakep! 👋</div>
        <div class="card-row">
            <div class="card">
                <div class="card-title">Jumlah Inovasi</div>
                <div class="metric">{jumlah_inovasi}</div>
            </div>
            <div class="card">
                <div class="card-title">Jumlah Penelitian</div>
                <div class="metric">{jumlah_penelitian}</div>
            </div>
            <div class="card">
                <div class="card-title">Perguruan Tinggi Terlibat</div>
                <div class="metric">{jumlah_pt}</div>
            </div>
            <div class="card">
                <div class="card-title">OPD Terlibat</div>
                <div class="metric">{jumlah_skpd}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tren & Update
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <div class="frame">
                <div class="frame-title"><span class="icon"></span> Tren Inovasi</div>
            """, unsafe_allow_html=True)
        # jumlah inovasi per tahun
        df_tren = data_inovasi.groupby("tahun").size().reset_index(name="jumlah")
        st.line_chart(df_tren.set_index("tahun"))

        st.markdown("</div>", unsafe_allow_html=True)
        

    with col2:
        st.markdown("""
            <div class="frame">
                <div class="frame-title"><span class="icon"></span> Tren Penelitian</div>
            """, unsafe_allow_html=True)
        # jumlah penelitian per tahun
        df_tren = data_penelitian.groupby("tahun").size().reset_index(name="jumlah")
        st.line_chart(df_tren.set_index("tahun"))

        st.markdown("</div>", unsafe_allow_html=True)

    # === Tren & Forecast Inovasi Berdasarkan Filter ===
    st.markdown("""
        <div class="frame">
            <div class="frame-title"><span class="icon"></span> Tren & Forecast Jumlah Inovasi Berdasarkan Filter</div>
    """, unsafe_allow_html=True)

    # Siapkan data tren inovasi
    df_forecast = data_inovasi.groupby(["tahun", "bentuk", "skpd"]).size().reset_index(name="jumlah_inovasi")

    # --- Dropdown filter ---
    col_filter1, col_filter2 = st.columns(2)

    with col_filter1:
        bentuk_opsi = sorted(df_forecast["bentuk"].dropna().unique())
        bentuk_pilihan = st.selectbox("📦 Pilih Bentuk Inovasi", bentuk_opsi)

    with col_filter2:
        skpd_opsi = sorted(df_forecast["skpd"].dropna().unique())
        skpd_pilihan = st.selectbox("🏛️ Pilih OPD / SKPD", skpd_opsi)

    # Filter sesuai pilihan user
    df_filtered = df_forecast[
        (df_forecast["bentuk"] == bentuk_pilihan) &
        (df_forecast["skpd"] == skpd_pilihan)
    ]

    if df_filtered.empty:
        st.warning("⚠️ Data tidak ditemukan untuk kombinasi filter tersebut.")
    else:
        # ==== Bar Chart ====
        st.subheader(f"📊 Jumlah Inovasi ({bentuk_pilihan}) oleh {skpd_pilihan}")
        fig_bar = px.bar(df_filtered, x="tahun", y="jumlah_inovasi", text="jumlah_inovasi",
                        labels={"tahun": "Tahun", "jumlah_inovasi": "Jumlah Inovasi"},
                        color_discrete_sequence=["#1C4B89"])
        fig_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_bar, use_container_width=True)

        # ==== Forecast Prophet ====
        st.subheader("📈 Prediksi Jumlah Inovasi (3 Tahun ke Depan)")

        df_prophet = df_filtered.rename(columns={"tahun": "ds", "jumlah_inovasi": "y"})
        df_prophet["ds"] = pd.to_datetime(df_prophet["ds"], format="%Y")

        # Fit model Prophet
        model = Prophet()
        model.fit(df_prophet)

        # Prediksi 3 tahun ke depan
        future = model.make_future_dataframe(periods=3, freq='Y')
        forecast = model.predict(future)

        # Plot tren + forecast
        fig_forecast = plot_plotly(model, forecast)
        st.plotly_chart(fig_forecast, use_container_width=True)

        st.caption(f"🔮 Prediksi berdasarkan tren historis inovasi {bentuk_pilihan} oleh {skpd_pilihan}.")
    
    st.markdown("</div>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("""
            <div class="frame">
                <div class="frame-title"><span class="icon"></span> Update Terbaru Inovasi</div>
            """, unsafe_allow_html=True)
        # Ambil update terbaru dari inovasi
        update_terbaru = data_inovasi.sort_values("tahun", ascending=False).head(9)[["tahun", "nama", "bentuk"]]
        update_terbaru.rename(columns={"nama": "Judul", "bentuk": "Bentuk Inovasi", "tahun": "Tahun"}, inplace=True)
        st.data_editor(update_terbaru,
                       hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
            <div class="frame">
                <div class="frame-title"><span class="icon"></span> Update Terbaru Penelitian</div>
            """, unsafe_allow_html=True)
        # Ambil update terbaru dari penelitian
        update_terbaru = data_penelitian.sort_values("tahun", ascending=False).head(9)[["tahun", "judul", "nama_bidang"]]
        update_terbaru.rename(columns={"judul": "Judul", "nama_bidang": "Bidang Penelitian", "tahun": "Tahun"}, inplace=True)
        st.data_editor(update_terbaru,
                       hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Distribusi Bentuk Inovasi
    st.markdown("""
        <div class="frame">
            <div class="frame-title"><span class="icon"></span> Distribusi Bentuk Inovasi</div>
    """, unsafe_allow_html=True)

    kategori_counts = data_inovasi['bentuk'].value_counts().reset_index()
    kategori_counts.columns = ["Bentuk", "Jumlah"]

    chart = (
        alt.Chart(kategori_counts)
        .mark_bar(color="#1C4B89")  
        .encode(
            y=alt.Y("Bentuk:N", sort="-x"),
            x="Jumlah:Q"
)

        .properties(width=600, height=400)
    )

    st.altair_chart(chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Distribusi Bidang Penelitian
    st.markdown("""
        <div class="frame">
            <div class="frame-title"><span class="icon"></span> Distribusi Bidang Penelitian</div>
    """, unsafe_allow_html=True)

    kategori_counts = data_penelitian['nama_bidang'].value_counts().reset_index()
    kategori_counts.columns = ["Bidang", "Jumlah"]

    chart2 = (
        alt.Chart(kategori_counts)
        .mark_bar(color="#1C4B89")
        .encode(
            x=alt.X("Bidang:N", sort="-y", axis=alt.Axis(labelAngle=0)),  
            y="Jumlah:Q",
            tooltip=["Bidang", "Jumlah"]
        )
        .properties(width=600, height=400)
    )

    st.altair_chart(chart2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
        
# ======================
# 2. DATA MASTER
# ======================
elif menu == "📚 Arsip":
    st.title("📚 Arsip")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Inovasi", "Penelitian", "OPD", "Perguruan Tinggi"]
    )

    with tab1:
            st.data_editor(
            data_inovasi.rename(columns={
                "nama":"Nama",
                "tahun": "Tahun",
                "jenis": "Jenis",
                "bentuk": "Bentuk",
                "skpd": "OPD"
            }),
            hide_index=True
        )

    with tab2:
        st.data_editor(
            data_penelitian.rename(columns={
                "judul":"Judul",
                "tahun":"Tahun",
                "nama_bidang":"Nama Bidang",
                "status":"Status"
            }),
            hide_index=True)

    with tab3:
        st.data_editor(
            pd.DataFrame({"nama_skpd": data_inovasi["skpd"].unique()}).rename(
                columns={"nama_skpd": "OPD"}
            ),
            hide_index=True)

    with tab4:
        st.data_editor(
            data_pt.rename(columns={
                "nama_perguruan_tinggi":"Perguruan Tinggi"
            }),
            hide_index=True)

# ======================
# 3. ANALISIS INOVASI
# ======================
elif menu == "📊 Lensa Inovasi":
    st.title("📊 Lensa Inovasi")

    sub = st.radio("Pilih Analisis", ["Deskriptif", "Jejaring"])

    if sub == "Deskriptif":
        st.subheader("Tren Inovasi per Tahun")
        st.line_chart(data_inovasi.groupby("tahun").size())

        st.subheader("Distribusi per Bidang")
        st.bar_chart(data_penelitian["bidang"].value_counts())

        st.subheader("Top SKPD Paling Aktif")
        st.bar_chart(data_inovasi["skpd"].value_counts())

        st.subheader("Top PT Paling Aktif")
        st.bar_chart(data_inovasi["pt"].value_counts())

    elif sub == "Jejaring":
        st.subheader("Analisis Jejaring SKPD ↔ PT ↔ Inovasi")

        G = nx.Graph()
        for _, row in data_inovasi.iterrows():
            G.add_edge(row["skpd"], row["pt"])

        fig, ax = plt.subplots(figsize=(6, 4))
        nx.draw(G, with_labels=True, node_color="lightblue", ax=ax, node_size=1000)
        st.pyplot(fig)

# ======================
# 4. PENILAIAN & INDEKS
# ======================
elif menu == "🏅 Indeks Inovasi":
    st.title("🏅 Penilaian & Indeks Inovasi")

    st.markdown("""
        <div class="frame">
            <div class="frame-title"><span class="icon"></span> Analisis & Prediksi Kinerja Inovasi per SKPD</div>
    """, unsafe_allow_html=True)

    # Siapkan data tren inovasi dari SQL
    df_forecast = data_inovasi.groupby(["tahun", "bentuk", "skpd"]).size().reset_index(name="jumlah_inovasi")

    # --- Filter pilihan user ---
    col_filter1, col_filter2 = st.columns(2)

    with col_filter1:
        bentuk_opsi = ["Semua Bentuk Inovasi"] + sorted(df_forecast["bentuk"].dropna().unique().tolist())
        bentuk_pilihan = st.selectbox("📦 Pilih Bentuk Inovasi", bentuk_opsi)

    with col_filter2:
        skpd_opsi = sorted(df_forecast["skpd"].dropna().unique().tolist())
        skpd_pilihan = st.selectbox("🏛️ Pilih OPD / SKPD", skpd_opsi)

    if bentuk_pilihan == "Semua Bentuk Inovasi":
        df_filtered = (
            df_forecast[df_forecast["skpd"] == skpd_pilihan]
            .groupby("tahun", as_index=False)["jumlah_inovasi"]
            .sum()
        )
    else:
        df_filtered = df_forecast[
            (df_forecast["bentuk"] == bentuk_pilihan) &
            (df_forecast["skpd"] == skpd_pilihan)
        ]

    if df_filtered.empty:
        st.warning("⚠️ Data tidak ditemukan untuk kombinasi filter tersebut.")
    else:
        # Pastikan tahun dibulatkan dan dikonversi ke string
        df_filtered["tahun"] = pd.to_numeric(df_filtered["tahun"], errors="coerce").round(0).astype("Int64")
        df_filtered["tahun"] = df_filtered["tahun"].astype(str)

        # === Grafik Tren Historis ===
        st.subheader(f"📊 Jumlah Inovasi ({bentuk_pilihan}) oleh {skpd_pilihan}")

        fig_bar = px.bar(
            df_filtered, 
            x="tahun", y="jumlah_inovasi", text="jumlah_inovasi",
            labels={"tahun": "Tahun", "jumlah_inovasi": "Jumlah Inovasi"},
            color_discrete_sequence=["#1C4B89"]
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_xaxes(type='category')
        st.plotly_chart(fig_bar, use_container_width=True)

        # === Forecast Prophet ===
        st.subheader("📈 Prediksi Jumlah Inovasi (3 Tahun ke Depan)")

        df_prophet = df_filtered.rename(columns={"tahun": "ds", "jumlah_inovasi": "y"})
        df_prophet["ds"] = pd.to_datetime(df_prophet["ds"], format="%Y")

        # ✅ CEK JUMLAH DATA DULU SEBELUM MODEL FIT
        if len(df_prophet) < 2:
            st.warning("⚠️ Data terlalu sedikit untuk melakukan prediksi (minimal 2 tahun data diperlukan).")
        else:
            model = Prophet()
            model.fit(df_prophet)

            future = model.make_future_dataframe(periods=3, freq='YE')
            forecast = model.predict(future)

            # 🧮 Bulatkan hasil prediksi agar jumlahnya realistis
            forecast["yhat"] = forecast["yhat"].round().clip(lower=0)
            forecast["yhat_lower"] = forecast["yhat_lower"].round().clip(lower=0)
            forecast["yhat_upper"] = forecast["yhat_upper"].round().clip(lower=0)

            fig_forecast = plot_plotly(model, forecast)
            st.plotly_chart(fig_forecast, use_container_width=True)

            # === ⬇️ Tambahan keterangan perubahan prediksi (% naik/turun) ===
            last_actual = df_prophet["y"].iloc[-1]
            next_year_pred = forecast["yhat"].iloc[-1]
            change_pct = ((next_year_pred - last_actual) / last_actual) * 100

            if change_pct > 0:
                arah = "peningkatan"
                emoji = "📈"
                warna = "green"
            else:
                arah = "penurunan"
                emoji = "📉"
                warna = "red"

            st.markdown(
                f"<p style='color:{warna}; font-size:16px; margin-top:10px;'>"
                f"{emoji} Prediksi menunjukkan <b>{arah}</b> sekitar "
                f"<b>{abs(change_pct):.2f}%</b> dibanding tahun terakhir "
                f"untuk inovasi <b>{bentuk_pilihan}</b> oleh <b>{skpd_pilihan}</b>.</p>",
                unsafe_allow_html=True
            )

            st.caption(f"🔮 Prediksi berdasarkan tren historis inovasi {bentuk_pilihan} oleh {skpd_pilihan}.")

    st.markdown("</div>", unsafe_allow_html=True)


# ======================
# 5. AI & REKOMENDASI
# ======================
elif menu == "🤖 Asisten Cerdas":
    st.title("🤖 Asisten Cerdas")

    query = st.text_input("Cari inovasi/penelitian (NLP search)...")
    if query:
        st.write("🔎 Hasil pencarian untuk:", query)
        st.write(data_penelitian.sample(3))

    st.subheader("💡 Rekomendasi Penelitian untuk SKPD")
    st.write("Contoh dummy rekomendasi:")

    st.write(data_penelitian.head(5))

# ======================
# 6. SDGs MAPPING
# ======================
elif menu == "🌍 Pemetaan SDGs":
    st.title("🌍 Mapping Inovasi ke SDGs")

    mapping = pd.DataFrame({
        "SDG": ["SDG 3", "SDG 4", "SDG 11"],
        "Jumlah Inovasi": [10, 15, 8]
    })
    st.bar_chart(mapping.set_index("SDG"))

# ======================
# 7. LAPORAN & EKSPOR
# ======================
elif menu == "📑 Rekap":
    st.title("📑 Laporan & Ekspor")
    st.write("💾 Fitur export ke CSV/Excel/PDF (coming soon).")

    st.download_button("Download Data Inovasi (CSV)", data_inovasi.to_csv().encode("utf-8"), "inovasi.csv")
    st.download_button("Download Data Penelitian (CSV)", data_penelitian.to_csv().encode("utf-8"), "penelitian.csv")
