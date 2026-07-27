import discord
from src.modules.oanda_client import fetch_oanda_candles, fetch_usdjpy_rate
from src.modules.chart_generator import generate_chart_image
from src.modules.signal_evaluator import evaluate_signal_score
from src.modules.macro_analyzer import fetch_macro_indicators
from src.modules.anomaly_detector import detect_market_anomaly

async def execute_hourly_report(channel: discord.TextChannel):
    df_h1 = fetch_oanda_candles("WTIC_USD", 100, "H1")
    if df_h1.empty: return
    
    usdjpy = fetch_usdjpy_rate()
    latest_usd = df_h1["Close"].iloc[-1]
    latest_jpy = latest_usd * usdjpy
    
    macro = fetch_macro_indicators()
    score, signal, reasons = evaluate_signal_score(df_h1, 60.0, 40.0)
    chart_path = generate_chart_image(df_h1, "h1_chart.png")
    
    embed = discord.Embed(title="📊 WTI原油 毎時統合レポート", color=0x00ff00 if score >= 0 else 0xff0000)
    embed.add_field(
        name="現在価格", 
        value=f"**${latest_usd:.2f}** / bbl （約 **¥{latest_jpy:,.0f}** / 為替: `{usdjpy:.2f}円`）", 
        inline=False
    )
    embed.add_field(name="総合判定", value=f"**{signal}** (Score: `{score}`)", inline=False)
    embed.add_field(name="マクロ指標連動", value=f"米10年債: `{macro['tnx_change']:+.2f}%` | 金先物: `{macro['gold_change']:+.2f}%`", inline=False)
    embed.add_field(name="根拠・内訳", value="\n".join(reasons), inline=False)
    
    file = discord.File(chart_path, filename="h1_chart.png")
    embed.set_image(url="attachment://h1_chart.png")
    await channel.send(file=file, embed=embed)

async def execute_anomaly_check(channel: discord.TextChannel):
    df_15m = fetch_oanda_candles("WTIC_USD", 30, "M15")
    anomaly = detect_market_anomaly(df_15m)
    
    if anomaly and anomaly["is_anomaly"]:
        usdjpy = fetch_usdjpy_rate()
        price_usd = anomaly["current_price"]
        price_jpy = price_usd * usdjpy
        range_usd = anomaly["candle_range"]
        range_jpy = range_usd * usdjpy
        
        embed = discord.Embed(title="🚨 【緊急】相場急変アラート", color=0xff0000)
        embed.add_field(name="検知方向", value=anomaly["direction"], inline=True)
        embed.add_field(
            name="現在値", 
            value=f"`${price_usd:.2f}` (約 `¥{price_jpy:,.0f}`)", 
            inline=True
        )
        embed.add_field(
            name="15分足値幅", 
            value=f"`${range_usd:.2f}` (約 `¥{range_jpy:,.0f}`) / ATR: `{anomaly['atr']:.2f}`", 
            inline=False
        )
        await channel.send(content="@everyone", embed=embed)
