import streamlit as st
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
st.set_page_config(page_title="Cr(VI)", layout="wide")

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
def create_pdf(slope, intercept, r_val, r2_val, kal_status, abs1, abs2, rpd, presisi_status, recov, akurasi_status, fig):
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
    pdf.cell(0, 6, f'Status: {kal_status}', ln=True)
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
    pdf.cell(0, 8, '2. Uji Presisi (Duplo)', ln=True)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 6, f'Absorbansi 1: {abs1:.4f}', ln=True)
    pdf.cell(0, 6, f'Absorbansi 2: {abs2:.4f}', ln=True)
    pdf.cell(0, 6, f'Relative Percent Difference (RPD): {rpd:.2f} %', ln=True)
    pdf.cell(0, 6, f'Status: {presisi_status}', ln=True)
    pdf.ln(5)
    
    # 3. Akurasi
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 8, '3. Uji Akurasi (Spike / Recovery)', ln=True)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 6, f'Persentase Recovery: {recov:.2f} %', ln=True)
    pdf.cell(0, 6, f'Status: {akurasi_status}', ln=True)
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
    2. **Uji Presisi:** Masukkan absorbansi dari pengujian sampel dan duplikasinya (duplo). RPD akan otomatis dihitung.
    3. **Uji Akurasi:** Masukkan data absorbansi sampel yang telah ditambahkan larutan standar (spike) untuk mendapatkan persentase Recovery.
    4. **Cetak Laporan PDF:** Buka tab terakhir dan klik tombol generate untuk mengunduh laporan utuh pengujian Anda.
    """)
    st.divider()

    st.markdown("### Tentang Aplikasi")
    st.markdown("Aplikasi ini dirancang untuk mengotomatisasi perhitungan evaluasi laboratorium untuk parameter Kromium Heksavalen (Cr(VI)).")
    
    st.markdown("### Standar Metode")
    st.markdown("- **SNI 6989.71:2009** (Air dan Air Limbah - Bagian 71: Cara uji krom heksavalen)")
    
    st.markdown("### Kriteria Penerimaan")
    st.markdown("- **Linearitas:** r &ge; 0.995\n- **Presisi (RPD):** &le; 10%\n- **Akurasi (% Rec):** 85% - 115%")
    st.divider()
    
    st.caption("Created by Kelompok 2")

# HEADER UTAMA
st.markdown('<p class="main-title">Otomasi Pengolahan Data Parameter Cr(VI)</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Automasi Perhitungan Kalibrasi, Presisi, dan Akurasi</p>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Kurva Kalibrasi", "Uji Presisi", "Uji Akurasi", "Cetak Laporan PDF"])

# Session State Init
if 'slope' not in st.session_state: st.session_state.slope = 0
if 'intercept' not in st.session_state: st.session_state.intercept = 0
if 'r_value' not in st.session_state: st.session_state.r_value = 0
if 'r_squared' not in st.session_state: st.session_state.r_squared = 0
if 'rerata_sampel' not in st.session_state: st.session_state.rerata_sampel = 0
if 'kal_status' not in st.session_state: st.session_state.kal_status = "Belum diuji"
if 'abs_1' not in st.session_state: st.session_state.abs_1 = 0
if 'abs_2' not in st.session_state: st.session_state.abs_2 = 0
if 'rpd' not in st.session_state: st.session_state.rpd = 0
if 'presisi_status' not in st.session_state: st.session_state.presisi_status = "Belum diuji"
if 'recovery' not in st.session_state: st.session_state.recovery = 0
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
    col1, col2 = st.columns(2, gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("Input Data Sampel")
            abs_1 = st.number_input("Absorbansi Sampel 1", value=0.100, format="%.4f")
            abs_2 = st.number_input("Absorbansi Duplo", value=0.105, format="%.4f")
            bobot_kg = st.number_input("Bobot Sampel (kg)", value=0.000400, format="%.6f")
            vol_L = st.number_input("Volume (L)", value=0.250, format="%.3f")
            st.session_state.abs_1, st.session_state.abs_2 = abs_1, abs_2
            with st.expander("Rumus Perhitungan RPD"): st.latex(r"RPD = \frac{|X_1 - X_2|}{\frac{(X_1 + X_2)}{2}} \times 100\%")
    
    with col2:
        with st.container(border=True):
            st.subheader("Hasil Presisi")
            if st.session_state.slope != 0:
                def hitung_kadar(a): return ((a - st.session_state.intercept) / st.session_state.slope * vol_L) / bobot_kg
                k1, k2 = hitung_kadar(abs_1), hitung_kadar(abs_2)
                rerata = (k1 + k2) / 2
                st.session_state.rerata_sampel = rerata
                rpd = (abs(k1 - k2) / rerata * 100) if rerata != 0 else 0
                st.session_state.rpd = rpd
                
                st.write(f"Rerata Kadar (C1): `{rerata:,.2f} mg/kg`")
                st.metric("Nilai RPD %", f"{rpd:.2f} %")
                
                if rpd <= 10.0:
                    st.session_state.presisi_status = "LULUS (RPD <= 10%)"
                    st.markdown('<div class="status-box-success">Presisi DITERIMA (RPD &le; 10%)</div>', unsafe_allow_html=True)
                else:
                    st.session_state.presisi_status = "GAGAL (RPD > 10%)"
                    st.markdown('<div class="status-box-error">Presisi DITOLAK (RPD &gt; 10%)</div>', unsafe_allow_html=True)
            else: 
                st.markdown('<div class="status-box-info">Buat kurva kalibrasi terlebih dahulu.</div>', unsafe_allow_html=True)

# TAB 3: AKURASI
with tab3:
    col1, col2 = st.columns(2, gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("Input Spike")
            abs_spike = st.number_input("Absorbansi Spike", value=0.150, format="%.4f")
            bobot_spike = st.number_input("Bobot Spike (kg)", value=0.000400, format="%.6f")
            cons_std = st.number_input("Konsentrasi Standar (mg/L)", value=1000.0)
            vol_std = st.number_input("Volume Spike (L)", value=0.001, format="%.4f")
            with st.expander("Rumus Perhitungan Recovery"): st.latex(r"\% Recovery = \frac{C_3 - C_1}{C_2} \times 100\%")
    
    with col2:
        with st.container(border=True):
            st.subheader("Hasil Recovery")
            if st.session_state.slope != 0 and st.session_state.rerata_sampel != 0:
                c3_mg_kg = (((abs_spike - st.session_state.intercept) / st.session_state.slope) * vol_L) / bobot_spike
                c2_mg_kg = (cons_std * vol_std) / bobot_spike
                recovery = ((c3_mg_kg - st.session_state.rerata_sampel) / c2_mg_kg) * 100
                st.session_state.recovery = recovery
                
                st.metric("Recovery (%)", f"{recovery:.2f} %")
                if 85.0 <= recovery <= 115.0:
                    st.session_state.akurasi_status = "LULUS (85% - 115%)"
                    st.markdown('<div class="status-box-success">Akurasi DITERIMA</div>', unsafe_allow_html=True)
                else:
                    st.session_state.akurasi_status = "GAGAL"
                    st.markdown('<div class="status-box-error">Akurasi DITOLAK</div>', unsafe_allow_html=True)
            else: 
                st.markdown('<div class="status-box-info">Selesaikan Uji Presisi terlebih dahulu.</div>', unsafe_allow_html=True)

# TAB 4: PDF REPORT
with tab4:
    with st.container(border=True):
        st.header("Export Laporan PDF (ISO 17025 Ready)")
        st.markdown("Cetak rangkuman hasil kalibrasi, presisi, dan akurasi langsung ke dalam format PDF yang rapi dengan kolom tanda tangan resmi untuk dilampirkan sebagai Raw Data laboratorium.")
        
        if st.button("Generate Laporan PDF", type="primary"):
            with st.spinner("Membuat dokumen PDF, harap tunggu..."):
                try:
                    pdf_bytes = create_pdf(
                        st.session_state.slope, st.session_state.intercept, st.session_state.r_value, st.session_state.r_squared, st.session_state.kal_status,
                        st.session_state.abs_1, st.session_state.abs_2, st.session_state.rpd, st.session_state.presisi_status,
                        st.session_state.recovery, st.session_state.akurasi_status, st.session_state.kal_fig
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
