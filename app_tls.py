import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="GLOBAL TLS - Devis", layout="wide")

# --- FONCTION POUR CRÉER LE FICHIER PDF ---
class PDF(FPDF):
    def header(self):
        # En-tête du document
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'GLOBAL TLS SARL - DEVIS OFFICIEL', 0, 1, 'C')
        self.ln(10)

def generer_le_pdf(info):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Infos Client
    pdf.cell(0, 10, f"Client : {info['nom_client']}", 0, 1)
    pdf.cell(0, 10, f"Marchandise : {info['produit']}", 0, 1)
    pdf.ln(5)
    
    # Prix
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Description", 1)
    pdf.cell(50, 10, "Prix", 1, 1)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, "Transport et Logistique", 1)
    pdf.cell(50, 10, f"{info['prix_total']:,} {info['monnaie']}", 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- L'INTERFACE QUE VOUS VOYEZ SUR VOTRE TÉLÉPHONE ---
st.title("🌐 GLOBAL TLS : Création de Devis")

nom = st.text_input("Nom du Client")
marchandise = st.text_input("Nature de la marchandise")
prix = st.number_input("Montant Total HT", value=0)
devise = st.selectbox("Monnaie", ["FCFA", "EUR", "USD"])

if st.button("Générer le PDF maintenant"):
    if nom and prix > 0:
        # On prépare les données
        mes_infos = {
            "nom_client": nom,
            "produit": marchandise,
            "prix_total": prix,
            "monnaie": devise
        }
        
        # On fabrique le PDF
        pdf_final = generer_le_pdf(mes_infos)
        
        # On affiche le bouton de téléchargement
        st.download_button(
            label="⬇️ Cliquez ici pour télécharger le Devis",
            data=pdf_final,
            file_name=f"Devis_{nom}.pdf",
            mime="application/pdf"
        )
        st.success("Le devis est prêt !")
    else:
        st.error("Veuillez entrer un nom et un prix.")
