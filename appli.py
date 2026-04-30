import streamlit as st 
import pandas as pd 
import numpy as np 
import os 
from datetime import datetime 
from sklearn.linear_model import LinearRegression 

# --- 1. CONFIGURATION & PERSISTANCE --- 
st.set_page_config(page_title="Agri-Collecte Pro - Wals", page_icon="🌿", layout="wide") 
DB_FILE = "database_agri_master.csv" 

def load_data(): 
    if os.path.exists(DB_FILE): 
        return pd.read_csv(DB_FILE) 
    return pd.DataFrame(columns=[ 
        "Date", "Collecteur", "Propriétaire", "Exploitant",  
        "Culture", "Surface_Ha", "Recolte_T", "Rendement_THa", "Etat" 
    ]) 

if 'inscrit' not in st.session_state: 
    st.session_state.inscrit = False 

# --- 2. DESIGN CSS --- 
st.markdown(""" 
    <style> 
    .stApp { background-color: #f8f9fa; } 
    .main-header {  
        background: linear-gradient(135deg, #1b5e20, #2e7d32);  
        padding: 20px; border-radius: 15px; color: white;  
        text-align: center; margin-bottom: 20px; 
    } 
    </style> 
    """, unsafe_allow_html=True) 

# --- 3. INTERFACE D'INSCRIPTION --- 
if not st.session_state.inscrit: 
    st.markdown('<div class="main-header"><h1>📝 INSCRIPTION COLLECTEUR</h1><p>TP INF 232 - Accès Sécurisé</p></div>', unsafe_allow_html=True) 
    
    with st.container(): 
        col_in1, col_in2 = st.columns(2) 
        with col_in1: 
            nom_c = st.text_input("👤 Nom et Prénom du Collecteur") 
            tel_c = st.text_input("📞 Numéro de téléphone", help="9 chiffres requis") 
        with col_in2: 
            zone = st.selectbox("📍 Zone de recensement", ["Centre", "Littoral", "Ouest", "Sud", "Nord", "Est"]) 

        if st.button("🚀 Valider mon Profil et Entrer"): 
            if nom_c and tel_c.isdigit() and len(tel_c) == 9: 
                st.session_state.inscrit = True 
                st.session_state.user = nom_c 
                st.session_state.zone = zone 
                st.rerun() 
            else: 
                st.error("❌ Erreur : Nom requis et 9 chiffres pour le téléphone.") 

