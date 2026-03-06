import numpy as np
import pandas as pd

def calculate_performance_metrics(returns_series):
    if returns_series.empty: return {}

    ann_factor = 8760 # Hourly 24/7
    mean_ret = returns_series.mean() * ann_factor
    vol = returns_series.std(ddof=1) * np.sqrt(ann_factor)
    
    # Sharpe Ratio
    sharpe = mean_ret / vol if vol != 0 else 0

    # Drawdown
    cum = (1 + returns_series).cumprod()
    max_dd = (cum / cum.cummax() - 1).min()
    
    # Recovery
    recovery = (cum.iloc[-1] - 1) / abs(max_dd) if max_dd != 0 else 0

    return {
        "sharpe": round(sharpe, 2),
        "max_dd": f"{max_dd*100:.2f}%",
        "recovery": round(recovery, 2)
    }
