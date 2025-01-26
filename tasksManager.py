# File: tasksManager.py
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters
from profileRegister import start, ask_first_name, ask_last_name, ask_age, ask_phone, ask_timezone, create_profile, cancel, ASK_LANGUAGE, ASK_FIRST_NAME, ASK_LAST_NAME, ASK_AGE, ASK_PHONE, ASK_TIMEZONE
from botDB import setup_database
import logging
token = '7405078046:AAGkucAWeLnbzomwAYYvSVn0wjXh_NFnZ1E'

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    setup_database()

    app = ApplicationBuilder().token(token).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_first_name)],
            ASK_FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_last_name)],
            ASK_LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_age)],
            ASK_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_PHONE: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), ask_timezone)],
            ASK_TIMEZONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_profile)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conversation_handler)

    logger.info("Bot is running...")
    app.run_polling()