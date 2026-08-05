import pandas as pd
import yfinance as yf

from src.config import TICKERS, CENT_BASED_TICKERS, SYSTEM_LOG_WEBHOOK_URL
from src.discord import send_discord_message

def get_usd_jpy_rate(df) -> float:
    """ドル円（JPY=X）の最新為替レートを取得"""
    try:
        close_df = df["Close"]
        usdjpy_series = close_df.xs("JPY=X", level=1, axis=1) if isinstance(close_df.columns, pd.MultiIndex) else close_df["JPY=X"]
        valid_usdjpy = usdjpy_series.dropna()
        if not valid_usdjpy.empty:
            return float(valid_usdjpy.iloc[-1])
    except Exception:
        pass
    return 155.0

def get_commodity_data():
    """yfinanceから最新価格を取得して円換算"""
    fetch_tickers = TICKERS + ["JPY=X"]
    try:
        df = yf.download(fetch_tickers, period="5d", interval="1m", progress=False)
        if df.empty:
            return {}, 155.0
        
        usdjpy = get_usd_jpy_rate(df)
        close_df = df["Close"]
        latest_prices = {}
        
        for ticker in TICKERS:
            ticker_series = close_df.xs(ticker, level=1, axis=1) if isinstance(close_df.columns, pd.MultiIndex) else close_df.get(ticker)
            if ticker_series is not None:
                valid_series = ticker_series.dropna()
                if not valid_series.empty:
                    raw_price = float(valid_series.iloc[-1])
                    price_usd = raw_price / 100.0 if ticker in CENT_BASED_TICKERS else raw_price
                    latest_prices[ticker] = round(price_usd * usdjpy, 2)
                
        return latest_prices, usdjpy
    except Exception as e:
        err_msg = f"⚠️ **[ERROR]** データ取得中に例外が発生しました: {e}"
        print(err_msg)
        send_discord_message(SYSTEM_LOG_WEBHOOK_URL, err_msg)
        return {}, 155.0
