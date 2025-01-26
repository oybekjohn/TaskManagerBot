# File: profileRegister.py
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
import sqlite3
import pytz
import re

ASK_LANGUAGE, ASK_FIRST_NAME, ASK_LAST_NAME, ASK_AGE, ASK_PHONE, ASK_TIMEZONE, CONFIRMATION = range(7)

def validate_phone_number(phone_number):
    pattern = re.compile(r"^\+?[1-9]\d{1,14}$")
    return bool(pattern.match(phone_number))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("English"), KeyboardButton("Русский"), KeyboardButton("Oʻzbekcha")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Please select your language:\nПожалуйста, выберите язык:\nIltimos, tilni tanlang:", reply_markup=reply_markup)
    return ASK_LANGUAGE

async def ask_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['language'] = update.message.text.strip()
    if context.user_data['language'] == "English":
        await update.message.reply_text("Please enter your first name:")
    elif context.user_data['language'] == "Русский":
        await update.message.reply_text("Пожалуйста, введите ваше имя:")
    else:
        await update.message.reply_text("Ismingizni kiriting:")
    return ASK_FIRST_NAME

async def ask_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['first_name'] = update.message.text.strip()
    lang = context.user_data['language']
    if lang == "English":
        await update.message.reply_text("Now enter your last name:")
    elif lang == "Русский":
        await update.message.reply_text("Теперь введите вашу фамилию:")
    else:
        await update.message.reply_text("Endi familiyangizni kiriting:")
    return ASK_LAST_NAME

async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['last_name'] = update.message.text.strip()
    lang = context.user_data['language']
    if lang == "English":
        await update.message.reply_text("Enter your age:")
    elif lang == "Русский":
        await update.message.reply_text("Введите ваш возраст:")
    else:
        await update.message.reply_text("Yoshingizni kiriting:")
    return ASK_AGE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['age'] = int(update.message.text.strip())
    except ValueError:
        lang = context.user_data['language']
        if lang == "English":
            await update.message.reply_text("Please enter a valid age.")
        elif lang == "Русский":
            await update.message.reply_text("Введите действительный возраст.")
        else:
            await update.message.reply_text("Iltimos, toʻgʻri yosh kiriting.")
        return ASK_AGE

    keyboard = [[KeyboardButton("Share Phone Number", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    lang = context.user_data['language']
    if lang == "English":
        await update.message.reply_text("Please share your phone number:", reply_markup=reply_markup)
    elif lang == "Русский":
        await update.message.reply_text("Поделитесь вашим номером телефона:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Telefon raqamingizni ulashing:", reply_markup=reply_markup)
    return ASK_PHONE

async def ask_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        context.user_data['phone_number'] = update.message.contact.phone_number
    else:
        context.user_data['phone_number'] = update.message.text.strip()

    if not validate_phone_number(context.user_data['phone_number']):
        lang = context.user_data['language']
        if lang == "English":
            await update.message.reply_text("Invalid phone number. Please enter again.")
        elif lang == "Русский":
            await update.message.reply_text("Недействительный номер телефона. Попробуйте еще раз.")
        else:
            await update.message.reply_text("Telefon raqami noto'g'ri. Qaytadan kiriting.")
        return ASK_PHONE

    keyboard = [[KeyboardButton(tz) for tz in pytz.all_timezones[:4]],  # Limit to 4 for simplicity
                [KeyboardButton(tz) for tz in pytz.all_timezones[4:8]]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    lang = context.user_data['language']
    if lang == "English":
        await update.message.reply_text("Please select your timezone:", reply_markup=reply_markup)
    elif lang == "Русский":
        await update.message.reply_text("Пожалуйста, выберите ваш часовой пояс:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Iltimos, vaqt zonasini tanlang:", reply_markup=reply_markup)
    return ASK_TIMEZONE

async def confirm_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['timezone'] = update.message.text.strip()
    lang = context.user_data['language']
    details = (f"First Name: {context.user_data['first_name']}\n"
               f"Last Name: {context.user_data['last_name']}\n"
               f"Age: {context.user_data['age']}\n"
               f"Phone: {context.user_data['phone_number']}\n"
               f"Timezone: {context.user_data['timezone']}")

    if lang == "English":
        await update.message.reply_text(f"Please confirm your details:\n{details}\nType 'yes' to confirm or 'no' to restart.")
    elif lang == "Русский":
        await update.message.reply_text(f"Пожалуйста, подтвердите ваши данные:\n{details}\nВведите 'да' для подтверждения или 'нет' для перезапуска.")
    else:
        await update.message.reply_text(f"Iltimos, ma'lumotlaringizni tasdiqlang:\n{details}\nTasdiqlash uchun 'ha', qayta boshlash uchun 'yo'q' deb yozing.")
    return CONFIRMATION

async def create_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() not in ["yes", "да", "ha"]:
        return await start(update, context)

    conn = sqlite3.connect("task_manager.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (first_name, last_name, age, timezone, phone_number) VALUES (?, ?, ?, ?, ?)",
        (context.user_data['first_name'], context.user_data['last_name'], context.user_data['age'], context.user_data['timezone'], context.user_data['phone_number'])
    )

    conn.commit()
    conn.close()

    keyboard = [[KeyboardButton("Create Task")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    lang = context.user_data['language']
    if lang == "English":
        await update.message.reply_text("Your profile has been successfully created! Now you can create tasks using the button below.", reply_markup=reply_markup)
    elif lang == "Русский":
        await update.message.reply_text("Ваш профиль успешно создан! Теперь вы можете создавать задачи, используя кнопку ниже.", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Profilingiz muvaffaqiyatli yaratildi! Endi quyidagi tugma orqali vazifalar yaratishingiz mumkin.", reply_markup=reply_markup)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('language', "English")
    if lang == "English":
        await update.message.reply_text("Registration canceled.")
    elif lang == "Русский":
        await update.message.reply_text("Регистрация отменена.")
    else:
        await update.message.reply_text("Roʻyxatdan oʻtish bekor qilindi.")
    return ConversationHandler.END
