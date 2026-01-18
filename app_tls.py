import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="GLOBAL TLS - Expert", layout="wide")

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
    pdf.cell(100, 10, "Designation", 1)
    pdf.cell(50, 10, "Montant", 1, 1)
    
    pdf.set_font("Arial", size=11)
    pdf.cell(100, 10, "Fret de base", 1)
    pdf.cell(50, 10, f"{data['fret_total']:,}", 1, 1)
    
    pdf.cell(100, 10, "Surcharge BAF", 1)
    pdf.cell(50, 10, f"{data['baf']:,}", 1, 1)
    
    pdf.cell(100, 10, "Frais Portuaires / Douane", 1)
    pdf.cell(50, 10, f"{data['port']:,}", 1, 1)
    
    pdf.cell(100, 10, "Livraison", 1)
    pdf.cell(50, 10, f"{data['livraison']:,}", 1, 1)
    
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 15, f"TOTAL FINAL : {data['total']:,} {data['devise']}", 1, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE CALCULATEUR ---
st.title("🌐 GLOBAL TLS : Calculateur & Devis avec BAF")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 Dimensions & Poids")
    client = st.text_input("Nom du Client")
    mode = st.selectbox("Mode de transport", ["Maritime (1t=1m3)", "Aérien (1t=6m3)", "Routier (1t=3m3)"])
    nb_colis = st.number_input("Nombre de colis", min_value=1, value=1)
    poids_brut = st.number_input("Poids Total (kg)", value=0.0)
    
    st.write("Dimensions par colis (m) :")
    lx, ly, lz = st.columns(3)
    L = lx.number_input("Long.", value=1.0)
    W = ly.number_input("Larg.", value=1.0)
    H = lz.number_input("Haut.", value=1.0)

# Calcul automatique de l'UP (Poids Taxable)
volume_total = nb_colis * (L * W * H)
if "Maritime" in mode: p_tax = max(poids_brut/1000, volume_total)
elif "Aérien" in mode: p_tax = max(poids_brut, volume_total * 166.67)
else: p_tax = max(poids_brut/1000, volume_total/3)

with col2:
    st.subheader("💰 Coûts du dossier")
    fret_unitaire = st.number_input("Taux de Fret (par UP)", value=0.0)
    # CASE BAF DEMANDÉE
    baf = st.number_input("Montant Surcharge BAF", value=0.0)
    frais_port = st.number_input("Frais Port / Douane", value=0.0)
    livraison = st.number_input("Livraison finale", value=0.0)
    devise = st.selectbox("Monnaie", ["FCFA", "EUR", "USD"])

# Calculs finaux
fret_total = p_tax * fret_unitaire
total_global = fret_total + baf + frais_port + livraison

st.divider()
st.metric("Poids Taxable (UP) retenu", f"{p_tax:.2f}")
st.header(f"Total Général : {total_global:,.2f} {devise}")

if st.button("📥 Générer le Devis PDF"):
    if client:
        donnees_pdf = {
            "client": client, "fret_total": fret_total, "baf": baf,
            "port": frais_port, "livraison": livraison, "total": total_global,
            "devise": devise, "ptax": p_tax, "mode": mode
        }
        pdf_out = generate_pdf(donnees_pdf)
        st.download_button("⬇️ Télécharger le PDF", data=pdf_out, file_name=f"Devis_{client}.pdf")
    else:
        st.error("Veuillez entrer le nom du client.")
