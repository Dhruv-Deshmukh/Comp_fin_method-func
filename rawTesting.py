import pandas as pd
import yfinance as yf

TICKER = "AAPL"
START = "2022-01-01"

df = yf.download(TICKER, start=START, auto_adjust=True, progress=False)

# Keep close and compute moving averages
df = df[["Close"]].dropna()
df["SMA20"] = df["Close"].rolling(20).mean()
df["SMA50"] = df["Close"].rolling(50).mean()

#  Simple signal --> 1 if SMA20 > SMA50 else 0
df["signal"] = (df["SMA20"] > df["SMA50"]).astype(int)

latest = df.dropna().iloc[-1]
print("Ticker:", TICKER)
print("Last close:", round(latest["Close"], 2))
print("SMA20:", round(latest["SMA20"], 2))
print("SMA50:", round(latest["SMA50"], 2))
print("Signal (1=BUY, 0=OUT):", int(latest["signal"]))

#####