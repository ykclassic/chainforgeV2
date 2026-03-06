import os
import ccxt
import pandas as pd
from core.engine import generate_signals
from core.intelligence import get_sentiment, get_obi
from core.tracker import check_exits, load_ledger, save_ledger
from discord_webhook import DiscordWebhook, DiscordEmbed

def run():
    # 1. Initialize Exchange & Webhook
    exchange = ccxt.bitget({'enableRateLimit': True})
    webhook_url = os.getenv('DISCORD_WEBHOOK')
    
    if not webhook_url:
        print("❌ Error: DISCORD_WEBHOOK environment variable not set.")
        return

    webhook = DiscordWebhook(url=webhook_url, username="🛡️ AEGIS Intelligence")
    symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "SUI/USDT"]
    
    print("🚀 Starting AEGIS Cycle...")

    # 2. PHASE 1: MONITOR ACTIVE TRADES
    try:
        # Fetch latest prices for all tracked symbols
        current_prices = {}
        for s in symbols:
            ticker = exchange.fetch_ticker(s)
            current_prices[s] = ticker['last']
        
        # Check if any ledger entries hit SL/TP
        exits = check_exits(current_prices)
        for ex in exits:
            color = "2ed573" if "PROFIT" in ex['exit_reason'] else "ff4757"
            embed = DiscordEmbed(title=f"🚨 EXIT: {ex['symbol']}", color=color)
            embed.add_embed_field(name="Result", value=f"**{ex['exit_reason']}**\nExit Price: ${ex['exit_price']:,.2f}")
            webhook.add_embed(embed)
            print(f"📉 Exit detected for {ex['symbol']} ({ex['exit_reason']})")
            
    except Exception as e:
        print(f"⚠️ Error during monitoring phase: {e}")

    # 3. PHASE 2: SCAN FOR NEW SIGNALS
    for symbol in symbols:
        try:
            # Fetch OHLCV Data
            bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
            df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Generate Signals (using engine logic)
            res = generate_signals(df)
            
            if res['verdict'] != "NEUTRAL":
                # Apply Intelligence Filters (Sentiment & OBI)
                sent = get_sentiment(symbol)
                obi = get_obi(exchange, symbol)
                
                # TechSolute Quality Standard: Requires positive sentiment and buy-side pressure
                if sent >= 0.5 and obi >= 0.1:
                    ledger = load_ledger()
                    
                    # Prevent duplicate entries for the same asset
                    if not any(t['symbol'] == symbol for t in ledger['active_trades']):
                        new_trade = {
                            "symbol": symbol,
                            "side": res['verdict'],
                            "entry": res['entry'],
                            "sl": res['sl'],
                            "tp": res['tp']
                        }
                        ledger['active_trades'].append(new_trade)
                        save_ledger(ledger)

                        # Create Discord Notification
                        embed = DiscordEmbed(title=f"🚀 NEW SIGNAL: {symbol}", color="1e90ff")
                        embed.add_embed_field(name="Trade Plan", value=(
                            f"Side: **{res['verdict']}**\n"
                            f"Entry: `${res['entry']:,.2f}`\n"
                            f"Stop Loss: `${res['sl']:,.2f}`\n"
                            f"Take Profit: `${res['tp']:,.2f}`"
                        ), inline=False)
                        webhook.add_embed(embed)
                        print(f"🔥 New signal approved for {symbol} at ${res['entry']:,.2f}")
                    else:
                        print(f"ℹ️ Signal for {symbol} ignored: Already in an active trade.")
                else:
                    print(f"⚠️ Signal for {symbol} rejected by Intelligence Filter (Sent: {sent}, OBI: {obi})")
        
        except Exception as e:
            print(f"⚠️ Error scanning {symbol}: {e}")

    # 4. FINAL STEP: DISCORD EXECUTION
    # 9/10 Quality: Only execute if there is at least one embed to send
    if len(webhook.get_embeds()) > 0:
        response = webhook.execute()
        if response.status_code == 200 or response.status_code == 204:
            print("✅ Discord report sent successfully.")
        else:
            print(f"❌ Failed to send Discord report. Status: {response.status_code}")
    else:
        print("🔍 Cycle Complete: No active exits or new signals found. Standing by.")

if __name__ == "__main__":
    run()
