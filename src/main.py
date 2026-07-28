import os
import sys
from discord import SyncWebhook, Embed
from src.config import REPORT_WEBHOOK_URL, ALERT_WEBHOOK_URL
from src.modules.oanda_client import fetch_oanda_candles, fetch_usdjpy_rate

def send_webhook(webhook_url: str, embed: Embed):
    """Webhookに埋め込みメッセージを送信する共通関数"""
    if not webhook_url:
        print("Webhook URLが設定されていないためスキップします。")
        return
    try:
        webhook = SyncWebhook.from_url(webhook_url)
        webhook.send(embed=embed)
        print("Webhook 送信成功！")
    except Exception as e:
        print(f"Webhook 送信エラー: {e}")

def run_task():
    # データを取得（yfinanceベース）
    df_m15 = fetch_oanda_candles("WTIC_USD", 20, "M15")
    df_h1 = fetch_oanda_candles("WTIC_USD", 50, "H1")
    usdjpy = fetch_usdjpy_rate()

    if df_h1.empty:
        print("データ取得に失敗したため終了します。")
        return

    latest_h1 = df_h1.iloc[-1]
    
    # -----------------------------------------------
    # 1. 定期レポート送信 (REPORT_WEBHOOK_URL)
    # -----------------------------------------------
    sma20 = float(latest_h1.get("SMA20", 0))
    sma50 = float(latest_h1.get("SMA50", 0))
    trend = "📈 上昇トレンド" if sma20 > sma50 else "📉 下降トレンド"

    report_embed = Embed(
        title="📊 コモディティ市況レポート (WTI原油)",
        color=0x3498db
    )
    report_embed.add_field(name="現在価格 (WTI)", value=f"${latest_h1['Close']:.2f}", inline=True)
    report_embed.add_field(name="為替 (USD/JPY)", value=f"¥{usdjpy:.2f}", inline=True)
    report_embed.add_field(name="トレンド判定", value=trend, inline=False)

    send_webhook(REPORT_WEBHOOK_URL, report_embed)

    # -----------------------------------------------
    # 2. 急変チェック・アラート送信 (ALERT_WEBHOOK_URL)
    # -----------------------------------------------
    if not df_m15.empty and len(df_m15) >= 2:
        latest_m15 = df_m15.iloc[-1]
        prev_m15 = df_m15.iloc[-2]
        
        price_change = float(latest_m15["Close"] - prev_m15["Close"])
        pct_change = (price_change / prev_m15["Close"]) * 100

        # 15分で1%以上の急変動があればアラート送信
        if abs(pct_change) >= 1.0:
            direction = "🚀 急騰" if pct_change > 0 else "📉 急落"
            alert_embed = Embed(
                title=f"🚨 コモディティ価格急変アラート ({direction})",
                color=0xe74c3c if pct_change < 0 else 0x2ecc71
            )
            alert_embed.add_field(name="現在価格", value=f"${latest_m15['Close']:.2f}", inline=True)
            alert_embed.add_field(name="15分前比", value=f"{pct_change:+.2f}% (${price_change:+.2f})", inline=True)
            
            send_webhook(ALERT_WEBHOOK_URL, alert_embed)

if __name__ == "__main__":
    run_task()
