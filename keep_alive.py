"""
═══════════════════════════════════════════════════════════
   خادم الويب الوهمي + البوت
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


@app.route('/<path:path>')
def catch_all(path):
    """يلتقط أي مسار آخر ويمنع 404"""
    return "<h1>🐋 Crypto Whale Bot</h1><p>Running...</p>", 200


def start_web_server():
    app.run(
        host='0.0.0.0',
        port=KEEP_ALIVE_PORT,
        debug=False,
        use_reloader=False
    )


if __name__ == "__main__":
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    logger.info(f"✅ خادم Keep-Alive على المنفذ {KEEP_ALIVE_PORT}")
    
    from bot import main
    main()