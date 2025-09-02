import streamlit as st
import pandas as pd
import json

DATA_DIR = "data"
DRAW_HISTORY_FILE = f"{DATA_DIR}/draw_history.json"
STATS_HISTORY_FILE = f"{DATA_DIR}/stats_history.json"

st.set_page_config(page_title="Keno Stats", page_icon="🎲", layout="wide")
st.title("🎲 Keno — Stats + Tirages Historiques")

# --- Load history ---
def load_history(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

draw_history = load_history(DRAW_HISTORY_FILE)
stats_history = load_history(STATS_HISTORY_FILE)

# --- Sélection du tirage ---
draw_options = [f"{d['datetime']} - {d['type']}" for d in draw_history]
draw_sel_idx = st.selectbox("Sélectionner un tirage", range(len(draw_options)), format_func=lambda x: draw_options[x]) if draw_options else None
selected_draw = draw_history[draw_sel_idx] if draw_sel_idx is not None else None

# --- Sélection du tableau de stats ---
stats_options = [s['datetime'] for s in stats_history]
stats_sel_idx = st.selectbox("Sélectionner un tableau de statistiques", range(len(stats_options)), format_func=lambda x: stats_options[x]) if stats_options else None
selected_stats = stats_history[stats_sel_idx]['table'] if stats_sel_idx is not None else None

# --- Affichage du tirage sélectionné ---
if selected_draw:
    st.subheader(f"Tirage choisi ({selected_draw['type']})")
    # Affichage sur une seule ligne, formaté
    st.markdown(" | ".join([f"**{n:02d}**" for n in selected_draw['numbers']]))

# --- Affichage du tableau des stats avec colonnes renommées ---
if selected_stats:
    st.subheader("Tableau des stats")
    df_stats = pd.DataFrame(selected_stats)

    # Renommer colonnes si nécessaire (comme dans les versions précédentes)
    new_columns = [
        "Num", "Réussite", "F récente", "F générale", "Écart max", "Écart actu",
        "Écart +fav", "Écart -favorable", "Affin+", "Affin-", "Annoncé+", "Annoncé-",
        "Annonciateur+", "Annonciateur-"
    ]
    if len(df_stats.columns) == len(new_columns):
        df_stats.columns = new_columns

    # Surlignage des numéros du tirage sélectionné
    def highlight_row(row):
        try:
            if selected_draw and int(row["Num"]) in selected_draw['numbers']:
                return ['background-color: #fff59d; font-weight: 600'] * len(row)
        except:
            pass
        return [''] * len(row)

    st.dataframe(df_stats.style.apply(highlight_row, axis=1), use_container_width=True)

# --- Bouton de rafraîchissement manuel ---
if st.button("Scraper maintenant"):
    st.experimental_run_js("window.location.reload();")  # relance l'app pour déclencher update_data.py
