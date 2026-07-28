import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

# Webhook URL の取得（前後空白の自動処理付き）
REPORT_WEBHOOK_URL = os.getenv("REPORT_WEBHOOK_URL", "").strip().strip("'").strip('"')
ALERT_WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL", "").strip().strip("'").strip('"')

# OANDA設定（もし残している場合）
OANDA_API_KEY = os.getenv("OANDA_API_KEY", "")
OANDA_ENV = os.getenv("OANDA_ENV", "practice")
