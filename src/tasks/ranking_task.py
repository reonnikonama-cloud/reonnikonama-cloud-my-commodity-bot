from discord import Embed
from src.config import RANKING_WEBHOOK_URL, SYSTEM_LOG_WEBHOOK_URL, COMMODITY_TARGETS
from src.modules.fetcher import fetch_commodity_data
from src.modules.state_manager import load_state
from src.modules.discord_notifier import send_webhook

def run_ranking():
    state = load_state()
    market_data = fetch_commodity_data()
    opens = state.get("opens", {})

    changes = []
    for sym, name in COMMODITY_TARGETS.items():
        if sym in market_data and sym in opens and opens[sym] > 0:
            price = market_data[sym]["price"]
            pct = ((price - opens[sym]) / opens[sym]) * 100
            changes.append({"name": name, "price": price, "pct": pct})

    changes.sort(key=lambda x: x["pct"], reverse=True)
    if not changes:
        return

    top3 = changes[:3]
    bottom3 = changes[-3:][::-1]

    embed = Embed(title="🏆 本日のコモディティ 騰落率ランキング", color=0xf1c40f)
    top_str = "\n".join([f"🥇 **{x['name']}**: `{x['pct']:+.2f}%` (${x['price']:.2f})" if i==0 else
                        f"🥈 **{x['name']}**: `{x['pct']:+.2f}%` (${x['price']:.2f})" if i==1 else
                        f"🥉 **{x['name']}**: `{x['pct']:+.2f}%` (${x['price']:.2f})" for i, x in enumerate(top3)])
    embed.add_field(name="📈 値上がり TOP3", value=top_str or "なし", inline=False)

    bot_str = "\n".join([f"📉 **{x['name']}**: `{x['pct']:+.2f}%` (${x['price']:.2f})" for x in bottom3])
    embed.add_field(name="📉 値下がり TOP3", value=bot_str or "なし", inline=False)

    send_webhook(RANKING_WEBHOOK_URL, embed, SYSTEM_LOG_WEBHOOK_URL)
