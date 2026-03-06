import pandas_ta as ta

# --- CONFIG ---
ACCOUNT_BALANCE = 10000 
RISK_PER_TRADE = 0.01   
FEE_RATE = 0.001        # 0.1% Taker Fee
SLIPPAGE_RATE = 0.0005  # 0.05% Slippage

def generate_signals(df):
    """Core logic with Phase 1 Realism Layer"""
    # Indicators
    df.ta.rsi(length=14, append=True)
    df.ta.macd(append=True)
    df.ta.aroon(append=True)
    df.ta.atr(length=14, append=True)
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Extract Values
    close = last['close']
    rsi = last['RSI_14']
    macd_diff = last['MACD_12_26_9'] - last['MACDs_12_26_9']
    prev_macd_diff = prev['MACD_12_26_9'] - prev['MACDs_12_26_9']
    aroon_osc = last['AROONOSC_14']
    atr = last['ATRr_14']

    verdict = "NEUTRAL"
    if rsi < 35 and (macd_diff > 0 >= prev_macd_diff) and aroon_osc > 0:
        verdict = "BUY / LONG"
    elif rsi > 65 and (macd_diff < 0 <= prev_macd_diff) and aroon_osc < 0:
        verdict = "SELL / SHORT"

    # Cost & Risk Modeling
    if verdict != "NEUTRAL":
        adj_entry = close * (1 + SLIPPAGE_RATE) if verdict == "BUY / LONG" else close * (1 - SLIPPAGE_RATE)
        sl_distance = atr * 2
        dollar_risk = ACCOUNT_BALANCE * RISK_PER_TRADE
        units = dollar_risk / sl_distance
        fees = (units * adj_entry * FEE_RATE) * 2
        
        diag = f"RSI: {rsi:.1f} | Sized: {units:.4f} units | Est. Fees: ${fees:.2f}"
    else:
        diag = f"RSI: {rsi:.1f} | MACD: {'🟢' if macd_diff > 0 else '🔴'} | Aroon: {aroon_osc:.0f}"

    return {"verdict": verdict, "price": close, "diag": diag, "atr": atr}
