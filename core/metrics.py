import numpy as np
import pandas as pd

def calculate_performance_metrics(returns_series, risk_free_rate=0.04):
    if returns_series.empty: return {}

    periods_per_year = 8760 # 24/7 Crypto Market
    rf_per_period = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
    excess_returns = returns_series - rf_per_period

    mean_ret = returns_series.mean() * periods_per_year
    sharpe = (np.sqrt(periods_per_year) * excess_returns.mean() / excess_returns.std(ddof=1) 
              if excess_returns.std(ddof=1) != 0 else np.nan)

    cumulative = (1 + returns_series).cumprod()
    max_dd = (cumulative / cumulative.cummax() - 1).min()
    recovery = (cumulative.iloc[-1] - 1) / abs(max_dd) if max_dd != 0 else np.nan

    return {"sharpe": round(sharpe, 2), "max_dd": f"{max_dd*100:.2f}%", "recovery": round(recovery, 2)}
