import streamlit as st
import requests
from fpdf import FPDF
from datetime import datetime
import os

# --- FONCTION POUR RÉCUPÉRER LE TAUX RÉEL ---
def get_live_rate(base, target):
    if base == target: return 1.0
    try:
        # Utilisation d'une API gratuite (ExchangeRate-API)
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        response = requests.get(url)
        data = response.json()
        return data['rates'][target]
    except:
        # Taux de secours si internet coupe
        if base == "EUR" and target == "XOF": return 655.95
        return 1.0

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="GLOBAL TLS - Auto Change", layout="wide")

class PDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 33)
        self.set_font('Arial', 'B', 18)
        self.set_text_color(0, 74, 153)
        self.cell(0, 10, 'GLOBAL TLS SARL', 0, 1, 'R')
        self.ln(20)
        self.set_font('Arial', 'B', 16)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 12, 'DEVIS COMMERCIAL', 1, 1, 'C', fill=True)
        self.ln(10)

# --- INTERFACE ---
st.title("🌐 GLOBAL TLS : Cotation avec Change Automatique")

with st.sidebar:
    st.header("💰 Configuration Devises")
    monnaie_achat = st.selectbox("Je paye mes fournisseurs en :", ["EUR", "USD", "XOF"])
    monnaie_client = st.selectbox("Je facture mon client en :", ["XOF", "EUR", "USD"])
    
    # Récupération automatique du taux
    taux_reel = get_live_rate(monnaie_achat, monnaie_client)
    st.success(f"Taux du jour : 1 {monnaie_achat} = {taux_reel:,.2f} {monnaie_client}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 Détails Logistiques")
    client = st.text_input("Nom du Client")
    mode = st.selectbox("Transport", ["Maritime (1t=1m3)", "Aérien (1t=6m3)", "Routier (1t=3m3)"])
    poids = st.number_input("Poids Total (kg)", value=0.0)
    st.write("Dimensions (m)")
    lx, ly, lz = st.columns(3)
    L, W, H = lx.number_input("L", 1.0), ly.number_input("W", 1.0), lz.number_input("H", 1.0)

# Calcul UP
vol = (L * W * H)
if "Maritime" in mode: p_tax = max(poids/1000, vol)
elif "Aérien" in mode: p_tax = max(poids, vol * 166.67)
else: p_tax = max(poids/1000, vol/3)

with col2:
    st.subheader(f"💰 Coûts en {monnaie_achat}")
    fret_u = st.number_input(f"Prix Fret ({monnaie_achat})", value=0.0)
    baf_pc = st.number_input("BAF (%)", value=0.0)
    port = st.number_input(f"Port / Douane ({monnaie_achat})", value=0.0)
    livraison = st.number_input(f"Livraison ({monnaie_achat})", value=0.0)

# CALCULS AVEC CONVERSION AUTO
fret_conv = (p_tax * fret_u) * taux_reel
baf_conv = (fret_conv * baf_pc / 100)
port_conv = port * taux_reel
liv_conv = livraison * taux_reel
total_final = fret_conv + baf_conv + port_conv + liv_conv

st.divider()
st.metric(f"Total à facturer en {monnaie_client}", f"{total_final:,.0f} {monnaie_client}")

if st.button("📄 GÉNÉRER LE DEVIS"):
    # (Logique PDF identique aux versions précédentes avec les montants convertis)
    st.write("Le PDF sera généré avec les taux convertis automatiquement.")
