import ccxt, pandas as pd, pandas_ta as ta, requests
from config import *

exchange = ccxt.binance()

def get_sentiment(symbol):
    q = symbol.split("/")[0]
    url = f"https://www.google.com/search?q={q}+crypto+news"
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
    txt = r.text.lower()
    pos = sum(w in txt for w in ["bull","pump","breakout","rally","adoption"])
    neg = sum(w in txt for w in ["dump","hack","scam","crash","ban"])
    return pos - neg

def analyze(symbol, balance, risk):
    ohlcv = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=200)
    df = pd.DataFrame(ohlcv, columns=["t","o","h","l","c","v"])

    df["rsi"] = ta.rsi(df["c"], 14)
    df["ema9"] = ta.ema(df["c"], 9)
    df["ema21"] = ta.ema(df["c"], 21)
    macd = ta.macd(df["c"])
    df["macd"] = macd["MACD_12_26_9"]
    df["macds"] = macd["MACDs_12_26_9"]

    last = df.iloc[-1]
    hype = get_sentiment(symbol)

    signal = "HOLD"
    confidence = 50

    if last.rsi < 35 and last.ema9 > last.ema21 and last.macd > last.macds and hype > 0:
        signal = "BUY"
        confidence = 70 + hype
    elif last.rsi > 65 and last.ema9 < last.ema21 and last.macd < last.macds and hype < 0:
        signal = "SELL"
        confidence = 70 + abs(hype)

    risk_usd = balance * (risk / 100)
    sl_pct = 1.2
    position = risk_usd / (sl_pct / 100)

    return {
        "symbol": symbol,
        "price": round(last.c,2),
        "rsi": round(last.rsi,2),
        "signal": signal,
        "confidence": min(confidence,99),
        "hype": hype,
        "position_usd": round(position,2)
    }

def scan_market(balance, risk):
    results = []
    for coin in TOP_COINS:
        try:
            results.append(analyze(coin, balance, risk))
        except:
            pass
    return results
