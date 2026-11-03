import urllib.request
import json
import os

CACHE_FILE = os.path.join(os.path.dirname(__file__), "champions_cache.json")

def update_champion_cache():
    try:
        v_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        v = json.loads(urllib.request.urlopen(v_url, timeout=5).read().decode('utf-8'))[0]
        c_url = f"https://ddragon.leagueoflegends.com/cdn/{v}/data/pt_BR/champion.json"
        data = json.loads(urllib.request.urlopen(c_url, timeout=8).read().decode('utf-8'))["data"]
        
        cache = {
            "version": v,
            "champions": {}
        }
        for c_id, c_info in data.items():
            cache["champions"][int(c_info["key"])] = {
                "id": c_id,
                "name": c_info["name"],
                "title": c_info["title"],
                "tags": c_info["tags"],
                "icon": f"https://ddragon.leagueoflegends.com/cdn/{v}/img/champion/{c_id}.png"
            }
            
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        print(f"[CACHE] {len(cache['champions'])} campeões cacheados na versão {v}!")
        return cache
    except Exception as e:
        print(f"Erro ao cachear campeões: {e}")
        return {}

if __name__ == "__main__":
    update_champion_cache()
