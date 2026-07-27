import sys
import datetime
import zoneinfo
from pathlib import Path
import discord

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DISCORD_TOKEN, REPORT_CHANNEL_ID, ALERT_CHANNEL_ID
from src.modules.oanda_client import fetch_oanda_candles
from src.modules.state_manager import load_state, save_state, reset_daily_state
from src.modules.market_tasks import execute_hourly_report, execute_anomaly_check, execute_daily_report

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name}")
    
    # 日本時間 (JST) の取得
    jst = zoneinfo.ZoneInfo("Asia/Tokyo")
    now_jst = datetime.datetime.now(jst)
    current_hm = now_jst.strftime("%H:%M")
    
    state = load_state()
    report_channel = client.get_channel(REPORT_CHANNEL_ID)
    alert_channel = client.get_channel(ALERT_CHANNEL_ID)

    try:
        # =========================================================
        # 1. 00:00 (日付更新時): 始値のセットのみ（通知なし・データ更新のみ）
        # =========================================================
        if current_hm == "00:00" or state.get("day_open") is None:
            df_m1 = fetch_oanda_candles("WTIC_USD", 1, "M1")
            if not df_m1.empty:
                state["day_open"] = float(df_m1["Close"].iloc[-1])
                print(f"[00:00 Log] Day Open Price Set: ${state['day_open']} (通知スキップ)")
            
            save_state(state)
            await client.close()
            return  # 00:00 はここで処理終了（Discord通知を出さない）

        # =========================================================
        # 2. 23:55: デイリーレポート発行 & データ初期化
        # =========================================================
        if current_hm == "23:55":
            if report_channel:
                await execute_daily_report(report_channel, state)
            reset_daily_state()
            print("[23:55 Log] Daily report sent and state reset successfully.")
            await client.close()
            return

        # =========================================================
        # 3. 通常時 (15分ごとのデータ蓄積 & 急変チェック)
        # =========================================================
        df_m15 = fetch_oanda_candles("WTIC_USD", 30, "M15")
        if not df_m15.empty:
            latest_bar = df_m15.iloc[-1]
            state["m15_history"].append({
                "time": now_jst.strftime("%Y-%m-%d %H:%M"),
                "close": float(latest_bar["Close"]),
                "high": float(latest_bar["High"]),
                "low": float(latest_bar["Low"])
            })
            if alert_channel:
                await execute_anomaly_check(alert_channel, df_m15)

        # =========================================================
        # 4. 毎時0分 (00:00を除く): 定時レポート送信
        # =========================================================
        if now_jst.minute == 0 and report_channel:
            await execute_hourly_report(report_channel)

        # 最新状態を保存
        save_state(state)

    except Exception as e:
        print(f"Execution Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
