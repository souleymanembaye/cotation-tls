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
        ("Surcharge Carburant (BAF)", "-", f"{data['baf']:,.0f}"),
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

# --- INTERFACE STREAMLIT ---
st.title("📋 GLOBAL TLS - Calculateur de Devis")

with st.sidebar:
    st.header("⚙️ Paramètres du Document")
    ref_devis = st.text_input("Numéro de l'offre", value="GTLS-COT-001")
    devise = st.selectbox("Devise de facturation", ["FCFA", "EUR", "USD"])

col_exp, col_prix = st.columns(2)

with col_exp:
    st.subheader("📦 Informations Expédition")
    client = st.text_input("Nom du Client / Entreprise")
    mode = st.selectbox("Mode de transport (Règle UP)", ["Maritime (1t=1m3)", "Aérien (1t=6m3)", "Routier (1t=3m3)"])
    
    c_poids, c_colis = st.columns(2)
    poids_brut = c_poids.number_input("Poids Brut Total (kg)", min_value=0.0)
    nb_colis = c_colis.number_input("Nombre de colis", min_value=1, value=1)
    
    st.write("**Dimensions par colis (m)**")
    lx, ly, lz = st.columns(3)
    L = lx.number_input("Longueur", value=1.0)
    W = ly.number_input("Largeur", value=1.0)
    H = lz.number_input("Hauteur", value=1.0)

# Calcul du Poids Taxable (UP)
vol_t = nb_colis * (L * W * H)
if "Maritime" in mode: p_tax = max(poids_brut/1000, vol_t)
elif "Aérien" in mode: p_tax = max(poids_brut, vol_t * 166.67)
else: p_tax = max(poids_brut/1000, vol_t/3)

with col_prix:
    st.subheader("💰 Détails des Coûts HT")
    fret_unit = st.number_input("Prix unitaire du Fret (par UP)", value=0.0)
    baf = st.number_input("Surcharge Carburant (BAF total)", value=0.0)
    port = st.number_input("Passage Portuaire / Douane / Manutention", value=0.0)
    livraison = st.number_input("Livraison & Transport Terrestre", value=0.0)

# Calcul total
total_fret = p_tax * fret_unit
total_general = total_fret + baf + port + livraison

st.divider()
st.info(f"💡 **Analyse Logistique :** Volume Total = {vol_t:.2f} m³ | Unité Payante retenue = **{p_tax:.2f}**")
st.success(f"### MONTANT TOTAL DU DEVIS : {total_general:,.2f} {devise}")

if st.button("📄 GÉNÉRER LE DEVIS PROFESSIONNEL"):
    if client:
        donnees = {
            "client": client, "ref": ref_devis, "ptax": p_tax, "mode": mode,
            "fret_total": total_fret, "baf": baf, "port": port,
            "livraison": livraison, "total": total_general, "devise": devise
        }
        pdf_file = generate_pdf(donnees)
        st.download_button("⬇️ Télécharger le Devis (PDF)", data=pdf_file, file_name=f"Devis_GTLS_{client}.pdf")
    else:
        st.error("⚠️ Erreur : Veuillez saisir le nom du client avant de générer le PDF.")
