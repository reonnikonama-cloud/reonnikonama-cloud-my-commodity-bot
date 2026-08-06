from src.config import CATEGORY_TICKERS, TICKER_NAMES, TICKERS


def generate_am_report_embed(state: dict, usdjpy: float) -> dict:
    """AM前場サマリー生成（Embed形式）"""
    opens = state.get("opens", {})
    snapshots = state.get("snapshots", {})
    if not snapshots:
        return None

    latest_time = list(snapshots.keys())[-1]
    current_prices = snapshots[latest_time]
    date_str = state.get("date", "")

    fields = [
        {
            "name": "💱 適用為替レート",
            "value": f"`1 USD = {usdjpy:.2f} JPY`",
            "inline": False,
        }
    ]

    for cat_name, tickers in CATEGORY_TICKERS.items():
        table_str = f"{'銘柄':<12} {'始値':<9} {'前場値':<9} {'前場変動率':<8}\n"
        table_str += "-" * 42 + "\n"
        has_data = False

        for ticker in tickers:
            name = TICKER_NAMES.get(ticker, ticker)
            open_p = opens.get(ticker)
            curr_p = current_prices.get(ticker)

            if open_p and curr_p:
                has_data = True
                diff = curr_p - open_p
                rate = (diff / open_p) * 100
                table_str += f"{name:<12} {open_p:>9.1f} {curr_p:>9.1f} {rate:>+7.2f}%\n"

        if has_data:
            fields.append(
                {
                    "name": cat_name,
                    "value": f"```text\n{table_str}```",
                    "inline": False,
                }
            )

    return {
        "title": "📊 コモディティ市況 AM前場サマリー",
        "description": f"**日付**: `{date_str}` | **時刻**: `{latest_time} JST`",
        "color": 3447003,  # ブルー (0x3498db)
        "fields": fields,
        "footer": {
            "text": "参照先: Osaka Exchange (JPX) / CBOT / NYMEX / ICE / LBMA",
        },
    }


def generate_pm_report_embed(state: dict, usdjpy: float) -> dict:
    """PM後場サマリー生成（Embed形式）"""
    opens = state.get("opens", {})
    snapshots = state.get("snapshots", {})
    if not snapshots:
        return None

    latest_time = list(snapshots.keys())[-1]
    current_prices = snapshots[latest_time]
    date_str = state.get("date", "")

    fields = [
        {
            "name": "💱 適用為替レート",
            "value": f"`1 USD = {usdjpy:.2f} JPY`",
            "inline": False,
        }
    ]

    for cat_name, tickers in CATEGORY_TICKERS.items():
        table_str = f"{'銘柄':<12} {'始値':<9} {'終値':<9} {'日次変動率':<8}\n"
        table_str += "-" * 42 + "\n"
        has_data = False

        for ticker in tickers:
            name = TICKER_NAMES.get(ticker, ticker)
            open_p = opens.get(ticker)
            curr_p = current_prices.get(ticker)

            if open_p and curr_p:
                has_data = True
                daily_diff = curr_p - open_p
                daily_rate = (daily_diff / open_p) * 100
                table_str += f"{name:<12} {open_p:>9.1f} {curr_p:>9.1f} {daily_rate:>+7.2f}%\n"

        if has_data:
            fields.append(
                {
                    "name": cat_name,
                    "value": f"```text\n{table_str}```",
                    "inline": False,
                }
            )

    return {
        "title": "📊 コモディティ市況 デイリーサマリー",
        "description": f"**日付**: `{date_str}` | **時刻**: `{latest_time} JST`",
        "color": 3066993,  # エメラルドグリーン (0x2ecc71)
        "fields": fields,
        "footer": {
            "text": "参照先: Osaka Exchange (JPX) / CBOT / NYMEX / ICE / LBMA",
        },
    }


def generate_volatility_time_ranking(state: dict, title: str) -> str:
    """銘柄ごとに全時間帯の中でボラティリティ（絶対変動率）が大きかった時間帯TOP3を分析"""
    snapshots = state.get("snapshots", {})
    time_keys = list(snapshots.keys())

    if len(time_keys) < 2:
        return f"⏱️ **【各銘柄 ボラティリティ時間帯ランキング - {title}】**\n分析に十分な時間差分データがありません。"

    ticker_volatilities = {ticker: [] for ticker in TICKERS}

    for i in range(1, len(time_keys)):
        t_prev = time_keys[i - 1]
        t_curr = time_keys[i]

        # 時間差分ガード: 飛んでいる・日付跨ぎデータのスキップ
        try:
            h_prev, m_prev = map(int, t_prev.split(":"))
            h_curr, m_curr = map(int, t_curr.split(":"))
            time_diff_min = (h_curr * 60 + m_curr) - (h_prev * 60 + m_prev)

            if time_diff_min <= 0 or time_diff_min > 30:
                continue
        except ValueError:
            pass

        prices_prev = snapshots[t_prev]
        prices_curr = snapshots[t_curr]

        for ticker in TICKERS:
            p0 = prices_prev.get(ticker)
            p1 = prices_curr.get(ticker)
            if p0 and p1 and p0 > 0:
                raw_rate = ((p1 - p0) / p0) * 100
                abs_rate = abs(raw_rate)

                # 異常値フィルタ（±50%超えはデータバグとしてスキップ）
                if abs_rate > 50:
                    continue

                ticker_volatilities[ticker].append(
                    {
                        "time_range": f"{t_prev} ~ {t_curr}",
                        "abs_rate": abs_rate,
                        "raw_rate": raw_rate,
                    }
                )

    rank_icons = ["🥇", "🥈", "🥉"]
    msg = f"⏱️ **【銘柄別 ボラティリティ時間帯ランキング TOP3 - {title}】** ({state.get('date')} JST)\n\n"

    for ticker in TICKERS:
        name = TICKER_NAMES.get(ticker, ticker)
        vols = ticker_volatilities.get(ticker, [])
        if not vols:
            continue

        top_3 = sorted(vols, key=lambda x: x["abs_rate"], reverse=True)[:3]

        msg += f"🔹 **`{name}`** (`{ticker}`)\n"
        for i, item in enumerate(top_3):
            msg += f"  {rank_icons[i]} `{item['time_range']}` : **{item['raw_rate']:>+6.2f}%**\n"
        msg += "\n"

    return msg
