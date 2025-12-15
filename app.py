import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
    page_title="Notes 2LM - Probabilité",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS pour masquer les éléments inutiles et styliser l'application
st.markdown("""
    <style>
    /* Masquer le menu, footer et header par défaut */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Masquer complètement la barre latérale */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Style pour le titre principal */
    .main-title {
        text-align: center;
        color: #1E3A8A;
        padding: 10px;
        margin-bottom: 20px;
    }
    
    /* Style pour les sous-titres */
    .sub-title {
        color: #374151;
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 10px;
        margin-top: 30px;
    }
    
    /* Style pour les cartes de statistiques */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Style pour le champ de saisie email */
    .email-input {
        font-size: 18px !important;
        padding: 15px !important;
        border-radius: 10px !important;
        border: 2px solid #3B82F6 !important;
    }
    
    /* Style pour les messages d'alerte */
    .alert-warning {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
    }
    
    .alert-error {
        background-color: #FEE2E2;
        border-left: 4px solid #EF4444;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
    }
    
    /* Style pour les données étudiant */
    .student-data {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Ajustements généraux */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    h1, h2, h3 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Titre principal avec HTML
st.markdown('<h1 class="main-title">📊 NOTES DS Probabilité</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="main-title" style="font-size: 1.5rem;">2LM - Année Universitaire 2024-2025</h2>', unsafe_allow_html=True)
csv_file_path = st.secrets['csv_file_path']
# Fonction pour charger les données
@st.cache_data
def load_data():
    try:
        # Chargement du fichier CSV
        df = pd.read_csv(csv_file_path, delimiter=";", encoding='utf-8')
        
        # Nettoyer les noms de colonnes
        df.columns = df.columns.str.strip()
        
        # Nettoyer les emails
        if 'Email' in df.columns:
            df["Email"] = df["Email"].astype(str).str.strip().str.lower()
        
        # Fonction pour convertir les nombres avec virgule
        def convert_comma_to_float(value):
            if isinstance(value, str):
                value = value.replace(',', '.').strip()
                try:
                    return float(value) if value else None
                except ValueError:
                    return None
            return value
        
        # Convertir les colonnes numériques
        numeric_columns = ['DS', 'TP', 'TPEX', 'D', 'B']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].apply(convert_comma_to_float)
        
        return df
    
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return None

# Chargement des données
df = load_data()

if df is None:
    st.stop()

# Fonction pour catégoriser les notes
def categorize_notes(note):
    try:
        if pd.isna(note):
            return "Non défini"
        note = float(note)
        if note < 10:
            return "Insuffisant (<10)"
        elif 10 <= note < 12:
            return "Passable (10-12)"
        elif 12 <= note < 14:
            return "Assez Bien (12-14)"
        elif 14 <= note < 16:
            return "Bien (14-16)"
        else:
            return "Très bien (>16)"
    except:
        return "Non défini"

# Préparation des données
if 'DS' in df.columns:
    df["DS"] = pd.to_numeric(df["DS"], errors='coerce')
    df["Catégorie_DS"] = df["DS"].apply(categorize_notes)

if 'TP' in df.columns:
    df["TP"] = pd.to_numeric(df["TP"], errors='coerce')
    df["Catégorie_TP"] = df["TP"].apply(categorize_notes)

# Section 1: Recherche par email
st.markdown('<h3 class="sub-title">🔍 Recherche de vos notes</h3>', unsafe_allow_html=True)

# Champ de saisie email
email = st.text_input(
    "Entrez votre adresse email universitaire :",
    key="email_input",
    placeholder="exemple@etudiant.univ-tln.fr",
    help="Veuillez entrer l'email exact utilisé pour l'inscription"
)

if email:
    email = email.strip().lower()
    
    if 'Email' in df.columns:
        mask = df["Email"] == email
        if mask.any():
            # Récupération des données de l'étudiant
            etudiant = df[mask].iloc[0]
            
            # Affichage des résultats
            st.markdown('<div class="student-data">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("👤 Nom", etudiant.get("Name", "Non disponible"))
            
            with col2:
                st.metric("👥 Groupe", etudiant.get("GR", "Non disponible"))
            
            with col3:
                ds_value = etudiant.get("DS", "Non disponible")
                if isinstance(ds_value, (int, float)):
                    st.metric("📝 Note DS", f"{ds_value:.2f}/20")
                else:
                    st.metric("📝 Note DS", str(ds_value))
            
            col4, col5, col6 = st.columns(3)
            
            with col4:
                tp_value = etudiant.get("TP", "Non disponible")
                if isinstance(tp_value, (int, float)):
                    st.metric("💻 Note TP", f"{tp_value:.2f}/20")
                else:
                    st.metric("💻 Note TP", str(tp_value))
            
            with col5:
                tpex_value = etudiant.get("TPEX", "Non disponible")
                if isinstance(tpex_value, (int, float)):
                    st.metric("📊 Note TPEX", f"{tpex_value:.2f}/20")
                else:
                    st.metric("📊 Note TPEX", str(tpex_value))
            
            with col6:
                # Calcul de la moyenne si toutes les notes sont disponibles
                notes = []
                for col in ['DS', 'TP', 'TPEX']:
                    if col in etudiant and isinstance(etudiant[col], (int, float)):
                        notes.append(etudiant[col])
                
                if notes:
                    moyenne = sum(notes) / len(notes)
                    st.metric("🎯 Moyenne", f"{moyenne:.2f}/20")
                else:
                    st.metric("🎯 Moyenne", "Non calculable")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Message d'alerte pour les absents
            if etudiant.get("DS") == -1:
                st.markdown("""
                    <div class="alert-warning">
                    ⚠️ <strong>Note : -1</strong><br>
                    Vous étiez absent au DS. Si vous ne régularisez pas votre situation, 
                    la note finale du DS sera de 0.
                    </div>
                """, unsafe_allow_html=True)
            
            # Graphique des notes de l'étudiant
            if isinstance(ds_value, (int, float)) and isinstance(tp_value, (int, float)):
                fig_indiv = go.Figure(data=[
                    go.Bar(
                        name='Vos notes',
                        x=['DS', 'TP', 'TPEX'],
                        y=[ds_value, tp_value, tpex_value if isinstance(tpex_value, (int, float)) else 0],
                        marker_color=['#3B82F6', '#10B981', '#8B5CF6']
                    )
                ])
                
                fig_indiv.update_layout(
                    title="📈 Vos notes détaillées",
                    yaxis_title="Note /20",
                    yaxis_range=[0, 20],
                    showlegend=False,
                    height=400
                )
                
                st.plotly_chart(fig_indiv, use_container_width=True)
        
        else:
            st.markdown("""
                <div class="alert-error">
                ❌ <strong>Email non trouvé</strong><br>
                Vérifiez que vous avez entré l'adresse email exacte utilisée lors de l'inscription.
                </div>
            """, unsafe_allow_html=True)
    
    else:
        st.error("Erreur : Colonne 'Email' non trouvée dans les données.")

# Section 2: Statistiques par groupe
st.markdown('<h3 class="sub-title">📊 Statistiques par groupe</h3>', unsafe_allow_html=True)

with st.expander("📈 Cliquez pour voir les statistiques détaillées par groupe", expanded=False):
    if 'GR' in df.columns:
        # Sélection du groupe
        groupes = sorted([str(g).strip() for g in df["GR"].dropna().unique() if str(g).strip()])
        
        if groupes:
            groupe_selectionne = st.selectbox(
                "Sélectionnez un groupe :",
                options=groupes,
                key="groupe_select"
            )
            
            if groupe_selectionne:
                # Filtrage des données
                df_groupe = df[df["GR"].astype(str).str.strip() == groupe_selectionne].copy()
                
                # Statistiques DS
                if 'DS' in df_groupe.columns:
                    ds_notes = pd.to_numeric(df_groupe["DS"], errors='coerce').dropna()
                    
                    if len(ds_notes) > 0:
                        # Métriques DS
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Moyenne DS", f"{ds_notes.mean():.2f}")
                        
                        with col2:
                            st.metric("Médiane DS", f"{ds_notes.median():.2f}")
                        
                        with col3:
                            st.metric("Écart-type DS", f"{ds_notes.std():.2f}")
                        
                        with col4:
                            st.metric("Effectif", len(ds_notes))
                        
                        # Graphiques DS
                        col_graph1, col_graph2 = st.columns(2)
                        
                        with col_graph1:
                            # Histogramme DS
                            fig_hist_ds = px.histogram(
                                ds_notes,
                                nbins=10,
                                title=f"Distribution des notes DS - Groupe {groupe_selectionne}",
                                labels={'value': 'Note DS', 'count': 'Nombre d\'étudiants'},
                                color_discrete_sequence=['#3B82F6']
                            )
                            fig_hist_ds.update_layout(bargap=0.1)
                            st.plotly_chart(fig_hist_ds, use_container_width=True)
                        
                        with col_graph2:
                            # Boxplot DS
                            fig_box_ds = px.box(
                                ds_notes,
                                title=f"Boxplot des notes DS - Groupe {groupe_selectionne}",
                                labels={'value': 'Note DS'}
                            )
                            st.plotly_chart(fig_box_ds, use_container_width=True)
                        
                        # Pie chart des catégories DS
                        if 'Catégorie_DS' in df_groupe.columns:
                            fig_pie_ds = px.pie(
                                df_groupe,
                                names='Catégorie_DS',
                                title=f"Répartition par catégorie - DS",
                                color_discrete_sequence=px.colors.sequential.RdBu
                            )
                            st.plotly_chart(fig_pie_ds, use_container_width=True)
                
                # Statistiques TP
                if 'TP' in df_groupe.columns:
                    tp_notes = pd.to_numeric(df_groupe["TP"], errors='coerce').dropna()
                    
                    if len(tp_notes) > 0:
                        st.markdown("---")
                        st.subheader(f"📊 Statistiques TP - Groupe {groupe_selectionne}")
                        
                        # Métriques TP
                        col5, col6, col7, col8 = st.columns(4)
                        
                        with col5:
                            st.metric("Moyenne TP", f"{tp_notes.mean():.2f}")
                        
                        with col6:
                            st.metric("Médiane TP", f"{tp_notes.median():.2f}")
                        
                        with col7:
                            st.metric("Écart-type TP", f"{tp_notes.std():.2f}")
                        
                        with col8:
                            st.metric("Effectif TP", len(tp_notes))
                        
                        # Graphiques TP
                        col_graph3, col_graph4 = st.columns(2)
                        
                        with col_graph3:
                            # Histogramme TP
                            fig_hist_tp = px.histogram(
                                tp_notes,
                                nbins=10,
                                title=f"Distribution des notes TP",
                                labels={'value': 'Note TP', 'count': 'Nombre d\'étudiants'},
                                color_discrete_sequence=['#10B981']
                            )
                            fig_hist_tp.update_layout(bargap=0.1)
                            st.plotly_chart(fig_hist_tp, use_container_width=True)
                        
                        with col_graph4:
                            # Boxplot TP
                            fig_box_tp = px.box(
                                tp_notes,
                                title=f"Boxplot des notes TP",
                                labels={'value': 'Note TP'}
                            )
                            st.plotly_chart(fig_box_tp, use_container_width=True)
                        
                        # Pie chart des catégories TP
                        if 'Catégorie_TP' in df_groupe.columns:
                            fig_pie_tp = px.pie(
                                df_groupe,
                                names='Catégorie_TP',
                                title=f"Répartition par catégorie - TP",
                                color_discrete_sequence=px.colors.sequential.Viridis
                            )
                            st.plotly_chart(fig_pie_tp, use_container_width=True)
        else:
            st.warning("Aucun groupe trouvé dans les données.")
    else:
        st.warning("La colonne 'GR' (groupe) n'existe pas dans les données.")

# Footer informatif
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
    <p>📚 <strong>Module de Probabilité - 2LM</strong> | Année Universitaire 2024-2025</p>
    <p>⚠️ Les notes sont susceptibles d'être modifiées après délibération du jury</p>
    </div>
""", unsafe_allow_html=True)