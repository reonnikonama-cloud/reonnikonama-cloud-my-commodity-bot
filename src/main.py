import os
import json
from datetime import datetime
import zoneinfo
import pandas as pd  # ← これを追加！
import yfinance as yf

# 1. 明示的に日本時間（JST）のタイムゾーンを定義
JST = zoneinfo.ZoneInfo("Asia/Tokyo")

# 監視対象のティッカーリスト（例）
TICKERS = [
    "CL=F", "BZ=F", "NG=F", "HO=F", "RB=F",
    "GC=F", "SI=F", "HG=F", "PL=F", "PA=F",
    "KC=F", "SB=F", "C=F", "W=F", "S=F"
]

STATE_FILE_PATH = "data/state.json"

def get_commodity_data():
    """
    yfinanceからデータを取得する関数
    period='1d' だとエラー（possibly delisted）になりやすいため '5d' で取得して最新行を採用する
    """
    try:
        # periodを5dにすることで取得失敗率を大幅に低減
        df = yf.download(TICKERS, period="5d", interval="1m", progress=False)
        if df.empty:
            print("[WARN] データが取得できませんでした。")
            return {}
        
        # 最新の終値（Close）を取得
        latest_prices = {}
        close_df = df["Close"].iloc[-1]
        
        for ticker in TICKERS:
            if ticker in close_df and not pd.isna(close_df[ticker]):
                latest_prices[ticker] = float(close_df[ticker])
                
        return latest_prices
    except Exception as e:
        print(f"[ERROR] データ取得中にエラーが発生しました: {e}")
        return {}

def run_snapshot():
    # 2. 現在時刻を必ず日本標準時（JST）で取得
    now_jst = datetime.now(JST)
    date_str = now_jst.strftime("%Y-%m-%d")
    time_str = now_jst.strftime("%H:%M")

    print(f"[INFO] スナップショット実行開始 (JST: {date_str} {time_str})")

    # 最新価格の取得
    prices = get_commodity_data()
    if not prices:
        print("[WARN] 取得できる価格データがないため処理を中断します。")
        return

    # state.json の読み込みと更新
    state = {}
    if os.path.exists(STATE_FILE_PATH):
        try:
            with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
                state = json.load(f)
        except json.JSONDecodeError:
            state = {}

    # 日付が変わっていたら新規作成、同じ日なら既存データを更新
    if state.get("date") != date_str:
        state = {
            "date": date_str,
            "opens": prices,  # その日の最初の取得価格を始値とする場合
            "snapshots": {}
        }

    # JST時刻のキー（例: "08:57"）でスナップショットを保存
    if "snapshots" not in state:
        state["snapshots"] = {}
        
    state["snapshots"][time_str] = prices

    # ファイルへ書き込み
    os.makedirs(os.path.dirname(STATE_FILE_PATH), exist_ok=True)
    with open(STATE_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    print(f"[INFO] スナップショット保存完了 [{time_str}]")

if __name__ == "__main__":
    run_snapshot()
