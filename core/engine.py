import pandas_ta_classic as ta

def generate_signals(df, balance=10000):
    # 1. Indicator Setup
    df.ta.rsi(length=14, append=True)
    df.ta.macd(append=True)
    df.ta.aroon(length=14, append=True)
    df.ta.atr(length=14, append=True)
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    close = last['close']
    atr = last['ATRr_14']
    rsi = last['RSI_14']
    macd_line = last['MACD_12_26_9']
    macd_sig = last['MACDs_12_26_9']
    prev_macd_line = prev['MACD_12_26_9']
    prev_macd_sig = prev['MACDs_12_26_9']
    aroon_osc = last['AROONOSC_14']

    verdict = "NEUTRAL"
    sl, tp = 0, 0

    # 2. Logic: Triple Convergence
    # 9/10 Quality: RSI + MACD Cross + Aroon Strength
    if rsi < 35 and (macd_line > macd_sig and prev_macd_line <= prev_macd_sig) and aroon_osc > 0:
        verdict = "BUY / LONG"
        # SL: 2x ATR below entry | TP: 4x ATR above entry (1:2 Risk/Reward)
        sl = close - (atr * 2)
        tp = close + (atr * 4)
        
    elif rsi > 65 and (macd_line < macd_sig and prev_macd_line >= prev_macd_sig) and aroon_osc < 0:
        verdict = "SELL / SHORT"
        sl = close + (atr * 2)
        tp = close - (atr * 4)

    # 3. Position Sizing logic remains 1% Risk
    sl_dist = abs(close - sl) if sl != 0 else 1
    units = (balance * 0.01) / sl_dist if verdict != "NEUTRAL" else 0

    return {
        "verdict": verdict,
        "entry": close,
        "sl": sl,
        "tp": tp,
        "units": units,
        "atr": atr,
        "diag": f"RSI: {rsi:.1f} | ATR: {atr:.2f}"
    }
