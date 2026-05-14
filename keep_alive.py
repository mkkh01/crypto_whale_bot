"""
═══════════════════════════════════════════════════════════
   خادم الويب الوهمي (يعمل في خيط ثانوي)
   البوت يعمل في الخيط الرئيسي
═══════════════════════════════════════════════════════════
"""

import logging
import threading
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


def start_web_server():
    """تشغيل خادم الويب في خيط منفصل"""
    app.run(
        host='0.0.0.0',
        port=KEEP_ALIVE_PORT,
        debug=False,
        use_reloader=False
    )


if __name__ == "__main__":
    # تشغيل الويب في خيط ثانوي
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    logger.info(f"✅ خادم Keep-Alive يعمل على المنفذ {KEEP_ALIVE_PORT}")
    
    # تشغيل البوت في الخيط الرئيسي
    from bot import main
    main()