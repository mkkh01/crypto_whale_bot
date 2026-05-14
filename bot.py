"""
═══════════════════════════════════════════════════════════
   البوت الرئيسي - Crypto Whale Bot (Webhook)
═══════════════════════════════════════════════════════════
"""

import logging
import asyncio
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from config import (
    BOT_TOKEN,
    CHAT_ID,
    MIN_IMPORTANCE_TO_SEND,
    MAX_NEWS_PER_CHECK,
    CHECK_INTERVAL,
)
from fetcher import fetcher
from analyzer import analyzer
from signal_generator import signal_generator
from storage import storage

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', 5000))


def format_news_message(analysis: dict, signal: dict) -> str:
    message = f"""
┌─────────────────────────────────┐
│   🐋 بوت الأخبار التحليلي      │
└─────────────────────────────────┘

📰 العنوان (AR):
{analysis['title_ar']}

📝 العنوان (EN):
_{analysis['title_en']}_

🔗 الرابط: [اقرأ المزيد]({analysis['link']})

┌─────────────────────────────────┐
│ 📊 بيانات التحليل              │
└─────────────────────────────────┘

🪙 العملات: {analysis['crypto_display']}
🏷️ التصنيف: {analysis['category']} ({analysis['category_en']})
{analysis['sentiment_emoji']} المشاعر: {analysis['sentiment']} ({analysis['sentiment_score']})
{analysis['importance_stars']} الأهمية: {analysis['importance']}/10
📢 المصدر: {analysis['source']}

┌─────────────────────────────────┐
│ 🎯 إشارة التداول               │
└─────────────────────────────────┘

{signal['emoji']} الإشارة: {signal['signal']}
📊 نسبة الثقة: {signal['confidence']}%
💡 السبب: {signal['reason']}
⏰ الإجراء: {signal['action']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    return message


async def check_news_job(context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info("🔍 جاري فحص الأخبار...")
        all_news = fetcher.fetch_all()
        
        if not all_news:
            logger.info("📭 لا توجد أخبار")
            return
        
        new_news = [n for n in all_news if not storage.is_sent(n["id"])]
        
        if not new_news:
            logger.info("📭 جميع الأخبار مرسلة مسبقاً")
            return
        
        logger.info(f"📰 {len(new_news)} أخبار جديدة")
        sent_count = 0
        
        for news in new_news:
            if sent_count >= MAX_NEWS_PER_CHECK:
                break
            
            analysis = analyzer.analyze(news)
            
            if analysis["importance"] < MIN_IMPORTANCE_TO_SEND:
                storage.mark_as_sent(news["id"])
                continue
            
            signal = signal_generator.generate(analysis)
            message = format_news_message(analysis, signal)
            
            keyboard = [[InlineKeyboardButton("🔗 قراءة المزيد", url=analysis["link"])]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=message,
                    parse_mode="Markdown",
                    disable_web_page_preview=True,
                    reply_markup=reply_markup
                )
                sent_count += 1
                logger.info(f"✅ تم الإرسال: {analysis['title_en'][:50]}")
            except Exception as e:
                logger.error(f"❌ خطأ الإرسال: {e}")
            
            storage.mark_as_sent(news["id"])
            await asyncio.sleep(1)
        
        logger.info(f"📤 تم إرسال {sent_count}")
        
    except Exception as e:
        logger.error(f"❌ خطأ الفحص: {e}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    try:
        if context.job_queue:
            jobs = context.job_queue.get_jobs()
            has_check = any("news_check" in str(j.name) for j in jobs)
            if not has_check:
                context.job_queue.run_repeating(
                    check_news_job,
                    interval=CHECK_INTERVAL,
                    first=5,
                    name="news_check"
                )
                logger.info("✅ تم بدء الفحص التلقائي")
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
    
    await update.message.reply_text(
        """
┌─────────────────────────────────┐
│   🐋 مرحباً بك!               │
└─────────────────────────────────┘

بوت الأخبار التحليلي للعملات الرقمية

✅ تم تفعيل الفحص التلقائي
🔄 فحص كل دقيقة
⭐ إرسال الأخبار المهمة فقط

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
أرسل /help لعرض الأوامر
""", parse_mode="Markdown"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    has_jobs = False
    if context.job_queue:
        try:
            jobs = context.job_queue.get_jobs()
            has_jobs = len(jobs) > 0
        except:
            has_jobs = True
    
    status = "🟢 يعمل" if has_jobs else "🔴 متوقف"
    
    await update.message.reply_text(f"""
┌─────────────────────────────────┐
│   📊 حالة البوت                │
└─────────────────────────────────┘

