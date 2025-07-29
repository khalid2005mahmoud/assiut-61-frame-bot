from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, MessageHandler, filters, CommandHandler,
    ContextTypes, CallbackQueryHandler
)
from PIL import Image
from io import BytesIO
from datetime import time
import logging
import random

# ✅ إعدادات البوت
TOKEN = '8207083317:AAHtSJ9pkUzyaZzzAFicXePj7t_OyNgP0vU'
ADMIN_ID = 1049380446
BOT_USERNAME = "@ka194_framebot"

# ✅ تسجيل الدخول
logging.basicConfig(level=logging.INFO)

# ✅ تحميل الفريم
frame = Image.open("frame.png").convert("RGBA")

# ✅ بيانات الإحصائيات
user_ids = set()
usernames = {}
photo_count = 0
daily_images = []
user_share_jobs = {}  # لتتبع الـ job لكل مستخدم

# ✅ اقتصاص الصورة لتكون مربعة
def crop_to_square(im):
    width, height = im.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    return im.crop((left, top, left + side, top + side))

# ✅ رسائل النجاح العشوائية
SUCCESS_MESSAGES = [
    "✅ تم تركيب الفريم بنجاح!\nالف مبروك هانت 🥳",
    "✅ الفريم جاهز 🎓\nألف مبروك و بالتوفيق دايمًا!",
    "✅ تم إضافة الفريم بنجاح!\nجهز نفسك للذكريات الجميلة 🎉"
]

# ✅ /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📸 أبدأ صنع الفريم الآن")],
        [KeyboardButton("📥 تحميل PNG"), KeyboardButton("🌐 فتح الموقع")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "👋 أهلاً وسهلاً في بوت فريم التخرج لدفعة ١٩٤ 🎓\n\n"
        "🔽 اضغط على الزر بالأسفل لتصميم صورتك بالفريم.\n"
        "💡 يفضل أن تكون الصورة مربعة (1:1) للحصول على أفضل نتيجة.\n\n"
        "\n"
        "📦 لو حابب تعمل الفريم يدويًا:\n"
        "\t•\tتقدر تحمّل الفريم بصيغة PNG وتعدّل عليه بنفسك.\n"
        "\t•\tأو تستخدم الويبسايت ترفع فيه الصورة وتعدلها يدويًا.\n\n"
        "🧑‍💻 Design and Bot by: @abdomahmood",
        reply_markup=reply_markup
    )

# ✅ زرار الإجراء من Inline buttons
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    query = update.callback_query

    if query.data == "get_png":
        try:
            with open("frame.png", "rb") as f:
                await query.message.reply_document(
                    document=f,
                    filename="graduation_frame.png",
                    caption="🖼️ لو مش حابب تبعت صورتك، ده الفريم بصيغة PNG ✨"
                )
        except Exception as e:
            await query.message.reply_text("❌ حصل خطأ أثناء تحميل الفريم.")
            logging.error(f"خطأ في تحميل الفريم: {e}")

    elif query.data == "send_photo":
        await query.message.reply_text("📸 أرسل صورتك الآن وسأضيف لك الفريم تلقائيًا!")

# ✅ أمر /get_png
async def get_png_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("frame.png", "rb") as f:
            await update.message.reply_document(
                document=f,
                filename="graduation_frame.png",
                caption="🖼️ الفريم بصيغة PNG لو حابب تعدل عليه يدويًا ✨"
            )
    except Exception as e:
        await update.message.reply_text("❌ حصل خطأ أثناء تحميل الفريم.")
        logging.error(f"خطأ في /get_png: {e}")

# ✅ أمر /website
async def website_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌐 تقدر تعدل صورتك يدويًا على الموقع:\nhttps://graduation194.github.io/Frame/")

# ✅ أمر /new_frame
async def send_photo_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 أرسل صورتك الآن وسأضيف لك الفريم تلقائيًا!")

