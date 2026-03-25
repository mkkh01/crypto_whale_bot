import os
import asyncio
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from news_fetcher import fetch_all_news
from analyzer import analyze_news
from signal_generator import generate_signal
from storage import save_news, is_news_sent

TOKEN = os.environ.get("BOT_TOKEN", "8715770007:AAGmDggZubTr6p1u9qJJX5QBgqPknmQBC44")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🐋 **بوت الحوت - النظام الاحترافي**\n\n"
        "📊 **الأوامر المتاحة:**\n"
        "/latest - آخر الأخبار مع تحليل (بالعربية)\n"
        "/signal - إشارة تداول فورية\n"
        "/price BTC - سعر البيتكوين\n"
        "/watchlist - أسعار العملات المفضلة\n\n"
        "⚡ **الإشارات تُرسل تلقائياً كل 15 دقيقة**",
        parse_mode='Markdown'
    )

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🔍 جاري جلب الأخبار...")
    news_list = fetch_all_news(limit=3)
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
    text = f"🚨 **إشارة فورية**\n\n"
    text += f"📰 {analysis['title_ar']}\n"
    text += f"💰 العملات: {', '.join(analysis['coins'])}\n"
    text += f"🎯 {signal['action']} {signal['emoji']}\n"
    text += f"📊 الثقة: {signal['confidence']}%\n"
    text += f"💡 {signal['reason']}"
    await update.message.reply_text(text, parse_mode='Markdown')

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    coin = args[0].lower() if args else "btc"
    
    # تسميات CoinPaprika
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
    except Exception as e:
        await update.message.reply_text(f"❌ لم يتم العثور على {coin.upper()}")

async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = {
        "btc-bitcoin": "BTC",
        "eth-ethereum": "ETH",
        "sol-solana": "SOL",
        "bnb-binance-coin": "BNB",
        "xrp-xrp": "XRP",
        "doge-dogecoin": "DOGE"
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

async def auto_signals(context: ContextTypes.DEFAULT_TYPE):
    news_list = fetch_all_news(limit=3)
    for news in news_list:
        if not is_news_sent(news['id']):
            analysis = analyze_news(news['title'])
            signal = generate_signal(analysis, news)
            if signal['confidence'] > 70:
                text = f"🚨 **إشارة تداول عاجلة** 🚨\n\n"
                text += f"📰 {analysis['title_ar']}\n"
                text += f"💰 العملات: {', '.join(analysis['coins'])}\n"
                text += f"🎯 {signal['action']} {signal['emoji']}\n"
                text += f"📊 الثقة: {signal['confidence']}%\n"
                text += f"💡 {signal['reason']}"
                await context.bot.send_message(chat_id=os.environ.get("CHAT_ID"), text=text, parse_mode='Markdown')
                save_news(news['id'])

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("latest", latest))
    app.add_handler(CommandHandler("signal", signal_command))
    app.add_handler(CommandHandler("price", price_command))
    app.add_handler(CommandHandler("watchlist", watchlist_command))
    
    if app.job_queue:
        app.job_queue.run_repeating(auto_signals, interval=900, first=10)
    
    print("🐋 بوت الحوت شغال...")
    app.run_polling()

if __name__ == "__main__":
    main()