{status}
🕐 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔄 فترة الفحص: كل {CHECK_INTERVAL} ثانية
⭐ عتبة الإرسال: أهمية ≥ {MIN_IMPORTANCE_TO_SEND}
📝 أخبار محفوظة: {storage.get_count()}
""", parse_mode="Markdown")


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("📝 الاستخدام: /price <رمز>\nمثال: /price BTC")
        return
    
    symbol = context.args[0].upper()
    coin_map = {
        "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
        "BNB": "binancecoin", "XRP": "ripple", "ADA": "cardano",
        "DOGE": "dogecoin", "DOT": "polkadot", "LINK": "chainlink",
        "LTC": "litecoin", "POL": "matic-network", "AVAX": "avalanche-2",
        "UNI": "uniswap", "ATOM": "cosmos", "NEAR": "near",
        "APT": "aptos", "SUI": "sui", "ARB": "arbitrum", "OP": "optimism",
    }
    
    coin_id = coin_map.get(symbol)
    if not coin_id:
        await update.message.reply_text(f"❌ العملة {symbol} غير مدعومة")
        return
    
    wait_msg = await update.message.reply_text(f"⏳ جاري جلب سعر {symbol}...")
    
    try:
        import requests
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"},
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            if coin_id in data:
                price = data[coin_id]["usd"]
                change = data[coin_id].get("usd_24hr_change", 0)
                emoji = "🟢" if change >= 0 else "🔴"
                await wait_msg.edit_text(f"""
┌─────────────────────────────────┐
│   💰 سعر {symbol}               │
└─────────────────────────────────┘

💵 السعر: ${price:,.2f}
{emoji} تغير 24س: {change:+.2f}%
🕐 {datetime.now().strftime('%H:%M:%S')}
""", parse_mode="Markdown")
            else:
                await wait_msg.edit_text(f"❌ لم يتم العثور على {symbol}")
        else:
            await wait_msg.edit_text(f"❌ خطأ (رمز {resp.status_code})")
    except Exception as e:
        await wait_msg.edit_text(f"❌ خطأ: {str(e)[:50]}")


async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
┌─────────────────────────────────┐
│   👁️ قائمة المراقبة            │
└─────────────────────────────────┘

₿ BTC | ⟠ ETH | ◎ SOL | 🔶 BNB
✕ XRP | 🔵 ADA | 🐕 DOGE | ⬡ DOT
⬡ LINK | Ł LTC | 🟣 POL | 🔺 AVAX
""", parse_mode="Markdown")


async def force_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wait_msg = await update.message.reply_text("🔄 جاري الفحص...")
    try:
        await check_news_job(context)
        await wait_msg.edit_text("✅ تم الفحص")
    except Exception as e:
        await wait_msg.edit_text(f"❌ خطأ: {str(e)[:50]}")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = storage.clear_all()
    await update.message.reply_text(f"✅ تم مسح {count} خبر\n🔄 أرسل /force")


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if context.job_queue:
            for job in context.job_queue.get_jobs():
                job.schedule_removal()
            await update.message.reply_text("⏹️ تم الإيقاف\nأرسل /start للتشغيل")
    except:
        await update.message.reply_text("❌ خطأ")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
┌─────────────────────────────────┐
│   📖 دليل الاستخدام             │
└─────────────────────────────────┘

├─ /start - تشغيل
├─ /status - الحالة
├─ /stop - إيقاف
├─ /help - المساعدة
├─ /price BTC - السعر
├─ /force - فحص يدوي
├─ /reset - مسح المحفوظات
└─ /watchlist - المراقبة
""", parse_mode="Markdown")


async def error_handler(update, context):
    error = context.error
    if "Conflict" in str(error) or "timed out" in str(error):
        return
    logger.error(f"❌ خطأ: {error}")


def main():
    logger.info("🐋 بدء تشغيل البوت (Webhook)...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_error_handler(error_handler)
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("price", price_command))
    app.add_handler(CommandHandler("watchlist", watchlist_command))
    app.add_handler(CommandHandler("force", force_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # بدء الفحص التلقائي
    app.job_queue.run_repeating(
        check_news_job,
        interval=CHECK_INTERVAL,
        first=10,
        name="news_check"
    )
    logger.info("✅ تم بدء الفحص التلقائي")
    
    logger.info("🚀 البوت جاهز!")
    
    # تشغيل بالـ Webhook بدل Polling (لا يسبب تعارض!)
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"https://crypto-whale-bot.onrender.com/{BOT_TOKEN}"
    )


if __name__ == "__main__":
    main()