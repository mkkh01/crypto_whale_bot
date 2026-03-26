import os
import asyncio
import requests
import time
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from analyzer import analyze_news, get_signal_explanation
from signal_generator import generate_signal
from storage import load_sent, save_sent, is_news_sent, save_news

# ========== خادم ويب بسيط لـ Render ==========
from flask import Flask
from threading import Thread

app_web = Flask('')

@app_web.route('/')
def home():
    return "🐋 Bot is running - Crypto Whale Bot"

@app_web.route('/alive')
def alive():
    return "I am alive!"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app_web.run(host='0.0.0.0', port=port)

Thread(target=run_web).start()
print("✅ خادم الويب شغال على المنفذ 10000")
# ===============================================

TOKEN = os.environ.get("BOT_TOKEN", "8715770007:AAGXV9GyGACyEeSEKGUTMNXwqaOZ14UQKcM")
CHAT_ID = None

# أخبار تجريبية مضمونة (تتغير باستمرار)
DEMO_NEWS = [
    {"title": "🚨 SEC Files Lawsuit Against Binance, BNB Drops 8%", "source": "cointelegraph.com"},
    {"title": "💰 Bitcoin Surges to $73,000 as ETF Inflows Hit Record", "source": "cointelegraph.com"},
    {"title": "🏦 Federal Reserve Signals Rate Cuts, Crypto Markets Rally", "source": "reuters.com"},
    {"title": "🔒 Major Exchange Hack: $200 Million in ETH Stolen", "source": "thehackernews.com"},
    {"title": "📈 Ethereum ETF Approval Expected Next Week", "source": "decrypt.co"},
    {"title": "⚡ Solana Network Suffers Outage, SOL Drops 5%", "source": "cryptoslate.com"},
    {"title": "🇺🇸 Trump Announces Pro-Crypto Policy, Bitcoin Jumps", "source": "politico.com"},
    {"title": "🌍 IMF Warns of Global Recession Risk, Bitcoin Drops", "source": "reuters.com"},
    {"title": "🔐 Quantum Computing Threatens Bitcoin Security", "source": "wired.com"},
    {"title": "📊 MicroStrategy Buys Another 10,000 BTC", "source": "newsbtc.com"},
    {"title": "💥 Bitcoin Dumps 5% After Fed Chair Comments", "source": "bloomberg.com"},
    {"title": "🚀 Ethereum Layer 2 Transaction Volume Hits New ATH", "source": "cointelegraph.com"},
]

def fetch_news(limit=8):
    """جلب أخبار تجريبية مع IDs متغيرة باستمرار"""
    # طابع زمني يتغير كل 10 ثوانٍ
    timestamp = int(time.time() / 10)
    
    # اختيار أخبار عشوائية
    random.seed(timestamp)
    selected = random.sample(DEMO_NEWS, min(limit, len(DEMO_NEWS)))
    
    news_list = []
    for i, item in enumerate(selected):
        # ID فريد لكل خبر (يتغير باستمرار)
        unique_id = f"{item['title']}_{timestamp}_{i}"
        news_id = hashlib.md5(unique_id.encode()).hexdigest()
        
        news_list.append({
            'id': news_id,
            'title': item['title'],
            'link': f"https://{item['source']}/news/{news_id[:8]}",
            'source': item['source']
        })
    
    return news_list

fetch_all_news = fetch_news

# متغيرات للتحكم
last_check_time = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    print(f"✅ تم تسجيل CHAT_ID: {CHAT_ID}")
    
    await update.message.reply_text(
        "🐋 **بوت الحوت - النظام الاحترافي**\n\n"
        "✅ **البوت يعمل الآن تلقائياً!**\n\n"
        f"📱 **معرف الدردشة:** `{CHAT_ID}`\n\n"
        "⚡ **سيتم إرسال الأخبار كل 15 ثانية**\n\n"
        "📌 **الأوامر:**\n"
        "/price BTC - سعر البيتكوين\n"
        "/watchlist - أسعار العملات\n"
        "/reset - مسح الذاكرة\n"
        "/stop - إيقاف الإرسال",
        parse_mode='Markdown'
    )
    
    # إرسال خبر تجريبي فوري للتأكد
    await asyncio.sleep(2)
    await test_news(context)

