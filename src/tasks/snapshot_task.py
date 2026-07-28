import datetime
from src.config import ALERT_WEBHOOK_URL, SYSTEM_LOG_WEBHOOK_URL, COMMODITY_TARGETS
from src.modules.fetcher import fetch_commodity_data
from src.modules.state_manager import load_state, save_state, check_and_reset_day
from src.modules.discord_notifier import send_webhook

def run_snapshot():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    today_str = now_utc.strftime("%Y-%m-%d")
    time_str = now_utc.strftime("%H:%M")

    state = check_and_reset_day(load_state(), today_str)
    market_data = fetch_commodity_data()

    if not market_data:
        print("[WARN] データが取得できなかったためスナップショットを中断します。")
        return

    current_prices = {}
    for sym, data in market_data.items():
        current_prices[sym] = data["price"]
        if sym not in state["opens"]:
            state["opens"][sym] = data["open"]

    state["snapshots"][time_str] = current_prices
    save_state(state)
    print(f"[INFO] スナップショット保存完了 [{time_str}]")
