import json
import os

FILE = "sent_news.json"

def load_sent():
    try:
        if os.path.exists(FILE):
            with open(FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return set(data)
                return set()
        return set()
    except:
        return set()

def save_sent(sent_ids):
    try:
        with open(FILE, 'w') as f:
            json.dump(list(sent_ids), f)
    except:
        pass

def is_news_sent(news_id):
    return news_id in load_sent()

def save_news(news_id):
    sent = load_sent()
    sent.add(news_id)
    save_sent(sent)