async def test_news(context: ContextTypes.DEFAULT_TYPE):
    """إرسال خبر تجريبي للتأكد من عمل البوت"""
    global CHAT_ID
    if not CHAT_ID:
        return
    
    text = "🧪 **خبر تجريبي - البوت يعمل!**\n\n"
    text += "✅ إذا وصلتك هذه الرسالة، البوت يعمل بشكل صحيح.\n"
    text += "⚡ ستصل الأخبار الحقيقية خلال 15 ثانية."
    
    await context.bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    coin = args[0].lower() if args else "btc"
    
    coin_map = {"btc": "btc-bitcoin", "eth": "eth-ethereum", "sol": "sol-solana", "bnb": "bnb-binance-coin"}
    coin_id = coin_map.get(coin, f"{coin}-{coin}")
    
    try:
        response = requests.get(f"https://api.coinpaprika.com/v1/tickers/{coin_id}", timeout=10)
        data = response.json()
        price = data['quotes']['USD']['price']
        await update.message.reply_text(f"💰 **{coin.upper()}/USD**\nالسعر: ${price:,.2f}", parse_mode='Markdown')
    except:
        await update.message.reply_text(f"❌ لم يتم العثور على {coin.upper()}")

async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = {"btc-bitcoin": "BTC", "eth-ethereum": "ETH", "sol-solana": "SOL", "bnb-binance-coin": "BNB"}
    text = "📊 **قائمة المراقبة**\n\n"
    for coin_id, symbol in coins.items():
        try:
            response = requests.get(f"https://api.coinpaprika.com/v1/tickers/{coin_id}", timeout=10)
            price = response.json()['quotes']['USD']['price']
            text += f"💰 {symbol}: ${price:,.2f}\n"
        except:
            text += f"❌ {symbol}: غير متاح\n"
    await update.message.reply_text(text, parse_mode='Markdown')

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if os.path.exists("sent_news.json"):
            os.remove("sent_news.json")
        await update.message.reply_text("🔄 **تم مسح الذاكرة**\n✅ ستصل الأخبار خلال 15 ثانية", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = None
    await update.message.reply_text("⏸️ **تم إيقاف الإرسال**\nأرسل /start للتشغيل", parse_mode='Markdown')

async def check_news_urgent(context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID, last_check_time
    
    if not CHAT_ID:
        return
    
    current_time = time.time()
    if current_time - last_check_time < 12:
        return
    last_check_time = current_time
    
    try:
        news_list = fetch_all_news(5)
        
        if not news_list:
            print(f"📭 [{time.strftime('%H:%M:%S')}] لا توجد أخبار")
            return
        
        sent_ids = load_sent()
        new_count = 0
        
        for news in news_list:
            if not is_news_sent(news['id']):
                analysis = analyze_news(news['title'])
                signal = generate_signal(analysis, news)
                explanation = get_signal_explanation(signal, analysis)
                
                text = f"🚨 **خبر جديد** 🚨\n\n"
                text += f"📰 {analysis['title_ar']}\n"
                text += f"🏷️ {analysis['category']} | {analysis['sentiment']}\n"
                text += f"💰 **العملات:** {', '.join(analysis['coins'])}\n"
                text += f"⭐ **الأهمية:** {analysis['importance']}/10\n"
                text += f"🎯 **الإشارة:** {signal['action']} {signal['emoji']}\n"
                text += f"📊 **الثقة:** {signal['confidence']}%\n"
                text += f"💡 {signal['reason']}\n\n"
                text += f"{explanation}\n\n"
                text += f"📌 **المصدر:** {news['source']}\n"
                text += f"🔗 [رابط الخبر]({news['link']})"
                
                await context.bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown', disable_web_page_preview=True)
                save_news(news['id'])
                new_count += 1
                print(f"📨 [{time.strftime('%H:%M:%S')}] تم إرسال خبر: {analysis['title_ar'][:50]}...")
                await asyncio.sleep(1)
        
        if new_count > 0:
            print(f"✅ [{time.strftime('%H:%M:%S')}] إجمالي {new_count} أخبار جديدة")
        else:
            print(f"🔍 [{time.strftime('%H:%M:%S')}] فحص {len(news_list)} خبر، لا جديد")
            
    except Exception as e:
        print(f"⚠️ [{time.strftime('%H:%M:%S')}] خطأ: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price_command))
    app.add_handler(CommandHandler("watchlist", watchlist_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("stop", stop_command))
    
    if app.job_queue:
        app.job_queue.run_repeating(check_news_urgent, interval=15, first=5)
    
    print("🐋 بوت الحوت شغال - إرسال تلقائي كل 15 ثانية...")
    print("✅ خادم الويب شغال")
    app.run_polling()

if __name__ == "__main__":
    main()
