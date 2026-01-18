import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="GLOBAL TLS - Devis PDF", layout="wide")

# --- FONCTION GÉNÉRATION PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'GLOBAL TLS SARL - DEVIS OFFICIEL', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f'Date: {datetime.now().strftime("%d/%m/%Y")}', 0, 1, 'R')
        self.ln(10)

def generate_pdf(data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Infos Client
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 10, f"Client : {data['client']}", 0, 1, 'L', 1)
    pdf.cell(0, 10, f"Référence : {data['ref']}", 0, 1, 'L')
    pdf.ln(5)
    
    # Détails Marchandise
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Détails de l'expédition :", 0, 1)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, f"Marchandise : {data['nature']}\nPoids Taxable : {data['ptax']:.2f} units\nTrajet : {data['mode']}")
    pdf.ln(5)
    
    # Tableau des prix
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 10, "Désignation", 1)
    pdf.cell(50, 10, "Montant", 1, 1)
    
    pdf.set_font("Arial", size=11)
    for item, price in data['details'].items():
        pdf.cell(140, 10, item, 1)
        pdf.cell(50, 10, f"{price:,.2f}", 1, 1)
        
    # Total
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 15, f"TOTAL FINAL : {data['total']:,.2f} {data['devise']}", 0, 1, 'R')
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE STREAMLIT ---
st.title("🌐 GLOBAL TLS : Cotation & Export PDF")

with st.sidebar:
    st.header("📋 Dossier")
    client = st.text_input("Nom du Client", "Client Exemple")
    ref = st.text_input("Référence", "DEV-2024-001")
    devise = st.selectbox("Devise", ["FCFA", "EUR", "USD"])

# Paramètres de calcul (Simplifiés pour l'exemple)
col1, col2 = st.columns(2)
with col1:
    nature = st.text_input("Nature marchandise", "Matériel divers")
    poids = st.number_input("Poids (kg)", value=1000.0)
    mode = st.selectbox("Mode", ["Maritime", "Aérien", "Routier"])
    fret_base = st.number_input("Taux de Fret", value=500.0)

with col2:
    frais_douane = st.number_input("Frais Douane", value=50000.0)
    livraison = st.number_input("Livraison", value=25000.0)
    marge = st.number_input("Marge Bénéficiaire", value=15000.0)

# Calcul du total
total_calcul = fret_base + frais_douane + livraison + marge

st.divider()
st.subheader(f"Total estimé : {total_calcul:,.2f} {devise}")

# Préparation des données pour le PDF
donnees_devis = {
    "client": client,
    "ref": ref,
    "nature": nature,
    "ptax": poids,
    "mode": mode,
    "devise": devise,
    "details": {
        "Fret Principal": fret_base,
        "Douane & Formalités": frais_douane,
        "Livraison": livraison,
        "Frais de dossier & Marge": marge
    },
    "total": total_calcul
}

# --- BOUTON DE TÉLÉCHARGEMENT ---
pdf_output = generate_pdf(donnees_devis)
st.download_button(
    label="📥 Télécharger le Devis en PDF",
    data=pdf_output,
    file_name=f"Devis_GLOBAL_TLS_{ref}.pdf",
    mime="application/pdf"
)
