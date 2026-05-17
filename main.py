import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes,
                          ConversationHandler)
import database

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Define states cleanly
ID, NAME, PHONE, ADDRESS, EMAIL = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to the Student Management Bot!\n"
        "Use /add to add a new student.\n"
        "Just type a student's name directly to search for them!"
    )

# --- CONVERSATION FLOW FUNCTIONS ---

async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔢 Please enter the student's ID:")
    return ID

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This step captures what the user typed in add_start (the ID!)
    context.user_data['id'] = update.message.text
    await update.message.reply_text("👤 Please enter the student's full name:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📞 Please enter the student's phone number:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("🏠 Please enter the student's address:")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text
    await update.message.reply_text("📧 Please enter the student's email:")
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text

    # Safely pull all keys now that they are guaranteed to exist
    s_id = context.user_data['id']
    name = context.user_data['name']
    phone = context.user_data['phone']
    address = context.user_data['address']
    email = context.user_data['email']

    success = database.add_student(s_id, name, phone, address, email)

    if success:
        await update.message.reply_text(f"✅ Student '{name}' added successfully!")
    else:
        await update.message.reply_text("❌ Failed to add student. The ID or Email might already exist.")

    return ConversationHandler.END

# --- SEARCH FUNCTION ---

async def search_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    results = database.search_students_by_name(query)

    if results:
        response = f"🔍 Found {len(results)} matching record(s):\n\n"
        for row in results:
            response += (
                f"🆔 ID: {row[0]}\n"
                f"👤 Name: {row[1]}\n"
                f"📞 Phone: {row[2]}\n"
                f"🏠 Address: {row[3]}\n"
                f"📧 Email: {row[4]}\n"
                f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            )
        await update.message.reply_text(response)
    else:
        await update.message.reply_text(f"ℹ️ No students found matching '{query}'.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('❌ Operation cancelled.')
    return ConversationHandler.END

if __name__ == "__main__":
    database.init_db()
    
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"

    app = ApplicationBuilder().token(TOKEN).build()

    # Fixed States Mapping: Step A collects data, saves it, and points to Step B's function handler

    conv_handler = ConversationHandler(entry_points=[CommandHandler('add', add_start)], 
        states={
            ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_id)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)]
        }, 
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(CommandHandler('start', start))
    app.add_handler(conv_handler)
    
    # Catch-all text handler for seamless searching
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_student))
    
    print("🤖 Bot is spinning up smoothly...")
    app.run_polling()