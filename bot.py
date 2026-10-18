from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
from flask import Flask
import threading
import logging
import os

# راه‌اندازی وب‌سرور برای Render
app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is running"


def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


threading.Thread(target=run_server, daemon=True).start()

# تنظیمات لاگین
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات فعال است.")


if __name__ == "__main__":
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    application.run_polling()
