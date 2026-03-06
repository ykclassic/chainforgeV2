import pandas_ta_classic as ta

def generate_signals(df, balance=10000):
    """Core logic with Phase 1 Realism Layer"""
    # 1. Indicator Setup
    df.ta.rsi(length=14, append=True)
    df.ta.macd(append=True)
    df.ta.aroon(append=True)
    df.ta.atr(length=14, append=True)
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 2. Values
    close = last['close']
    rsi = last['RSI_14']
    macd_diff = last['MACD_12_26_9'] - last['MACDs_12_26_9']
    prev_macd_diff = prev['MACD_12_26_9'] - prev['MACDs_12_26_9']
    aroon_osc = last['AROONOSC_14']
    atr = last['ATRr_14']

    # 3. Strategy Logic
    verdict = "NEUTRAL"
    if rsi < 35 and (macd_diff > 0 >= prev_macd_diff) and aroon_osc > 0:
        verdict = "BUY / LONG"
    elif rsi > 65 and (macd_diff < 0 <= prev_macd_diff) and aroon_osc < 0:
        verdict = "SELL / SHORT"

    # 4. Realism & Sizing
    if verdict != "NEUTRAL":
        # Risk 1% per trade, 2x ATR Stop Loss
        sl_dist = atr * 2
        units = (balance * 0.01) / sl_dist
        est_fee = (units * close * 0.001) * 2 # 0.1% Taker in/out
        diag = f"RSI: {rsi:.1f} | Units: {units:.4f} | Est. Fee: ${est_fee:.2f}"
    else:
        diag = f"RSI: {rsi:.1f} | MACD: {'🟢' if macd_diff > 0 else '🔴'}"

    return {"verdict": verdict, "price": close, "diag": diag}