# ✅ دالة مشاركة البوت
async def send_share_message(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="📣 شارك البوت ده مع صحابك وخليهم يعملوا فريمهم كمان\nhttps://t.me/ka194_framebot"
    )

# ✅ معالجة الصور
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global photo_count
    user = update.message.from_user
    user_ids.add(user.id)
    photo_count += 1

    username = f"@{user.username}" if user.username else f"{user.first_name}"
    usernames[user.id] = username

    await update.message.reply_text("📥 تم استلام الصورة... جاري تركيب الفريم ⏳")
    await update.message.reply_text("⏳")

    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()

    image = Image.open(BytesIO(photo_bytes)).convert("RGBA")
    cropped = crop_to_square(image).resize(frame.size)
    combined = Image.alpha_composite(cropped, frame)

    output = BytesIO()
    combined.save(output, format="PNG")
    output.seek(0)

    await update.message.reply_photo(
        photo=output,
        caption=random.choice(SUCCESS_MESSAGES),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 إنشاء فريم جديد", callback_data="send_photo")],
            [InlineKeyboardButton("✏️ تعديل يدوي", url="https://graduation194.github.io/Frame/")],
            [InlineKeyboardButton("📢 شارك البوت مع دفعتك", url="https://t.me/ka194_framebot")]
        ])
    )

    daily_images.append(BytesIO(output.getvalue()))

    await update.message.reply_text("لو في أي مشكلة اتواصل مع: @abdomahmood 😊")

    try:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=output,
            caption=f"👤 صورة جديدة من {username}"
        )
    except Exception as e:
        logging.warning(f"فشل إرسال الصورة للإدمن: {e}")

    # ✅ إلغاء أي Job مشاركة سابق لهذا المستخدم
    old_job = user_share_jobs.get(user.id)
    if old_job:
        old_job.schedule_removal()

    # ✅ جدولة مشاركة جديدة بعد 5 دقايق من آخر تفاعل
    new_job = context.job_queue.run_once(send_share_message, when=300, chat_id=update.message.chat_id)
    user_share_jobs[user.id] = new_job

# ✅ التعامل مع الرسائل النصية
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📸 أبدأ صنع الفريم الآن":
        await send_photo_prompt(update, context)
        return
    elif text == "📥 تحميل PNG":
        await get_png_command(update, context)
        return
    elif text == "🌐 فتح الموقع":
        await website_command(update, context)
        return

    await update.message.reply_text("📤 أرسل صورة فقط لإضافة الفريم.")

# ✅ تقرير يومي
async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
    global photo_count, daily_images

    if photo_count == 0:
        message = "📊 لم يتم استخدام البوت حتى الآن اليوم."
    else:
        user_list = "\n".join([f"• {name}" for name in usernames.values()])
        message = (
            f"📊 تقرير اليوم:\n"
            f"📸 عدد الصور المُعالجة: {photo_count}\n"
            f"👥 عدد المستخدمين: {len(user_ids)}\n"
            f"👤 المستخدمون:\n{user_list}"
        )

    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=message)

        for img in daily_images:
            img.seek(0)
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=img)

    except Exception as e:
        logging.warning(f"فشل إرسال التقرير اليومي: {e}")

    photo_count = 0
    daily_images = []

# ✅ إعداد الأوامر
async def setup_bot(app):
    commands = [
        BotCommand("new_frame", "🧩 إنشاء فريم جديد في ثواني"),
        BotCommand("get_png", "📥 تحميل الفريم (PNG)"),
        BotCommand("website", "🌐 الموقع التفاعلي"),
        BotCommand("start", "ابدأ من جديد")
    ]
    await app.bot.set_my_commands(commands)

# ✅ Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new_frame", send_photo_prompt))
    app.add_handler(CommandHandler("get_png", get_png_command))
    app.add_handler(CommandHandler("website", website_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.job_queue.run_daily(send_daily_report, time=time(hour=0, minute=0))
    app.post_init = setup_bot

    app.run_polling()

if __name__ == "__main__":
    main()