import argparse
import json
import os
from datetime import datetime

from src.config import (
    JST,
    RANKING_WEBHOOK_URL,
    REPORT_WEBHOOK_URL,
    STATE_FILE_PATH,
    SYSTEM_LOG_WEBHOOK_URL,
    TICKERS,
)
from src.discord import send_discord_message
from src.modules.fetcher import get_commodity_data
from src.reporters import (
    generate_am_report_embed,
    generate_pm_report_embed,
    generate_volatility_time_ranking,
)


def load_state():
    if os.path.exists(STATE_FILE_PATH):
        try:
            with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE_PATH), exist_ok=True)
    with open(STATE_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def run_snapshot():
    now_jst = datetime.now(JST)
    date_str = now_jst.strftime("%Y-%m-%d")
    time_str = now_jst.strftime("%H:%M")

    prices, usdjpy = get_commodity_data()
    if not prices:
        print("[WARN] 価格データが取得できなかったためスキップします。")
        return

    state = load_state()

    # 日付更新時の初期化
    if state.get("date") != date_str:
        state = {"date": date_str, "opens": prices, "snapshots": {}}

    if "snapshots" not in state:
        state["snapshots"] = {}

    state["snapshots"][time_str] = prices

    hour = now_jst.hour
    minute = now_jst.minute

    # 前場サマリー（12:00〜12:15）
    if hour == 12 and minute < 15:
        state["am_prices"] = prices
        embed = generate_am_report_embed(state, usdjpy)
        send_discord_message(REPORT_WEBHOOK_URL, embed=embed)

        vol_ranking = generate_volatility_time_ranking(state, "前場サマリー")
        send_discord_message(RANKING_WEBHOOK_URL, message=vol_ranking)

    # 後場サマリー（23:50〜23:59）
    elif hour == 23 and minute >= 50:
        embed = generate_pm_report_embed(state, usdjpy)
        send_discord_message(REPORT_WEBHOOK_URL, embed=embed)

        vol_ranking = generate_volatility_time_ranking(state, "後場サマリー")
        send_discord_message(RANKING_WEBHOOK_URL, message=vol_ranking)

    save_state(state)

    # 15分ごとのスナップショット保存完了ログを送信
    count = len(prices)
    total_tickers = len(TICKERS)
    log_msg = f"✅ `[{date_str} {time_str}]` スナップショット保存完了 (円換算済み / 取得数: {count}/{total_tickers})"
    send_discord_message(SYSTEM_LOG_WEBHOOK_URL, message=log_msg)


def run_daily_report():
    """デイリーレポート送信ジョブ"""
    prices, usdjpy = get_commodity_data()
    state = load_state()
    if not state.get("snapshots") and prices:
        now_jst = datetime.now(JST)
        state = {
            "date": now_jst.strftime("%Y-%m-%d"),
            "opens": prices,
            "snapshots": {now_jst.strftime("%H:%M"): prices},
        }

    embed = generate_pm_report_embed(state, usdjpy)
    send_discord_message(REPORT_WEBHOOK_URL, embed=embed)


def run_ranking():
    """ランキング送信ジョブ"""
    state = load_state()
    vol_ranking = generate_volatility_time_ranking(state, "日次サマリー")
    send_discord_message(RANKING_WEBHOOK_URL, message=vol_ranking)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["snapshot", "daily_report", "ranking"],
        default="snapshot",
    )
    args = parser.parse_args()

    if args.mode == "snapshot":
        run_snapshot()
    elif args.mode == "daily_report":
        run_daily_report()
    elif args.mode == "ranking":
        run_ranking()
