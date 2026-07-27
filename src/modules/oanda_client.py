import requests
import pandas as pd
from src.config import BASE_URL, HEADERS

def fetch_usdjpy_rate() -> float:
    url = f"{BASE_URL}/instruments/USD_JPY/candles"
    params = {"count": 1, "granularity": "M1", "price": "M"}
    try:
        res = requests.get(url, headers=HEADERS, params=params)
        if res.status_code == 200:
            candles = res.json().get("candles", [])
            if candles:
                return float(candles[-1]["mid"]["c"])
    except Exception as e:
        print(f"USDJPY Fetch Error: {e}")
    return 155.0

def fetch_oanda_candles(instrument: str, count: int, granularity: str) -> pd.DataFrame:
    url = f"{BASE_URL}/instruments/{instrument}/candles"
    params = {"count": count, "granularity": granularity, "price": "M"}
    res = requests.get(url, headers=HEADERS, params=params)
    if res.status_code != 200:
        return pd.DataFrame()
        
    candles = res.json().get("candles", [])
    parsed = [{
        "Time": pd.to_datetime(c["time"]),
        "Open": float(c["mid"]["o"]),
        "High": float(c["mid"]["h"]),
        "Low": float(c["mid"]["l"]),
        "Close": float(c["mid"]["c"]),
        "Volume": int(c["volume"])
    } for c in candles if c["complete"]]
    
    df = pd.DataFrame(parsed)
    if not df.empty:
        df.set_index("Time", inplace=True)
        df["SMA20"] = df["Close"].rolling(20).mean()
        df["SMA50"] = df["Close"].rolling(50).mean()
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df["RSI"] = 100 - (100 / (1 + (gain / loss)))
        tr = pd.concat([df["High"] - df["Low"], (df["High"] - df["Close"].shift()).abs(), (df["Low"] - df["Close"].shift()).abs()], axis=1).max(axis=1)
        df["ATR"] = tr.rolling(14).mean()
    return df
