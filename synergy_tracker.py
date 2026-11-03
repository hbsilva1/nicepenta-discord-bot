import json
import os

SYNERGY_FILE = os.path.join(os.path.dirname(__file__), "synergy_db.json")

def load_synergy():
    if os.path.exists(SYNERGY_FILE):
        try:
            with open(SYNERGY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_synergy(data):
    try:
        with open(SYNERGY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar synergy_db: {e}")

def get_synergy_key(discord_ids):
    # Chave única ordenada para o grupo de jogadores (ex: "189010116379541504_219156433139269632")
    return "_".join(sorted(str(i) for i in discord_ids))

def record_synergy(discord_ids, win: bool):
    if len(discord_ids) < 2:
        return None
    db = load_synergy()
    key = get_synergy_key(discord_ids)
    if key not in db:
        db[key] = {"wins": 0, "losses": 0}
    if win:
        db[key]["wins"] += 1
    else:
        db[key]["losses"] += 1
    save_synergy(db)
    
    total = db[key]["wins"] + db[key]["losses"]
    wr = round((db[key]["wins"] / total) * 100, 1) if total > 0 else 0
    return db[key]["wins"], db[key]["losses"], wr, total
