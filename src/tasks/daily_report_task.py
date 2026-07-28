import datetime
from discord import Embed
from src.config import REPORT_WEBHOOK_URL, SYSTEM_LOG_WEBHOOK_URL, COMMODITY_TARGETS
from src.modules.fetcher import fetch_commodity_data
from src.modules.state_manager import load_state
from src.modules.discord_notifier import send_webhook

def run_daily_report():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    today_str = now_utc.strftime("%Y-%m-%d")

    state = load_state()
    market_data = fetch_commodity_data()
    opens = state.get("opens", {})

    # 1. 激動時間帯の解析
    snapshots = state.get("snapshots", {})
    times = sorted(snapshots.keys())
    max_vol_time = "データ不足"
    max_vol_val = 0.0

    for i in range(1, len(times)):
        t_prev, t_curr = times[i-1], times[i]
        p_prev, p_curr = snapshots[t_prev], snapshots[t_curr]
        
        vol_sum, count = 0, 0
        for sym in COMMODITY_TARGETS.keys():
            if sym in p_prev and sym in p_curr and p_prev[sym] > 0:
                vol_sum += abs((p_curr[sym] - p_prev[sym]) / p_prev[sym]) * 100
                count += 1
        if count > 0:
            avg_vol = vol_sum / count
            if avg_vol > max_vol_val:
                max_vol_val = avg_vol
                max_vol_time = f"{t_prev} ～ {t_curr}"

    # 2. 市況レポートEmbed作成
    embed = Embed(title=f"🌙 本日のコモディティ全般サマリー ({today_str})", color=0x3498db)
    embed.add_field(name="⚡ 本日最も激動した時間帯", value=f"**{max_vol_time}** (平均変動: `{max_vol_val:.2f}%`)", inline=False)

    lines = []
    for sym, name in COMMODITY_TARGETS.items():
        if sym in market_data:
            price = market_data[sym]["price"]
            open_p = opens.get(sym, price)
            pct = ((price - open_p) / open_p) * 100 if open_p > 0 else 0.0
            lines.append(f"• **{name}**: ${price:.2f} (`{pct:+.2f}%`)")

    if lines:
        embed.add_field(name="📊 全15銘柄の終値・本日騰落率", value="\n".join(lines[:8]), inline=True)
        embed.add_field(name="​", value="\n".join(lines[8:]), inline=True)

    send_webhook(REPORT_WEBHOOK_URL, embed, SYSTEM_LOG_WEBHOOK_URL)
