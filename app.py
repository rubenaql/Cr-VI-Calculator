import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import linregress
import time
import datetime
from fpdf import FPDF
import tempfile
import os

# Konfigurasi Halaman
st.set_page_config(page_title="Cr(VI) Kelompok 2", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main-title { text-align: center; color: var(--primary-color); font-size: 2.8rem; font-weight: 800; margin-bottom: 0; }
    .sub-title { text-align: center; color: var(--text-color); font-size: 1.2rem; font-weight: 500; margin-top: 0; margin-bottom: 2rem; opacity: 0.8; }
    .status-box-success { padding: 15px; border-radius: 8px; border-left: 6px solid #27ae60; background-color: rgba(39, 174, 96, 0.1); color: var(--text-color); font-weight: bold; margin-top: 15px; }
    .status-box-error { padding: 15px; border-radius: 8px; border-left: 6px solid #c0392b; background-color: rgba(192, 57, 43, 0.1); color: var(--text-color); font-weight: bold; margin-top: 15px; }
    .status-box-info { padding: 15px; border-radius: 8px; border-left: 6px solid #2980b9; background-color: rgba(41, 128, 185, 0.1); color: var(--text-color); margin-top: 15px; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# Helper function to generate PDF
def create_pdf(slope, intercept, r_val, r2_val, kal_status, abs1, abs2, rpd, presisi_status, recov, akurasi_status, fig,
               tipe_presisi="Duplo", rsd=0.0, sd=0.0, n_replikasi=2, rerata_sampel=0.0):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0, 10, 'LAPORAN PENGUJIAN LABORATORIUM', ln=True, align='C')
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, 'Parameter: Kromium Heksavalen (Cr(VI))', ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 6, f'Tanggal Cetak: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True)
    pdf.cell(0, 6, 'Metode: SNI 6989.71:2009', ln=True)
    pdf.line(10, 40, 200, 40)
    pdf.ln(10)
    
    # 1. Kalibrasi
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 8, '1. Kurva Kalibrasi', ln=True)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 6, f'Persamaan Garis: y = {slope:.4f}x + {intercept:.4f}', ln=True)
    pdf.cell(0, 6, f'Korelasi (r): {r_val:.5f}', ln=True)
    pdf.cell(0, 6, f'Koef. Determinasi (R2): {r2_val:.5f}', ln=True)
    clean_kal_status = str(kal_status).replace('≤', '<=').replace('≥', '>=').replace('—', '-')
    pdf.cell(0, 6, f'Status: {clean_kal_status}', ln=True)
    pdf.ln(5)
    
    # Plotly Chart export
    if fig is not None:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                fig.write_image(tmp.name, format="png", width=800, height=400, engine="kaleido")
                pdf.image(tmp.name, x=10, w=150)
                pdf.ln(5)
                os.unlink(tmp.name)
        except Exception as e:
            pdf.set_text_color(200, 0, 0)
            pdf.cell(0, 6, f'(Grafik tidak dapat dimuat dalam PDF)', ln=True)
            pdf.set_text_color(0, 0, 0)
            
    # 2. Presisi
    pdf.set_font('helvetica', 'B', 12)
    if tipe_presisi == "Duplo":
        pdf.cell(0, 8, '2. Uji Presisi (Duplo)', ln=True)
        pdf.set_font('helvetica', '', 10)
        pdf.cell(0, 6, f'Metode: Duplo (n = 2)', ln=True)
        pdf.cell(0, 6, f'Absorbansi 1: {abs1:.4f} | Absorbansi 2: {abs2:.4f}', ln=True)
        if rerata_sampel > 0:
            pdf.cell(0, 6, f'Rerata Kadar Sampel: {rerata_sampel:.2f} mg/kg', ln=True)
        if rpd is not None and rpd > 0:
            pdf.cell(0, 6, f'Relative Percent Difference (%RPD): {rpd:.2f} %', ln=True)
        if rsd > 0:
            pdf.cell(0, 6, f'Relative Standard Deviation (%RSD): {rsd:.2f} %', ln=True)
    else:
        pdf.cell(0, 8, f'2. Uji Presisi (Replikasi, n = {n_replikasi})', ln=True)
        pdf.set_font('helvetica', '', 10)
        pdf.cell(0, 6, f'Metode: Replikasi Keterulangan (n = {n_replikasi})', ln=True)
        if rerata_sampel > 0:
            pdf.cell(0, 6, f'Rerata Kadar Sampel: {rerata_sampel:.2f} mg/kg', ln=True)
        if sd > 0:
            pdf.cell(0, 6, f'Standar Deviasi Sampel (s): {sd:.4f} mg/kg', ln=True)
        if rsd > 0:
            pdf.cell(0, 6, f'Relative Standard Deviation (%RSD): {rsd:.2f} %', ln=True)
    
    clean_presisi_status = str(presisi_status).replace('≤', '<=').replace('≥', '>=').replace('—', '-')
    pdf.cell(0, 6, f'Status: {clean_presisi_status}', ln=True)
    pdf.ln(5)
    
    # 3. Akurasi
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 8, '3. Uji Akurasi (Spike / Recovery)', ln=True)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 6, f'Persentase Recovery: {recov:.2f} %', ln=True)
    clean_akurasi_status = str(akurasi_status).replace('≤', '<=').replace('≥', '>=').replace('—', '-')
    pdf.cell(0, 6, f'Status: {clean_akurasi_status}', ln=True)
    pdf.ln(15)
    
    # Tanda tangan
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    pdf.cell(90, 6, 'Dianalisis oleh,', align='C')
    pdf.cell(90, 6, 'Diperiksa oleh,', align='C', ln=True)
    pdf.ln(20)
    pdf.cell(90, 6, '(______________________)', align='C')
    pdf.cell(90, 6, '(______________________)', align='C', ln=True)
    
    return pdf.output()

