import hashlib
import random

def fetch_news(limit=2):
    test_news = [
        {
            'id': '1',
            'title': '🚨 BREAKING: SEC Files Lawsuit Against Binance, BNB Drops 8%',
            'link': 'https://cointelegraph.com/news/sec-sues-binance',
            'source': 'cointelegraph.com'
        },
        {
            'id': '2',
            'title': '💰 Bitcoin Surges to $73,000 as ETF Inflows Hit Record $1.2B',
            'link': 'https://cointelegraph.com/news/bitcoin-etf-record',
            'source': 'cointelegraph.com'
        },
        {
            'id': '3',
            'title': '🏦 Federal Reserve Signals Rate Cuts in September, Crypto Markets Rally',
            'link': 'https://reuters.com/fed-rate-cuts',
            'source': 'reuters.com'
        },
        {
            'id': '4',
            'title': '🔒 Major Exchange Hack: $200 Million in ETH Stolen from Hot Wallet',
            'link': 'https://thehackernews.com/crypto-hack',
            'source': 'thehackernews.com'
        },
        {
            'id': '5',
            'title': '📈 Ethereum ETF Approval Expected Next Week, Analysts Predict 30% Rally',
            'link': 'https://decrypt.co/ethereum-etf-approval',
            'source': 'decrypt.co'
        }
    ]
    
    random.shuffle(test_news)
    return test_news[:limit]

fetch_all_news = fetch_news
