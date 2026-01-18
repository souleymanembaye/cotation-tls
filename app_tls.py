import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="GLOBAL TLS - Devis", layout="wide")

class PDF(FPDF):
    def header(self):
        # 1. LOGO (Si logo.png est présent sur GitHub)
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 33)
        
        # 2. INFOS SOCIÉTÉ
        self.set_font('Arial', 'B', 18)
        self.set_text_color(0, 74, 153) # Bleu Marine
        self.cell(0, 10, 'GLOBAL TLS SARL', 0, 1, 'R')
        
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, 'Transport International - Logistique - Transit', 0, 1, 'R')
        self.ln(20)
        
        # 3. TITRE DU DOCUMENT : DEVIS
        self.set_font('Arial', 'B', 16)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 12, 'DEVIS COMMERCIAL / COTATION', 1, 1, 'C', fill=True)
        self.ln(10)

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'GLOBAL TLS SARL - Siege Social - Dakar, Senegal', 0, 1, 'C')
        self.cell(0, 5, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(data):
    pdf = PDF()
    pdf.add_page()
    
    # Infos Client
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(100, 7, f"DESTINATAIRE : {data['client'].upper()}", 0, 0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 7, f"Date d'émission : {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')
    pdf.cell(0, 7, f"Offre N° : {data['ref']}", 0, 1, 'R')
    pdf.ln(10)
    
    # Tableau de Cotation
    pdf.set_font("Arial", 'B', 11)
    pdf.set_fill_color(0, 74, 153)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(110, 10, " DESCRIPTION DES PRESTATIONS", 1, 0, 'L', True)
    pdf.cell(35, 10, " UNITE", 1, 0, 'C', True)
    pdf.cell(45, 10, " TOTAL ", 1, 1, 'C', True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 11)
    
    # Lignes du devis
    lignes = [
        (f"Fret Principal ({data['mode']})", f"{data['ptax']:.2f} UP", f"{data['fret_total']:,.0f}"),
        ("Surcharge BAF (Fuel)", "-", f"{data['baf']:,.0f}"),
        ("Frais Portuaires / Manutention", "-", f"{data['port']:,.0f}"),
        ("Transport Terrestre / Livraison", "-", f"{data['livraison']:,.0f}")
    ]
    
    for desc, qte, mnt in lignes:
        pdf.cell(110, 10, f" {desc}", 1)
        pdf.cell(35, 10, qte, 1, 0, 'C')
        pdf.cell(45, 10, f"{mnt} ", 1, 1, 'R')
    
    # Total
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(145, 12, f" MONTANT TOTAL HT ({data['devise']}) ", 0, 0, 'R')
    pdf.cell(45, 12, f" {data['total']:,.0f} ", 1, 1, 'C')
    
    # Validité
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, "Conditions de validité :", 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, "- Offre valable 15 jours sous réserve de place et de matériel.", 0, 1)
    pdf.cell(0, 5, "- Selon conditions générales de GLOBAL TLS SARL.", 0, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE STREAMLIT ---
st.title("📋 GLOBAL TLS - Générateur de Devis")

with st.sidebar:
    st.subheader("Réglages du Devis")
    ref_devis = st.text_input("Numéro de Devis", value="GTLS-COT-001")
    devise = st.selectbox("Devise du devis", ["FCFA", "EUR", "USD"])

c1, c2 = st.columns(2)
with c1:
    client = st.text_input("Nom du Client / Prospect")
    mode = st.selectbox("Mode de transport", ["Maritime", "Aérien", "Routier"])
    p_tax = st.number_input("Poids Taxable (UP)", value=1.0)
    fret_u = st.number_input("Taux de Fret unitaire", value=0)

with c2:
    baf = st.number_input("Surcharge BAF", value=0)
    port = st.number_input("Frais Port / Terminal", value=0)
    livraison = st.number_input("Livraison / Transport Local", value=0)

total = (p_tax * fret_u) + baf + port + livraison

st.divider()
if st.button("📄 GÉNÉRER LE DEVIS PDF"):
    if client:
        donnees = {
            "client": client, "ref": ref_devis, "ptax": p_tax, "mode": mode,
            "fret_total": p_tax * fret_u, "baf": baf, "port": port,
            "livraison": livraison, "total": total, "devise": devise
        }
        pdf_file = generate_pdf(donnees)
        st.download_button("⬇️ Télécharger le Devis", data=pdf_file, file_name=f"Devis_{client}.pdf")
    else:
        st.error("Veuillez indiquer le nom du client.")
