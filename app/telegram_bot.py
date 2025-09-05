from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from sqlalchemy.orm import Session
import database, models
import logging
logging.basicConfig(level=logging.INFO)

TOKEN = "7999182011:AAE2MK6dgezNrLDBh7N_swNhTBmCIr6NYng"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I am your Job Tracker Bot. Ask me about your applications!")

async def get_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Please provide a company name, e.g. `/status Microsoft`")
        return

    db = database.SessionLocal()
    apps = db.query(models.Application).filter(models.Application.company_name.ilike(f"%{query}%")).all()
    db.close()

    if not apps:
        await update.message.reply_text(f"No applications found for {query}.")
    else:
        reply = "\n".join([f"{a.company_name} - {a.role} [{a.status}]" for a in apps])
        await update.message.reply_text(reply)

def run_bot():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", get_status))

    print("🤖 Telegram bot running...")
    app.run_polling()
