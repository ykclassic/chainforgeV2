import os
import ccxt
import pandas as pd
from core.engine import generate_signals
from core.intelligence import get_sentiment, get_obi
from core.tracker import check_exits, load_ledger, save_ledger
from discord_webhook import DiscordWebhook, DiscordEmbed

def run():
    exchange = ccxt.bitget()
    webhook = DiscordWebhook(url=os.getenv('DISCORD_WEBHOOK'))
    
    # --- PHASE 1: CHECK OPEN TRADES ---
    current_prices = {s: exchange.fetch_ticker(s)['last'] for s in ["BTC/USDT", "ETH/USDT", "SOL/USDT", "SUI/USDT"]}
    exits = check_exits(current_prices)
    
    for ex in exits:
        color = "00ff00" if "PROFIT" in ex['exit_reason'] else "ff0000"
        exit_embed = DiscordEmbed(title=f"🚨 TRADE CLOSED: {ex['symbol']}", color=color)
        exit_embed.add_embed_field(name="Result", value=f"**{ex['exit_reason']}**\nExit: ${ex['exit_price']:,.2f}")
        webhook.add_embed(exit_embed)

    # --- PHASE 2: SCAN FOR NEW QUALITY ENTRIES ---
    for symbol in current_prices.keys():
        bars = exchange.fetch_ohlcv(symbol, '1h', limit=100)
        df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
        
        res = generate_signals(df)
        sent = get_sentiment(symbol)
        obi = get_obi(exchange, symbol)
        
        if res['verdict'] != "NEUTRAL":
            # 9/10 Quality Filter
            if sent >= 0.5 and obi >= 0.1:
                status = "🚀 APPROVED SIGNAL"
                
                # Save to Ledger
                ledger = load_ledger()
                # Prevent duplicate trades for same symbol
                if not any(t['symbol'] == symbol for t in ledger['active_trades']):
                    ledger['active_trades'].append({
                        "symbol": symbol, "side": res['verdict'], 
                        "entry": res['entry'], "sl": res['sl'], "tp": res['tp']
                    })
                    save_ledger(ledger)

                # Discord Report
                embed = DiscordEmbed(title=f"⚡ {symbol}: {status}", color="00e5ff")
                embed.add_embed_field(name="Trade Setup", value=(
                    f"Entry: **${res['entry']:,.2f}**\n"
                    f"Stop Loss: `${res['sl']:,.2f}`\n"
                    f"Take Profit: `${res['tp']:,.2f}`\n"
                    f"Size: `{res['units']:.4f} units`"
                ), inline=False)
                webhook.add_embed(embed)

    webhook.execute()

if __name__ == "__main__":
    run()
