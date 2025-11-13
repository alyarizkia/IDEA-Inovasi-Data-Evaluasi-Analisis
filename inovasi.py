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
    ["🏠 Beranda", "📚 Arsip", "📊 Lensa Inovasi", "🌍 Pemetaan SDGs"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.image("D:\\magang\\projek akhir\\foto\\ilustrasi-1.png", width="stretch")
st.sidebar.info("Welcome back 👋 Admin")

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
        <div class="hero-text">Selamat Pagi, Admin! 👋</div>
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

    # === Deskripsi Program IDEA ===
    st.markdown("""
    <div class="program-description">
        <h3 style="color:#1C4B89;">IDEA</h3>
        <p style="text-align:justify; font-size:18px;">
            <b>IDEA (Inovasi, Data, Evaluasi, Analisis)</b> platform analitik terintegrasi yang dikembangkan untuk memantau, mengevaluasi, dan memetakan berbagai inovasi
            serta penelitian dari perangkat daerah dan lembaga di Kota Surabaya. Sistem ini hadir untuk membantu pengambilan keputusan berbasis data,
            memperkuat kolaborasi antar perangkat daerah, dan meningkatkan efektivitas program pembangunan.
        </p>
        <p style="text-align:justify; font-size:18px;">
            Melalui IDEA, setiap inovasi dapat dipetakan kontribusinya terhadap <b>Sustainable Development Goals (SDGs)</b>, 
            dianalisis trennya, serta dibandingkan dengan kinerja sektor lain. 
            Tujuannya adalah menciptakan tata kelola inovasi yang lebih transparan, terukur, dan berkelanjutan, 
            untuk mewujudkan Surabaya sebagai kota yang <i>inovatif, adaptif, dan kolaboratif</i>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Tren & Update
    col1, col2 = st.columns(2)

    with col1:
        # Grafik Tren Inovasi
        st.markdown("""
        <div class="frame">
            <div class="frame-title"><span class="icon"></span> Grafik Tren Inovasi</div>
        """, unsafe_allow_html=True)

        # Deskripsi Tren Inovasi
        st.markdown("""
            <div class="section-description">
                <p style="font-size:15px; text-align:justify; color:#444; margin-top:0;">
                    Visualisasi ini menampilkan pola perkembangan jumlah inovasi dari tahun ke tahun.
                    Data ini membantu melihat dinamika semangat inovatif di berbagai Perangkat Daerah
                    dalam menciptakan solusi baru untuk pelayanan publik.
                </p>
            </div>
        """, unsafe_allow_html=True)

        df_tren_inovasi = data_inovasi.groupby("tahun").size().reset_index(name="jumlah")
        st.line_chart(df_tren_inovasi.set_index("tahun"))

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # Grafik Tren Penelitian
        st.markdown("""
            <div class="frame">
                <div class="frame-title"><span class="icon"></span> Grafik Tren Penelitian</div>
            """, unsafe_allow_html=True)
        
        # Deskripsi Tren Penelitian
        st.markdown("""
            <div class="section-description">
                <p style="font-size:15px; text-align:justify; color:#444; margin-top:0;">
                    Visualisasi ini menampilkan pola perkembangan penelitian dari tahun ke tahun yang
                    bertujuan untuk menunjukkan arah pertumbuhan aktivitas riset
                    dan kontribusi perguruan tinggi terhadap pengembangan kebijakan berbasis data.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # jumlah penelitian per tahun
        df_tren = data_penelitian.groupby("tahun").size().reset_index(name="jumlah")
        st.line_chart(df_tren.set_index("tahun"))

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

    st.markdown("""
        <div class="section-description">
            <p style="font-size:15px; text-align:justify; color:#444; margin-top:0;">
                Visualisasi ini menampilkan distribusi jenis inovasi yang dikembangkan oleh berbagai Perangkat Daerah. 
                Klasifikasi bentuk inovasi mencakup <b>Inovasi Pelayanan Publik</b>, 
                <b>Inovasi Tata Kelola Pemerintahan Daerah</b>, 
                serta <b>Inovasi Daerah Lainnya yang sesuai dengan urusan pemerintahan yang menjadi kewenangan daerah</b>. 
                Melalui visualisasi ini, dapat melihat fokus pengembangan inovasi di lingkungan Pemerintah Kota Surabaya.
            </p>
        </div>
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

    st.markdown("""
        <div class="section-description">
            <h3 style="color:#1C4B89; margin-bottom:4px;">Distribusi Bidang Penelitian</h3>
            <p style="font-size:15px; text-align:justify; color:#444; margin-top:0;">
                Visualisasi ini menampilkan sebaran jumlah penelitian berdasarkan bidang kajian strategis daerah. 
                Bidang-bidang tersebut mencakup <b>Infrastruktur dan Kewilayahan</b>, 
                <b>Perencanaan dan Evaluasi</b>, 
                <b>Pemerintahan dan Pembangunan Manusia</b>, 
                <b>Perekonomian dan Sumber Daya Alam</b>, 
                <b>Sekretariat</b>, serta <b>Penelitian dan Pengembangan</b>. 
                Distribusi ini membantu melihat fokus riset yang sedang dikembangkan oleh pemerintah daerah dan mitra akademik, 
                sekaligus menunjukkan arah prioritas pembangunan berbasis data dan ilmu pengetahuan di Kota Surabaya.
            </p>
        </div>
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
# 3. LENSA INOVASI
# ======================
elif menu == "📊 Lensa Inovasi":
    st.title("📊 Lensa Inovasi")

    sub_menu = st.radio(
        "📂 Pilih Analisis:",
        [
            "📈 Analisis & Prediksi Tren Inovasi", 
            "🎯 Radar Skor Indikator OPD", 
            "🧠 Korelasi Semantik Bentuk"
        ],
        horizontal=True
    )

    # ======================================================
    # === 1️⃣ SUB-MENU: ANALISIS & PREDIKSI TREN INOVASI (FORECAST) ===
    # ======================================================
    if sub_menu == "📈 Analisis & Prediksi Tren Inovasi":
        st.markdown("""
            <div class="frame">
                <div class="frame-title"><span class="icon"></span> Analisis & Prediksi Inovasi</div>
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

# ======================================================
# === 2️⃣ SUB-MENU: RADAR PLOT SKOR INDIKATOR OPD ===
# ======================================================
    elif sub_menu == "🎯 Radar Skor Indikator OPD":
        st.markdown("""
            <div class="frame">
                <div class="frame-title"><span class="icon"></span> Perbandingan Skor Indikator antar OPD</div>
        """, unsafe_allow_html=True)

        # === Ambil data dari database ===
        query_bobot_inovasis = "SELECT * FROM public.bobot_inovasis;"
        bobot_inovasis = pd.read_sql(query_bobot_inovasis, engine)

        query_bobot = "SELECT * FROM public.bobots;"
        bobot = pd.read_sql(query_bobot, engine)

        query_inovasi = """
            SELECT 
                i.id AS inovasi_id,
                i.nama,
                i.tahun,
                s.unit_nama AS skpd
            FROM public.inovasi i
            LEFT JOIN public.master_skpd s
                ON i.skpd_kode = s.unit_id::varchar;
        """
        inovasi = pd.read_sql(query_inovasi, engine)

        # === Daftar indikator yang relevan ===
        indikator_target = {
            16: "Regulasi Inovasi Daerah",
            17: "Ketersediaan SDM terhadap inovasi daerah",
            18: "Dukungan anggaran",
            19: "Bimtek inovasi",
            20: "Program dan Kegiatan Inovasi Perangkat Daerah dalam RKPD",
            21: "Keterlibatan aktor inovasi",
            22: "Pelaksana inovasi daerah",
            23: "Jejaring inovasi",
            24: "Sosialisasi Inovasi Daerah",
            25: "Pedoman teknis",
            26: "Kemudahan informasi layanan",
            27: "Kecepatan penciptaan inovasi",
            28: "Kemudahan proses inovasi yang dihasilkan",
            29: "Penyelesaian layanan pengaduan",
            30: "Layanan Terintegrasi",
            31: "Replikasi",
            32: "Alat Kerja",
            33: "Kemanfaatan inovasi",
            34: "Monitoring dan Evaluasi Inovasi Daerah",
            35: "Kualitas inovasi daerah"
        }

        # === Gabung data dari tabel ===
        df_join = (
            bobot_inovasis
            .merge(bobot, on="nomor", how="left")
            .merge(inovasi, on="inovasi_id", how="left")
        )

        # === Bersihkan data numerik ===
        df_join["perhitungan_nilai_bobot"] = pd.to_numeric(df_join["perhitungan_nilai_bobot"], errors="coerce")
        df_join = df_join.dropna(subset=["perhitungan_nilai_bobot", "indikator", "skpd"])

        # === Filter hanya indikator yang sesuai daftar ===
        df_join = df_join[df_join.apply(lambda row: row["nomor"] in indikator_target and row["indikator"] == indikator_target[row["nomor"]], axis=1)]

        # ==== HITUNG OPSI DARI df_join (harus dipanggil setelah df_join dibuat + difilter) ====
        skpd_opsi = sorted(df_join["skpd"].dropna().unique().tolist())
        indikator_opsi = sorted(df_join["indikator"].dropna().unique().tolist())

        # jika kosong, set list kosong agar code selanjutnya aman
        if not skpd_opsi:
            skpd_opsi = []
        if not indikator_opsi:
            indikator_opsi = []

        # --- STATE untuk menyimpan pilihan (buat UX tombol select all / clear) ---
        if "skpd_pilihan" not in st.session_state:
            st.session_state["skpd_pilihan"] = skpd_opsi[:5] if len(skpd_opsi) >= 5 else skpd_opsi.copy()
        if "indikator_pilihan" not in st.session_state:
            st.session_state["indikator_pilihan"] = indikator_opsi[:5] if len(indikator_opsi) >= 5 else indikator_opsi.copy()

        # ===== Tombol select all / clear =====
        col1, col2, col3, col4 = st.columns([1,1,1,1])

        with col1:
            if st.button("✅ Pilih Semua OPD"):
                # pakai copy() supaya session_state bebas dari mutasi list asli
                st.session_state["skpd_pilihan"] = skpd_opsi.copy()

        with col2:
            if st.button("❌ Hapus Semua OPD"):
                st.session_state["skpd_pilihan"] = []

        with col3:
            if st.button("✅ Pilih Semua Indikator"):
                st.session_state["indikator_pilihan"] = indikator_opsi.copy()

        with col4:
            if st.button("❌ Hapus Semua Indikator"):
                st.session_state["indikator_pilihan"] = []

        # ===== Multiselects (default sinkron dengan session_state) =====
        skpd_pilihan = st.multiselect(
            "🏛️ Pilih OPD untuk dibandingkan:",
            options=skpd_opsi,
            default=[x for x in st.session_state["skpd_pilihan"] if x in skpd_opsi]  # only keep valid defaults
        )

        indikator_pilihan = st.multiselect(
            "📊 Pilih indikator untuk dibandingkan:",
            options=indikator_opsi,
            default=[x for x in st.session_state["indikator_pilihan"] if x in indikator_opsi]
        )

        # jika user tidak memilih apapun
        if not skpd_pilihan:
            st.info("Pilih minimal 1 OPD. Pakai tombol '✅ Pilih Semua OPD' untuk memilih semua.")
        if not indikator_pilihan:
            st.info("Pilih minimal 1 indikator. Pakai tombol '✅ Pilih Semua Indikator' untuk memilih semua.")

        # === Olah data untuk radar ===
        df_radar = (
            df_join[
                (df_join["indikator"].isin(indikator_pilihan)) &
                (df_join["skpd"].isin(skpd_pilihan))
            ]
            .groupby(["skpd", "indikator"], as_index=False)["perhitungan_nilai_bobot"]
            .count()
        )

        # === Validasi data ===
        if df_radar.empty:
            st.warning("⚠️ Tidak ada data yang cocok dengan pilihan indikator.")
        else:
            import plotly.express as px

            fig = px.line_polar(
                df_radar,
                r="perhitungan_nilai_bobot",
                theta="indikator",
                color="skpd",
                line_close=True,
                markers=True,
                title="Radar Skor Indikator per OPD"
            )
            fig.update_traces(fill='toself')
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, df_radar["perhitungan_nilai_bobot"].max() * 1.2])
                )
            )

            st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

# === RADAR PLOT PER INOVASI ===
        st.markdown("""
            <div class="frame">
                <div class="frame-title"><span class="icon"></span> Perbandingan Skor Indikator antar Inovasi</div>
        """, unsafe_allow_html=True)

        # === Filter indikator & inovasi ===
        inovasi_opsi = sorted(df_join["nama"].dropna().unique().tolist())
        indikator_opsi2 = sorted(df_join["indikator"].dropna().unique().tolist())

        # --- STATE untuk menyimpan pilihan ---
        if "inovasi_pilihan" not in st.session_state:
            st.session_state["inovasi_pilihan"] = inovasi_opsi[:5] if len(inovasi_opsi) >= 5 else inovasi_opsi
        if "indikator_pilihan2" not in st.session_state:
            st.session_state["indikator_pilihan2"] = indikator_opsi2[:5] if len(indikator_opsi2) >= 5 else indikator_opsi2

        col1, col2, col3, col4 = st.columns([1,1,1,1])

        with col1:
            if st.button("✅ Pilih Semua Inovasi"):
                st.session_state["inovasi_pilihan"] = inovasi_opsi

        with col2:
            if st.button("❌ Hapus Semua Inovasi"):
                st.session_state["inovasi_pilihan"] = []

        with col3:
            if st.button("✅ Pilih Semua Indikator (Inovasi)"):
                st.session_state["indikator_pilihan2"] = indikator_opsi2

        with col4:
            if st.button("❌ Hapus Semua Indikator (Inovasi)"):
                st.session_state["indikator_pilihan2"] = []

        # --- Multiselects ---
        inovasi_pilihan = st.multiselect(
            "💡 Pilih inovasi untuk dibandingkan:",
            inovasi_opsi,
            default=st.session_state["inovasi_pilihan"]
        )

        indikator_pilihan2 = st.multiselect(
            "📊 Pilih indikator untuk dibandingkan (inovasi):",
            indikator_opsi2,
            default=st.session_state["indikator_pilihan2"]
        )

        # jika user tidak memilih apapun
        if not inovasi_pilihan:
            st.info("Pilih minimal 1 Inovasi. Pakai tombol '✅ Pilih Semua Inovasi' untuk memilih semua.")
        if not indikator_pilihan2:
            st.info("Pilih minimal 1 indikator. Pakai tombol '✅ Pilih Semua Indikator (Inovasi)' untuk memilih semua.")

        # === Olah data untuk radar versi inovasi ===
        df_radar_inovasi = (
            df_join[
                (df_join["indikator"].isin(indikator_pilihan2)) &
                (df_join["nama"].isin(inovasi_pilihan))
            ]
            .groupby(["nama", "indikator"], as_index=False)["perhitungan_nilai_bobot"]
            .count()
        )

        # === Validasi data ===
        if df_radar_inovasi.empty:
            st.warning("⚠️ Tidak ada data yang cocok dengan pilihan indikator atau inovasi.")
        else:
            import plotly.express as px

            fig2 = px.line_polar(
                df_radar_inovasi,
                r="perhitungan_nilai_bobot",
                theta="indikator",
                color="nama",
                line_close=True,
                markers=True,
                title="Radar Skor Indikator per Inovasi"
            )
            fig2.update_traces(fill='toself')
            fig2.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, df_radar_inovasi["perhitungan_nilai_bobot"].max() * 1.2])
                )
            )

            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# === 3️⃣ SUB-MENU: KORELASI SEMANTIK BENTUK INOVASI ===
# ======================================================
    elif sub_menu == "🧠 Korelasi Semantik Bentuk":
        st.markdown("""
            <div class="frame">
                <div class="frame-title"><span class="icon"></span> Korelasi Semantik antar Bentuk Inovasi</div>
                <p>Analisis makna deskripsi <b>manfaat</b> dan <b>hasil</b> antar bentuk inovasi daerah menggunakan <b>IndoBERT</b> untuk embedding semantik, serta <b>TF-IDF</b> untuk visualisasi kata kunci dominan.</p>
            </div>
        """, unsafe_allow_html=True)

        # === 1️⃣ Ambil data dari database ===
        query = """
            SELECT 
                i.id,
                i.nama,
                i.bentuk,
                i.manfaat,
                i.hasil,
                i.tahun,
                s.unit_nama AS skpd
            FROM public.inovasi i
            LEFT JOIN public.master_skpd s
                ON i.skpd_kode = s.unit_id::varchar
            WHERE i.manfaat IS NOT NULL OR i.hasil IS NOT NULL;
        """
        df_inovasi = pd.read_sql(query, engine)

        if df_inovasi.empty:
            st.warning("⚠️ Tidak ada data inovasi yang memiliki deskripsi manfaat atau hasil.")
        else:
            # === 2️⃣ Mapping Bentuk agar seragam (hapus angka 1/2/3) ===
            mapping_bentuk = {
                "1": "Inovasi tata kelola pemerintahan daerah",
                "2": "Inovasi pelayanan publik",
                "3": "Inovasi Daerah lainnya sesuai dengan Urusan Pemerintahan yang menjadi kewenangan Daerah"
            }
            df_inovasi["bentuk"] = df_inovasi["bentuk"].astype(str).replace(mapping_bentuk)

            # === 3️⃣ Filter Tahun dan OPD ===
            tahun_list = sorted(df_inovasi["tahun"].dropna().unique().tolist())
            opd_list = sorted(df_inovasi["skpd"].dropna().unique().tolist())

            col1, col2 = st.columns(2)
            selected_tahun = col1.selectbox("📅 Pilih Tahun:", ["Semua"] + tahun_list)
            selected_opd = col2.selectbox("🏢 Pilih OPD:", ["Semua"] + opd_list)

            # Terapkan filter
            df_filtered = df_inovasi.copy()
            if selected_tahun != "Semua":
                df_filtered = df_filtered[df_filtered["tahun"] == selected_tahun]
            if selected_opd != "Semua":
                df_filtered = df_filtered[df_filtered["skpd"] == selected_opd]

            if df_filtered.empty:
                st.warning("⚠️ Tidak ada data inovasi untuk filter yang dipilih.")
            else:
                # === 4️⃣ Gabungkan teks manfaat + hasil ===
                df_filtered["gabungan"] = (
                    df_filtered["manfaat"].fillna('') + " " + df_filtered["hasil"].fillna('')
                )

                # === 5️⃣ Kelompokkan per bentuk inovasi ===
                df_text = (
                    df_filtered.groupby("bentuk", as_index=False)["gabungan"]
                    .apply(lambda x: " ".join(x))
                )

                # Hapus bentuk yang kosong / null
                df_text = df_text[df_text["bentuk"].notna() & (df_text["bentuk"] != "")].drop_duplicates(subset=["bentuk"])

                # =========================================================
                # === 🔹 HEATMAP KORELASI SEMANTIK (IndoBERT) ===
                # =========================================================
                st.subheader("🧩 Heatmap Korelasi Semantik antar Bentuk Inovasi (IndoBERT)")

                from sentence_transformers import SentenceTransformer
                from sklearn.metrics.pairwise import cosine_similarity
                import seaborn as sns
                import matplotlib.pyplot as plt
                import textwrap

                with st.spinner("🔍 Menghitung embedding semantik dengan IndoBERT..."):
                    model = SentenceTransformer("indobenchmark/indobert-base-p1")
                    embeddings = model.encode(df_text["gabungan"].tolist(), show_progress_bar=True)

                # === Hitung similarity matrix ===
                sim_matrix = cosine_similarity(embeddings)

                # === Bungkus label panjang biar nggak tumpuk di heatmap ===
                bentuk_labels_wrapped = [
                    "\n".join(textwrap.wrap(label, width=40)) for label in df_text["bentuk"].tolist()
                ]

                # === Bikin DataFrame pakai label yang udah dibungkus ===
                sim_df = pd.DataFrame(sim_matrix, index=bentuk_labels_wrapped, columns=bentuk_labels_wrapped)

                # === Plot Heatmap ===
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(sim_df, cmap="coolwarm", annot=True, fmt=".2f", linewidths=0.5, ax=ax)
                plt.title(f"Korelasi Semantik antar Bentuk Inovasi ({selected_tahun if selected_tahun!='Semua' else 'Semua Tahun'})", fontsize=14)
                st.pyplot(fig)

                # === Top 5 Korelasi Tertinggi (kompatibel) ===
                st.markdown("### 🔝 5 Pasangan Bentuk Inovasi Paling Mirip (Berdasarkan Semantik)")

                # stack -> reset_index -> set column names
                sim_pairs = sim_df.stack().reset_index()
                sim_pairs.columns = ["bentuk_1", "bentuk_2", "similarity"]

                # hapus self-pairs (A,A)
                sim_pairs = sim_pairs[sim_pairs["bentuk_1"] != sim_pairs["bentuk_2"]]

                # supaya (A,B) dan (B,A) nggak muncul dua kali, keep only one ordering (lexicographic)
                sim_pairs = sim_pairs[sim_pairs["bentuk_1"] < sim_pairs["bentuk_2"]]

                # urutkan dan ambil top 5
                top_sim = sim_pairs.sort_values("similarity", ascending=False).head(5).reset_index(drop=True)

                st.dataframe(top_sim)

                st.info("""
                    💡 **Interpretasi:**
                    Semakin tinggi nilai similarity (mendekati 1), semakin mirip makna teks *manfaat + hasil* antar bentuk inovasi.
                    Nilai mendekati 0 berarti kedua bentuk berbeda secara semantik.
                """)

                # ======================================================
                # === 🔹 WORDCLOUD BERDASARKAN TF-IDF PER BENTUK (DENGAN STOPWORDS EXCEL) ===
                # ======================================================
                st.subheader("☁️ WordCloud Kata Dominan per Bentuk Inovasi (TF-IDF)")

                from sklearn.feature_extraction.text import TfidfVectorizer
                from wordcloud import WordCloud
                import pandas as pd
                import matplotlib.pyplot as plt
                import streamlit as st

                # === 1️⃣ Baca Stopwords dari Excel ===
                stopwords_path = "D:/magang/projek akhir/list_stopwords.csv"
                stopwords_df = pd.read_csv(stopwords_path)

                stopwords_list = (
                    stopwords_df.iloc[:, 0]        # ambil kolom pertama
                    .dropna()                      # hapus baris kosong
                    .astype(str)                   # ubah ke string
                    .str.lower()                   # lowercase semua
                    .tolist()                      # ubah ke list
                )

                # === 2️⃣ TF-IDF Vectorizer dengan stopwords dari Excel ===
                vectorizer = TfidfVectorizer(stop_words=stopwords_list, max_features=1000)
                tfidf_matrix = vectorizer.fit_transform(df_text["gabungan"])
                feature_names = vectorizer.get_feature_names_out()

                # === 3️⃣ Generate WordCloud untuk tiap kategori bentuk ===
                for i, bentuk in enumerate(df_text["bentuk"]):
                    st.markdown(f"#### 🌀 {bentuk}")
                    vector = tfidf_matrix[i].toarray()[0]
                    tfidf_dict = {feature_names[j]: float(vector[j]) for j in range(len(feature_names)) if vector[j] > 0}

                    if tfidf_dict:
                        wc = WordCloud(
                            width=800, height=400, background_color="white",
                            colormap="viridis", max_words=100
                        ).generate_from_frequencies(tfidf_dict)

                        fig_wc, ax_wc = plt.subplots(figsize=(8, 4))
                        ax_wc.imshow(wc, interpolation="bilinear")
                        ax_wc.axis("off")
                        st.pyplot(fig_wc)
                    else:
                        st.warning(f"Tidak ada kata signifikan untuk bentuk '{bentuk}'.")

# ======================
# 4. SDGs MAPPING
# ======================
elif menu == "🌍 Pemetaan SDGs":
    st.title("🌍 Mapping Inovasi ke SDGs")

    sub_menu = st.radio(
        "📂 Pilih Jenis Pemetaan:",
        ["🤖 Mapping Otomatis", 
         "🏛️ Kontribusi OPD terhadap SDGs",
         "📈 Tren SDGs"],
        horizontal=True
    )
    # ==============================
    # MAPPING OTOMATIS SDGs
    # ==============================
    if sub_menu == "🤖 Mapping Otomatis":
        st.markdown("### 🤖 Pemetaan Otomatis Inovasi ke SDGs Berdasarkan Teks")

        import pandas as pd
        import numpy as np
        import streamlit as st
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        from sklearn.feature_extraction.text import TfidfVectorizer
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt
        import seaborn as sns
        import plotly.graph_objects as go
        import plotly.express as px
        import textwrap

        # === Ambil data dari database ===
        query = """
            SELECT 
                i.id,
                i.nama,
                i.bentuk,
                i.manfaat,
                i.hasil,
                i.tahun,
                s.unit_nama AS skpd
            FROM public.inovasi i
            LEFT JOIN public.master_skpd s
                ON i.skpd_kode = s.unit_id::varchar
            WHERE i.manfaat IS NOT NULL OR i.hasil IS NOT NULL;
        """
        df_inovasi = pd.read_sql(query, engine)
        df_inovasi.rename(columns={"skpd": "opd"}, inplace=True)

        # === Daftar SDGs dan deskripsi singkatnya ===
        sdg_deskripsi = {
            "SDG 1": "No Poverty – mengakhiri kemiskinan dengan mengembangkan strategi pengembangan ekonomi lokal, meningkatkan pendapatan dan membangun ketahanan masyarakat terhadap potensi-potensi bencana",
            "SDG 2": "Zero Hunger – mengakhiri kelaparan mencapai ketahanan pangan dan meningkatkan gizi dan mendukung pertanian berkelanjutan",
            "SDG 3": "Good Health and Well-Being – menjamin kehidupan sehat dan mendukung kesejahteraan bagi semua di segala usia",
            "SDG 4": "Quality Education – menjamin pendidikan yang inklusif dan  setara secara kualitas dan mendukung kesempatan belajar seumur hidup bagi semua",
            "SDG 5": "Gender Equality – mencapai kesetaraan gender dan pemberdayaan perempuan dan anak perempuan",
            "SDG 6": "Clean Water and Sanitation – menjamin ketersediaan dan manajemen air dan sanitasi Yang berkelanjutan untuk semua",
            "SDG 7": "Affordable and Clean Energy – menjamin akses terhadap energi yang terjangkau, dapat diandalkan, berkelanjutan dan modern bagi semua",
            "SDG 8": "Decent Work and Economic Growth – mendukung pertumbuhan ekonomi yang inklusif dan berkelanjutan, penyerapan tenaga kerja Penuh dan produktif serta pekerjaan yang layak bagi semua",
            "SDG 9": "Industry, Innovation and Infrastructure – membangun infrastruktur berketahanan mendukung industrialisasi yang inkulsif dan berkelanjutan serta mendorong inovasi",
            "SDG 10": "Reduced Inequalities – mengurangi ketimpangan atau kesenjangan di dalam dan di antara negara-negara",
            "SDG 11": "Sustainable Cities and Communities – mewujudkan kota-kota dan permukiman yang inklusif, aman, tangguh dan berkelanjutan",
            "SDG 12": "Responsible Consumption and Production – menjamin pola produksi dan konsumsi yang berkelanjutan",
            "SDG 13": "Climate Action – segera mengambil tindakan untuk melawan perubahan iklim dan dampaknya",
            "SDG 14": "Life Below Water – mengkonservasi dan memanfaatkan secara berkelanjutan sumber data maritim, laut, dan samudera untuk pembangunan yang berkelanjutan",
            "SDG 15": "Life on Land – melindungi, memulihkan, dan mendukung penggunaan yang bekelanjutan terhadap ekosistem daratan",
            "SDG 16": "Peace, Justice and Strong Institutions – memperjuangkan masyarakat yang damai dan inklusi dan menyediakan akses terhadap keadilan bagi semua",
            "SDG 17": "Partnerships for the Goals – menguatkan perangkat implementasi dan merevitalisasi kemitraan global untuk pembangunan yang berkelanjutan."
        }

        # === Filter tahun dan OPD ===
        tahun_list = sorted(df_inovasi["tahun"].dropna().unique().tolist())
        opd_list = sorted(df_inovasi["opd"].dropna().unique().tolist())

        col1, col2 = st.columns(2)
        selected_tahun = col1.selectbox("📅 Pilih Tahun:", ["Semua"] + tahun_list)
        selected_opd = col2.selectbox("🏢 Pilih OPD:", ["Semua"] + opd_list)

        df_filtered = df_inovasi.copy()
        if selected_tahun != "Semua":
            df_filtered = df_filtered[df_filtered["tahun"] == selected_tahun]
        if selected_opd != "Semua":
            df_filtered = df_filtered[df_filtered["opd"] == selected_opd]

        if df_filtered.empty:
            st.warning("⚠️ Tidak ada data inovasi untuk filter yang dipilih.")
            st.stop()

        # === Gabungkan teks manfaat + hasil ===
        df_filtered["gabungan"] = (
            df_filtered["manfaat"].fillna('') + " " + df_filtered["hasil"].fillna('')
        )

        # === Encode teks inovasi dan deskripsi SDGs ===
        with st.spinner("🤖 Menghitung kemiripan teks dengan IndoBERT..."):
            model = SentenceTransformer("indobenchmark/indobert-base-p1")

            inovasi_embeddings = model.encode(df_filtered["gabungan"].tolist(), show_progress_bar=True)
            sdg_embeddings = model.encode(list(sdg_deskripsi.values()), show_progress_bar=True)

        # === Hitung cosine similarity ===
        similarity_matrix = cosine_similarity(inovasi_embeddings, sdg_embeddings)

        # === Tentukan SDG dengan similarity tertinggi untuk setiap inovasi ===
        best_match_indices = similarity_matrix.argmax(axis=1)
        df_filtered["SDG_Terkait"] = [
            list(sdg_deskripsi.keys())[i] for i in best_match_indices
        ]
        df_filtered["Nilai_Kemiripan"] = [
            similarity_matrix[idx, i] for idx, i in enumerate(best_match_indices)
        ]

        # === Tampilkan hasil ===
        st.success("✅ Pemetaan otomatis selesai!")
        st.dataframe(
            df_filtered[["id", "nama", "opd", "tahun", "SDG_Terkait", "Nilai_Kemiripan"]],
            hide_index=True
        )

        # === Visualisasi: Jumlah Inovasi per SDG ===
        st.subheader("📊 Distribusi Hasil Pemetaan ke SDGs")
        sdg_counts = df_filtered["SDG_Terkait"].value_counts().reset_index()
        sdg_counts.columns = ["SDG", "Jumlah Inovasi"]

        fig = px.bar(
            sdg_counts, 
            x="SDG", 
            y="Jumlah Inovasi",
            text="Jumlah Inovasi",
            color="SDG",
            color_discrete_sequence=px.colors.qualitative.Safe,
            title="Jumlah Inovasi per SDG"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(xaxis_title="SDG", yaxis_title="Jumlah Inovasi", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # ==============================
    # 2️⃣ KONTRIBUSI OPD TERHADAP SDGs
    # ==============================
    elif sub_menu == "🏛️ Kontribusi OPD terhadap SDGs":
        st.markdown("### 🏛️ Analisis Kontribusi OPD terhadap Pencapaian SDGs")

        import plotly.express as px
        import plotly.graph_objects as go
        import numpy as np
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity

        # === Daftar SDGs dan deskripsi singkatnya ===
        sdg_deskripsi = {
            "SDG 1": "No Poverty – mengakhiri kemiskinan dengan mengembangkan strategi pengembangan ekonomi lokal, meningkatkan pendapatan dan membangun ketahanan masyarakat terhadap potensi-potensi bencana",
            "SDG 2": "Zero Hunger – mengakhiri kelaparan mencapai ketahanan pangan dan meningkatkan gizi dan mendukung pertanian berkelanjutan",
            "SDG 3": "Good Health and Well-Being – menjamin kehidupan sehat dan mendukung kesejahteraan bagi semua di segala usia",
            "SDG 4": "Quality Education – menjamin pendidikan yang inklusif dan  setara secara kualitas dan mendukung kesempatan belajar seumur hidup bagi semua",
            "SDG 5": "Gender Equality – mencapai kesetaraan gender dan pemberdayaan perempuan dan anak perempuan",
            "SDG 6": "Clean Water and Sanitation – menjamin ketersediaan dan manajemen air dan sanitasi Yang berkelanjutan untuk semua",
            "SDG 7": "Affordable and Clean Energy – menjamin akses terhadap energi yang terjangkau, dapat diandalkan, berkelanjutan dan modern bagi semua",
            "SDG 8": "Decent Work and Economic Growth – mendukung pertumbuhan ekonomi yang inklusif dan berkelanjutan, penyerapan tenaga kerja Penuh dan produktif serta pekerjaan yang layak bagi semua",
            "SDG 9": "Industry, Innovation and Infrastructure – membangun infrastruktur berketahanan mendukung industrialisasi yang inkulsif dan berkelanjutan serta mendorong inovasi",
            "SDG 10": "Reduced Inequalities – mengurangi ketimpangan atau kesenjangan di dalam dan di antara negara-negara",
            "SDG 11": "Sustainable Cities and Communities – mewujudkan kota-kota dan permukiman yang inklusif, aman, tangguh dan berkelanjutan",
            "SDG 12": "Responsible Consumption and Production – menjamin pola produksi dan konsumsi yang berkelanjutan",
            "SDG 13": "Climate Action – segera mengambil tindakan untuk melawan perubahan iklim dan dampaknya",
            "SDG 14": "Life Below Water – mengkonservasi dan memanfaatkan secara berkelanjutan sumber data maritim, laut, dan samudera untuk pembangunan yang berkelanjutan",
            "SDG 15": "Life on Land – melindungi, memulihkan, dan mendukung penggunaan yang bekelanjutan terhadap ekosistem daratan",
            "SDG 16": "Peace, Justice and Strong Institutions – memperjuangkan masyarakat yang damai dan inklusi dan menyediakan akses terhadap keadilan bagi semua",
            "SDG 17": "Partnerships for the Goals – menguatkan perangkat implementasi dan merevitalisasi kemitraan global untuk pembangunan yang berkelanjutan."
        }

        if "df_mapping" not in st.session_state:
            with st.spinner("🔄 Belum ada hasil mapping. Menjalankan proses otomatis..."):
                query = """
                SELECT 
                    i.id,
                    i.nama,
                    i.manfaat,
                    i.hasil,
                    s.unit_nama AS opd
                FROM public.inovasi i
                LEFT JOIN public.master_skpd s
                    ON i.skpd_kode = s.unit_id::varchar
                WHERE i.manfaat IS NOT NULL OR i.hasil IS NOT NULL;
            """
            df_inovasi = pd.read_sql(query, engine)
            df_inovasi["gabungan"] = df_inovasi["manfaat"].fillna('') + " " + df_inovasi["hasil"].fillna('')

            # Buat embedding dan hitung kesamaan
            model = SentenceTransformer("indobenchmark/indobert-base-p1")
            sdg_names = list(sdg_deskripsi.keys())
            sdg_texts = list(sdg_deskripsi.values())
            sdg_embeddings = model.encode(sdg_texts)
            inovasi_embeddings = model.encode(df_inovasi["gabungan"].tolist())

            sim_matrix = cosine_similarity(inovasi_embeddings, sdg_embeddings)
            best_match_idx = np.argmax(sim_matrix, axis=1)

            df_inovasi["SDG_Terkait"] = [sdg_names[i] for i in best_match_idx]
            df_inovasi["Skor_Kemiripan"] = [sim_matrix[i, j] for i, j in enumerate(best_match_idx)]

            st.session_state["df_mapping"] = df_inovasi
            st.success("✅ Mapping otomatis selesai!")

        # === Setelah itu, lanjut analisis kontribusi seperti biasa ===
        df_mapping = st.session_state["df_mapping"]

        contrib = df_mapping.groupby(["opd", "SDG_Terkait"]).size().reset_index(name="Jumlah_Inovasi")

        st.subheader("🏆 Ranking OPD per SDG")
        selected_sdg = st.selectbox("🎯 Pilih SDG:", sorted(df_mapping["SDG_Terkait"].unique()))
        ranking = contrib[contrib["SDG_Terkait"] == selected_sdg].sort_values("Jumlah_Inovasi", ascending=False)
        st.dataframe(ranking)

        st.subheader(f"📊 Ranking Kontribusi OPD pada {selected_sdg}")
        fig = px.bar(ranking, x="Jumlah_Inovasi", y="opd", orientation="h",
                    title=f"Kontribusi OPD terhadap {selected_sdg}",
                    color="Jumlah_Inovasi", color_continuous_scale="Viridis")
        st.plotly_chart(fig, use_container_width=True)

        # Radar chart tetap sama
        st.subheader("🎯 Profil Kontribusi SDGs per OPD")
        selected_opd = st.selectbox("🏢 Pilih OPD:", sorted(df_mapping["opd"].dropna().unique()))
        opd_profile = contrib[contrib["opd"] == selected_opd].pivot(index="opd", columns="SDG_Terkait", values="Jumlah_Inovasi").fillna(0)
        categories = opd_profile.columns.tolist()
        values = opd_profile.values.flatten().tolist()
        values += values[:1]
        fig_radar = go.Figure(data=go.Scatterpolar(r=values, theta=categories + [categories[0]], fill='toself', name=selected_opd))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False,
                                title=f"Radar Kontribusi {selected_opd} terhadap SDGs")
        st.plotly_chart(fig_radar, use_container_width=True)

    # ==============================
    # 3️⃣ TREN SDGs DARI WAKTU KE WAKTU (MANDIRI + WARNA SDG RESMI)
    # ==============================
    elif sub_menu == "📈 Tren SDGs":
        st.markdown("### 📈 Tren Kontribusi Inovasi terhadap SDGs dari Waktu ke Waktu")

        import plotly.express as px
        import plotly.graph_objects as go
        import numpy as np
        import pandas as pd
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity

        # === Warna resmi SDGs (United Nations style) ===
        sdg_colors = {
            "SDG 1": "#E5243B",  # No Poverty
            "SDG 2": "#DDA63A",  # Zero Hunger
            "SDG 3": "#4C9F38",  # Good Health and Well-Being
            "SDG 4": "#C5192D",  # Quality Education
            "SDG 5": "#FF3A21",  # Gender Equality
            "SDG 6": "#26BDE2",  # Clean Water and Sanitation
            "SDG 7": "#FCC30B",  # Affordable and Clean Energy
            "SDG 8": "#A21942",  # Decent Work and Economic Growth
            "SDG 9": "#FD6925",  # Industry, Innovation and Infrastructure
            "SDG 10": "#DD1367", # Reduced Inequalities
            "SDG 11": "#FD9D24", # Sustainable Cities and Communities
            "SDG 12": "#BF8B2E", # Responsible Consumption and Production
            "SDG 13": "#3F7E44", # Climate Action
            "SDG 14": "#0A97D9", # Life Below Water
            "SDG 15": "#56C02B", # Life on Land
            "SDG 16": "#00689D", # Peace, Justice and Strong Institutions
            "SDG 17": "#19486A"  # Partnerships for the Goals
        }

        # === Daftar SDGs dan deskripsi singkatnya ===
        sdg_deskripsi = {
            "SDG 1": "No Poverty – mengakhiri kemiskinan dengan mengembangkan strategi pengembangan ekonomi lokal, meningkatkan pendapatan dan membangun ketahanan masyarakat terhadap potensi-potensi bencana",
            "SDG 2": "Zero Hunger – mengakhiri kelaparan mencapai ketahanan pangan dan meningkatkan gizi dan mendukung pertanian berkelanjutan",
            "SDG 3": "Good Health and Well-Being – menjamin kehidupan sehat dan mendukung kesejahteraan bagi semua di segala usia",
            "SDG 4": "Quality Education – menjamin pendidikan yang inklusif dan  setara secara kualitas dan mendukung kesempatan belajar seumur hidup bagi semua",
            "SDG 5": "Gender Equality – mencapai kesetaraan gender dan pemberdayaan perempuan dan anak perempuan",
            "SDG 6": "Clean Water and Sanitation – menjamin ketersediaan dan manajemen air dan sanitasi yang berkelanjutan untuk semua",
            "SDG 7": "Affordable and Clean Energy – menjamin akses terhadap energi yang terjangkau, dapat diandalkan, berkelanjutan dan modern bagi semua",
            "SDG 8": "Decent Work and Economic Growth – mendukung pertumbuhan ekonomi yang inklusif dan berkelanjutan, penyerapan tenaga kerja penuh dan produktif serta pekerjaan yang layak bagi semua",
            "SDG 9": "Industry, Innovation and Infrastructure – membangun infrastruktur berketahanan mendukung industrialisasi yang inklusif dan berkelanjutan serta mendorong inovasi",
            "SDG 10": "Reduced Inequalities – mengurangi ketimpangan atau kesenjangan di dalam dan di antara negara-negara",
            "SDG 11": "Sustainable Cities and Communities – mewujudkan kota-kota dan permukiman yang inklusif, aman, tangguh dan berkelanjutan",
            "SDG 12": "Responsible Consumption and Production – menjamin pola produksi dan konsumsi yang berkelanjutan",
            "SDG 13": "Climate Action – segera mengambil tindakan untuk melawan perubahan iklim dan dampaknya",
            "SDG 14": "Life Below Water – mengkonservasi dan memanfaatkan secara berkelanjutan sumber daya maritim, laut, dan samudera untuk pembangunan yang berkelanjutan",
            "SDG 15": "Life on Land – melindungi, memulihkan, dan mendukung penggunaan yang berkelanjutan terhadap ekosistem daratan",
            "SDG 16": "Peace, Justice and Strong Institutions – memperjuangkan masyarakat yang damai dan inklusi dan menyediakan akses terhadap keadilan bagi semua",
            "SDG 17": "Partnerships for the Goals – memperkuat perangkat implementasi dan merevitalisasi kemitraan global untuk pembangunan berkelanjutan"
        }

        # === Ambil data dari database ===
        with st.spinner("📥 Mengambil data inovasi dari database..."):
            query = """
            SELECT 
                i.id,
                i.nama,
                i.manfaat,
                i.hasil,
                i.tahun,
                s.unit_nama AS opd
                FROM public.inovasi i
                LEFT JOIN public.master_skpd s
                    ON i.skpd_kode = s.unit_id::varchar
            WHERE i.manfaat IS NOT NULL OR i.hasil IS NOT NULL;
            """
            df_inovasi = pd.read_sql(query, engine)
            df_inovasi["gabungan"] = df_inovasi["manfaat"].fillna('') + " " + df_inovasi["hasil"].fillna('')

        # === Pemetaan ke SDGs (IndoBERT) ===
        with st.spinner("🤖 Melakukan pemetaan otomatis ke 17 SDGs..."):
            model = SentenceTransformer("indobenchmark/indobert-base-p1")
            sdg_names = list(sdg_deskripsi.keys())
            sdg_texts = list(sdg_deskripsi.values())
            sdg_embeddings = model.encode(sdg_texts)
            inovasi_embeddings = model.encode(df_inovasi["gabungan"].tolist())

            sim_matrix = cosine_similarity(inovasi_embeddings, sdg_embeddings)
            best_match_idx = np.argmax(sim_matrix, axis=1)

            df_inovasi["SDG_Terkait"] = [sdg_names[i] for i in best_match_idx]
            df_inovasi["Skor_Kemiripan"] = [sim_matrix[i, j] for i, j in enumerate(best_match_idx)]

        st.success("✅ Pemetaan SDGs berhasil dilakukan!")

        # === Analisis Tren ===
        st.subheader("📊 Jumlah Inovasi per SDG per Tahun")

        tren = df_inovasi.groupby(["tahun", "SDG_Terkait"]).size().reset_index(name="Jumlah_Inovasi")

        fig_line = px.line(
            tren,
            x="tahun",
            y="Jumlah_Inovasi",
            color="SDG_Terkait",
            markers=True,
            title="Tren Jumlah Inovasi berdasarkan SDGs",
            color_discrete_map=sdg_colors
        )
        fig_line.update_layout(legend_title_text="SDG")
        st.plotly_chart(fig_line, use_container_width=True)

        # === Fokus SDG tertentu ===
        selected_sdg = st.selectbox("🎯 Pilih SDG untuk analisis mendalam:", sorted(df_inovasi["SDG_Terkait"].unique()))
        tren_sdg = tren[tren["SDG_Terkait"] == selected_sdg]

        fig_bar = px.bar(
            tren_sdg,
            x="tahun",
            y="Jumlah_Inovasi",
            title=f"📅 Tren Inovasi untuk {selected_sdg}",
            color="SDG_Terkait",
            color_discrete_map=sdg_colors,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # === SDG dengan perubahan signifikan ===
        st.subheader("📈 SDG dengan Perubahan Signifikan")

        # --- Filter tambahan untuk bagian ini ---
        col1, col2 = st.columns(2)
        selected_opd_sig = col1.selectbox("🏢 Pilih OPD (Opsional):", ["Semua"] + sorted(df_inovasi["opd"].dropna().unique().tolist()))
        selected_tahun_sig = col2.selectbox("📅 Batas Tahun (Opsional):", ["Semua"] + sorted(df_inovasi["tahun"].dropna().unique().tolist()))

        # --- Terapkan filter jika dipilih ---
        df_sig = tren.copy()
        if selected_opd_sig != "Semua":
            df_sig = df_inovasi[df_inovasi["opd"] == selected_opd_sig]
            df_sig = df_sig.groupby(["tahun", "SDG_Terkait"]).size().reset_index(name="Jumlah_Inovasi")

        if selected_tahun_sig != "Semua":
            df_sig = df_sig[df_sig["tahun"] <= selected_tahun_sig]

        # --- Hitung perubahan signifikan ---
        if df_sig.empty:
            st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
        else:
            perubahan = df_sig.pivot(index="tahun", columns="SDG_Terkait", values="Jumlah_Inovasi").fillna(0)
            delta = perubahan.diff().fillna(0).sum().sort_values(ascending=False)

            naik_terbanyak = delta.index[0]
            turun_terbanyak = delta.index[-1]

            st.success(f"📈 SDG dengan peningkatan kontribusi paling signifikan: **{naik_terbanyak}** (+{delta.iloc[0]:.0f} inovasi)")
            st.error(f"📉 SDG dengan penurunan kontribusi paling signifikan: **{turun_terbanyak}** ({delta.iloc[-1]:.0f} inovasi)")

            st.info("💡 Filter ini memungkinkan kamu melihat perubahan SDGs spesifik untuk OPD atau tahun tertentu.")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🚀 SDG dengan Kenaikan Terbesar", naik_terbanyak, f"+{int(delta.max())} inovasi")
        with col2:
            st.metric("📉 SDG dengan Penurunan Terbesar", turun_terbanyak, f"{int(delta.min())} inovasi")

        # === Distribusi per tahun ===
        st.subheader("🗓️ Distribusi SDGs per Tahun")
        selected_year = st.selectbox("Pilih Tahun:", sorted(df_inovasi["tahun"].dropna().unique()))
        distribusi = tren[tren["tahun"] == selected_year].sort_values("Jumlah_Inovasi", ascending=False)

        fig_pie = px.pie(
            distribusi,
            names="SDG_Terkait",
            values="Jumlah_Inovasi",
            title=f"Proporsi Inovasi per SDG di Tahun {selected_year}",
            color="SDG_Terkait",
            color_discrete_map=sdg_colors,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

