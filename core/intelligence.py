# core/intelligence.py
import os
import requests

def get_sentiment(symbol): # Adjusted name
    """Phase 3: CryptoPanic Filter"""
    token = os.getenv('CRYPTOPANIC_KEY')
    coin = symbol.split('/')[0]
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={token}&currencies={coin}&filter=hot"
    try:
        data = requests.get(url, timeout=5).json()
        votes = [p.get('votes', {}) for p in data.get('results', [])]
        pos = sum([v.get('positive', 0) for v in votes])
        neg = sum([v.get('negative', 0) for v in votes])
        return pos / (pos + neg) if (pos + neg) > 0 else 0.5
    except:
        return 0.5

def get_obi(exchange, symbol): # Adjusted name
    """Phase 3: Order Book Imbalance"""
    try:
        ob = exchange.fetch_order_book(symbol, limit=20)
        bids = sum([x[1] for x in ob['bids']])
        asks = sum([x[1] for x in ob['asks']])
        return (bids - asks) / (bids + asks)
    except:
        return 0.0
