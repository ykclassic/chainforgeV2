import os
import requests

def get_sentiment_score(symbol):
    """Phase 3: CryptoPanic News Sentiment"""
    api_key = os.getenv('CRYPTOPANIC_KEY')
    base = symbol.split('/')[0]
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={api_key}&currencies={base}&filter=hot"
    try:
        data = requests.get(url, timeout=5).json()
        # Parse positive/negative votes to calculate a score 0-1
        votes = [p.get('votes', {}) for p in data.get('results', [])]
        pos = sum([v.get('positive', 0) for v in votes])
        neg = sum([v.get('negative', 0) for v in votes])
        return pos / (pos + neg) if (pos + neg) > 0 else 0.5
    except:
        return 0.5

def get_order_book_imbalance(exchange, symbol):
    """Phase 3: L2 Order Book Imbalance"""
    try:
        ob = exchange.fetch_order_book(symbol, limit=50)
        bid_vol = sum([b[1] for b in ob['bids']])
        ask_vol = sum([a[1] for a in ob['asks']])
        return (bid_vol - ask_vol) / (bid_vol + ask_vol)
    except:
        return 0.0
