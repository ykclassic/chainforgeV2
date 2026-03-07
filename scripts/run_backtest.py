import os
import ccxt
import pandas as pd
from datetime import datetime
from core.engine import generate_signals
from core.intelligence import get_sentiment, get_obi
from core.tracker import check_exits, load_ledger, save_ledger
from discord_webhook import DiscordWebhook, DiscordEmbed

def run():
    exchange = ccxt.bitget({'enableRateLimit': True})
    webhook_url = os.getenv('DISCORD_WEBHOOK')
    webhook = DiscordWebhook(url=webhook_url, username="🛡️ AEGIS Intelligence")
    symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "SUI/USDT"]
    
    # 1. Monitor Phase
    current_prices = {s: exchange.fetch_ticker(s)['last'] for s in symbols}
    exits = check_exits(current_prices)
    for ex in exits:
        color = "2ed573" if "PROFIT" in ex['exit_reason'] else "ff4757"
        embed = DiscordEmbed(title=f"🚨 EXIT: {ex['symbol']}", color=color)
        embed.add_embed_field(name="Result", value=f"**{ex['exit_reason']}**\nExit: ${ex['exit_price']:,.2f}")
        webhook.add_embed(embed)

    # 2. Scan Phase
    for symbol in symbols:
        bars = exchange.fetch_ohlcv(symbol, '1h', limit=100)
        df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
        res = generate_signals(df)
        
        if res['verdict'] != "NEUTRAL":
            sent, obi = get_sentiment(symbol), get_obi(exchange, symbol)
            if sent >= 0.5 and obi >= 0.1:
                ledger = load_ledger()
                if not any(t['symbol'] == symbol for t in ledger['active_trades']):
                    ledger['active_trades'].append({
                        "symbol": symbol, "side": res['verdict'], 
                        "entry": res['entry'], "sl": res['sl'], "tp": res['tp']
                    })
                    save_ledger(ledger)
                    embed = DiscordEmbed(title=f"🚀 NEW SIGNAL: {symbol}", color="1e90ff")
                    embed.add_embed_field(name="Plan", value=f"Entry: ${res['entry']:,.2f}\nSL: ${res['sl']:,.2f}\nTP: ${res['tp']:,.2f}")
                    webhook.add_embed(embed)

    # 3. Heartbeat Logic (9/10 TechSolute Style)
    if len(webhook.get_embeds()) == 0:
        # If no news, send the heartbeat message
        heartbeat = DiscordEmbed(title="💓 ChainForge System Heartbeat", color="7289da")
        heartbeat.set_description("“With ChainForge, Patience is directly proportional to Profit.”")
        heartbeat.add_embed_field(name="Status", value="🟢 Active & Scanning")
        heartbeat.add_embed_field(name="Time (UTC)", value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
        heartbeat.set_footer(text="Your bot is still busy forging quality setups for you.")
        webhook.add_embed(heartbeat)

    webhook.execute()

if __name__ == "__main__":
    run()
