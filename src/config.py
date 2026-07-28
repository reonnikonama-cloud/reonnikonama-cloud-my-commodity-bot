import os
from dotenv import load_dotenv

load_dotenv()

REPORT_WEBHOOK_URL = os.getenv("REPORT_WEBHOOK_URL", "").strip()
ALERT_WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL", "").strip()
RANKING_WEBHOOK_URL = os.getenv("RANKING_WEBHOOK_URL", os.getenv("REPORT_WEBHOOK_URL", "")).strip()

# システムログ用（設定されていない場合は通知をスキップまたはフォールバック）
SYSTEM_LOG_WEBHOOK_URL = os.getenv("SYSTEM_LOG_WEBHOOK_URL", "").strip()
