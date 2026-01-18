import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURATION DE LA BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('global_tls_quotes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS quotes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, client TEXT, marchandise TEXT, 
                  poids REAL, prix_total INTEGER, marge INTEGER)''')
    conn.commit()
    conn.close()

def save_quote(client, marchandise, poids, prix_total, marge):
    conn = sqlite3.connect('global_tls_quotes.db')
    c = conn.cursor()
    date_now = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.execute("INSERT INTO quotes (date, client, marchandise, poids, prix_total, marge) VALUES (?,?,?,?,?,?)",
              (date_now, client, marchandise, poids, prix_total, marge))
    conn.commit()
    conn.close()

# --- INITIALISATION ---
init_db()
st.set_page_config(page_title="GLOBAL TLS - Cotation", layout="wide")

# --- INTERFACE ---
st.title("🌐 GLOBAL TLS SARL - Gestion des Cotations")

tabs = st.tabs(["🆕 Nouvelle Cotation", "📂 Historique des Devis"])

with tabs[0]:
    col_in, col_out = st.columns([1, 1])
    
    with col_in:
        st.subheader("Paramètres")
        client = st.text_input("Client", "Client Anonyme")
        marchandise = st.selectbox("Marchandise", ["Matériel Informatique", "Produits Frais", "BTP", "Divers"])
        valeur = st.number_input("Valeur Marchandise (€)", value=50000)
        poids = st.number_input("Poids (Tonnes)", value=1.0)
        marge = st.slider("Marge (%)", 5, 40, 15)

    # Logique de calcul simple
    fret_base = 2500 * 655.95 # Base maritime
    assurance = (valeur * 0.008) * 655.95 # 0.8% de la valeur
    transport_mali = 1200000 if poids > 5 else poids * 200000
    
    total_achat = fret_base + assurance + transport_mali
    prix_final = int(total_achat * (1 + marge/100))

    with col_out:
        st.subheader("Résultat")
        st.metric("Prix Final (FCFA)", f"{prix_final:,}")
        
        if st.button("💾 Enregistrer et Générer PDF"):
            save_quote(client, marchandise, poids, prix_final, marge)
            st.success(f"Devis enregistré pour {client} !")
            st.download_button("Télécharger le Devis (Simulation)", "Contenu du devis...", file_name="devis_tls.txt")

with tabs[1]:
    st.subheader("Dernières Cotations Enregistrées")
    conn = sqlite3.connect('global_tls_quotes.db')
    df_history = pd.read_sql_query("SELECT * FROM quotes ORDER BY id DESC", conn)
    conn.close()
    
    if not df_history.empty:
        st.dataframe(df_history, use_container_width=True)
        
        # Petit graphique d'analyse
        st.line_chart(df_history.set_index('date')['prix_total'])
    else:
        st.info("Aucun devis dans l'historique.")

# --- FOOTER ---
st.divider()
st.caption("Propriété de GLOBAL TLS SARL - Système Sécurisé")