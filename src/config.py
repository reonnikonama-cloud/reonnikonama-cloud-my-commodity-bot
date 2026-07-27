import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
REPORT_CHANNEL_ID = int(os.getenv("REPORT_CHANNEL_ID", "0"))
ALERT_CHANNEL_ID = int(os.getenv("ALERT_CHANNEL_ID", "0"))

OANDA_API_KEY = os.getenv("OANDA_API_KEY", "")
OANDA_ENV = os.getenv("OANDA_ENV", "practice")
BASE_URL = "https://api-fxpractice.oanda.com/v3" if OANDA_ENV == "practice" else "https://api.fxtrade.oanda.com/v3"
HEADERS = {"Authorization": f"Bearer {OANDA_API_KEY}"}
