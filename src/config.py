import os
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートの .env ファイルを自動読み込み
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

# ------------------------------------------------------------------
# 1. Webhook URL 設定 (前後空白・引用符の自動ストリップ処理付き)
# ------------------------------------------------------------------
REPORT_WEBHOOK_URL = os.getenv("REPORT_WEBHOOK_URL", "").strip().strip("'").strip('"')
ALERT_WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL", "").strip().strip("'").strip('"')

# RANKING_WEBHOOK_URL が未設定の場合は REPORT_WEBHOOK_URL を自動フォールバック
_ranking_url = os.getenv("RANKING_WEBHOOK_URL", "").strip().strip("'").strip('"')
RANKING_WEBHOOK_URL = _ranking_url if _ranking_url else REPORT_WEBHOOK_URL

# SYSTEM_LOG_WEBHOOK_URL (管理者ログ用)
SYSTEM_LOG_WEBHOOK_URL = os.getenv("SYSTEM_LOG_WEBHOOK_URL", "").strip().strip("'").strip('"')


# ------------------------------------------------------------------
# 2. 監視対象コモディティ 15銘柄 (yfinance Symbol : 表示用名称)
# ------------------------------------------------------------------
COMMODITY_TARGETS = {
    # エネルギー
    "CL=F": "WTI原油",
    "BZ=F": "ブレント原油",
    "NG=F": "天然ガス",
    "HO=F": "暖房油",
    "RB=F": "RBOBガソリン",
    
    # 貴金属・産業用金属
    "GC=F": "金 (Gold)",
    "SI=F": "銀 (Silver)",
    "HG=F": "銅 (Copper)",
    "PL=F": "プラチナ",
    "PA=F": "パラジウム",
    
    # 農産物
    "C=F": "トウモロコシ",
    "W=F": "小麦",
    "S=F": "大豆",
    "KC=F": "コーヒー",
    "SB=F": "砂糖"
}
