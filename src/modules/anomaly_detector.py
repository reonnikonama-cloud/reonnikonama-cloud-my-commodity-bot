import pandas as pd

def detect_market_anomaly(df_15m: pd.DataFrame, atr_threshold_multiplier: float = 2.5) -> dict | None:
    if df_15m.empty or "ATR" not in df_15m.columns:
        return None
        
    latest = df_15m.iloc[-1]
    candle_range = latest["High"] - latest["Low"]
    atr = latest["ATR"]
    
    if pd.isna(atr) or atr == 0:
        return None

    if candle_range > (atr * atr_threshold_multiplier):
        is_bullish = latest["Close"] > latest["Open"]
        return {
            "is_anomaly": True,
            "direction": "急騰 🚀" if is_bullish else "急落 📉",
            "candle_range": candle_range,
            "atr": atr,
            "current_price": latest["Close"]
        }
        
    return None
