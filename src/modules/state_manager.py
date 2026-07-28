import os
import json
import datetime

STATE_FILE = "data/state.json"

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"date": "", "opens": {}, "snapshots": {}}

def save_state(state: dict):
    os.makedirs("data", exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def check_and_reset_day(state: dict, today_str: str) -> dict:
    """日付変更を検知して状態をリセット"""
    if state.get("date") != today_str:
        print(f"[INFO] 日付更新検知: {state.get('date')} -> {today_str}")
        return {"date": today_str, "opens": {}, "snapshots": {}}
    return state
