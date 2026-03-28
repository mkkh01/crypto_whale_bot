"""
═══════════════════════════════════════════════════════════
   البوت الرئيسي - Crypto Whale Bot (نسخة محدثة)
═══════════════════════════════════════════════════════════
"""

import logging
import asyncio
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


# ══════════════════════════════════════════════════════════
# وظيفة الفحص (مركزية - تستخدم للأتمتة واليدوي)
# ══════════════════════════════════════════════════════════

async def check_news_job(context: ContextTypes.DEFAULT_TYPE):
    """وظيفة فحص الأخبار"""
    try:
        logger.info("🔍 جاري فحص الأخبار...")
        
        # 1. جلب الأخبار
        all_news = fetcher.fetch_all()
        
        if not all_news:
            logger.info("📭 لا توجد أخبار من المصادر")
            return "no_news"
        
        # 2. تصفية الأخبار المرسلة مسبقاً
        new_news = [n for n in all_news if not storage.is_sent(n["id"])]
        
        if not new_news:
            logger.info("📭 جميع الأخبار تم إرسالها مسبقاً")
            return "all_sent"
        
        logger.info(f"📰 تم العثور على {len(new_news)} أخبار جديدة")
        
        # 3. تحليل وإرسال الأخبار المهمة
        sent_count = 0
        skipped_count = 0
        
        for news in new_news:
            if sent_count >= MAX_NEWS_PER_CHECK:
                break
            
            # تحليل الخبر
            analysis = analyzer.analyze(news)
            
            # التحقق من الأهمية
            if analysis["importance"] < MIN_IMPORTANCE_TO_SEND:
                storage.mark_as_sent(news["id"])
                skipped_count += 1
                continue
            
            # توليد الإشارة
            signal = signal_generator.generate(analysis)
            
            # تنسيق الرسالة
            message = format_news_message(analysis, signal)
            
            # إضافة زر
            keyboard = [
                [InlineKeyboardButton("🔗 قراءة المزيد", url=analysis["link"])]
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
            await asyncio.sleep(1)
        
        logger.info(f"📤 تم إرسال {sent_count} | تم تخطي {skipped_count}")
        return f"sent:{sent_count}"
        
    except Exception as e:
        logger.error(f"❌ خطأ في فحص الأخبار: {e}")
        return f"error:{str(e)[:30]}"


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

بوت الأخبار التحليلي للعملات الرقمية

✅ تم تفعيل الفحص التلقائي
🔄 سيتم فحص الأخبار كل دقيقة
⭐ سيتم إرسال الأخبار المهمة فقط

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
أرسل /help لعرض الأوامر
"""
    
    # بدء الفحص التلقائي
    try:
        if context.job_queue:
            existing_jobs = context.job_queue.get_jobs_by_name("news_check")
            if not existing_jobs:
                context.job_queue.run_repeating(
                    check_news_job,
                    interval=CHECK_INTERVAL,
                    first=5,
                    name="news_check"
                )
                logger.info("✅ تم بدء الفحص التلقائي")
        else:
            logger.warning("⚠️ JobQueue غير متاح")
    except Exception as e:
        logger.error(f"❌ خطأ في بدء الفحص التلقائي: {e}")
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=welcome,
        parse_mode="Markdown"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر الحالة"""
    has_jobs = False
    if context.job_queue:
        jobs = context.job_queue.get_jobs_by_name("news_check")
        has_jobs = bool(jobs)
    
    status = "🟢 يعمل" if has_jobs else "🔴 متوقف"
    
    message = f"""
┌─────────────────────────────────┐
│   📊 حالة البوت                │
└─────────────────────────────────┘

{status}
🕐 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔄 فترة الفحص: كل {CHECK_INTERVAL} ثانية
⭐ عتبة الإرسال: أهمية ≥ {MIN_IMPORTANCE_TO_SEND}
📝 أخبار محفوظة: {storage.get_count()}
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
    
    coin_map = {
        "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
        "BNB": "binancecoin", "XRP": "ripple", "ADA": "cardano",
        "DOGE": "dogecoin", "DOT": "polkadot", "LINK": "chainlink",
        "LTC": "litecoin", "POL": "matic-network", "AVAX": "avalanche-2",
        "UNI": "uniswap", "ATOM": "cosmos", "NEAR": "near",
        "APT": "aptos", "SUI": "sui", "ARB": "arbitrum",
        "OP": "optimism",
    }
    
    coin_id = coin_map.get(symbol)
    if not coin_id:
        await update.message.reply_text(
            f"❌ العملة {symbol} غير مدعومة\n\n"
            "المدعومة: BTC ETH SOL BNB XRP ADA DOGE DOT LINK LTC POL AVAX"
        )
        return
    
    wait_msg = await update.message.reply_text(f"⏳ جاري جلب سعر {symbol}...")
    
    try:
        import requests
        
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if coin_id in data:
                price = data[coin_id]["usd"]
                change = data[coin_id].get("usd_24hr_change", 0)
                change_emoji = "🟢" if change >= 0 else "🔴"
                
                message = f"""
┌─────────────────────────────────┐
│   💰 سعر {symbol}               │
└─────────────────────────────────┘

💵 السعر: ${price:,.2f}
{change_emoji} تغير 24س: {change:+.2f}%
🕐 الوقت: {datetime.now().strftime('%H:%M:%S')}
"""
                await wait_msg.edit_text(message, parse_mode="Markdown")
            else:
                await wait_msg.edit_text(f"❌ لم يتم العثور على بيانات {symbol}")
        else:
            await wait_msg.edit_text(f"❌ خطأ في جلب البيانات (رمز {response.status_code})")
            
    except requests.exceptions.Timeout:
        await wait_msg.edit_text("❌ انتهت مهلة الاتصال، حاول لاحقاً")
    except Exception as e:
        await wait_msg.edit_text(f"❌ خطأ: {str(e)[:50]}")


async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر قائمة المراقبة"""
    message = """
┌─────────────────────────────────┐
│   👁️ قائمة المراقبة            │
└─────────────────────────────────┘

العملات الرئيسية:
₿ BTC | ⟠ ETH | ◎ SOL | 🔶 BNB
✕ XRP | 🔵 ADA | 🐕 DOGE | ⬡ DOT

العملات الثانوية:
⬡ LINK | Ł LTC | 🟣 POL | 🔺 AVAX
🦄 UNI | ⚛️ ATOM | 🔵 NEAR | 🟢 APT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 يتم مراقبة الأخبار تلقائياً
"""
    await update.message.reply_text(message, parse_mode="Markdown")


async def force_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر الفحص اليدوي"""
    wait_msg = await update.message.reply_text("🔄 جاري الفحص اليدوي...")
    
    try:
        # فحص مباشر بدون job_queue
        result = await check_news_job(context)
        
        if result == "no_news":
            await wait_msg.edit_text("📭 لا توجد أخبار من المصادر حالياً")
        elif result == "all_sent":
            await wait_msg.edit_text("📭 جميع الأخبار الحالية تم إرسالها مسبقاً\n\n💡 أرسل /reset لمسح المحفوظات")
        elif result.startswith("sent:"):
            count = result.split(":")[1]
            await wait_msg.edit_text(f"✅ تم إرسال {count} أخبار جديدة")
        elif result.startswith("error:"):
            err = result.split(":")[1]
            await wait_msg.edit_text(f"❌ خطأ: {err}")
        else:
            await wait_msg.edit_text("📭 لا توجد أخبار مهمة الآن")
            
    except Exception as e:
        await wait_msg.edit_text(f"❌ خطأ: {str(e)[:50]}")
        logger.error(f"❌ خطأ في الفحص اليدوي: {e}")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر مسح الأخبار المحفوظة"""
    count = storage.clear_all()
    await update.message.reply_text(
        f"✅ تم مسح {count} خبر محفوظ\n"
        "🔄 أرسل /force لفحص فوري"
    )


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر إيقاف الفحص التلقائي"""
    try:
        if context.job_queue:
            jobs = context.job_queue.get_jobs_by_name("news_check")
            if jobs:
                for job in jobs:
                    job.schedule_removal()
                await update.message.reply_text("⏹️ تم إيقاف الفحص التلقائي\nأرسل /start لإعادة التشغيل")
            else:
                await update.message.reply_text("ℹ️ الفحص التلقائي متوقف بالفعل")
        else:
            await update.message.reply_text("ℹ️ JobQueue غير متاح")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)[:30]}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر المساعدة"""
    message = """
┌─────────────────────────────────┐
│   📖 دليل الاستخدام             │
└─────────────────────────────────┘

الأوامر الأساسية:
├─ /start - تشغيل البوت
├─ /status - حالة البوت
├─ /stop - إيقاف الفحص
└─ /help - هذه المساعدة

أوامر الأسعار:
├─ /price BTC - سعر بيتكوين
├─ /price ETH - سعر إيثريوم
└─ /price <رمز> - أي عملة

أوامر متقدمة:
├─ /force - فحص يدوي فوري
├─ /reset - مسح المحفوظات
└─ /watchlist - قائمة المراقبة

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 الفحص التلقائي كل دقيقة
⭐ إرسال أهمية ≥ 7 فقط
"""
    await update.message.reply_text(message, parse_mode="Markdown")


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
    
    # بدء البوت
    logger.info("🚀 البوت جاهز!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
