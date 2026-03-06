import json
import os

LEDGER_PATH = 'data/ledger.json'

def load_ledger():
    if not os.path.exists(LEDGER_PATH):
        return {"active_trades": []}
    with open(LEDGER_PATH, 'r') as f:
        return json.load(f)

def save_ledger(data):
    os.makedirs('data', exist_ok=True)
    with open(LEDGER_PATH, 'w') as f:
        json.dump(data, f, indent=4)

def check_exits(current_prices):
    """
    Checks if active trades hit TP or SL.
    current_prices: dict like {'BTC/USDT': 65000, ...}
    """
    ledger = load_ledger()
    still_active = []
    exited_trades = []

    for trade in ledger['active_trades']:
        symbol = trade['symbol']
        current_price = current_prices.get(symbol)
        
        if not current_price:
            still_active.append(trade)
            continue

        # Check Stop Loss
        if (trade['side'] == 'BUY' and current_price <= trade['sl']) or \
           (trade['side'] == 'SELL' and current_price >= trade['sl']):
            trade['exit_reason'] = "🛑 STOP LOSS HIT"
            trade['exit_price'] = current_price
            exited_trades.append(trade)
            
        # Check Take Profit (Set at 3x Risk)
        elif (trade['side'] == 'BUY' and current_price >= trade['tp']) or \
             (trade['side'] == 'SELL' and current_price <= trade['tp']):
            trade['exit_reason'] = "💰 TAKE PROFIT HIT"
            trade['exit_price'] = current_price
            exited_trades.append(trade)
        
        else:
            still_active.append(trade)

    ledger['active_trades'] = still_active
    save_ledger(ledger)
    return exited_trades
