import os
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

def parse_int_env(key: str, default: int = 0) -> int:
    """環境変数から数字のみを抽出して safe に int 化する"""
    raw_val = os.getenv(key, "")
    # 数字（0-9）だけを抽出（クォーテーションやスペースを全削除）
    digits_only = re.sub(r"\D", "", raw_val)
    return int(digits_only) if digits_only else default

REPORT_CHANNEL_ID = parse_int_env("REPORT_CHANNEL_ID")
ALERT_CHANNEL_ID = parse_int_env("ALERT_CHANNEL_ID")

SYSTEM_LOG_WEBHOOK_URL = os.getenv("SYSTEM_LOG_WEBHOOK_URL", "")

OANDA_API_KEY = os.getenv("OANDA_API_KEY", "")
OANDA_ENV = os.getenv("OANDA_ENV", "practice")
BASE_URL = "https://api-fxpractice.oanda.com/v3" if OANDA_ENV == "practice" else "https://api.fxtrade.oanda.com/v3"
HEADERS = {"Authorization": f"Bearer {OANDA_API_KEY}"}
