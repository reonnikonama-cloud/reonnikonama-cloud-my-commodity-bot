import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "state.json"

def load_state() -> dict:
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        return {"day_open": None, "m15_history": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"day_open": None, "m15_history": []}

def save_state(state: dict):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def reset_daily_state():
    """23:55のデイリー送信後にデータを初期化"""
    state = load_state()
    state["m15_history"] = []
    # day_openは00:00まで念のため残すかクリア
    save_state(state)
