import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    filters,
)
from groq import Groq

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
You are the elite, slightly unhinged Chief Crypto Oracle and Top Trader.
When the user asks for a trade decision, generate a mock professional trading setup wrapped in intense sarcasm, technical jargon, and mysticism.

You MUST use this exact format in Persian (Farsi):

🪙 **جفت‌ارز:** [نام ارز]
📊 **جهت پوزیشن:** [LONG 🟢 / SHORT 🔴]
⚡ **لورج پیشنهادی:** [مثلاً 20x تا 50x]
📍 **نقطه ورود (Entry):** [یک عدد یا قیمت منطقی/طنز]
🛑 **حد زیان (Stop Loss):** [یک عدد مشخص + توضیح کوتاه طنز درباره شکار نقدینگی]
🎯 **حد سود (Take Profit):** [یک عدد مشخص + توضیح کوتاه طنز]

🔮 **تحلیل رمال برتر:**
[۲ الی ۳ جمله تحلیل خنده‌دار بر اساس پرایس اکشن، واگرایی یا رفتار نهنگ‌ها]

⚠️ **هشدار مهم حقوقی:**
این خروجی صرفاً جنبه سرگرمی و طنز دارد و به هیچ عنوان سیگنال، تحلیل یا پیشنهاد ریسک مالی نیست. مسئولیت تمام معاملات و مدیریت ریسک با خود کاربر است.

STRICT SAFETY RULES:
1. NO insults to intelligence, mental health, race, gender, or religion.
2. Keep it light-hearted and focused on crypto market trading humor.
"""


def generate_ai_text(user_prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.8,
            max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Groq API Error: {e}")
        return "کائنات امروز در حال به‌روزرسانی است! فعلاً لورج باز نکن و بخواب."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("🔮 فال روزانه کریپتو (رایگان)", callback_data="free_oracle")],
        [InlineKeyboardButton("⚡ استخاره تخصصی پوزیشن (1 Star ⭐)", callback_data="paid_oracle")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"سلام {user_name}! 🏛✨\n\n"
        "به **Crypto Oracle** (رمال بزرگ بازار) خوش اومدی.\n"
        "قبل از اینکه لورج ۵۰ باز کنی و حسابت صفر بشه، اول تکلیفت رو با کائنات مشخص کن!\n\n"
        "⚠️ *Not financial advice. For entertainment only.*"
    )
    await update.message.reply_text(
        welcome_text, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "free_oracle":
        prompt = "Give a short sarcastic crypto market verdict or horoscope in Persian."
        ai_response = generate_ai_text(prompt)
        await query.message.reply_text(ai_response)  # بدون parse_mode برای جلوگیری از خطای Markdown

    elif query.data == "paid_oracle":
        title = "استخاره تخصصی پوزیشن"
        description = "تأییدیه فوری کائنات برای لانگ یا شورت گرفتن قبل از لیکوئید شدن!"
        payload = "position_oracle_payload"
        currency = "XTR"  # Telegram Stars
        prices = [LabeledPrice("استخاره پوزیشن", 1)]

        await context.bot.send_invoice(
            chat_id=query.message.chat_id,
            title=title,
            description=description,
            payload=payload,
            provider_token="",  # برای Stars خالی بمونه
            currency=currency,
            prices=prices,
        )


async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.invoice_payload == "position_oracle_payload":
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Invalid payload")


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 🔧 باگ قبلی: query تعریف نشده بود
    message = update.effective_message
    prompt = (
        "Give a full trading setup with Entry, Stop Loss, Take Profit, "
        "and technical oracle analysis in Persian according to the SYSTEM_PROMPT."
    )
    ai_response = generate_ai_text(prompt)
    await message.reply_text(ai_response)


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(PreCheckoutQueryHandler(pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()