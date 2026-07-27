import sys
from pathlib import Path
import discord
from discord.ext import commands, tasks

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DISCORD_TOKEN, REPORT_CHANNEL_ID, ALERT_CHANNEL_ID
from src.modules.market_tasks import execute_hourly_report, execute_anomaly_check

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot booted successfully: {bot.user.name}")
    hourly_report_task.start()
    anomaly_check_task.start()

@tasks.loop(hours=1)
async def hourly_report_task():
    channel = bot.get_channel(REPORT_CHANNEL_ID)
    if channel:
        await execute_hourly_report(channel)

@tasks.loop(minutes=5)
async def anomaly_check_task():
    channel = bot.get_channel(ALERT_CHANNEL_ID)
    if channel:
        await execute_anomaly_check(channel)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