# --- 4. INTERFACE PRINCIPALE (MENU DE NAVIGATION) --- 
else: 
    with st.sidebar: 
        st.header(f"🌳 Bienvenue, {st.session_state.user}") 
        st.divider() 
        # AJOUT DE L'OPTION DANS LE MENU RADIO
        menu = st.radio( 
            "Navigation", 
            ["Nouvelle Saisie", "Analyse & Visualisation", "Prédiction par Régression", "Historique complet", "Exportation CSV"] 
        ) 
        st.divider() 
        if st.button("🔌 Se déconnecter"): 
            st.session_state.inscrit = False 
            st.rerun() 

    df = load_data() 

    # --- SECTION : NOUVELLE SAISIE --- 
    if menu == "Nouvelle Saisie": 
        st.markdown('<div class="main-header"><h1>📝 SAISIE DE TERRAIN</h1></div>', unsafe_allow_html=True) 
        with st.form("form_collecte"): 
            c1, c2 = st.columns(2) 
            with c1: 
                proprio = st.text_input("🏠 Nom du Propriétaire") 
                exploitant = st.text_input("👨‍🌾 Nom de l'Exploitant") 
                
                culture_base = st.selectbox("🌱 Type de Culture", ["Maïs", "Manioc", "Cacao", "Café", "Banane", "Autre"]) 
                culture_finale = culture_base 
                if culture_base == "Autre": 
                    culture_finale = st.text_input("👉 Saisissez votre type de culture") 
                
            with c2: 
                col_s1, col_s2 = st.columns([2, 1]) 
                val_surf = col_s1.number_input("📏 Valeur Surface", min_value=0.01, step=0.1) 
                unit_surf = col_s2.selectbox("Unité", ["Hectares", "m²"]) 
                
                col_q1, col_q2 = st.columns([2, 1]) 
                val_qte = col_q1.number_input("📦 Valeur Récolte", min_value=0.0, step=0.1) 
                unit_qte = col_q2.selectbox("Unité", ["Tonnes", "Kilogrammes (kg)"]) 
                
                etat = st.select_slider("🌡️ État de santé", ["Mauvais", "Moyen", "Bon", "Excellent"]) 

            surf_ha = val_surf if unit_surf == "Hectares" else val_surf / 10000 
            qte_t = val_qte if unit_qte == "Tonnes" else val_qte / 1000 

            if st.form_submit_button("💾 Enregistrer dans la Base"): 
                if proprio and exploitant and culture_finale: 
                    rend = qte_t / surf_ha 
                    new_data = { 
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                        "Collecteur": st.session_state.user, 
                        "Propriétaire": proprio, 
                        "Exploitant": exploitant, 
                        "Culture": culture_finale, 
                        "Surface_Ha": round(surf_ha, 4), 
                        "Recolte_T": round(qte_t, 3), 
                        "Rendement_THa": round(rend, 2), 
                        "Etat": etat 
                    } 
                    pd.DataFrame([new_data]).to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False) 
                    st.success(f"Données enregistrées avec succès !") 
                else: 
                    st.error("⚠️ Veuillez remplir tous les champs.") 

    # --- SECTION : ANALYSE & VISUALISATION --- 
    elif menu == "Analyse & Visualisation": 
        st.markdown('<div class="main-header"><h1>📊 ANALYSE DESCRIPTIVE</h1></div>', unsafe_allow_html=True) 
        if not df.empty: 
            m1, m2, m3 = st.columns(3) 
            m1.metric("Surface Totale", f"{df['Surface_Ha'].sum():.2f} Ha") 
            m2.metric("Récolte Totale", f"{df['Recolte_T'].sum():.2f} T") 
            m3.metric("Rendement Moyen", f"{df['Rendement_THa'].mean():.2f} T/Ha") 

            st.write("### 📈 Visualisation des données") 
            col_chart1, col_chart2 = st.columns(2) 
            with col_chart1: 
                st.write("**Production par Culture (Tonnes)**") 
                st.bar_chart(df.groupby("Culture")["Recolte_T"].sum()) 
            with col_chart2: 
                st.write("**Répartition des Surfaces (Ha)**") 
                st.area_chart(df.groupby("Culture")["Surface_Ha"].sum()) 
        else: 
            st.info("Aucune donnée disponible pour l'analyse.") 

    # --- SECTION : PRÉDICTION --- 
    elif menu == "Prédiction par Régression": 
        st.markdown('<div class="main-header"><h1>🤖 MODÈLE DE PRÉDICTION</h1></div>', unsafe_allow_html=True) 
        if len(df) >= 3: 
            model = LinearRegression().fit(df[['Surface_Ha']].values, df['Recolte_T'].values) 
            st.write("### Simulation de rendement") 
            s_test = st.slider("Choisissez une surface (Ha) :", 0.1, 50.0, 5.0) 
            p_test = model.predict([[s_test]])[0] 
            st.info(f"💡 Estimation : Pour **{s_test} Ha**, la récolte prévue est d'environ **{p_test:.2f} Tonnes**.") 
        else: 
            st.warning("Il faut au moins 3 entrées dans la base de données pour activer la prédiction.") 

    # --- SECTION : HISTORIQUE --- 
    elif menu == "Historique complet": 
        st.markdown('<div class="main-header"><h1>📜 HISTORIQUE DES DONNÉES</h1></div>', unsafe_allow_html=True) 
        if not df.empty: 
            st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True) 
        else: 
            st.info("L'historique est actuellement vide.")

    # --- SECTION : EXPORTATION CSV (NOUVELLE) ---
    elif menu == "Exportation CSV":
        st.markdown('<div class="main-header"><h1>📥 EXPORTATION DES DONNÉES</h1></div>', unsafe_allow_html=True)
        if not df.empty:
            st.write("### Préparation de votre fichier")
            st.write(f"Nombre d'enregistrements à exporter : **{len(df)}**")
            
            # Préparation du CSV
            csv_data = df.to_csv(index=False).encode('utf-8')
            
            st.info("Cliquez sur le bouton ci-dessous pour télécharger la base de données au format Excel/CSV.")
            st.download_button(
                label="📥 Télécharger (.csv)",
                data=csv_data,
                file_name=f"export_agri_wals_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key='download-csv'
            )
        else:
            st.warning("La base de données est vide. Rien à exporter.")
