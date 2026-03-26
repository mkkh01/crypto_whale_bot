import hashlib
import random
import time

def fetch_news(limit=5):
    """
    أخبار تجريبية فقط - تعمل 100%
    """
    # أخبار تجريبية متنوعة
    test_news = [
        {
            'title': '🚨 SEC Files Lawsuit Against Binance, BNB Drops 8%',
            'link': 'https://cointelegraph.com/news/sec-sues-binance',
            'source': 'cointelegraph.com'
        },
        {
            'title': '💰 Bitcoin Surges to $73,000 as ETF Inflows Hit Record',
            'link': 'https://cointelegraph.com/news/bitcoin-etf-record',
            'source': 'cointelegraph.com'
        },
        {
            'title': '🏦 Federal Reserve Signals Rate Cuts, Crypto Markets Rally',
            'link': 'https://reuters.com/fed-rate-cuts',
            'source': 'reuters.com'
        },
        {
            'title': '🔒 Major Exchange Hack: $200 Million in ETH Stolen',
            'link': 'https://thehackernews.com/crypto-hack',
            'source': 'thehackernews.com'
        },
        {
            'title': '📈 Ethereum ETF Approval Expected Next Week',
            'link': 'https://decrypt.co/ethereum-etf-approval',
            'source': 'decrypt.co'
        },
        {
            'title': '⚡ Solana Network Suffers Outage, SOL Drops 5%',
            'link': 'https://cryptoslate.com/solana-outage',
            'source': 'cryptoslate.com'
        },
        {
            'title': '🇺🇸 Trump Announces Pro-Crypto Policy, Bitcoin Jumps',
            'link': 'https://politico.com/trump-crypto',
            'source': 'politico.com'
        }
    ]
    
    # إضافة طابع زمني لمنع التكرار
    timestamp = int(time.time() / 60)
    
    news_list = []
    for item in test_news[:limit]:
        unique_string = f"{item['link']}_{timestamp}"
        news_id = hashlib.md5(unique_string.encode()).hexdigest()
        news_list.append({
            'id': news_id,
            'title': item['title'],
            'link': item['link'],
            'source': item['source']
        })
    
    return news_list

fetch_all_news = fetch_news
