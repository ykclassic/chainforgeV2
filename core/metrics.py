import numpy as np
import pandas as pd

def calculate_performance_metrics(returns_series, risk_free_rate=0.04):

    if returns_series.empty:
        return {}

    periods_per_year = 8760

    rf_per_period = (1 + risk_free_rate) ** (1 / periods_per_year) - 1

    excess_returns = returns_series - rf_per_period

    mean_ret = returns_series.mean() * periods_per_year
    vol = returns_series.std(ddof=1) * np.sqrt(periods_per_year)

    sharpe = (
        np.sqrt(periods_per_year) * excess_returns.mean() / excess_returns.std(ddof=1)
        if excess_returns.std(ddof=1) != 0 else np.nan
    )

    downside = np.minimum(0, returns_series - rf_per_period)
    downside_dev = np.sqrt((downside ** 2).mean()) * np.sqrt(periods_per_year)

    sortino = (
        (mean_ret - risk_free_rate) / downside_dev
        if downside_dev != 0 else np.nan
    )

    cumulative = (1 + returns_series).cumprod()
    peak = cumulative.cummax()
    drawdown = cumulative / peak - 1
    max_dd = drawdown.min()

    total_return = cumulative.iloc[-1] - 1
    recovery_factor = total_return / abs(max_dd) if max_dd != 0 else np.nan

    return {
        "sharpe": round(sharpe, 2),
        "sortino": round(sortino, 2),
        "max_dd": round(max_dd, 4),
        "recovery": round(recovery_factor, 2)
    }
