import json
import os


PROFILES_DIR = "data/profiles"


def _ensure_dir():
    os.makedirs(PROFILES_DIR, exist_ok=True)


def list_profiles():
    _ensure_dir()
    profiles = []
    for f in os.listdir(PROFILES_DIR):
        if f.endswith(".json"):
            profiles.append(f[:-5])
    return profiles


def create_profile(name):
    _ensure_dir()
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    if os.path.exists(path):
        return False
    data = {
        "name": name,
        "level": 1,
        "xp": 0,
        "stats": {
            "total_kills": 0,
            "total_deaths": 0,
            "matches_won": 0,
            "matches_played": 0,
            "total_damage": 0,
        },
        "unlocks": [],
        "keybindings": {
            "up": "W", "down": "S", "left": "A", "right": "D",
            "shoot": "E", "ability": "Q", "sprint": "LSHIFT", "dodge": "SPACE",
        },
        "settings": {
            "master_volume": 0.8,
            "sfx_volume": 0.9,
            "music_volume": 0.6,
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return True


def load_profile(name):
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(data):
    _ensure_dir()
    path = os.path.join(PROFILES_DIR, f"{data['name']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def delete_profile(name):
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
