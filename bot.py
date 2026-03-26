import os
import asyncio
import requests
import time
import hashlib
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from news_fetcher import fetch_all_news
from analyzer import analyze_news, get_signal_explanation
from signal_generator import generate_signal
from storage import load_sent, save_sent, is_news_sent, save_news

# ========== خادم ويب لـ Render ==========
from flask import Flask
from threading import Thread

app_web = Flask('')

@app_web.route('/')
def home():
    return "🐋 Crypto Whale Bot is running"

@app_web.route('/alive')
def alive():
    return "I am alive!"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app_web.run(host='0.0.0.0', port=port)

Thread(target=run_web).start()
print("✅ خادم الويب شغال على المنفذ 10000")
# ========================================

TOKEN = os.environ.get("BOT_TOKEN", "8715770007:AAGXV9GyGACyEeSEKGUTMNXwqaOZ14UQKcM")
CHAT_ID = None
last_check_time = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    print(f"✅ تم تسجيل CHAT_ID: {CHAT_ID}")
    
    await update.message.reply_text(
        "🐋 **بوت الحوت - النظام الاحترافي**\n\n"
        "✅ **البوت يعمل الآن تلقائياً!**\n\n"
        f"📱 **معرف الدردشة:** `{CHAT_ID}`\n\n"
        "📊 **سيتم إرسال الأخبار المهمة إليك فور ظهورها:**\n"
        "• تحليل فوري للخبر\n"
        "• تحديد العملات المتأثرة\n"
        "• إشارة شراء/بيع/ترقب\n"
        "• تفسير سبب الإشارة\n\n"
        "⚡ **الأخبار تصل تلقائياً كل 15 ثانية**\n\n"
        "📌 **الأوامر المساعدة:**\n"
        "/price BTC - سعر البيتكوين\n"
        "/watchlist - أسعار العملات المفضلة\n"
        "/reset - مسح ذاكرة الأخبار المرسلة\n"
        "/stop - إيقاف الإرسال التلقائي",
        parse_mode='Markdown'
    )
    
    # إرسال خبر تجريبي فوري للتأكد
    await asyncio.sleep(1)
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
    
    coin_map = {
        "btc": "btc-bitcoin",
        "eth": "eth-ethereum",
        "sol": "sol-solana",
        "xrp": "xrp-xrp",
        "doge": "doge-dogecoin",
        "bnb": "bnb-binance-coin"
    }
    
    coin_id = coin_map.get(coin, f"{coin}-{coin}")
    
    try:
        response = requests.get(f"https://api.coinpaprika.com/v1/tickers/{coin_id}", timeout=10)
        data = response.json()
        price = data['quotes']['USD']['price']
        symbol = coin.upper()
        await update.message.reply_text(f"💰 **{symbol}/USD**\nالسعر: ${price:,.2f}", parse_mode='Markdown')
    except:
        await update.message.reply_text(f"❌ لم يتم العثور على {coin.upper()}")

async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = {
        "btc-bitcoin": "BTC",
        "eth-ethereum": "ETH",
        "sol-solana": "SOL",
        "bnb-binance-coin": "BNB",
    }
    
    text = "📊 **قائمة المراقبة**\n\n"
    
    for coin_id, symbol in coins.items():
        try:
            response = requests.get(f"https://api.coinpaprika.com/v1/tickers/{coin_id}", timeout=10)
            data = response.json()
            price = data['quotes']['USD']['price']
            text += f"💰 {symbol}: ${price:,.2f}\n"
        except:
            text += f"❌ {symbol}: غير متاح\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مسح جميع الأخبار المرسلة سابقاً"""
    try:
        if os.path.exists("sent_news.json"):
            os.remove("sent_news.json")
            await update.message.reply_text(
                "🔄 **تم مسح ذاكرة الأخبار المرسلة**\n\n"
                "✅ ستصل إليك الأخبار الجديدة خلال 15 ثانية",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "ℹ️ **لا توجد أخبار مرسلة سابقاً**\n\n"
                "✅ البوت جاهز لاستقبال الأخبار الجديدة",
                parse_mode='Markdown'
            )
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = None
    print(f"⏸️ تم إيقاف الإرسال التلقائي بواسطة المستخدم")
    await update.message.reply_text(
        "⏸️ **تم إيقاف الإرسال التلقائي**\n"
        "لإعادة التشغيل، أرسل /start مرة أخرى",
        parse_mode='Markdown'
    )

async def check_news_urgent(context: ContextTypes.DEFAULT_TYPE):
    """
    فحص الأخبار وإرسالها تلقائياً كل 15 ثانية
    """
    global CHAT_ID, last_check_time
    
    if not CHAT_ID:
        return
    
    current_time = time.time()
    if current_time - last_check_time < 10:
        return
    last_check_time = current_time
    
    try:
        # جلب 10 أخبار
        news_list = fetch_all_news(10)
        print(f"📡 [{time.strftime('%H:%M:%S')}] جلب {len(news_list)} خبر")
        
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
                text += f"💰 **العملات المتأثرة:** {', '.join(analysis['coins'])}\n"
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
    
    # تحديث كل 15 ثانية
    if app.job_queue:
        app.job_queue.run_repeating(check_news_urgent, interval=15, first=5)
    
    print("🐋 بوت الحوت شغال - إرسال تلقائي كل 15 ثانية...")
    print("✅ خادم الويب شغال")
    print("📱 انتظر إرسال /start لتسجيل معرف الدردشة")
    app.run_polling()

if __name__ == "__main__":
    main()
