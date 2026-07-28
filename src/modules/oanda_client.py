import yfinance as yf
import pandas as pd

def fetch_usdjpy_rate() -> float:
    """ドル円の現在レートを取得"""
    try:
        ticker = yf.Ticker("USDJPY=X")
        data = ticker.history(period="1d")
        if not data.empty:
            return float(data["Close"].iloc[-1])
    except Exception as e:
        print(f"USDJPY Fetch Error: {e}")
    return 155.0

def fetch_oanda_candles(instrument: str = "WTIC_USD", count: int = 100, granularity: str = "H1") -> pd.DataFrame:
    """
    WTI原油(CL=F)のローソク足データを yfinance から取得
    """
    interval_map = {
        "M1": "1m",
        "M15": "15m",
        "H1": "1h",
        "D": "1d"
    }
    interval = interval_map.get(granularity, "1h")
    period = "5d" if interval in ["1m", "15m"] else "1mo"

    try:
        df = yf.download(tickers="CL=F", period=period, interval=interval, progress=False)
        if df.empty:
            return pd.DataFrame()

        # MultiIndex カラムの解消
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 列名の統一
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        
        # 移動平均線（トレンド判定用）
        df["SMA20"] = df["Close"].rolling(20).mean()
        df["SMA50"] = df["Close"].rolling(50).mean()
        
        # RSI（買われすぎ・売られすぎ判定用）
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df["RSI"] = 100 - (100 / (1 + (gain / loss)))
        
        # ATR（ボラティリティ・急変検知用）
        tr = pd.concat([
            df["High"] - df["Low"], 
            (df["High"] - df["Close"].shift()).abs(), 
            (df["Low"] - df["Close"].shift()).abs()
        ], axis=1).max(axis=1)
        df["ATR"] = tr.rolling(14).mean()

        return df.tail(count)

    except Exception as e:
        print(f"yfinance Fetch Error: {e}")
        return pd.DataFrame()
