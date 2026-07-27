import pandas as pd

def evaluate_signal_score(df: pd.DataFrame, long_pct: float, short_pct: float) -> tuple[int, str, list[str]]:
    score = 0
    reasons = []
    
    latest = df.iloc[-1]
    
    if "SMA20" in df.columns and "SMA50" in df.columns:
        if latest["Close"] > latest["SMA20"] and latest["SMA20"] > latest["SMA50"]:
            score += 30
            reasons.append("🟢 パーフェクトオーダー形成 (+30)")
        elif latest["Close"] < latest["SMA20"] and latest["SMA20"] < latest["SMA50"]:
            score -= 30
            reasons.append("🔴 下降パーフェクトオーダー (-30)")

    if "RSI" in df.columns:
        rsi = latest["RSI"]
        if rsi <= 30:
            score += 25
            reasons.append(f"🟢 RSI売られすぎ圏 (RSI: {rsi:.1f}) (+25)")
        elif rsi >= 70:
            score -= 25
            reasons.append(f"🔴 RSI買われすぎ圏 (RSI: {rsi:.1f}) (-25)")
        else:
            reasons.append(f"⚪ RSI中立域 (RSI: {rsi:.1f}) (0)")

    if long_pct >= 75.0:
        score -= 20
        reasons.append(f"⚠️ ロング極端偏重({long_pct:.1f}%) -> 投げ売り警戒 (-20)")
    elif short_pct >= 75.0:
        score += 20
        reasons.append(f"🔥 ショート極端偏重({short_pct:.1f}%) -> 踏み上げ期待 (+20)")

    if score >= 40:
        signal = "強気 (BULLISH)"
    elif score <= -40:
        signal = "弱気 (BEARISH)"
    else:
        signal = "中立 (NEUTRAL)"
        
    return score, signal, reasons
