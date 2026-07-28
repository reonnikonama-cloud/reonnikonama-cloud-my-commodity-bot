import pandas as pd
import yfinance as yf
from src.config import COMMODITY_TARGETS

def fetch_commodity_data() -> dict:
    """15銘柄の現在値・高値・安値・始値を一括取得"""
    symbols = list(COMMODITY_TARGETS.keys())
    results = {}

    try:
        data = yf.download(tickers=symbols, period="1d", interval="1m", progress=False)
        for sym in symbols:
            try:
                df = data.xs(sym, level=1, axis=1) if isinstance(data.columns, pd.MultiIndex) else data
                df = df.dropna(how="all")
                if not df.empty:
                    results[sym] = {
                        "price": float(df["Close"].iloc[-1]),
                        "high": float(df["High"].max()),
                        "low": float(df["Low"].min()),
                        "open": float(df["Open"].iloc[0]),
                    }
            except Exception as e:
                print(f"[ERROR] 銘柄取得失敗 ({sym}): {e}")
    except Exception as e:
        print(f"[CRITICAL] データ取得処理全体でエラー: {e}")

    return results
