import numpy as np
import pandas as pd
import yfinance as yf


# FETCHING clean prices
def load_close_prices(ticker: str, start: str, end: str | None = None) -> pd.DataFrame:
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    return df[["Close"]].dropna()


# strategy --> SMA crossover signal

def add_sma_crossover_signal(df: pd.DataFrame, fast: int = 20, slow: int = 50) -> pd.DataFrame:
    out = df.copy()
    out["SMA_FAST"] = out["Close"].rolling(fast).mean()
    out["SMA_SLOW"] = out["Close"].rolling(slow).mean()

    # 1 = “we want to be long”, 0 = “we want to be out”
    out["entry_signal"] = (out["SMA_FAST"] > out["SMA_SLOW"]).astype(int)
    return out



# Backtest engine --> long only with stop loss/take profit

def backtest_long_with_sl_tp(
    close: pd.Series,
    entry_signal: pd.Series,
    stop_loss_pct: float = 0.05,     # --> 0.05 = 5% stop-loss
    take_profit_pct: float = 0.10,   # --> 0.10 = 10% take-profit
    cost_bps: float = 10             # --> 10 bps per entry/exit
) -> pd.DataFrame:
    

    close = close.dropna()
    entry_signal = entry_signal.reindex(close.index).fillna(0).astype(int)

    pos = np.zeros(len(close), dtype=int)        # 0 or 1
    entry_px = np.full(len(close), np.nan)       # entry price while in trade

    in_trade = False
    my_entry = np.nan

    for i in range(len(close)):
        price_today = float(close.iloc[i])
        signal_today = int(entry_signal.iloc[i])

        if not in_trade:
            # Not in a trade --> can we enter?
            if signal_today == 1:
                in_trade = True
                my_entry = price_today
                pos[i] = 1
                entry_px[i] = my_entry
        else:
            # In a trade --> check exit rules
            pos[i] = 1
            entry_px[i] = my_entry

            stop_price = my_entry * (1 - stop_loss_pct)
            target_price = my_entry * (1 + take_profit_pct)

            hit_stop = price_today <= stop_price
            hit_target = price_today >= target_price
            trend_turned_off = signal_today == 0

            if hit_stop or hit_target or trend_turned_off:
                in_trade = False
                my_entry = np.nan
                pos[i] = 0
                entry_px[i] = np.nan

    out = pd.DataFrame({"Close": close, "entry_signal": entry_signal})
    out["position"] = pos
    out["entry_price"] = entry_px

    # Daily returns -----------
    out["ret"] = out["Close"].pct_change().fillna(0)

    # GET yesterday’s position for today’s return 
    out["pos_lag"] = out["position"].shift(1).fillna(0)

    # Costs WEHN position Changes (enter or exit) 
    out["turnover"] = out["position"].diff().abs().fillna(0)
    out["cost"] = out["turnover"] * (cost_bps / 10000.0)

    out["net_strat_ret"] = out["pos_lag"] * out["ret"] - out["cost"]
    out["equity_strat"] = (1 + out["net_strat_ret"]).cumprod()
    out["equity_bh"] = (1 + out["ret"]).cumprod()
    return out


def performance_stats(equity: pd.Series, daily_rets: pd.Series, trading_days: int = 252) -> dict:
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    cagr = equity.iloc[-1] ** (1 / years) - 1 if years > 0 else np.nan

    vol = daily_rets.std() * np.sqrt(trading_days)
    sharpe = (daily_rets.mean() * trading_days) / vol if vol and vol != 0 else np.nan

    peak = equity.cummax()
    max_dd = (equity / peak - 1.0).min()

    return {"CAGR": cagr, "Sharpe": sharpe, "MaxDrawdown": float(max_dd)}


# on AAPL
TICKER = "AAPL"
START = "2022-01-01"

prices = load_close_prices(TICKER, START)
data = add_sma_crossover_signal(prices, fast=20, slow=50)

bt = backtest_long_with_sl_tp(
    close=data["Close"],
    entry_signal=data["entry_signal"],
    stop_loss_pct=0.05,
    take_profit_pct=0.10,
    cost_bps=10
)

stats = performance_stats(bt["equity_strat"], bt["net_strat_ret"])
print(TICKER, stats)
