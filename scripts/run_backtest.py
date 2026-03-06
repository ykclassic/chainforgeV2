import os
import ccxt
import pandas as pd
from core.engine import generate_signals
from core.intelligence import get_sentiment_score, get_order_book_imbalance
from discord_webhook import DiscordWebhook, DiscordEmbed

ASSETS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "SUI/USDT"]

def run_nexus_scan():
    exchange = ccxt.bitget()
    webhook_url = os.getenv('DISCORD_WEBHOOK')
    webhook = DiscordWebhook(url=webhook_url)
    embed = DiscordEmbed(title="🛡️ AEGIS: Nexus Intelligence Suite", color="03a9f4")

    for symbol in ASSETS:
        # 1. Fetch Data
        bars = exchange.fetch_ohlcv(symbol, '1h', limit=100)
        df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
        
        # 2. Get Signal & Intelligence
        res = generate_signals(df)
        sentiment = get_sentiment_score(symbol)
        obi = get_order_book_imbalance(exchange, symbol)
        
        # 3. Decision Logic (9/10 Standard)
        status = res['verdict']
        if res['verdict'] == "BUY / LONG":
            if sentiment < 0.5 or obi < 0.1:
                status = "⚠️ BLOCKED (Weak Sentiment/OB)"
            else:
                status = "🚀 APPROVED LONG"

        # 4. Format Discord Field
        field_val = (f"Price: **${res['price']:,.2f}**\n"
                     f"`{res['diag']}`\n"
                     f"Sentiment: `{sentiment:.2f}` | OBI: `{obi:.2f}`")
        embed.add_embed_field(name=f"{symbol}: {status}", value=field_val, inline=False)

    webhook.add_embed(embed)
    webhook.execute()

if __name__ == "__main__":
    run_nexus_scan()
