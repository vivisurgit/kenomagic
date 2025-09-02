import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import os

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    )
}

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

FDJ_RESULT_URL = "https://www.fdj.fr/jeux-de-tirage/keno/resultats"
SECRETS_URL = "https://www.secretsdujeu.com/page/jeux_keno_statistiques.html"

DRAW_HISTORY_FILE = os.path.join(DATA_DIR, "draw_history.json")
STATS_HISTORY_FILE = os.path.join(DATA_DIR, "stats_history.json")

def fetch_last_draw():
    try:
        r = requests.get(FDJ_RESULT_URL, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Tirage midi
        draw_midi_div = soup.find("div", id="result-wrapper-grid-2")
        draw_soir_div = soup.find("div", id="result-wrapper-grid-3")

        draws = []
        for div, ttype in [(draw_midi_div, "midi"), (draw_soir_div, "soir")]:
            if div:
                numbers = [int(li.get_text(strip=True)) for li in div.find_all("li") if li.get_text(strip=True).isdigit()]
                if numbers:
                    draws.append({
                        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": ttype,
                        "numbers": numbers[:20]
                    })
        return draws
    except Exception as e:
        print("Erreur lors de la récupération des tirages :", e)
        return []

def fetch_stats():
    try:
        r = requests.get(SECRETS_URL, headers=HEADERS, timeout=10)
        r.raise_for_status()
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", {"id": "stats"})
        if table is None:
            print("Impossible de trouver la table des stats")
            return []

        df = pd.read_html(str(table))[0]
        df.columns = [str(c).strip() for c in df.columns]

        return {
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "table": df.to_dict(orient="records")
        }
    except Exception as e:
        print("Erreur lors de la récupération des stats :", e)
        return []

def load_history(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(file_path, data):
    history = load_history(file_path)
    history.append(data)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

def main():
    draws = fetch_last_draw()
    if draws:
        for d in draws:
            save_history(DRAW_HISTORY_FILE, d)
        print(f"{len(draws)} tirages ajoutés à l'historique")
    else:
        print("Aucun tirage disponible")

    stats = fetch_stats()
    if stats:
        save_history(STATS_HISTORY_FILE, stats)
        print("Statistiques ajoutées à l'historique")
    else:
        print("Aucune stats disponible")

if __name__ == "__main__":
    main()
