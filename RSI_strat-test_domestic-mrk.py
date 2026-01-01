import pandas as pd
import yfinance as yf

# Fetching (Reliance Industries) (NSE)

data = yf.download("RELIANCE.NS", start="2024-01-01", end="2025-01-01")

# Calc RSI (std 14-day period)
delta = data['Close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)

avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()

rs = avg_gain / avg_loss
data['RSI'] = 100 - (100 / (1 + rs))

# Strategy --> Buy when RSI < 30 (Oversold), Sell when RSI > 70 (Overbought)
data['Signal'] = 0
data.loc[data['RSI'] < 30, 'Signal'] = 1
data.loc[data['RSI'] > 70, 'Signal'] = -1

# Performance Trail
data['Strategy_Return'] = data['Signal'].shift(1) * data['Close'].pct_change()
data['Cumulative_Return'] = (1 + data['Strategy_Return'].fillna(0)).cumprod()

print(data[['Close', 'RSI', 'Cumulative_Return']].tail());

