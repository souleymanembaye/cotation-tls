import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="GLOBAL TLS - Cotation Universelle", layout="wide")

st.markdown("""
    <style>
    .stHeader { background-color: #004a99; color: white; padding: 10px; border-radius: 5px; }
    .main-price { font-size: 40px; color: #004a99; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 GLOBAL TLS SARL : Outil de Cotation Intelligent")

# --- BARRE LATÉRALE (INFOS GÉNÉRALES) ---
with st.sidebar:
    st.header("📋 Information Dossier")
    client = st.text_input("Nom du Client")
    reference = st.text_input("Référence Dossier (ex: DKR-2024-001)")
    devise = st.selectbox("Monnaie de facturation", ["EUR", "FCFA", "USD"])
    taux_change = st.number_input("Taux de change (si différent de 1)", value=1.0)

# --- ZONE 1 : LA MARCHANDISE (CALCUL DU POIDS TAXABLE) ---
st.subheader("📦 1. Nature et Dimensions de la Marchandise")
col1, col2, col3 = st.columns(3)

with col1:
    type_marchandise = st.text_input("Nature de la marchandise (ex: Riz, Informatique...)")
    nb_colis = st.number_input("Nombre de colis", min_value=1, value=1)
    poids_brut_total = st.number_input("Poids Brut Total (kg)", min_value=0.1, value=100.0)

with col2:
    st.write("**Dimensions moyennes par colis (m)**")
    l = st.number_input("Longueur", value=1.0)
    w = st.number_input("Largeur", value=1.0)
    h = st.number_input("Hauteur", value=1.0)

with col3:
    mode_transport = st.selectbox("Mode de transport (Règle de taxation)", ["Maritime (1t = 1m3)", "Aérien (1t = 6m3)", "Routier (1t = 3m3)"])
    
    # Calcul du volume et du poids taxable
    volume_total = nb_colis * (l * w * h)
    
    if "Maritime" in mode_transport:
        poids_taxable = max(poids_brut_total / 1000, volume_total)
        label_up = "UP (Unités Payantes)"
    elif "Aérien" in mode_transport:
        poids_taxable = max(poids_brut_total, volume_total * 166.67)
        label_up = "kg taxables"
    else: # Routier
        poids_taxable = max(poids_brut_total / 1000, volume_total / 3)
        label_up = "Tonnes taxables"

    st.metric(label_up, f"{poids_taxable:.2f}")

st.divider()

# --- ZONE 2 : CALCUL DES COÛTS (DÉTAILLÉS) ---
st.subheader("💰 2. Décomposition des Coûts")
c_pre, c_main, c_post = st.columns(3)

with c_pre:
    st.markdown("**🚛 Pré-acheminement & Port**")
    frais_ramassage = st.number_input("Ramassage / Transport amont", value=0.0)
    frais_douane_export = st.number_input("Douane Export / Formalités", value=0.0)
    frais_port_depart = st.number_input("Passage Port/Aéroport départ", value=0.0)

with c_main:
    st.markdown("**🚢 Transport Principal**")
    fret_unitaire = st.number_input(f"Taux de Fret (par {label_up})", value=0.0)
    surcharges = st.number_input("Surcharges totales (BAF, CAF, Sécurité...)", value=0.0)
    assurance = st.number_input("Assurance Ad Valorem", value=0.0)

with c_post:
    st.markdown("**🚚 Post-acheminement & Livraison**")
    frais_port_arrivee = st.number_input("Passage Port/Aéroport arrivée", value=0.0)
    douane_import = st.number_input("Douane Import / Taxes", value=0.0)
    livraison_finale = st.number_input("Livraison dernier kilomètre", value=0.0)

# --- ZONE 3 : MARGE ET TOTAL ---
st.divider()
col_marge, col_total = st.columns([1, 2])

with col_marge:
    marge_type = st.radio("Type de marge", ["Pourcentage (%)", "Forfait fixe"])
    valeur_marge = st.number_input("Valeur de la marge", value=15.0)

# CALCUL DU TOTAL
total_couts = frais_ramassage + frais_douane_export + frais_port_depart + (fret_unitaire * poids_taxable) + surcharges + assurance + frais_port_arrivee + douane_import + livraison_finale

if marge_type == "Pourcentage (%)":
    prix_final = total_couts * (1 + valeur_marge / 100)
else:
    prix_final = total_couts + valeur_marge

prix_final_devise = prix_final * taux_change

with col_total:
    st.write(f"### Prix de vente final pour {client if client else 'le client'}")
    st.markdown(f'<p class="main-price">{prix_final_devise:,.2f} {devise}</p>', unsafe_allow_html=True)
    
    if st.button("✅ Valider et Générer le Devis"):
        st.balloons()
        st.success(f"Dossier {reference} enregistré avec succès !")
        # Ici on peut ajouter la fonction de génération PDF ou sauvegarde DB

# --- FOOTER ---
st.caption(f"GLOBAL TLS SARL - Logiciel de Cotation Interne - {datetime.now().year}")
