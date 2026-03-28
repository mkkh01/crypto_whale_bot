"""
═══════════════════════════════════════════════════════════
   البوت الرئيسي - Crypto Whale Bot
═══════════════════════════════════════════════════════════
"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    JobQueue,
)

from config import (
    BOT_TOKEN,
    CHAT_ID,
    MIN_IMPORTANCE_TO_SEND,
    MAX_NEWS_PER_CHECK,
    CHECK_INTERVAL,
    CRYPTO_MAP,
)
from fetcher import fetcher
from analyzer import analyzer
from signal_generator import signal_generator
from storage import storage

# ══════════════════════════════════════════════════════════
# إعداد التسجيل (Logging)
# ══════════════════════════════════════════════════════════

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════
# دوال تنسيق الرسائل
# ══════════════════════════════════════════════════════════

def format_news_message(analysis: dict, signal: dict) -> str:
    """تنسيق رسالة الخبر"""
    message = f"""
┌─────────────────────────────────┐
│   🐋 بوت الأخبار التحليلي      │
└─────────────────────────────────┘

📰 **العنوان (AR):**
{analysis['title_ar']}

📝 **العنوان (EN):**
_{analysis['title_en']}_

🔗 **الرابط:** [اقرأ المزيد]({analysis['link']})

┌─────────────────────────────────┐
│ 📊 بيانات التحليل              │
└─────────────────────────────────┘

🪙 **العملات:** {analysis['crypto_display']}
🏷️ **التصنيف:** {analysis['category']} ({analysis['category_en']})
{analysis['sentiment_emoji']} **المشاعر:** {analysis['sentiment']} ({analysis['sentiment_score']})
{analysis['importance_stars']} **الأهمية:** {analysis['importance']}/10
📢 **المصدر:** {analysis['source']}

┌─────────────────────────────────┐
│ 🎯 إشارة التداول               │
└─────────────────────────────────┘

