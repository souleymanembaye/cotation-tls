import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="GLOBAL TLS - Expert Devis", layout="wide")

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
    pdf.cell(0, 5, f"- Taux de change appliqué : {data['change']}", 0, 1) if data['change'] != 1 else None
    pdf.cell(0, 5, "- Selon conditions générales de GLOBAL TLS SARL.", 0, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE ---
st.title("🌍 GLOBAL TLS : Devis Multi-Devises")

with st.sidebar:
    st.header("⚙️ Configuration")
    ref_devis = st.text_input("Numéro de l'offre", value="GTLS-COT-001")
    devise_client = st.selectbox("Devise de facturation (Cible)", ["FCFA", "EUR", "USD"])
    taux_change = st.number_input("Taux de conversion (ex: 1€ = 655.957)", value=655.957 if devise_client == "FCFA" else 1.0)
    st.caption("Si vous travaillez déjà dans la devise cible, laissez le taux à 1.0")

col_exp, col_prix = st.columns(2)

with col_exp:
    st.subheader("📦 Expédition")
    client = st.text_input("Client")
    mode = st.selectbox("Mode de transport", ["Maritime (1t=1m3)", "Aérien (1t=6m3)", "Routier (1t=3m3)"])
    poids_brut = st.number_input("Poids Total (kg)", value=0.0)
    nb_colis = st.number_input("Nb de colis", min_value=1, value=1)
    
    st.write("Dimensions moyennes (m)")
    lx, ly, lz = st.columns(3)
    L, W, H = lx.number_input("L"), ly.number_input("W"), lz.number_input("H")

# Calcul UP
vol_t = nb_colis * (L * W * H)
if "Maritime" in mode: p_tax = max(poids_brut/1000, vol_t)
elif "Aérien" in mode: p_tax = max(poids_brut, vol_t * 166.67)
else: p_tax = max(poids_brut/1000, vol_t/3)

with col_prix:
    st.subheader("💰 Coûts (Devise d'achat)")
    fret_u = st.number_input("Taux de Fret unitaire", value=0.0)
    baf = st.number_input("BAF Totale", value=0.0)
    port = st.number_input("Port / Douane", value=0.0)
    livraison = st.number_input("Livraison Local", value=0.0)

# Calcul totaux avec conversion
total_ht_origine = (p_tax * fret_u) + baf + port + livraison
total_final = total_ht_origine * taux_change

st.divider()
st.metric(f"Total en {devise_client}", f"{total_final:,.0f} {devise_client}", delta=f"UP: {p_tax:.2f}")

if st.button("📄 GÉNÉRER LE DEVIS PDF"):
    if client:
        donnees = {
            "client": client, "ref": ref_devis, "ptax": p_tax, "mode": mode,
            "fret_total": (p_tax * fret_u) * taux_change, 
            "baf": baf * taux_change, 
            "port": port * taux_change,
            "livraison": livraison * taux_change, 
            "total": total_final, "devise": devise_client, "change": taux_change
        }
        pdf_file = generate_pdf(donnees)
        st.download_button("⬇️ Télécharger", data=pdf_file, file_name=f"Devis_{client}.pdf")
