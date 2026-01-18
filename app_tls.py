import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="GLOBAL TLS - Calculateur Expert", layout="wide")

# --- CLASSE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'GLOBAL TLS SARL - DEVIS OFFICIEL', 0, 1, 'C')
        self.ln(10)

def generate_pdf(data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Client : {data['client']}", 0, 1)
    pdf.cell(0, 10, f"Date : {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "DETAIL DE LA COTATION :", 0, 1)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, f"Marchandise : {data['nature']}\nPoids Taxable : {data['ptax']:.2f} UP\nMode : {data['mode']}")
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 15, f"TOTAL FINAL : {data['total']:,} {data['devise']}", 1, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE CALCULATEUR ---
st.title("🌐 GLOBAL TLS : Calculateur & Devis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 Marchandise")
    client = st.text_input("Nom du Client")
    nature = st.text_input("Nature du produit")
    mode = st.selectbox("Mode de transport", ["Maritime (1t=1m3)", "Aérien (1t=6m3)", "Routier (1t=3m3)"])
    nb_colis = st.number_input("Nombre de colis", min_value=1, value=1)
    poids_brut = st.number_input("Poids Total (kg)", value=100.0)
    st.write("Dimensions (m) :")
    lx, ly, lz = st.columns(3)
    L = lx.number_input("Long.", value=1.0)
    W = ly.number_input("Larg.", value=1.0)
    H = lz.number_input("Haut.", value=1.0)

# Calcul du Poids Taxable
vol = nb_colis * (L * W * H)
if "Maritime" in mode: p_tax = max(poids_brut/1000, vol)
elif "Aérien" in mode: p_tax = max(poids_brut, vol * 166.67)
else: p_tax = max(poids_brut/1000, vol/3)

with col2:
    st.subheader("💰 Frais & Marges")
    fret_unit = st.number_input("Taux de Fret (par unité)", value=0.0)
    frais_port = st.number_input("Frais Portuaires / Douane", value=0.0)
    livraison = st.number_input("Livraison finale", value=0.0)
    marge = st.number_input("Marge / Frais de dossier", value=0.0)
    devise = st.selectbox("Devise", ["FCFA", "EUR", "USD"])

# Calcul final
total_ht = (fret_unit * p_tax) + frais_port + livraison + marge

st.divider()
st.header(f"Total : {total_ht:,.2f} {devise}")

# Bouton PDF
if st.button("📥 Générer le Devis PDF"):
    if client:
        data_devis = {
            "client": client, "nature": nature, "ptax": p_tax, 
            "mode": mode, "total": total_ht, "devise": devise
        }
        pdf_file = generate_pdf(data_devis)
        st.download_button("⬇️ Télécharger le PDF", data=pdf_file, file_name=f"Devis_{client}.pdf", mime="application/pdf")
    else:
        st.warning("Entrez le nom du client avant de générer.")
