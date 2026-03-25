import json
import os

FILE = "sent_news.json"

def load_sent():
    if os.path.exists(FILE):
        with open(FILE) as f:
            return set(json.load(f))
    return set()

def save_sent(sent_ids):
    with open(FILE, 'w') as f:
        json.dump(list(sent_ids), f)

def is_news_sent(news_id):
    return news_id in load_sent()

def save_news(news_id):
    sent = load_sent()
    sent.add(news_id)
    save_sent(sent)
