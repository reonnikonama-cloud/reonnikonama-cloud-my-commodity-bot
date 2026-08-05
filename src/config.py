import os
import zoneinfo

# 日本時間（JST）
JST = zoneinfo.ZoneInfo("Asia/Tokyo")

# 環境変数（GitHub Secrets）
SYSTEM_LOG_WEBHOOK_URL = os.getenv("SYSTEM_LOG_WEBHOOK_URL", "")
REPORT_WEBHOOK_URL = os.getenv("REPORT_WEBHOOK_URL", "")
RANKING_WEBHOOK_URL = os.getenv("RANKING_WEBHOOK_URL", "")

TICKERS = [
    # エネルギー
    "CL=F", "BZ=F", "NG=F", "HO=F", "RB=F",
    # 貴金属・非鉄金属
    "GC=F", "SI=F", "HG=F", "PL=F", "PA=F", "ALI=F",
    # ソフトコモディティ・農産物 (CBOTコード)
    "KC=F", "SB=F", "ZC=F", "ZW=F", "ZS=F"
]

CENT_BASED_TICKERS = {"KC=F", "SB=F", "ZC=F", "ZW=F", "ZS=F"}
STATE_FILE_PATH = "data/state.json"
