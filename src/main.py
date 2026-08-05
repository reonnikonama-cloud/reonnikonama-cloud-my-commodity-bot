import os
import json
from datetime import datetime

from .config import JST, REPORT_WEBHOOK_URL, RANKING_WEBHOOK_URL, STATE_FILE_PATH
from .discord import send_discord_message
from .fetcher import get_commodity_data
from .reporters import generate_am_report, generate_pm_report, generate_volatility_time_ranking

def run_snapshot():
    now_jst = datetime.now(JST)
    date_str = now_jst.strftime("%Y-%m-%d")
    time_str = now_jst.strftime("%H:%M")

    prices, usdjpy = get_commodity_data()
    if not prices:
        return

    # state.json の読み込み
    state = {}
    if os.path.exists(STATE_FILE_PATH):
        try:
            with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
                state = json.load(f)
        except json.JSONDecodeError:
            state = {}

    # 日付更新時の初期化
    if state.get("date") != date_str:
        state = {
            "date": date_str,
            "opens": prices,
            "snapshots": {}
        }

    if "snapshots" not in state:
        state["snapshots"] = {}
        
    state["snapshots"][time_str] = prices

    # -------------------------------------------------------------
    # 時間帯別レポート・ランキング判定（前場：12:00付近 / 後場：23:50以降）
    # -------------------------------------------------------------
    hour = now_jst.hour
    minute = now_jst.minute

    # 前場サマリー（12:00〜12:15の間）
    if hour == 12 and minute < 15:
        state["am_prices"] = prices
        
        # 市況レポートチャンネル
        report = generate_am_report(state, usdjpy)
        send_discord_message(REPORT_WEBHOOK_URL, report)
        
        # 各銘柄別ボラティリティ時間帯ランキング
        vol_ranking = generate_volatility_time_ranking(state, "前場サマリー")
        send_discord_message(RANKING_WEBHOOK_URL, vol_ranking)

    # 後場サマリー（23:50〜23:59の間）
    elif hour == 23 and minute >= 50:
        # 市況レポートチャンネル
        report = generate_pm_report(state, usdjpy)
        send_discord_message(REPORT_WEBHOOK_URL, report)

        # 各銘柄別ボラティリティ時間帯ランキング
        vol_ranking = generate_volatility_time_ranking(state, "後場サマリー")
        send_discord_message(RANKING_WEBHOOK_URL, vol_ranking)

    # 状態の最終保存
    os.makedirs(os.path.dirname(STATE_FILE_PATH), exist_ok=True)
    with open(STATE_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_snapshot()
