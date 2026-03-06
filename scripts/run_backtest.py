import os
import ccxt
import pandas as pd
from core.engine import generate_signals
from core.intelligence import get_sentiment, get_obi
from discord_webhook import DiscordWebhook, DiscordEmbed

def run():
    exchange = ccxt.bitget()
    webhook_url = os.getenv('DISCORD_WEBHOOK')
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK not found.")
        return
        
    webhook = DiscordWebhook(url=webhook_url)
    embed = DiscordEmbed(title="🛡️ AEGIS | Nexus Intelligence Suite", color="00e5ff")
    
    # Standard Assets
    for symbol in ["BTC/USDT", "ETH/USDT", "SOL/USDT", "SUI/USDT"]:
        try:
            bars = exchange.fetch_ohlcv(symbol, '1h', limit=100)
            # FIX: Use full names 'open', 'high', 'low', 'volume'
            df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
            
            # 1. Technical Signal
            res = generate_signals(df)
            
            # 2. Intelligence Filter
            sent = get_sentiment(symbol)
            obi = get_obi(exchange, symbol)
            
            # 3. Decision Logic
            status = res['verdict']
            if res['verdict'] == "BUY / LONG":
                if sent < 0.5 or obi < 0.1:
                    status = "⚠️ BLOCKED (Weak Sentiment/OB)"
                else:
                    status = "✅ APPROVED LONG"

            embed.add_embed_field(
                name=f"{symbol}: {status}",
                value=f"Price: **${res['price']:,.2f}**\n`{res['diag']}`\nSent: `{sent:.2f}` | OBI: `{obi:.2f}`",
                inline=False
            )
        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    webhook.add_embed(embed)
    webhook.execute()

if __name__ == "__main__":
    run()