{signal['emoji']} **الإشارة:** {signal['signal']}
📊 **نسبة الثقة:** {signal['confidence']}%
💡 **السبب:** {signal['reason']}
⏰ **الإجراء:** {signal['action']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    return message


def format_status_message() -> str:
    """تنسيق رسالة الحالة"""
    return f"""
┌─────────────────────────────────┐
│   📊 حالة البوت                │
└─────────────────────────────────┘

🟢 **الحالة:** يعمل
🕐 **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔄 **فترة الفحص:** كل {CHECK_INTERVAL} ثانية
⭐ **عتبة الإرسال:** أهمية ≥ {MIN_IMPORTANCE_TO_SEND}
📝 **أخبار محفوظة:** {storage.get_count()}
📡 **المصادر:** {len(RSS_SOURCES)} مصدر

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**الأوامر المتاحة:**
/start - تشغيل البوت
/status - حالة البوت
/price <عملة> - سعر العملة
/watchlist - قائمة المراقبة
/force - فحص يدوي فوري
/reset - مسح الأخبار المحفوظة
/stop - إيقاف الفحص التلقائي
/help - المساعدة
"""


# ══════════════════════════════════════════════════════════
# معالجات الأوامر
# ══════════════════════════════════════════════════════════

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البدء"""
    chat_id = update.effective_chat.id
    
    welcome = """
┌─────────────────────────────────┐
│   🐋 مرحباً بك!               │
└─────────────────────────────────┘

**بوت الأخبار التحليلي للعملات الرقمية**

✅ تم تفعيل الفحص التلقائي
🔄 سيتم فحص الأخبار كل دقيقة
⭐ سيتم إرسال الأخبار المهمة فقط

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
أرسل /help لعرض الأوامر
"""
    
    # بدء الفحص التلقائي إذا لم يكن بدأ
    if not context.job_queue.get_jobs_by_name("news_check"):
        context.job_queue.run_repeating(
            check_news_job,
            interval=CHECK_INTERVAL,
            first=1,
            name="news_check"
        )
        logger.info(f"✅ تم بدء الفحص التلقائي للدردشة {chat_id}")
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=welcome,
        parse_mode="Markdown"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر الحالة"""
    jobs = context.job_queue.get_jobs_by_name("news_check")
    status = "🟢 يعمل" if jobs else "🔴 متوقف"
    
    message = f"""
┌─────────────────────────────────┐
│   📊 حالة البوت                │
└─────────────────────────────────┘

{status}
🕐 **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔄 **فترة الفحص:** كل {CHECK_INTERVAL} ثانية
⭐ **عتبة الإرسال:** أهمية ≥ {MIN_IMPORTANCE_TO_SEND}
📝 **أخبار محفوظة:** {storage.get_count()}
"""
    await update.message.reply_text(message, parse_mode="Markdown")


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر سعر العملة"""
    if not context.args:
        await update.message.reply_text(
            "📝 الاستخدام: /price <رمز العملة>\n"
            "مثال: /price BTC"
        )
        return
    
    symbol = context.args[0].upper()
    
    # محاولة جلب السعر من API مجاني
    try:
        import requests
        response = requests.get(
            f"https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": get_coinGecko_id(symbol),
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            coin_id = get_coinGecko_id(symbol)
            if coin_id in data:
                price = data[coin_id]["usd"]
                change = data[coin_id].get("usd_24h_change", 0)
                change_emoji = "🟢" if change >= 0 else "🔴"
                
                message = f"""
┌─────────────────────────────────┐
│   💰 سعر {symbol}               │
└─────────────────────────────────┘

💵 **السعر:** ${price:,.2f}
{change_emoji} **تغير 24س:** {change:+.2f}%
🕐 **الوقت:** {datetime.now().strftime('%H:%M:%S')}
"""
                await update.message.reply_text(message, parse_mode="Markdown")
            else:
                await update.message.reply_text(f"❌ لم يتم العثور على {symbol}")
        else:
            await update.message.reply_text("❌ خطأ في جلب البيانات")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")


def get_coinGecko_id(symbol: str) -> str:
    """تحويل الرمز إلى معرف CoinGecko"""
    ids = {
        "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
        "BNB": "binancecoin", "XRP": "ripple", "ADA": "cardano",
        "DOGE": "dogecoin", "DOT": "polkadot", "LINK": "chainlink",
        "LTC": "litecoin", "POL": "matic-network", "AVAX": "avalanche-2",
        "UNI": "uniswap", "ATOM": "cosmos", "NEAR": "near",
        "APT": "aptos", "SUI": "sui", "ARB": "arbitrum",
        "OP": "optimism",
    }
    return ids.get(symbol, symbol.lower())


async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر قائمة المراقبة"""
    watchlist = """
┌─────────────────────────────────┐
│   👁️ قائمة المراقبة            │
└─────────────────────────────────┘

**العملات الرئيسية:**
₿ BTC | ⟠ ETH | ◎ SOL | 🔶 BNB
✕ XRP | 🔵 ADA | 🐕 DOGE | ⬡ DOT

**العملات الثانوية:**
⬡ LINK | Ł LTC | 🟣 POL | 🔺 AVAX
🦄 UNI | ⚛️ ATOM | 🔵 NEAR | 🟢 APT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 يتم مراقبة الأخبار المتعلقة بهذه العملات تلقائياً
"""
    await update.message.reply_text(watchlist, parse_mode="Markdown")


async def force_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر الفحص اليدوي"""
    await update.message.reply_text("🔄 جاري الفحص اليدوي...")
    
    # تنفيذ الفحص فوراً
    await check_news_job(context)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر مسح الأخبار المحفوظة"""
    count = storage.clear_all()
    await update.message.reply_text(
        f"✅ تم مسح {count} خبر محفوظ\n"
        "🔄 سيتم إعادة إرسال الأخبار القديمة إذا ظهرت"
    )


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر إيقاف الفحص التلقائي"""
    jobs = context.job_queue.get_jobs_by_name("news_check")
    if jobs:
        for job in jobs:
            job.schedule_removal()
        await update.message.reply_text("⏹️ تم إيقاف الفحص التلقائي\nأرسل /start لإعادة التشغيل")
    else:
        await update.message.reply_text("ℹ️ الفحص التلقائي متوقف بالفعل")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر المساعدة"""
    help_text = """
┌─────────────────────────────────┐
│   📖 دليل الاستخدام             │
└─────────────────────────────────┘

**الأوامر الأساسية:**
├─ /start - تشغيل البوت والفحص التلقائي
├─ /status - عرض حالة البوت
├─ /stop - إيقاف الفحص التلقائي
└─ /help - عرض هذه المساعدة

**أوامر الأسعار:**
├─ /price BTC - سعر بيتكوين
├─ /price ETH - سعر إيثريوم
└─ /price <رمز> - أي عملة

**أوامر متقدمة:**
├─ /force - فحص يدوي فوري
├─ /reset - مسح الأخبار المحفوظة
└─ /watchlist - قائمة المراقبة

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **ملاحظات:**
• يتم فحص الأخبار كل دقيقة
• يتم إرسال الأخبار ذات الأهمية ≥ 7 فقط
• كل خبر يتضمن تحليل وإشارة تداول
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")


# ══════════════════════════════════════════════════════════
# وظيفة الفحص الدوري
# ══════════════════════════════════════════════════════════

async def check_news_job(context: ContextTypes.DEFAULT_TYPE):
    """وظيفة فحص الأخبار الدورية"""
    try:
        logger.info("🔍 جاري فحص الأخبار...")
        
        # 1. جلب الأخبار
        all_news = fetcher.fetch_all()
        
        if not all_news:
            logger.info("📭 لا توجد أخبار جديدة")
            return
        
        # 2. تصفية الأخبار المرسلة مسبقاً
        new_news = [n for n in all_news if not storage.is_sent(n["id"])]
        
        if not new_news:
            logger.info("📭 جميع الأخبار تم إرسالها مسبقاً")
            return
        
        logger.info(f"📰 تم العثور على {len(new_news)} أخبار جديدة")
        
        # 3. تحليل وإرسال الأخبار المهمة
        sent_count = 0
        
        for news in new_news:
            if sent_count >= MAX_NEWS_PER_CHECK:
                break
            
            # تحليل الخبر
            analysis = analyzer.analyze(news)
            
            # التحقق من الأهمية
            if analysis["importance"] < MIN_IMPORTANCE_TO_SEND:
                storage.mark_as_sent(news["id"])
                continue
            
            # توليد الإشارة
            signal = signal_generator.generate(analysis)
            
            # تنسيق الرسالة
            message = format_news_message(analysis, signal)
            
            # إضافة أزرار
            keyboard = [
                [
                    InlineKeyboardButton("🔗 قراءة المزيد", url=analysis["link"]),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # إرسال الرسالة
            try:
                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=message,
                    parse_mode="Markdown",
                    disable_web_page_preview=True,
                    reply_markup=reply_markup
                )
                sent_count += 1
                logger.info(f"✅ تم إرسال: {analysis['title_en'][:50]}...")
            except Exception as e:
                logger.error(f"❌ خطأ في الإرسال: {e}")
            
            # وضع علامة كمرسل
            storage.mark_as_sent(news["id"])
            
            # انتظار قصير بين الرسائل
            import asyncio
            await asyncio.sleep(1)
        
        logger.info(f"📤 تم إرسال {sent_count} أخبار")
        
    except Exception as e:
        logger.error(f"❌ خطأ في فحص الأخبار: {e}")


# ══════════════════════════════════════════════════════════
# نقطة الدخول الرئيسية
# ══════════════════════════════════════════════════════════

def main():
    """تشغيل البوت"""
    logger.info("🐋 بدء تشغيل بوت الأخبار التحليلي...")
    
    # إنشاء التطبيق
    app = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة معالجات الأوامر
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("price", price_command))
    app.add_handler(CommandHandler("watchlist", watchlist_command))
    app.add_handler(CommandHandler("force", force_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # بدء البوت مع وضع polling
    logger.info("🚀 البوت جاهز!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
