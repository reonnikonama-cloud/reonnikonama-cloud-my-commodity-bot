import os
import json
import urllib.request
from datetime import datetime
import zoneinfo
import pandas as pd
import yfinance as yf

# 1. 日本時間（JST）のタイムゾーン定義
JST = zoneinfo.ZoneInfo("Asia/Tokyo")

# GitHub Secretsから受け取る環境変数
SYSTEM_LOG_WEBHOOK_URL = os.getenv("SYSTEM_LOG_WEBHOOK_URL", "")

# 監視対象のティッカーリスト（16銘柄）
TICKERS = [
    # エネルギー
    "CL=F", "BZ=F", "NG=F", "HO=F", "RB=F",
    # 貴金属・非鉄金属
    "GC=F", "SI=F", "HG=F", "PL=F", "PA=F", "ALI=F",
    # ソフトコモディティ・農産物 (CBOTコード)
    "KC=F", "SB=F", "ZC=F", "ZW=F", "ZS=F"
]

# セント単位で取引されている農産物銘柄（ドルに直すため100で割る対象）
CENT_BASED_TICKERS = {"KC=F", "SB=F", "ZC=F", "ZW=F", "ZS=F"}

STATE_FILE_PATH = "data/state.json"

def send_discord_log(message: str):
    """DiscordのWebHook宛にログメッセージを送信する"""
    if not SYSTEM_LOG_WEBHOOK_URL:
        print("[WARN] SYSTEM_LOG_WEBHOOK_URL が設定されていないためDiscord通知をスキップします。")
        return

    payload = {"content": message}
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        req = urllib.request.Request(
            SYSTEM_LOG_WEBHOOK_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req) as res:
            if res.status in (200, 204):
                print("[INFO] Discord通知送信成功")
            else:
                print(f"[WARN] Discord通知失敗 (Status: {res.status})")
    except Exception as e:
        print(f"[ERROR] Discord通知送信エラー: {e}")

def get_usd_jpy_rate(df) -> float:
    """ドル円（JPY=X）の最新為替レートを取得"""
    try:
        close_df = df["Close"]
        if isinstance(close_df.columns, pd.MultiIndex):
            usdjpy_series = close_df.xs("JPY=X", level=1, axis=1) if "JPY=X" in close_df.columns.levels[1] else None
        else:
            usdjpy_series = close_df["JPY=X"] if "JPY=X" in close_df.columns else None

        if usdjpy_series is not None:
            valid_usdjpy = usdjpy_series.dropna()
            if not valid_usdjpy.empty:
                rate = float(valid_usdjpy.iloc[-1])
                print(f"[INFO] 適用為替レート (USD/JPY): {rate:.2f} 円")
                return rate
    except Exception as e:
        print(f"[WARN] ドル円レートの取得に失敗しました: {e}")
    
    print("[WARN] 為替レートが取得できないためデフォルト値 155.0 円を使用します。")
    return 155.0  # 取得失敗時のフォールバック値

def get_commodity_data():
    """yfinanceから最新の有効データを取得し円換算して返す"""
    fetch_tickers = TICKERS + ["JPY=X"]
    try:
        df = yf.download(fetch_tickers, period="5d", interval="1m", progress=False)
        if df.empty:
            print("[WARN] データが取得できませんでした。")
            return {}
        
        # ドル円レートの取得
        usdjpy = get_usd_jpy_rate(df)
        
        close_df = df["Close"]
        latest_prices = {}
        
        for ticker in TICKERS:
            if isinstance(close_df.columns, pd.MultiIndex):
                ticker_series = close_df.xs(ticker, level=1, axis=1) if ticker in close_df.columns.levels[1] else None
            else:
                ticker_series = close_df[ticker] if ticker in close_df.columns else None

            if ticker_series is not None:
                valid_series = ticker_series.dropna()
                if not valid_series.empty:
                    raw_price = float(valid_series.iloc[-1])
                    
                    # セント表記の銘柄はドル表記（÷100）に補正してから円換算
                    if ticker in CENT_BASED_TICKERS:
                        price_usd = raw_price / 100.0
                    else:
                        price_usd = raw_price

                    # 日本円換算（小数第2位までに丸め）
                    price_jpy = round(price_usd * usdjpy, 2)
                    latest_prices[ticker] = price_jpy
                
        return latest_prices
    except Exception as e:
        err_msg = f"⚠️ **[ERROR]** データ取得処理でエラーが発生しました: {e}"
        print(err_msg)
        send_discord_log(err_msg)
        return {}

def run_snapshot():
    now_jst = datetime.now(JST)
    date_str = now_jst.strftime("%Y-%m-%d")
    time_str = now_jst.strftime("%H:%M")

    print(f"[INFO] スナップショット実行開始 (JST: {date_str} {time_str})")

    prices = get_commodity_data()
    if not prices:
        warn_msg = f"⚠️ **[WARN]** [{date_str} {time_str}] 取得できる価格データがないため処理を中断しました。"
        print(warn_msg)
        send_discord_log(warn_msg)
        return

    state = {}
    if os.path.exists(STATE_FILE_PATH):
        try:
            with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
                state = json.load(f)
        except json.JSONDecodeError:
            state = {}

    if state.get("date") != date_str:
        state = {
            "date": date_str,
            "opens": prices,
            "snapshots": {}
        }

    if "snapshots" not in state:
        state["snapshots"] = {}
        
    state["snapshots"][time_str] = prices

    os.makedirs(os.path.dirname(STATE_FILE_PATH), exist_ok=True)
    with open(STATE_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    success_msg = f"✅ [{date_str} {time_str}] スナップショット保存完了（円換算済み / 取得数: {len(prices)}/{len(TICKERS)}）"
    print(success_msg)
    send_discord_log(success_msg)

if __name__ == "__main__":
    run_snapshot()
