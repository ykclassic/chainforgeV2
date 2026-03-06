import os
import ccxt
import pandas as pd
from core.engine import generate_signals
from core.intelligence import get_sentiment, get_obi
from discord_webhook import DiscordWebhook, DiscordEmbed

def run():
    exchange = ccxt.bitget()
    webhook = DiscordWebhook(url=os.getenv('DISCORD_WEBHOOK'))
    embed = DiscordEmbed(title="🛡️ AEGIS | Nexus Intelligence Suite", color="00e5ff")
    
    for symbol in ["BTC/USDT", "ETH/USDT", "SOL/USDT", "SUI/USDT"]:
        bars = exchange.fetch_ohlcv(symbol, '1h', limit=100)
        df = pd.DataFrame(bars, columns=['ts', 'o', 'h', 'l', 'close', 'v'])
        
        # 1. Technical Signal
        res = generate_signals(df)
        
        # 2. Intelligence Filter
        sent = get_sentiment(symbol)
        obi = get_obi(exchange, symbol)
        
        # 3. Decision
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

    webhook.add_embed(embed)
    webhook.execute()

if __name__ == "__main__":
    run()
