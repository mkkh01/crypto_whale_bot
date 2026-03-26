import os
import asyncio
import requests
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from news_fetcher import fetch_all_news
from analyzer import analyze_news, get_signal_explanation
from signal_generator import generate_signal
from storage import load_sent, save_sent, is_news_sent, save_news

TOKEN = os.environ.get("BOT_TOKEN", "8715770007:AAGmDggZubTr6p1u9qJJX5QBgqPknmQBC44")
CHAT_ID = None

# متغيرات لمنع التوقف
last_check_time = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    await update.message.reply_text(
        "🐋 **بوت الحوت - النظام الاحترافي**\n\n"
        "📊 **الأوامر المتاحة:**\n"
        "/latest - آخر الأخبار مع تحليل (بالعربية)\n"
        "/signal - إشارة تداول فورية\n"
        "/price BTC - سعر البيتكوين\n"
        "/watchlist - أسعار العملات المفضلة\n\n"
        "⚡ **الإشارات تُرسل فوراً عند ظهور أخبار مهمة (تحديث كل 10 ثوانٍ)**",
        parse_mode='Markdown'
    )

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🔍 جاري جلب الأخبار...")
    news_list = fetch_all_news(limit=5)
    if not news_list:
        await msg.edit_text("❌ لا توجد أخبار حالياً")
        return
    for news in news_list:
        analysis = analyze_news(news['title'])
        text = f"📰 *{analysis['title_ar']}*\n\n"
        text += f"🏷️ *التصنيف:* {analysis['category']}\n"
        text += f"📊 *المشاعر:* {analysis['sentiment']}\n"
        text += f"💰 *العملات:* {', '.join(analysis['coins'])}\n"
        text += f"⭐ *الأهمية:* {analysis['importance']}/10\n"
        text += f"📌 *المصدر:* {news['source']}\n"
        text += f"🔗 [رابط الخبر]({news['link']})"
        await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True)
        await asyncio.sleep(0.5)
    await msg.delete()

async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news_list = fetch_all_news(limit=1)
    if not news_list:
        await update.message.reply_text("❌ لا توجد أخبار حالياً")
        return
    news = news_list[0]
    analysis = analyze_news(news['title'])
    signal = generate_signal(analysis, news)
    explanation = get_signal_explanation(signal, analysis)
    
    text = f"🚨 **إشارة فورية**\n\n"
    text += f"📰 {analysis['title_ar']}\n"
    text += f"💰 العملات: {', '.join(analysis['coins'])}\n"
    text += f"🎯 {signal['action']} {signal['emoji']}\n"
    text += f"📊 الثقة: {signal['confidence']}%\n"
    text += f"💡 {signal['reason']}\n\n"
    text += f"{explanation}\n\n"
    text += f"🔗 [رابط الخبر]({news['link']})"
    
    await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True)

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

async def check_news_urgent(context: ContextTypes.DEFAULT_TYPE):
    """فحص الأخبار كل 10 ثوانٍ وإرسال الأخبار المهمة فوراً مع تفسير"""
    global CHAT_ID, last_check_time
    
    if not CHAT_ID:
        return
    
    current_time = time.time()
    if current_time - last_check_time < 5:
        return
    last_check_time = current_time
    
    try:
        news_list = await asyncio.wait_for(
            asyncio.to_thread(fetch_all_news, 8),
            timeout=12
        )
        
        sent_ids = load_sent()
        
        for news in news_list:
            if not is_news_sent(news['id']):
                analysis = analyze_news(news['title'])
                signal = generate_signal(analysis, news)
                
                # إرسال الأخبار ذات أهمية 3 أو أكثر
                if analysis['importance'] >= 3:
                    explanation = get_signal_explanation(signal, analysis)
                    
                    text = f"🚨 **خبر عاجل - تأثير على السوق** 🚨\n\n"
                    text += f"📰 {analysis['title_ar']}\n"
                    text += f"🏷️ {analysis['category']} | {analysis['sentiment']}\n"
                    text += f"💰 **العملات المتأثرة:** {', '.join(analysis['coins'])}\n"
                    text += f"⭐ **الأهمية:** {analysis['importance']}/10\n"
                    text += f"🎯 **الإشارة:** {signal['action']} {signal['emoji']}\n"
                    text += f"📊 **الثقة:** {signal['confidence']}%\n"
                    text += f"💡 {signal['reason']}\n\n"
                    text += f"{explanation}\n\n"
                    text += f"🔗 [رابط الخبر]({news['link']})"
                    
                    await context.bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown', disable_web_page_preview=True)
                    save_news(news['id'])
                    await asyncio.sleep(1)
                    
    except asyncio.TimeoutError:
        pass
    except Exception as e:
        print(f"خطأ: {e}")

def main():
    global CHAT_ID
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("latest", latest))
    app.add_handler(CommandHandler("signal", signal_command))
    app.add_handler(CommandHandler("price", price_command))
    app.add_handler(CommandHandler("watchlist", watchlist_command))
    
    # تحديث كل 10 ثوانٍ (أسرع استجابة للأخبار المهمة)
    if app.job_queue:
        app.job_queue.run_repeating(check_news_urgent, interval=10, first=5)
    
    print("🐋 بوت الحوت شغال - جلب وإرسال تلقائي كل 10 ثوانٍ...")
    app.run_polling()

if __name__ == "__main__":
    main()