# SIDEBAR: Informasi & Panduan
with st.sidebar:
    st.markdown("### Panduan Penggunaan")
    st.markdown("""
    1. **Kurva Kalibrasi:** Masukkan nilai konsentrasi dan absorbansi deret standar. Pastikan kurva memiliki korelasi linear (r >= 0.995).
    2. **Uji Presisi:** Pilih metode presisi: **Uji Duplo** (%RPD & %RSD) atau **Uji Replikasi** (%RSD / %KV). Nilai presisi dan status otomatis dihitung beserta rumusnya.
    3. **Uji Akurasi:** Masukkan data absorbansi sampel yang telah ditambahkan larutan standar (spike) untuk mendapatkan persentase Recovery.
    4. **Cetak Laporan PDF:** Buka tab laporan untuk mengunduh laporan utuh pengujian resmi Anda.
    """)
    st.divider()

    st.markdown("### Tentang Aplikasi")
    st.markdown("Aplikasi ini dirancang untuk mengotomatisasi perhitungan evaluasi laboratorium untuk parameter Kromium Heksavalen (Cr(VI)).")
    
    st.markdown("### Standar Metode")
    st.markdown("- **SNI 6989.71:2009** (Air dan Air Limbah - Bagian 71: Cara uji krom heksavalen)")
    
    st.markdown("### Kriteria Penerimaan")
    st.markdown("""
    - **Linearitas:** r &ge; 0.995
    - **Presisi (%RPD):** &le; 10% (Uji Duplo)
    - **Presisi (%RSD):** &le; 5% s/d 10% (Uji Replikasi / HorRat &le; 2.0)
    - **Akurasi (% Rec):** 85% - 115%
    """)
    st.divider()
    
    st.caption("Kelompok 2 Praktikum Spektrofotometri")

