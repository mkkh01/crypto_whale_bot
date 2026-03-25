import requests

def get_price(coin="bitcoin"):
    try:
        coin_map = {
            "btc": "bitcoin",
            "eth": "ethereum",
            "sol": "solana",
            "xrp": "ripple",
            "doge": "dogecoin",
            "bnb": "binancecoin"
        }
        coin_id = coin_map.get(coin.lower(), coin.lower())
        response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd", timeout=10)
        data = response.json()
        return float(data[coin_id]['usd'])
    except:
        return None
