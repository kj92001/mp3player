import json
import os

CONFIG_FILE = "player_config.json"

def save_settings(playlist_paths, current_index, volume, window_geometry=None):
    """플레이리스트 정보와 창 위치/크기 정보를 json 파일로 저장합니다."""
    data = {
        "playlist": playlist_paths,
        "current_index": current_index,
        "volume": volume,
        "window_geometry": window_geometry  # 창 위치/크기 데이터 추가
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_settings():
    """저장된 json 파일에서 데이터를 읽어오며, 데이터가 없으면 기본값을 반환합니다."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 이전 버전의 json 파일에 window_geometry가 없을 경우를 위한 처리
                if "window_geometry" not in data:
                    data["window_geometry"] = None
                return data
        except Exception:
            pass
    return {"playlist": [], "current_index": -1, "volume": 70, "window_geometry": None}


