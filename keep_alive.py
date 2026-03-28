"""
═══════════════════════════════════════════════════════════
   خادم الويب الوهمي - Keep Alive
═══════════════════════════════════════════════════════════
يحافظ على استمرار تشغيل التطبيق على Render
"""

from flask import Flask
from threading import Thread
import logging

from config import KEEP_ALIVE_PORT

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إنشاء تطبيق Flask خفيف
app = Flask(__name__)


@app.route('/alive')
def alive():
    """نقطة النهاية للفحص"""
    return "🐋 Crypto Whale Bot is alive!", 200


@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return """
    <html>
    <head><title>Crypto Whale Bot</title></head>
    <body style="text-align:center; padding-top:50px; font-family:Arial;">
        <h1>🐋 Crypto Whale Bot</h1>
        <p>✅ The bot is running!</p>
        <p>Go to <a href="/alive">/alive</a> for health check</p>
    </body>
    </html>
    """, 200


def run_keep_alive():
    """تشغيل خادم الويب في خيط منفصل"""
    logger.info(f"🌐 خادم Keep-Alive يعمل على المنفذ {KEEP_ALIVE_PORT}")
    app.run(
        host='0.0.0.0',
        port=KEEP_ALIVE_PORT,
        debug=False,
        use_reloader=False
    )


def start_keep_alive():
    """بدء خادم الويب في خيط منفصل"""
    thread = Thread(target=run_keep_alive, daemon=True)
    thread.start()
    logger.info("✅ تم بدء خادم Keep-Alive")
    return thread


if __name__ == "__main__":
    start_keep_alive()
    
    # تشغيل البوت الرئيسي
    from bot import main
    main()
