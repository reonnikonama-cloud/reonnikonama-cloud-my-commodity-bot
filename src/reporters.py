from config import TICKERS

def generate_am_report(state: dict, usdjpy: float) -> str:
    """AM前場サマリー生成"""
    opens = state.get("opens", {})
    snapshots = state.get("snapshots", {})
    latest_time = list(snapshots.keys())[-1]
    current_prices = snapshots[latest_time]

    msg = f"📊 **【コモディティ市況 AM前場サマリー】** ({state.get('date')} {latest_time} JST)\n"
    msg += f"💱 適用為替レート: 1 USD = {usdjpy:.2f} JPY\n"
    msg += "```text\n"
    msg += f"{'銘柄':<7} {'始値(円)':<10} {'前場値(円)':<10} {'前場騰落額':<10} {'前場変動率':<7}\n"
    msg += "-" * 50 + "\n"

    for ticker in TICKERS:
        open_p = opens.get(ticker)
        curr_p = current_prices.get(ticker)

        if open_p and curr_p:
            diff = curr_p - open_p
            rate = (diff / open_p) * 100
            msg += f"{ticker:<7} {open_p:>10.2f} {curr_p:>10.2f} {diff:>+10.2f} {rate:>+6.2f}%\n"

    msg += "```"
    return msg

def generate_pm_report(state: dict, usdjpy: float) -> str:
    """PM後場サマリー生成"""
    opens = state.get("opens", {})
    snapshots = state.get("snapshots", {})
    latest_time = list(snapshots.keys())[-1]
    current_prices = snapshots[latest_time]
    am_prices = state.get("am_prices", opens)

    msg = f"📊 **【コモディティ市況 PM後場サマリー】** ({state.get('date')} {latest_time} JST)\n"
    msg += f"💱 適用為替レート: 1 USD = {usdjpy:.2f} JPY\n"
    msg += "```text\n"
    msg += f"{'銘柄':<7} {'始値(円)':<10} {'前場値(円)':<10} {'終値(円)':<10} {'日次変動率':<8} {'後場推移':<15}\n"
    msg += "-" * 66 + "\n"

    for ticker in TICKERS:
        open_p = opens.get(ticker)
        am_p = am_prices.get(ticker, open_p)
        curr_p = current_prices.get(ticker)

        if open_p and curr_p and am_p:
            daily_diff = curr_p - open_p
            daily_rate = (daily_diff / open_p) * 100
            pm_diff = curr_p - am_p
            pm_rate = (pm_diff / am_p) * 100 if am_p else 0.0

            pm_str = f"{pm_diff:>+7.2f} ({pm_rate:>+5.2f}%)"
            msg += f"{ticker:<7} {open_p:>10.2f} {am_p:>10.2f} {curr_p:>10.2f} {daily_rate:>+7.2f}% {pm_str:<15}\n"

    msg += "```"
    return msg

def generate_volatility_time_ranking(state: dict, title: str) -> str:
    """銘柄ごとに全時間帯の中でボラティリティ（絶対変動率）が大きかった時間帯TOP3を分析"""
    snapshots = state.get("snapshots", {})
    time_keys = list(snapshots.keys())

    if len(time_keys) < 2:
        return f"⏱️ **【各銘柄 ボラティリティ時間帯ランキング - {title}】**\n分析に十分な時間差分データがありません。"

    ticker_volatilities = {ticker: [] for ticker in TICKERS}

    for i in range(1, len(time_keys)):
        t_prev = time_keys[i-1]
        t_curr = time_keys[i]
        
        prices_prev = snapshots[t_prev]
        prices_curr = snapshots[t_curr]

        for ticker in TICKERS:
            p0 = prices_prev.get(ticker)
            p1 = prices_curr.get(ticker)
            if p0 and p1 and p0 > 0:
                raw_rate = ((p1 - p0) / p0) * 100
                abs_rate = abs(raw_rate)
                ticker_volatilities[ticker].append({
                    "time_range": f"{t_prev} ~ {t_curr}",
                    "abs_rate": abs_rate,
                    "raw_rate": raw_rate
                })

    rank_icons = ["🥇", "🥈", "🥉"]
    msg = f"⏱️ **【銘柄別 ボラティリティ時間帯ランキング TOP3 - {title}】** ({state.get('date')} JST)\n\n"

    for ticker in TICKERS:
        vols = ticker_volatilities.get(ticker, [])
        if not vols:
            continue

        top_3 = sorted(vols, key=lambda x: x["abs_rate"], reverse=True)[:3]

        msg += f"🔹 **`{ticker}`**\n"
        for i, item in enumerate(top_3):
            msg += f"  {rank_icons[i]} `{item['time_range']}` : **{item['raw_rate']:>+6.2f}%**\n"
        msg += "\n"

    return msg
