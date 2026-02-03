import yfinance as yf
import matplotlib.pyplot as plt

# Def the indexes
indexes = {
    "India": "^NSEI",      # NIFTY 50
    "Europe": "^STOXX50E", # Euro Stoxx 50
    "US": "^GSPC"          # S&P 500
}

# Fetch historical data --> past year
data = yf.download(list(indexes.values()), start="2025-02-03", end="2026-02-03")["Adj Close"]

# Plotting
plt.figure(figsize=(12, 6))
for country, ticker in indexes.items():
    plt.plot(data[ticker], label=f"{country} ({ticker})")

plt.title("Comparison of Indian, European, and US Indexes (Past Year)")
plt.xlabel("Date")
plt.ylabel("Adjusted Closing Price")
plt.legend()
plt.grid(True)
plt.show()
