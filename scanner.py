import numpy as np
import pandas as pd
from urllib.parse import quote


def _lower_band(c):
    s = pd.Series(c)
    return (s.rolling(20).mean() - 2 * s.rolling(20).std(ddof=0)).values


def _signal(i, o, h, l, c, v, lo, cond, volx):
    """i নম্বর candle-এ কন্ডিশন মেলে কিনা। মিললে (pattern, volume_ratio)।"""
    if np.isnan(lo[i]):
        return None
    if cond == "A":
        # green candle, Lower BB তার body-র মাঝামাঝি (৩০–৭০%), সাথে volume
        if c[i] <= o[i]:
            return None
        pos = (lo[i] - o[i]) / (c[i] - o[i])
        avg = v[i - 20:i].mean()
        if 0.3 <= pos <= 0.7 and avg > 0 and v[i] / avg >= volx:
            return "Green candle @ Lower BB", v[i] / avg
        return None
    # cond B: Lower BB-র নিচে Hammer / Morning Star, কোনো candle band ছোঁবে না
    body = abs(c[i] - o[i])
    low_w = min(o[i], c[i]) - l[i]
    up_w = h[i] - max(o[i], c[i])
    avg = v[i - 20:i].mean()
    vr = v[i] / avg if avg > 0 else np.nan
    if body > 0 and low_w >= 2 * body and up_w <= 0.5 * body and h[i] < lo[i]:
        return "Hammer", vr
    a, s, t = i - 2, i - 1, i
    if (not np.isnan(lo[a]) and c[a] < o[a] and abs(c[s] - o[s]) < 0.5 * abs(c[a] - o[a])
            and c[t] > o[t] and c[t] > (o[a] + c[a]) / 2
            and h[a] < lo[a] and h[s] < lo[s] and h[t] < lo[t]):
        return "Morning Star", vr
    return None


def scan(data, cond, window="day", volx=1.5):
    """data: {symbol: DataFrame(Open,High,Low,Close,Volume)}  →  ফলাফলের DataFrame"""
    rows = []
    for sym, d in data.items():
        o, h, l, c, v = (d[k].values.astype(float) for k in ("Open", "High", "Low", "Close", "Volume"))
        n = len(c)
        if n < 30:
            continue
        lo = _lower_band(c)
        idx = d.index
        days = np.array([t.date() for t in idx])
        last_day = days[-1]
        k = {"last": 1, "hour": 12}.get(window, int((days == last_day).sum()))
        for i in range(n - 1, max(n - k, 22) - 1, -1):
            r = _signal(i, o, h, l, c, v, lo, cond, volx)
            if r:
                prev = c[days < last_day]
                chg = (c[-1] / prev[-1] - 1) * 100 if len(prev) else np.nan
                rows.append({
                    "Stock": sym, "Signal Time": idx[i], "Signal Price": c[i], "LTP": c[-1],
                    "Change %": chg, "Lower BB": lo[i], "Pattern": r[0], "Volume ×": r[1],
                    "Chart": "https://in.tradingview.com/chart/?symbol=NSE%3A" + quote(sym.replace("-", "_"), safe=""),
                })
                break
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("Signal Time", ascending=False).reset_index(drop=True)
        df["Signal Time"] = df["Signal Time"].dt.strftime("%d %b, %H:%M")
    return df
