# 📈 Commodity Market Alert Discord Bot

WTI原油を中心とした商品先物（コモディティ）市場の価格データ、テクニカル指標、マクロ経済指標を自動収集し、定期レポートおよび急変アラートをDiscordへ配信するBotです。

---

## 🌟 主な機能

* **📊 毎時統合レポート（H1足）**
  * OANDA APIからのリアルタイム価格取得（ドル建て `$` / 円換算 `¥` 併記）
  * テクニカル分析（SMA20/50, RSI）とポジション偏重による自動スコアリング
  * マクロ指標（米国10年債利回り、金先物）の直近騰落率の連動表示
  * `mplfinance` によるローソク足チャート画像の動的生成・添付

* **🚨 5分足急変アラート（M15足）**
  * ATR（Average True Range）をベースにした異常値検知
  * 急激なボラティリティ拡大時に `@everyone` メンションで緊急通知

---

## 📂 ディレクトリ構造 (`src` Layout)

```text
my-commodity-bot/
├── .gitignore            # Git除外設定
├── .env.example          # 環境変数サンプル
├── requirements.txt      # 依存ライブラリ
├── README.md             # 本ドキュメント
├── SPECIFICATION.md      # 詳細仕様書
└── src/
    ├── __init__.py
    ├── main.py            # エントリーポイント
    ├── config.py          # 設定値ロード
    └── modules/
        ├── __init__.py
        ├── oanda_client.py     # OANDA API通信
        ├── chart_generator.py  # チャート描画
        ├── signal_evaluator.py # スコアリング
        ├── macro_analyzer.py   # マクロ指標取得
        ├── anomaly_detector.py # 異常値検知
        └── market_tasks.py     # Discord送信処理
