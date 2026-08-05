import pandas as pd
import yfinance as yf
from src.config import COMMODITY_TARGETS

def fetch_commodity_data() -> dict:
    """15銘柄の現在値・高値・安値・始値を一括取得"""
    symbols = list(COMMODITY_TARGETS.keys())
    results = {}

    try:
        # period="1d" だと休場日や市場時間外に「no price data found」エラーになるため "5d" に変更
        data = yf.download(tickers=symbols, period="5d", interval="1m", progress=False)
        
        for sym in symbols:
            try:
                df = data.xs(sym, level=1, axis=1) if isinstance(data.columns, pd.MultiIndex) else data
                df = df.dropna(subset=["Close"])
                
                if not df.empty:
                    # 本日分（最新の日付）のデータのみに絞り込む
                    latest_date = df.index[-1].date()
                    today_df = df[df.index.date == latest_date]
                    
                    if not today_df.empty:
                        results[sym] = {
                            "price": float(today_df["Close"].iloc[-1]),
                            "high": float(today_df["High"].max()),
                            "low": float(today_df["Low"].min()),
                            "open": float(today_df["Open"].iloc[0]),
                        }
            except Exception as e:
                print(f"[ERROR] 銘柄取得失敗 ({sym}): {e}")
                
    except Exception as e:
        print(f"[CRITICAL] データ取得処理全体でエラー: {e}")

    return results
