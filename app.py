import streamlit as st
import pandas as pd
import os 
import plotly.express as px

st.set_page_config(page_title="Notes 2LM", page_icon=":bar_chart:", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# CSS pour cacher l'icône de GitHub et la barre latérale
st.markdown(
    """
    <style>
    .stApp .main-header a {
        display: none !important;
    }
    
    /* Masquer la barre latérale */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Ajuster la largeur du contenu principal */
    .block-container {
        padding-top: 2rem;
        max-width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

csv_file_path = st.secrets['csv_file_path']
#csv_file_path = "2lm2526.csv"

# Fonction pour convertir les nombres avec virgule en float
def convert_comma_to_float(value):
    if isinstance(value, str):
        # Remplace la virgule par un point et convertit en float
        value = value.replace(',', '.')
        try:
            return float(value)
        except ValueError:
            return None
    return value

# Chargement du fichier CSV avec le séparateur point-virgule
try:
    df = pd.read_csv(csv_file_path, delimiter=";", encoding='utf-8')
except Exception as e:
    st.error(f"Erreur lors du chargement du fichier CSV: {e}")
    st.stop()

# Nettoyer les noms de colonnes
df.columns = df.columns.str.strip()

# Nettoyer les emails
if 'Email' in df.columns:
    df["Email"] = df["Email"].astype(str).str.strip().str.lower()

# Convertir les colonnes numériques (remplacer les virgules par des points)
numeric_columns = ['DS', 'TP', 'TPEX', 'D', 'B']
for col in numeric_columns:
    if col in df.columns:
        df[col] = df[col].apply(convert_comma_to_float)

# Titre de l'application
st.title("NOTES DS Probabilité")
st.header("2LM A.U 2025-2026")

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

# Vérification si les colonnes existent et conversion en numérique
if 'DS' in df.columns:
    df["DS"] = pd.to_numeric(df["DS"], errors='coerce')
    df["Catégorie de notes DS"] = df["DS"].apply(categorize_notes)

if 'TP' in df.columns:
    df["TP"] = pd.to_numeric(df["TP"], errors='coerce')
    df["Catégorie de notes TP"] = df["TP"].apply(categorize_notes)

# CSS pour personnaliser la taille de la police
st.markdown(
    """
    <style>
    .custom-text-input label {
        font-size: 28px !important;
        font-weight: bold;
    }
    input[data-testid="stTextInput"] {
        font-size: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True
)

# Champ de saisie pour l'email de l'étudiant avec une classe personnalisée
email = st.text_input("Saisissez votre email", key="email_input", 
                     label_visibility="visible", 
                     placeholder="Exemple: nom@example.com")

# Appliquer la classe personnalisée via JavaScript
st.markdown(
    """
    <script>
    const inputElement = document.querySelector('input[data-testid="stTextInput"]');
    if (inputElement) {
        inputElement.parentElement.classList.add('custom-text-input');
    }
    </script>
    """, unsafe_allow_html=True
)

if email:
    email = email.strip().lower()
    
    if 'Email' in df.columns:
        # Chercher l'email dans la colonne
        mask = df["Email"] == email
        if mask.any():
            # Récupération des informations de l'étudiant correspondant à l'email
            etudiant = df[mask].iloc[0]
            nom = etudiant["Name"] if 'Name' in df.columns else "Non disponible"
            groupe = etudiant["GR"] if 'GR' in df.columns else "Non disponible"
            noteDS = etudiant["DS"] if 'DS' in df.columns else "Non disponible"
            noteTP = etudiant["TP"] if 'TP' in df.columns else "Non disponible"
            
            # Création d'un dictionnaire contenant les informations de l'étudiant
            etudiant_info = {
                "Nom": str(nom),
                "Groupe": str(groupe),
                "DS": f"{noteDS:.2f}" if isinstance(noteDS, (int, float)) else str(noteDS),
                "TP": f"{noteTP:.2f}" if isinstance(noteTP, (int, float)) else str(noteTP),
            }
            
            res = pd.DataFrame.from_dict(etudiant_info, orient='index', columns=['Résultats'])
            
            # Affichage des informations de l'étudiant dans un tableau
            st.subheader("Résultats de l'étudiant")
            a, b, c = st.columns([1, 2, 1])
            with b:
                st.dataframe(res, use_container_width=True)
                
            if noteDS == -1:
                st.warning("-1 : absent au DS. Si vous ne réglez pas votre situation, la note finale au DS sera 0")
        else:
            st.error("Email non trouvé dans la base de données")
    else:
        st.error("Colonne 'Email' non trouvée dans le fichier CSV")

# Bloc avec la possibilité de cacher/afficher les statistiques des groupes
with st.expander("Afficher/Masquer les statistiques des groupes"):
    if 'GR' in df.columns:
        # Champ de sélection pour choisir un groupe
        groupes = df["GR"].dropna().unique()
        groupes = [str(g).strip() for g in groupes]
        groupes = sorted([g for g in groupes if g and str(g) != 'nan'])
        
        if len(groupes) > 0:
            groupe_selectionne = st.selectbox("Choisissez un groupe", options=groupes)

            if groupe_selectionne:
                # Filtrer les données pour le groupe sélectionné
                df_groupe = df[df["GR"].astype(str).str.strip() == groupe_selectionne].copy()
                
                # Vérifier si la colonne DS existe et contient des données numériques
                if 'DS' in df_groupe.columns:
                    # Convertir en numérique si ce n'est pas déjà fait
                    df_groupe["DS"] = pd.to_numeric(df_groupe["DS"], errors='coerce')
                    
                    # Filtrer les valeurs NaN
                    df_groupe_ds = df_groupe.dropna(subset=['DS'])
                    
                    if len(df_groupe_ds) > 0:
                        # Statistiques du groupe
                        moyenne = df_groupe_ds["DS"].mean()
                        variance = df_groupe_ds["DS"].var()
                        ecart_type = df_groupe_ds["DS"].std()

                        # Affichage des statistiques
                        col1, col2 = st.columns(2)
                        
                        with col2:
                            # Boxplot
                            fig_box = px.box(df_groupe_ds, y="DS", points="all", 
                                            title=f"Boxplot des notes DS - Groupe {groupe_selectionne}",
                                            labels={"DS": "Note DS"})
                            st.plotly_chart(fig_box, use_container_width=True)
                            
                            st.metric("Moyenne", f"{moyenne:.2f}")
                            st.metric("Variance", f"{variance:.2f}")
                            st.metric("Écart-type", f"{ecart_type:.2f}")

                        # Graphiques
                        with col1:
                            # Pie chart des catégories
                            if 'Catégorie de notes DS' in df_groupe_ds.columns:
                                fig_pie = px.pie(df_groupe_ds, names="Catégorie de notes DS", 
                                               title=f"Répartition des catégories - Groupe {groupe_selectionne}")
                                st.plotly_chart(fig_pie, use_container_width=True)
                            
                            # Histogramme
                            fig_hist = px.histogram(
                                df_groupe_ds,
                                x="DS",
                                nbins=10,
                                title=f"Histogramme des notes DS - Groupe {groupe_selectionne}",
                                labels={"DS": "Notes DS"},
                                color_discrete_sequence=["#636EFA"],
                            )
                            fig_hist.update_layout(bargap=0.2)
                            st.plotly_chart(fig_hist, use_container_width=True)
                            
                        # Section pour les statistiques du TP si la colonne existe
                        if 'TP' in df_groupe.columns:
                            st.subheader(f"Statistiques des notes TP - Groupe {groupe_selectionne}")
                            
                            # Convertir les notes TP en numérique
                            df_groupe["TP"] = pd.to_numeric(df_groupe["TP"], errors='coerce')
                            df_groupe_tp = df_groupe.dropna(subset=['TP'])
                            
                            if len(df_groupe_tp) > 0:
                                col3, col4 = st.columns(2)
                                
                                with col3:
                                    # Boxplot TP
                                    fig_box_tp = px.box(df_groupe_tp, y="TP", points="all", 
                                                       title=f"Boxplot des notes TP",
                                                       labels={"TP": "Note TP"})
                                    st.plotly_chart(fig_box_tp, use_container_width=True)
                                
                                with col4:
                                    # Pie chart TP
                                    if 'Catégorie de notes TP' in df_groupe_tp.columns:
                                        fig_pie_tp = px.pie(df_groupe_tp, names="Catégorie de notes TP", 
                                                          title=f"Répartition des catégories TP")
                                        st.plotly_chart(fig_pie_tp, use_container_width=True)
                                    
                                    # Statistiques TP
                                    moyenne_tp = df_groupe_tp["TP"].mean()
                                    variance_tp = df_groupe_tp["TP"].var()
                                    ecart_type_tp = df_groupe_tp["TP"].std()
                                    
                                    st.metric("Moyenne TP", f"{moyenne_tp:.2f}")
                                    st.metric("Variance TP", f"{variance_tp:.2f}")
                                    st.metric("Écart-type TP", f"{ecart_type_tp:.2f}")
                    else:
                        st.warning(f"Aucune donnée de notes DS disponible pour le groupe {groupe_selectionne}")
                else:
                    st.warning(f"Colonne 'DS' non trouvée pour le groupe {groupe_selectionne}")
        else:
            st.warning("Aucun groupe trouvé dans les données.")
    else:
        st.warning("La colonne 'GR' (groupe) n'existe pas dans les données.")