import os

# 원래 의도하셨던 순수한 설정 파일 경로 지정
CONFIG_DIR = os.path.expanduser("~/.local/share/my_player")
CONFIG_FILE = os.path.join(CONFIG_DIR, "player_config.json")

def save_settings(playlist_paths, current_index, volume, window_geometry=None):
    import json
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    data = {"playlist": playlist_paths, "current_index": current_index, "volume": volume, "window_geometry": window_geometry}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_settings():
    import json
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "window_geometry" not in data: data["window_geometry"] = None
                return data
        except Exception: pass
    return {"playlist": [], "current_index": -1, "volume": 70, "window_geometry": None}

