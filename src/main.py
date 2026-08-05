import os
import json
from datetime import datetime
import zoneinfo
import pandas as pd
import yfinance as yf

# 1. 明示的に日本時間（JST）のタイムゾーンを定義
JST = zoneinfo.ZoneInfo("Asia/Tokyo")

# 監視対象のティッカーリスト（16銘柄）
TICKERS = [
    # エネルギー
    "CL=F", "BZ=F", "NG=F", "HO=F", "RB=F",
    # 貴金属・非鉄金属
    "GC=F", "SI=F", "HG=F", "PL=F", "PA=F", "ALI=F",
    # ソフトコモディティ・農産物 (CBOTコード)
    "KC=F", "SB=F", "ZC=F", "ZW=F", "ZS=F"
]

STATE_FILE_PATH = "data/state.json"

def get_commodity_data():
    """
    yfinanceからデータを取得する関数
    銘柄ごとに最新の有効価格（NaNでないデータ）を確実に取得する
    """
    try:
        df = yf.download(TICKERS, period="5d", interval="1m", progress=False)
        if df.empty:
            print("[WARN] データが取得できませんでした。")
            return {}
        
        close_df = df["Close"]
        latest_prices = {}
        
        for ticker in TICKERS:
            # MultiIndex構造かどうかの判定と取得
            if isinstance(close_df.columns, pd.MultiIndex):
                ticker_series = close_df.xs(ticker, level=1, axis=1) if ticker in close_df.columns.levels[1] else None
            else:
                ticker_series = close_df[ticker] if ticker in close_df.columns else None

            if ticker_series is not None:
                # NaNを除外した上で一番最後の有効データ（最新価格）を取得
                valid_series = ticker_series.dropna()
                if not valid_series.empty:
                    latest_prices[ticker] = float(valid_series.iloc[-1])
                
        return latest_prices
    except Exception as e:
        print(f"[ERROR] データ取得中にエラーが発生しました: {e}")
        return {}

def run_snapshot():
    now_jst = datetime.now(JST)
    date_str = now_jst.strftime("%Y-%m-%d")
    time_str = now_jst.strftime("%H:%M")

    print(f"[INFO] スナップショット実行開始 (JST: {date_str} {time_str})")

    prices = get_commodity_data()
    if not prices:
        print("[WARN] 取得できる価格データがないため処理を中断します。")
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

    print(f"[INFO] スナップショット保存完了 [{time_str}]")

if __name__ == "__main__":
    run_snapshot()
