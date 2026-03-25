import requests

def get_price(coin="BTC"):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['price'])
    except:
        return None
