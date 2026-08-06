import os
import zoneinfo

# 日本時間（JST）
JST = zoneinfo.ZoneInfo("Asia/Tokyo")

# 環境変数（GitHub Secrets）
SYSTEM_LOG_WEBHOOK_URL = os.getenv("SYSTEM_LOG_WEBHOOK_URL", "")
REPORT_WEBHOOK_URL = os.getenv("REPORT_WEBHOOK_URL", "")
RANKING_WEBHOOK_URL = os.getenv("RANKING_WEBHOOK_URL", "")

# --------------------------------------------------
# 銘柄定義・カテゴリ分け
# --------------------------------------------------
CATEGORY_TICKERS = {
    "✨ 貴金属・産業用金属（Metals）": [
        "JAU=F",  # 東京金先物 (JPX/円) ※JAU.CMXから変更
        "GC=F",  # NY金 (COMEX)
        "XAUUSD=X",  # ロンドン金 (LBMA)
        "JAG.CMX",  # 東京銀先物 (JPX/円)
        "SI=F",  # NY銀 (COMEX)
        "1693.T",  # 銅 (東証/円建てETF)
        "HG=F",  # NY銅 (COMEX)
        "JPL.CMX",  # 東京プラチナ先物 (JPX/円)
        "PL=F",  # NYプラチナ (NYMEX)
        "JPA.CMX",  # 東京パラジウム先物 (JPX/円)
        "PA=F",  # NYパラジウム (NYMEX)
        "ALI=F",  # アルミニウム (COMEX)
    ],
    "🛢️ エネルギー（Energy）": [
        "CL=F",  # WTI原油 (NYMEX)
        "BZ=F",  # ブレント原油 (ICE)
        "NG=F",  # 天然ガス (NYMEX)
        "HO=F",  # 暖房油 (NYMEX)
        "RB=F",  # RBOBガソリン (NYMEX)
    ],
    "🌽 農産物・コモディティ（Agri / Softs）": [
        "ZC=F",  # トウモロコシ (CBOT)
        "ZW=F",  # シカゴ小麦 (CBOT)
        "ZS=F",  # 大豆 (CBOT)
        "KC=F",  # カフェ・アラビカコーヒー (ICE)
        "SB=F",  # 粗糖 (ICE)
    ],
}

# 全銘柄の一覧フラットリスト
TICKERS = [
    ticker for tickers in CATEGORY_TICKERS.values() for ticker in tickers
]

# セント単位表記の銘柄（100で割ってドル建てにする）
CENT_BASED_TICKERS = {"KC=F", "SB=F", "ZC=F", "ZW=F", "ZS=F"}

# 日本市場・円建て（ドル円を乗算しない）銘柄
JPY_BASED_TICKERS = {
    "JAU=F",
    "JAG.CMX",
    "JPL.CMX",
    "JPA.CMX",
    "1693.T",
}

# レポート用表示名マッピング
TICKER_NAMES = {
    # 貴金属・産業用金属
    "JAU=F": "東京金 (JPX/円)",
    "GC=F": "NY金 (COMEX)",
    "XAUUSD=X": "ロンドン金 (LBMA)",
    "JAG.CMX": "東京銀 (JPX/円)",
    "SI=F": "NY銀 (COMEX)",
    "1693.T": "銅 (東証/円)",
    "HG=F": "NY銅 (COMEX)",
    "JPL.CMX": "東京プラ (JPX/円)",
    "PL=F": "NYプラ (NYMEX)",
    "JPA.CMX": "東京パラ (JPX/円)",
    "PA=F": "NYパラ (NYMEX)",
    "ALI=F": "アルミ (COMEX)",
    # エネルギー
    "CL=F": "WTI原油 (NYMEX)",
    "BZ=F": "ブレント (ICE)",
    "NG=F": "天然ガス (NYMEX)",
    "HO=F": "暖房油 (NYMEX)",
    "RB=F": "ガソリン (NYMEX)",
    # 農産物
    "ZC=F": "コーン (CBOT)",
    "ZW=F": "小麦 (CBOT)",
    "ZS=F": "大豆 (CBOT)",
    "KC=F": "コーヒー (ICE)",
    "SB=F": "粗糖 (ICE)",
}

STATE_FILE_PATH = "data/state.json"
