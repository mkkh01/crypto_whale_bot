import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from news_fetcher import fetch_all_news
from analyzer import analyze_news
from signal_generator import generate_signal
from storage import save_news, is_news_sent
from price_monitor import get_price

TOKEN = os.environ.get("BOT_TOKEN", "8715770007:AAGmDggZubTr6p1u9qJJX5QBgqPknmQBC44")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🐋 **بوت الحوت - النظام الاحترافي**\n\n"
        "📊 **الأوامر المتاحة:**\n"
        "/latest - آخر 5 أخبار مع تحليل\n"
        "/signal - إشارات تداول لحظية\n"
        "/price BTC - سعر البيتكوين\n"
        "/watchlist - قائمة المراقبة\n\n"
        "⚡ **الإشارات ترسل تلقائياً كل 15 دقيقة**",
        parse_mode='Markdown'
    )

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🔍 جاري جلب وتحليل الأخبار...")
    news_list = fetch_all_news(limit=5)
    if not news_list:
        await msg.edit_text("❌ لم يتم العثور على أخبار")
        return
    for news in news_list:
        analysis = analyze_news(news['title'])
        signal = generate_signal(analysis, news)
        text = f"📰 **{news['title']}**\n\n"
        text += f"🏷️ {analysis['category']} | {analysis['sentiment']}\n"
        text += f"💰 العملات: {', '.join(analysis['coins'])}\n"
        text += f"⭐ الأهمية: {analysis['importance']}/10\n"
        text += f"🎯 **الإشارة:** {signal['action']} {signal['emoji']}\n"
        text += f"📌 الثقة: {signal['confidence']}%\n"
        text += f"🔗 [المصدر]({news['link']})"
        await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True)
        await asyncio.sleep(0.8)
    await msg.delete()

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    coin = args[0].upper() if args else "BTC"
    price = get_price(coin)
    if price:
        await update.message.reply_text(f"💰 {coin}: ${price:,.2f}")
    else:
        await update.message.reply_text(f"❌ لم يتم العثور على {coin}")

async def auto_signals(context: ContextTypes.DEFAULT_TYPE):
    news_list = fetch_all_news(limit=3)
    for news in news_list:
        if not is_news_sent(news['id']):
            analysis = analyze_news(news['title'])
            signal = generate_signal(analysis, news)
            if signal['confidence'] > 70:
                text = f"🚨 **إشارة تداول عاجلة** 🚨\n\n"
                text += f"📰 {news['title']}\n"
                text += f"🎯 {signal['action']} {signal['emoji']}\n"
                text += f"📊 الثقة: {signal['confidence']}%\n"
                text += f"💡 {signal['reason']}"
                await context.bot.send_message(chat_id=os.environ.get("CHAT_ID"), text=text, parse_mode='Markdown')
                save_news(news['id'])

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("latest", latest))
    app.add_handler(CommandHandler("price", price_command))
    
    if app.job_queue:
        app.job_queue.run_repeating(auto_signals, interval=900, first=10)
    
    print("🐋 بوت الحوت شغال...")
    app.run_polling()

if __name__ == "__main__":
    main()
