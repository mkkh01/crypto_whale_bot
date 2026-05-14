"""
═══════════════════════════════════════════════════════════
   خادم الويب الوهمي + إعادة تشغيل تلقائية
═══════════════════════════════════════════════════════════
"""

import os
import logging
import threading
import time
from flask import Flask
from config import KEEP_ALIVE_PORT

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/alive')
def alive():
    return "🐋 Bot is alive!", 200


@app.route('/')
def index():
    return "<h1>🐋 Crypto Whale Bot</h1><p>Running...</p>", 200


def run_bot():
    """تشغيل البوت مع إعادة تشغيل تلقائية"""
    while True:
        try:
            logger.info("🚀 بدء تشغيل البوت...")
            from bot import main
            main()
        except Exception as e:
            logger.error(f"❌ البوت توقف: {e}")
        logger.info("🔄 إعادة تشغيل البوت بعد 10 ثواني...")
        time.sleep(10)


def run_flask():
    """تشغيل خادم الويب"""
    app.run(
        host='0.0.0.0',
        port=KEEP_ALIVE_PORT,
        debug=False,
        use_reloader=False
    )


if __name__ == "__main__":
    # تشغيل البوت في خيط منفصل مع إعادة تشغيل تلقائية
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info(f"✅ تم بدء خادم Keep-Alive على المنفذ {KEEP_ALIVE_PORT}")
    
    # تشغيل Flask في الخيط الرئيسي
    run_flask()