# HEADER UTAMA
st.markdown('<p class="main-title">Smart Cr(VI) Parameter Analyzer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Automasi Perhitungan Kalibrasi, Presisi, dan Akurasi</p>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Kurva Kalibrasi", "Uji Presisi", "Uji Akurasi", "Cetak Laporan PDF", "3D Spektrofotometer UV-Vis"])

# Session State Init
if 'slope' not in st.session_state: st.session_state.slope = 0.0
if 'intercept' not in st.session_state: st.session_state.intercept = 0.0
if 'r_value' not in st.session_state: st.session_state.r_value = 0.0
if 'r_squared' not in st.session_state: st.session_state.r_squared = 0.0
if 'rerata_sampel' not in st.session_state: st.session_state.rerata_sampel = 0.0
if 'kal_status' not in st.session_state: st.session_state.kal_status = "Belum diuji"
if 'abs_1' not in st.session_state: st.session_state.abs_1 = 0.100
if 'abs_2' not in st.session_state: st.session_state.abs_2 = 0.105
if 'bobot_kg' not in st.session_state: st.session_state.bobot_kg = 0.000400
if 'vol_L' not in st.session_state: st.session_state.vol_L = 0.250
if 'tipe_presisi' not in st.session_state: st.session_state.tipe_presisi = "Duplo"
if 'rpd' not in st.session_state: st.session_state.rpd = 0.0
if 'rsd' not in st.session_state: st.session_state.rsd = 0.0
if 'sd_presisi' not in st.session_state: st.session_state.sd_presisi = 0.0
if 'n_replikasi' not in st.session_state: st.session_state.n_replikasi = 2
if 'presisi_status' not in st.session_state: st.session_state.presisi_status = "Belum diuji"
if 'df_replikasi' not in st.session_state:
    st.session_state.df_replikasi = pd.DataFrame({
        "Replikasi": [f"Ulangan {i+1}" for i in range(6)],
        "Absorbansi": [0.1000, 0.1025, 0.1012, 0.1038, 0.0995, 0.1020]
    })
if 'recovery' not in st.session_state: st.session_state.recovery = 0.0
if 'akurasi_status' not in st.session_state: st.session_state.akurasi_status = "Belum diuji"
if 'kal_fig' not in st.session_state: st.session_state.kal_fig = None
if 'data_kalibrasi_ok' not in st.session_state: st.session_state.data_kalibrasi_ok = False

# TAB 1: KALIBRASI
with tab1:
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("Data Deret Standar")
            default_data = pd.DataFrame({"Konsentrasi (mg/L)": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5], "Absorbansi": [0.0, 0.080, 0.155, 0.234, 0.312, 0.380]})
            edited_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True)
            with st.expander("Rumus"): st.latex(r"y = bx + a")
    
    with col2:
        with st.container(border=True):
            st.subheader("Grafik Kurva Kalibrasi")
            x = edited_df["Konsentrasi (mg/L)"].values
            y = edited_df["Absorbansi"].values
            if len(x) > 1 and len(y) > 1:
                slope, intercept, r_value, p_value, std_err = linregress(x, y)
                r_squared = r_value ** 2
                
                st.session_state.slope, st.session_state.intercept = slope, intercept
                st.session_state.r_value, st.session_state.r_squared = r_value, r_squared
                
                fig = go.Figure()
                line_x = np.linspace(min(x), max(x), 100)
                line_y = slope * line_x + intercept
                fig.add_trace(go.Scatter(x=line_x, y=line_y, mode='lines', name='Tren', line=dict(color='rgba(52, 152, 219, 0.8)', width=3), fill='tozeroy', fillcolor='rgba(52, 152, 219, 0.1)'))
                fig.add_trace(go.Scatter(x=x, y=y, mode='markers', name='Data', marker=dict(color='#e74c3c', size=12)))
                fig.update_layout(title="Kurva Kalibrasi", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)
                st.session_state.kal_fig = fig
                
                st.markdown(f'<div class="status-box-info"><b>Persamaan Regresi:</b> y = {slope:.4f}x + {intercept:.4f}</div>', unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                c1.metric("Korelasi (r)", f"{r_value:.5f}")
                c2.metric("R-Squared (R²)", f"{r_squared:.5f}")
                
                if r_value >= 0.995:
                    st.session_state.kal_status = "LULUS (r >= 0.995)"
                    st.markdown('<div class="status-box-success">Status: Memenuhi Syarat (r &ge; 0.995)</div>', unsafe_allow_html=True)
                    if not st.session_state.data_kalibrasi_ok:
                        st.toast('Kurva kalibrasi ideal!')
                        st.session_state.data_kalibrasi_ok = True
                else:
                    st.session_state.kal_status = "GAGAL (r < 0.995)"
                    st.markdown('<div class="status-box-error">Peringatan: Tidak Linier (r &lt; 0.995)</div>', unsafe_allow_html=True)
                    st.session_state.data_kalibrasi_ok = False

# TAB 2: PRESISI
with tab2:
    st.markdown("### 🧪 Uji Presisi (Keterulangan Hasil Analisis)")
    # Radio Pilihan Metode
    mode_presisi = st.radio(
        "Pilih Metode Evaluasi Presisi:",
        [
            "Uji Duplo (n = 2) — Evaluasi %RPD & %RSD",
            "Uji Replikasi (n ≥ 3) — Evaluasi %RSD / %KV"
        ],
        horizontal=True
    )
    
    col1, col2 = st.columns(2, gap="large")
    
    if "Duplo" in mode_presisi:
        st.session_state.tipe_presisi = "Duplo"
        st.session_state.n_replikasi = 2
        
        with col1:
            with st.container(border=True):
                st.subheader("Input Data Sampel Duplo")
                abs_1 = st.number_input("Absorbansi Sampel 1", value=float(st.session_state.abs_1) if st.session_state.abs_1 != 0 else 0.100, format="%.4f", step=0.001)
                abs_2 = st.number_input("Absorbansi Duplo (Sampel 2)", value=float(st.session_state.abs_2) if st.session_state.abs_2 != 0 else 0.105, format="%.4f", step=0.001)
                bobot_kg = st.number_input("Bobot Sampel (kg)", value=float(st.session_state.bobot_kg), format="%.6f", step=0.0001)
                vol_L = st.number_input("Volume Labu Takar (L)", value=float(st.session_state.vol_L), format="%.3f", step=0.05)
                
                st.session_state.abs_1 = abs_1
                st.session_state.abs_2 = abs_2
                st.session_state.bobot_kg = bobot_kg
                st.session_state.vol_L = vol_L
                
                st.markdown("##### Parameter Evaluasi Keberterimaan")
                kriteria_duplo = st.radio(
                    "Acuan Evaluasi Utama:",
                    ["%RPD (Batas ≤ 10.0%)", "%RSD (Batas ≤ 5.0%)", "Kustom"],
                    horizontal=True
                )
                if kriteria_duplo == "Kustom":
                    c_param, c_val = st.columns(2)
                    eval_param = c_param.selectbox("Parameter Acuan:", ["%RPD", "%RSD"])
                    batas_kustom = c_val.number_input("Batas Maksimal (%):", min_value=0.1, max_value=100.0, value=10.0 if eval_param == "%RPD" else 5.0, step=0.5)
                elif "%RPD" in kriteria_duplo:
                    eval_param = "%RPD"
                    batas_kustom = 10.0
                else:
                    eval_param = "%RSD"
                    batas_kustom = 5.0

        with col2:
            with st.container(border=True):
                st.subheader("Hasil Evaluasi Presisi Duplo")
                if st.session_state.slope != 0:
                    def hitung_kadar(a):
                        return ((a - st.session_state.intercept) / st.session_state.slope * vol_L) / bobot_kg
                    
                    k1 = hitung_kadar(abs_1)
                    k2 = hitung_kadar(abs_2)
                    rerata = (k1 + k2) / 2.0
                    st.session_state.rerata_sampel = rerata
                    
                    # Standar deviasi sampel n = 2: s = |k1 - k2| / sqrt(2)
                    sd = abs(k1 - k2) / np.sqrt(2)
                    st.session_state.sd_presisi = sd
                    
                    # Perhitungan %RPD dan %RSD
                    rpd = (abs(k1 - k2) / rerata * 100.0) if rerata != 0 else 0.0
                    rsd = (sd / rerata * 100.0) if rerata != 0 else 0.0
                    st.session_state.rpd = rpd
                    st.session_state.rsd = rsd
                    
                    c_k1, c_k2 = st.columns(2)
                    c_k1.write(f"Kadar Sampel 1: **{k1:,.2f} mg/kg**")
                    c_k2.write(f"Kadar Duplo 2: **{k2:,.2f} mg/kg**")
                    
                    c_r, c_sd = st.columns(2)
                    c_r.write(f"Rerata Kadar (C1): **{rerata:,.2f} mg/kg**")
                    c_sd.write(f"Standar Deviasi (s): **{sd:,.4f} mg/kg**")
                    
                    st.divider()
                    
                    m1, m2 = st.columns(2)
                    m1.metric("Nilai %RPD", f"{rpd:.2f} %", help="Relative Percent Difference (|X1 - X2| / Mean * 100%)")
                    m2.metric("Nilai %RSD", f"{rsd:.2f} %", help="Relative Standard Deviation (s / Mean * 100%)")
                    
                    # Evaluasi kelulusan
                    if eval_param == "%RPD":
                        lulus = (rpd <= batas_kustom)
                        status_label = f"%RPD {rpd:.2f}% (Batas <= {batas_kustom}%)"
                    else:
                        lulus = (rsd <= batas_kustom)
                        status_label = f"%RSD {rsd:.2f}% (Batas <= {batas_kustom}%)"
                    
                    if lulus:
                        st.session_state.presisi_status = f"LULUS ({status_label})"
                        st.markdown(f'<div class="status-box-success">Presisi DITERIMA &mdash; {status_label}</div>', unsafe_allow_html=True)
                    else:
                        st.session_state.presisi_status = f"GAGAL ({status_label})"
                        st.markdown(f'<div class="status-box-error">Presisi DITOLAK &mdash; {status_label}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-box-info">⚠️ Buat kurva kalibrasi pada Tab 1 terlebih dahulu untuk menghitung kadar dan presisi.</div>', unsafe_allow_html=True)

    else:
        # Mode Replikasi (n >= 3)
        st.session_state.tipe_presisi = "Replikasi"
        with col1:
            with st.container(border=True):
                st.subheader("Input Data Deret Replikasi")
                st.caption("Masukkan hasil absorbansi dari pengukuran berulang (umumnya 6-7 replikasi untuk keterulangan metode).")
                
                edited_rep_df = st.data_editor(
                    st.session_state.df_replikasi,
                    num_rows="dynamic",
                    use_container_width=True,
                    key="replikasi_editor"
                )
                st.session_state.df_replikasi = edited_rep_df
                
                bobot_kg = st.number_input("Bobot Sampel (kg)", value=float(st.session_state.bobot_kg), format="%.6f", step=0.0001, key="bobot_rep")
                vol_L = st.number_input("Volume Labu Takar (L)", value=float(st.session_state.vol_L), format="%.3f", step=0.05, key="vol_rep")
                st.session_state.bobot_kg = bobot_kg
                st.session_state.vol_L = vol_L
                
                st.markdown("##### Parameter Evaluasi Keberterimaan")
                col_b1, col_b2 = st.columns(2)
                batas_rsd = col_b1.number_input("Batas Maksimal %RSD (%):", min_value=0.1, max_value=100.0, value=5.0, step=0.5)
                eval_horwitz = col_b2.checkbox("Evaluasi Kriteria Horwitz (HorRat)", value=True, help="Menghitung HorRat (RSD / CV Horwitz <= 2.0)")

        with col2:
            with st.container(border=True):
                st.subheader("Hasil Evaluasi Presisi Replikasi")
                if st.session_state.slope != 0:
                    abs_vals = pd.to_numeric(edited_rep_df["Absorbansi"], errors="coerce").dropna().values
                    n_vals = len(abs_vals)
                    st.session_state.n_replikasi = n_vals
                    
                    if n_vals < 2:
                        st.markdown('<div class="status-box-error">⚠️ Masukkan minimal 2 data ulangan untuk menghitung presisi.</div>', unsafe_allow_html=True)
                    else:
                        def hitung_kadar(a):
                            return ((a - st.session_state.intercept) / st.session_state.slope * vol_L) / bobot_kg
                        
                        kadar_arr = np.array([hitung_kadar(a) for a in abs_vals])
                        rerata = float(np.mean(kadar_arr))
                        sd = float(np.std(kadar_arr, ddof=1))
                        rsd = float((sd / rerata * 100.0) if rerata != 0 else 0.0)
                        
                        st.session_state.rerata_sampel = rerata
                        st.session_state.sd_presisi = sd
                        st.session_state.rsd = rsd
                        
                        # Hitung %RPD jika n == 2
                        if n_vals == 2:
                            rpd = float((abs(kadar_arr[0] - kadar_arr[1]) / rerata * 100.0) if rerata != 0 else 0.0)
                            st.session_state.rpd = rpd
                        else:
                            st.session_state.rpd = 0.0
                        
                        c_r, c_sd = st.columns(2)
                        c_r.write(f"Rerata Kadar (C1): **{rerata:,.2f} mg/kg**")
                        c_sd.write(f"Standar Deviasi (s): **{sd:,.4f} mg/kg**")
                        st.caption(f"Jumlah Replikasi (n): **{n_vals} ulangan**")
                        
                        st.divider()
                        
                        horrat = None
                        if n_vals == 2:
                            m1, m2 = st.columns(2)
                            m1.metric("Nilai %RSD", f"{rsd:.2f} %")
                            m2.metric("Nilai %RPD", f"{rpd:.2f} %")
                        else:
                            m1, m2 = st.columns(2)
                            m1.metric("Nilai %RSD (%KV)", f"{rsd:.2f} %")
                            if eval_horwitz and rerata > 0:
                                c_fraction = rerata * 1e-6
                                if c_fraction > 0:
                                    cv_horwitz = 2.0 ** (1.0 - 0.5 * np.log10(c_fraction))
                                    horrat = rsd / cv_horwitz
                                    m2.metric("HorRat Value", f"{horrat:.2f}", help=f"CV Horwitz: {cv_horwitz:.2f}%, Kriteria HorRat <= 2.0")
                                else:
                                    m2.metric("Standar Deviasi (s)", f"{sd:.4f}")
                            else:
                                m2.metric("Standar Deviasi (s)", f"{sd:.4f}")
                        
                        # Evaluasi Status
                        lulus_rsd = (rsd <= batas_rsd)
                        if horrat is not None and n_vals > 2:
                            lulus_horrat = (horrat <= 2.0)
                            if lulus_rsd and lulus_horrat:
                                st.session_state.presisi_status = f"LULUS (%RSD {rsd:.2f}% <= {batas_rsd}%, HorRat {horrat:.2f} <= 2.0)"
                                st.markdown(f'<div class="status-box-success">Presisi DITERIMA &mdash; %RSD {rsd:.2f}% &le; {batas_rsd}%, HorRat {horrat:.2f} &le; 2.0</div>', unsafe_allow_html=True)
                            elif lulus_rsd:
                                st.session_state.presisi_status = f"LULUS (%RSD {rsd:.2f}% <= {batas_rsd}%)"
                                st.markdown(f'<div class="status-box-success">Presisi DITERIMA &mdash; %RSD {rsd:.2f}% &le; {batas_rsd}% (HorRat {horrat:.2f} > 2.0)</div>', unsafe_allow_html=True)
                            else:
                                st.session_state.presisi_status = f"GAGAL (%RSD {rsd:.2f}% > {batas_rsd}%)"
                                st.markdown(f'<div class="status-box-error">Presisi DITOLAK &mdash; %RSD {rsd:.2f}% &gt; {batas_rsd}%</div>', unsafe_allow_html=True)
                        else:
                            if lulus_rsd:
                                st.session_state.presisi_status = f"LULUS (%RSD {rsd:.2f}% <= {batas_rsd}%)"
                                st.markdown(f'<div class="status-box-success">Presisi DITERIMA &mdash; %RSD {rsd:.2f}% &le; {batas_rsd}%</div>', unsafe_allow_html=True)
                            else:
                                st.session_state.presisi_status = f"GAGAL (%RSD {rsd:.2f}% > {batas_rsd}%)"
                                st.markdown(f'<div class="status-box-error">Presisi DITOLAK &mdash; %RSD {rsd:.2f}% &gt; {batas_rsd}%</div>', unsafe_allow_html=True)
                        
                        with st.expander("🔍 Lihat Detail Data dan Kadar Tiap Replikasi"):
                            detail_df = pd.DataFrame({
                                "Replikasi": [f"Ulangan {i+1}" for i in range(n_vals)],
                                "Absorbansi": abs_vals,
                                "Kadar (mg/kg)": [round(float(k), 4) for k in kadar_arr],
                                "Selisih dari Rerata (|Xi - Mean|)": [round(float(abs(k - rerata)), 4) for k in kadar_arr]
                            })
                            st.dataframe(detail_df, use_container_width=True)
                else:
                    st.markdown('<div class="status-box-info">⚠️ Buat kurva kalibrasi pada Tab 1 terlebih dahulu untuk menghitung kadar dan presisi.</div>', unsafe_allow_html=True)

    # BAGIAN RUMUS LENGKAP & LANDASAN TEORI
    st.divider()
    with st.expander("Rumus Lengkap & Prinsip Perhitungan Presisi (%RPD dan %RSD)", expanded=True):
        col_r1, col_r2 = st.columns(2, gap="medium")
        
        with col_r1:
            st.markdown("#### 1. Rumus %RPD (Relative Percent Difference)")
            st.markdown(r"Digunakan khusus untuk pengujian berpasangan / duplo ($n = 2$).")
            st.latex(r"\%RPD = \frac{|X_1 - X_2|}{\frac{X_1 + X_2}{2}} \times 100\% = \frac{|X_1 - X_2|}{\bar{X}} \times 100\%")
            st.markdown(r"""
            **Keterangan Simbol:**
            - $X_1$ = Kadar analit pada pengukuran pertama (mg/kg atau mg/L)
            - $X_2$ = Kadar analit pada pengukuran kedua / duplo (mg/kg atau mg/L)
            - $\bar{X} = \frac{X_1 + X_2}{2}$ = Nilai rata-rata dari kedua hasil pengukuran
            - $|X_1 - X_2|$ = Selisih mutlak antara kedua hasil pengujian
            
            **Kriteria Keberterimaan SNI / US-EPA:**
            - Presisi duplo diterima jika $\%RPD \le 10.0\%$ (atau $\le 5.0\%$ tergantung matriks sampel dan regulasi laboratorium).
            """)
            
            st.markdown("#### 3. Hubungan Matematis %RPD dan %RSD pada Uji Duplo ($n = 2$)")
            st.markdown(r"""
            Pada uji duplo ($n = 2$), standar deviasi sampel ($s$) dihitung sebagai:
            """)
            st.latex(r"s = \sqrt{\frac{(X_1 - \bar{X})^2 + (X_2 - \bar{X})^2}{2 - 1}} = \frac{|X_1 - X_2|}{\sqrt{2}}")
            st.markdown(r"""
            Sehingga substitusi ke dalam rumus $\%RSD$ menghasilkan hubungan langsung:
            """)
            st.latex(r"\%RSD = \frac{\frac{|X_1 - X_2|}{\sqrt{2}}}{\bar{X}} \times 100\% = \frac{\%RPD}{\sqrt{2}} \approx 0.7071 \times \%RPD")
            st.caption("Artinya, untuk 2 pengulangan data, nilai %RSD bernilai sekitar 70.71% dari nilai %RPD.")

        with col_r2:
            st.markdown("#### 2. Rumus %RSD (Relative Standard Deviation) / %KV")
            st.markdown(r"Digunakan untuk pengujian replikasi / keterulangan ($n \ge 2$, umumnya $n \ge 3$, misal 6 atau 7 ulangan).")
            st.latex(r"\%RSD = \frac{s}{\bar{X}} \times 100\%")
            st.markdown("di mana komponen penyusunnya dihitung dengan rumus:")
            st.latex(r"\bar{X} = \frac{1}{n} \sum_{i=1}^{n} X_i")
            st.latex(r"s = \sqrt{\frac{\sum_{i=1}^{n} (X_i - \bar{X})^2}{n - 1}}")
            st.markdown(r"""
            **Keterangan Simbol:**
            - $X_i$ = Kadar analit pada ulangan ke-$i$
            - $\bar{X}$ = Nilai rata-rata aritmatika dari seluruh replikasi
            - $s$ = Standar deviasi sampel (*sample standard deviation*, derajat bebas $n-1$)
            - $n$ = Jumlah pengulangan (replikasi pengujian)
            - $\%RSD$ = *Relative Standard Deviation* (atau Koefisien Variasi / %KV)
            
            **Kriteria Keberterimaan:**
            - Keterulangan metode: $\%RSD \le 5.0\%$ s/d $10.0\%$
            - Kriteria Horwitz: $HorRat = \frac{\%RSD}{CV_{Horwitz}} \le 2.0$, di mana $CV_{Horwitz} = 2^{(1 - 0.5 \log_{10} C)}$.
            """)
            
            st.markdown("#### 4. Rumus Perhitungan Kadar dari Absorbansi (SNI 6989.71:2009)")
            st.latex(r"Kadar\ (mg/kg) = \frac{\left(\frac{A - a}{b}\right) \times V}{W}")
            st.markdown(r"""
            - $A$ = Nilai absorbansi terukur pada spektrofotometer UV-Vis ($\lambda = 540\text{ nm}$)
            - $a$ = Nilai intersep garis regresi kurva kalibrasi ($y = bx + a$)
            - $b$ = Nilai kemiringan (*slope*) garis kurva kalibrasi
            - $V$ = Volume labu takar / pengenceran akhir (L)
            - $W$ = Bobot sampel awal yang ditimbang (kg)
            """)

# TAB 3: AKURASI
with tab3:
    col1, col2 = st.columns(2, gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("Input Spike")
            if st.session_state.rerata_sampel > 0:
                st.info(f"Kadar Sampel Dasar (C1): **{st.session_state.rerata_sampel:,.2f} mg/kg** (diperoleh dari Uji Presisi)")
            else:
                st.warning("⚠️ Rerata kadar sampel (C1) belum tersedia. Lakukan Uji Presisi pada Tab 2 terlebih dahulu.")
                
            abs_spike = st.number_input("Absorbansi Spike", value=0.150, format="%.4f")
            bobot_spike = st.number_input("Bobot Spike (kg)", value=float(st.session_state.bobot_kg), format="%.6f")
            cons_std = st.number_input("Konsentrasi Standar (mg/L)", value=1000.0)
            vol_std = st.number_input("Volume Spike (L)", value=0.001, format="%.4f")
            with st.expander("Rumus Perhitungan Recovery"): st.latex(r"\% Recovery = \frac{C_3 - C_1}{C_2} \times 100\%")
    
    with col2:
        with st.container(border=True):
            st.subheader("Hasil Recovery")
            if st.session_state.slope != 0 and st.session_state.rerata_sampel != 0:
                vol_L = float(st.session_state.vol_L) if 'vol_L' in st.session_state else 0.250
                c3_mg_kg = (((abs_spike - st.session_state.intercept) / st.session_state.slope) * vol_L) / bobot_spike
                c2_mg_kg = (cons_std * vol_std) / bobot_spike
                recovery = ((c3_mg_kg - st.session_state.rerata_sampel) / c2_mg_kg) * 100
                st.session_state.recovery = recovery
                
                st.metric("Recovery (%)", f"{recovery:.2f} %")
                if 85.0 <= recovery <= 115.0:
                    st.session_state.akurasi_status = "LULUS (85% - 115%)"
                    st.markdown('<div class="status-box-success">Akurasi DITERIMA (85% - 115%)</div>', unsafe_allow_html=True)
                else:
                    st.session_state.akurasi_status = "GAGAL"
                    st.markdown('<div class="status-box-error">Akurasi DITOLAK (< 85% atau > 115%)</div>', unsafe_allow_html=True)
            else: 
                st.markdown('<div class="status-box-info">Selesaikan Kurva Kalibrasi dan Uji Presisi terlebih dahulu.</div>', unsafe_allow_html=True)

# TAB 4: PDF REPORT
with tab4:
    with st.container(border=True):
        st.header("Export Laporan PDF (ISO 17025 Ready)")
        st.markdown("Cetak rangkuman hasil kalibrasi, presisi (%RPD / %RSD), dan akurasi langsung ke dalam format PDF yang rapi dengan kolom tanda tangan resmi untuk dilampirkan sebagai Raw Data laboratorium.")
        
        if st.button("Generate Laporan PDF", type="primary"):
            with st.spinner("Membuat dokumen PDF, harap tunggu..."):
                try:
                    pdf_bytes = create_pdf(
                        st.session_state.slope, st.session_state.intercept, st.session_state.r_value, st.session_state.r_squared, st.session_state.kal_status,
                        st.session_state.abs_1, st.session_state.abs_2, st.session_state.rpd, st.session_state.presisi_status,
                        st.session_state.recovery, st.session_state.akurasi_status, st.session_state.kal_fig,
                        tipe_presisi=st.session_state.tipe_presisi,
                        rsd=st.session_state.rsd,
                        sd=st.session_state.sd_presisi,
                        n_replikasi=st.session_state.n_replikasi,
                        rerata_sampel=st.session_state.rerata_sampel
                    )
                    st.markdown('<div class="status-box-success">Laporan berhasil dibuat!</div>', unsafe_allow_html=True)
                    st.download_button(
                        label="Unduh PDF Laporan",
                        data=bytes(pdf_bytes),
                        file_name=f"Laporan_Pengujian_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.markdown(f'<div class="status-box-error">Gagal membuat PDF: {e}</div>', unsafe_allow_html=True)

# TAB 5: SIMULATOR 3D UV-VIS
with tab5:
    st.markdown("###3D Spektrofotometer UV-Vis (Shimadzu UV-1700)")
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html_code = f.read()
        components.html(html_code, height=780, scrolling=True)
    else:
        st.error("File index.html simulator 3D tidak ditemukan di direktori proyek.")
