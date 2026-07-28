import os
import sys
import json
import datetime
import pandas as pd
import yfinance as yf
from discord import SyncWebhook, Embed

# プロジェクトルートのパス追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import REPORT_WEBHOOK_URL, ALERT_WEBHOOK_URL, RANKING_WEBHOOK_URL, COMMODITY_TARGETS

STATE_FILE = "data/state.json"

# --- 状態管理関数 ---
def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"date": "", "opens": {}, "snapshots": {}}

def save_state(state: dict):
    os.makedirs("data", exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def send_webhook(webhook_url: str, embed: Embed):
    if not webhook_url:
        print("Webhook URL未設定のためスキップします。")
        return
    try:
        webhook = SyncWebhook.from_url(webhook_url)
        webhook.send(embed=embed)
        print("Webhook 送信成功！")
    except Exception as e:
        print(f"Webhook 送信エラー: {e}")

# --- メイン処理 ---
def run_task():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    today_str = now_utc.strftime("%Y-%m-%d")
    time_str = now_utc.strftime("%H:%M")

    state = load_state()

    # 日付切り替わり検知 & クリーンアップ（日付が変わっていたらリセット）
    if state.get("date") != today_str:
        print(f"日付更新検知: {state.get('date')} -> {today_str}")
        state = {
            "date": today_str,
            "opens": {},
            "snapshots": {}
        }

    # 1. 15銘柄の価格データ取得
    symbols = list(COMMODITY_TARGETS.keys())
    print("データ取得中...")
    tickers_data = yf.download(tickers=symbols, period="1d", interval="1m", progress=False)

    current_prices = {}
    high_prices = {}
    low_prices = {}

    for sym in symbols:
        try:
            df = tickers_data.xs(sym, level=1, axis=1) if isinstance(tickers_data.columns, pd.MultiIndex) else tickers_data
            df = df.dropna(how="all")
            if not df.empty:
                latest_close = float(df["Close"].iloc[-1])
                day_high = float(df["High"].max())
                day_low = float(df["Low"].min())
                
                current_prices[sym] = latest_close
                high_prices[sym] = day_high
                low_prices[sym] = day_low

                # 始値の初期登録（その日最初のデータ）
                if sym not in state["opens"]:
                    state["opens"][sym] = float(df["Open"].iloc[0])
        except Exception as e:
            print(f"銘柄取得エラー ({sym}): {e}")

    # 2. 30分スナップショットの蓄積
    state["snapshots"][time_str] = current_prices
    save_state(state)
    print(f"スナップショット保存完了 [{time_str}]")

    # -----------------------------------------------
    # 3. 騰落率ランキング配信 (23:50 UTC 基準)
    # -----------------------------------------------
    changes = []
    for sym, name in COMMODITY_TARGETS.items():
        price = current_prices.get(sym)
        open_price = state["opens"].get(sym)
        if price and open_price:
            pct = ((price - open_price) / open_price) * 100
            changes.append({"symbol": sym, "name": name, "price": price, "pct": pct})

    changes.sort(key=lambda x: x["pct"], reverse=True)

    # 23時台（日次締め前）ならランキング・日次レポートを実行
    if now_utc.hour == 23 and now_utc.minute >= 45:
        # --- 騰落率ランキング Embed ---
        top3 = changes[:3]
        bottom3 = changes[-3:][::-1]

        rank_embed = Embed(title="🏆 本日のコモディティ 騰落率ランキング", color=0xf1c40f)
        
        top_str = "\n".join([f"🥇 **{x['name']}**: `{x['pct']:+.2f}%` (${x['price']:.2f})" if i==0 else
                            f"🥈 **{x['name']}**: `{x['pct']:+.2f}%` (${x['price']:.2f})" if i==1 else
                            f"🥉 **{x['name']}**: `{x['pct']:+.2f}%` (${x['price']:.2f})" for i, x in enumerate(top3)])
        rank_embed.add_field(name="📈 値上がり TOP3", value=top_str or "なし", inline=False)

        bot_str = "\n".join([f"📉 **{x['name']}**: `{x['pct']:+.2f}%` (${x['price']:.2f})" for x in bottom3])
        rank_embed.add_field(name="📉 値下がり TOP3", value=bot_str or "なし", inline=False)

        send_webhook(RANKING_WEBHOOK_URL, rank_embed)

        # --- 激動時間帯（ボラティリティ）解析 ---
        max_vol_time = "解析不可"
        max_vol_val = 0.0
        
        snapshots = state.get("snapshots", {})
        times = sorted(snapshots.keys())
        for i in range(1, len(times)):
            t_prev, t_curr = times[i-1], times[i]
            p_prev, p_curr = snapshots[t_prev], snapshots[t_curr]
            
            # 15銘柄の平均変動率絶対値を算出
            vol_sum = 0
            count = 0
            for sym in symbols:
                if sym in p_prev and sym in p_curr and p_prev[sym] > 0:
                    vol_sum += abs((p_curr[sym] - p_prev[sym]) / p_prev[sym]) * 100
                    count += 1
            if count > 0:
                avg_vol = vol_sum / count
                if avg_vol > max_vol_val:
                    max_vol_val = avg_vol
                    max_vol_time = f"{t_prev} ～ {t_curr}"

        # --- 日次市況レポート Embed (全15銘柄) ---
        report_embed = Embed(title=f"🌙 本日のコモディティ全般サマリー ({today_str})", color=0x3498db)
        report_embed.add_field(name="⚡ 本日最も激動した時間帯", value=f"**{max_vol_time}** (平均変動: `{max_vol_val:.2f}%`)", inline=False)

        # 15銘柄を3列形式で一覧表示
        lines = []
        for item in changes:
            lines.append(f"• **{item['name']}**: ${item['price']:.2f} (`{item['pct']:+.2f}%`)")
        
        report_embed.add_field(name="📊 全15銘柄の終値・本日騰落率", value="\n".join(lines[:8]), inline=True)
        report_embed.add_field(name="​", value="\n".join(lines[8:]), inline=True)

        send_webhook(REPORT_WEBHOOK_URL, report_embed)

if __name__ == "__main__":
    run_task()
