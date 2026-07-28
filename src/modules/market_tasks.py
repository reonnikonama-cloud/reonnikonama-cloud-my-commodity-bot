import discord
from src.modules.oanda_client import fetch_oanda_candles, fetch_usdjpy_rate

async def execute_anomaly_check(channel: discord.TextChannel, df_m15):
    """
    15分ごとの急変チェック
    ・直近15分での一定以上の価格変動
    ・RSIの過熱感（70以上 / 30以下）
    """
    if df_m15.empty or len(df_m15) < 2:
        return

    latest = df_m15.iloc[-1]
    prev = df_m15.iloc[-2]
    
    price_change = float(latest["Close"] - prev["Close"])
    pct_change = (price_change / prev["Close"]) * 100
    rsi = float(latest["RSI"]) if "RSI" in latest and not pd.isna(latest["RSI"]) else 50.0

    # アラート条件: 15分で1%以上の変動、またはRSIの過熱
    is_anomaly = abs(pct_change) >= 1.0 or rsi >= 70 or rsi <= 30

    if is_anomaly:
        direction = "🚀 急騰" if pct_change > 0 else "📉 急落"
        embed = discord.Embed(
            title=f"⚠️ 原油価格 急変アラート ({direction})",
            color=0xe74c3c if pct_change < 0 else 0x2ecc71
        )
        embed.add_field(name="現在価格", value=f"${latest['Close']:.2f}", inline=True)
        embed.add_field(name="15分前比", value=f"{pct_change:+.2f}% (${price_change:+.2f})", inline=True)
        embed.add_field(name="RSI(14)", value=f"{rsi:.1f}", inline=True)
        
        await channel.send(embed=embed)

async def execute_hourly_report(channel: discord.TextChannel):
    """毎時の定時レポート送信"""
    df_h1 = fetch_oanda_candles("WTIC_USD", 50, "H1")
    usdjpy = fetch_usdjpy_rate()

    if df_h1.empty:
        return

    latest = df_h1.iloc[-1]
    sma20 = float(latest["SMA20"])
    sma50 = float(latest["SMA50"])
    trend = "📈 上昇トレンド" if sma20 > sma50 else "📉 下降トレンド"

    embed = discord.Embed(
        title="📊 WTI原油 毎時レポート",
        color=0x3498db
    )
    embed.add_field(name="現在価格 (WTI)", value=f"${latest['Close']:.2f}", inline=True)
    embed.add_field(name="為替 (USD/JPY)", value=f"¥{usdjpy:.2f}", inline=True)
    embed.add_field(name="トレンド判定 (SMA20/50)", value=trend, inline=False)
    
    await channel.send(embed=embed)

async def execute_daily_report(channel: discord.TextChannel, state: dict):
    """23:55 のデイリーサマリー"""
    df_h1 = fetch_oanda_candles("WTIC_USD", 50, "H1")
    if df_h1.empty:
        return

    latest_close = float(df_h1["Close"].iloc[-1])
    day_open = state.get("day_open", latest_close)
    day_change = latest_close - day_open
    day_pct = (day_change / day_open) * 100 if day_open else 0.0

    embed = discord.Embed(
        title="🌙 本日の原油市場 デイリーサマリー",
        color=0xf1c40f
    )
    embed.add_field(name="本日始値", value=f"${day_open:.2f}", inline=True)
    embed.add_field(name="本日終値", value=f"${latest_close:.2f}", inline=True)
    embed.add_field(name="日中騰落率", value=f"{day_pct:+.2f}% (${day_change:+.2f})", inline=False)

    await channel.send(embed=embed)
