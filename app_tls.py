import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="GLOBAL TLS - Devis Pro", layout="wide")

class PDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 33)
        self.set_font('Arial', 'B', 18)
        self.set_text_color(0, 74, 153)
        self.cell(0, 10, 'GLOBAL TLS SARL', 0, 1, 'R')
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, 'Transport International - Logistique - Transit', 0, 1, 'R')
        self.ln(20)
        self.set_font('Arial', 'B', 16)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 12, 'DEVIS COMMERCIAL / COTATION', 1, 1, 'C', fill=True)
        self.ln(10)

def generate_pdf(data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(100, 7, f"DESTINATAIRE : {data['client'].upper()}", 0, 0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 7, f"Date d'émission : {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')
    pdf.cell(0, 7, f"Offre N° : {data['ref']}", 0, 1, 'R')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.set_fill_color(0, 74, 153)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(110, 10, " DESCRIPTION DES PRESTATIONS", 1, 0, 'L', True)
    pdf.cell(35, 10, " UNITE / QTE", 1, 0, 'C', True)
    pdf.cell(45, 10, " TOTAL ", 1, 1, 'C', True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 11)
    
    lignes = [
        (f"Fret Principal ({data['mode']})", f"{data['ptax']:.2f} UP", f"{data['fret_total']:,.0f}"),
        (f"Surcharge Carburant (BAF {data['baf_pc']}%)", "-", f"{data['baf_val']:,.0f}"),
        ("Passage Portuaire & Formalités", "-", f"{data['port']:,.0f}"),
        ("Livraison & Transport Local", "-", f"{data['livraison']:,.0f}")
    ]
    
    for desc, qte, mnt in lignes:
        pdf.cell(110, 10, f" {desc}", 1)
        pdf.cell(35, 10, qte, 1, 0, 'C')
        pdf.cell(45, 10, f"{mnt} ", 1, 1, 'R')
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(145, 12, f" MONTANT TOTAL HT ({data['devise']}) ", 0, 0, 'R')
    pdf.cell(45, 12, f" {data['total']:,.0f} ", 1, 1, 'C')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, "Conditions de validité :", 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, "- Offre valable 15 jours sous réserve de place et de matériel.", 0, 1)
    pdf.cell(0, 5, "- Selon conditions générales de GLOBAL TLS SARL.", 0, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE ---
st.title("📋 GLOBAL TLS - Calculateur avec BAF %")

with st.sidebar:
    st.header("⚙️ Configuration")
    ref_devis = st.text_input("Numéro de l'offre", value="GTLS-COT-001")
    devise = st.selectbox("Devise", ["FCFA", "EUR", "USD"])
    change = st.number_input("Taux de change (si besoin)", value=1.0)

col_exp, col_prix = st.columns(2)

with col_exp:
    st.subheader("📦 Expédition")
    client = st.text_input("Nom du Client")
    mode = st.selectbox("Mode de transport", ["Maritime (1t=1m3)", "Aérien (1t=6m3)", "Routier (1t=3m3)"])
    poids_brut = st.number_input("Poids Total (kg)", value=0.0)
    nb_colis = st.number_input("Nombre de colis", min_value=1, value=1)
    
    st.write("Dimensions par colis (m)")
    lx, ly, lz = st.columns(3)
    L, W, H = lx.number_input("L", 1.0), ly.number_input("W", 1.0), lz.number_input("H", 1.0)

# Calcul UP
vol_t = nb_colis * (L * W * H)
if "Maritime" in mode: p_tax = max(poids_brut/1000, vol_t)
elif "Aérien" in mode: p_tax = max(poids_brut, vol_t * 166.67)
else: p_tax = max(poids_brut/1000, vol_t/3)

with col_prix:
    st.subheader("💰 Coûts HT")
    fret_u = st.number_input("Prix unitaire du Fret (par UP)", value=0.0)
    
    # CASE BAF EN POURCENTAGE
    baf_pourcent = st.number_input("Surcharge BAF (en % du Fret)", value=0.0, step=0.5)
    
    port = st.number_input("Passage Portuaire / Douane", value=0.0)
    livraison = st.number_input("Livraison finale", value=0.0)

# Calculs
fret_total_converti = (p_tax * fret_u) * change
baf_calculee = fret_total_converti * (baf_pourcent / 100)
port_converti = port * change
livraison_converti = livraison * change

total_global = fret_total_converti + baf_calculee + port_converti + livraison_converti

st.divider()
st.info(f"UP retenue : {p_tax:.2f} | BAF calculée : {baf_calculee:,.0f} {devise}")
st.success(f"### TOTAL DEVIS : {total_global:,.0f} {devise}")

if st.button("📄 GÉNÉRER LE DEVIS PDF"):
    if client:
        donnees = {
            "client": client, "ref": ref_devis, "ptax": p_tax, "mode": mode,
            "fret_total": fret_total_converti, 
            "baf_pc": baf_pourcent, "baf_val": baf_calculee,
            "port": port_converti, "livraison": livraison_converti, 
            "total": total_global, "devise": devise
        }
        pdf_file = generate_pdf(donnees)
        st.download_button("⬇️ Télécharger le Devis", data=pdf_file, file_name=f"Devis_{client}.pdf")
