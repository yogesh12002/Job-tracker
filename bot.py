
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from sqlalchemy.orm import Session
from app import database, models
from app.main import sync_emails_job 
# reuse Gmail sync



TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  
# set in your .env

# ------------------- DB Dependency ------------------- #
def get_db():
    db = database.SessionLocal()
    return db
    


# ------------------- Handlers ------------------- #
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "👋 Hi! I'm your Job Tracker Bot.\n\n"
        "Commands:\n"
        "• /status <company> → Check status of a company\n"
        "• /list → Show all applications\n"
        "• /sync → Sync latest job updates from Gmail\n"
        "• /add <company> <status> → Add new application\n"
        "• /update <company> <status> → Update application status\n"
        "• /delete <company> → Delete an application"
    )

async def status(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("Please provide a company name. Example: /status Google")
        return

    company = " ".join(context.args)
    db: Session = get_db()
    apps = db.query(models.Application).filter(models.Application.company_name.ilike(f"%{company}%")).all()
    db.close()

    if not apps:
        await update.message.reply_text(f"No applications found for {company}.")
        return

    reply = "\n".join([f"🏢 {a.company_name} → 📌 {a.status}" for a in apps])
    await update.message.reply_text(reply)

async def list_applications(update: Update, context: CallbackContext):
    db: Session = get_db()
    apps = db.query(models.Application).all()
    db.close()

    if not apps:
        await update.message.reply_text("📂 No applications found in the tracker.")
        return

    reply = "\n".join([f"🏢 {a.company_name} → 📌 {a.status}" for a in apps])
    await update.message.reply_text("📋 All Applications:\n" + reply)

async def sync(update: Update, context: CallbackContext):
    await update.message.reply_text("🔄 Syncing Gmail for updates... Please wait.")
    updated = sync_emails_job()
    if updated:
        reply = "\n".join([f"🏢 {u['company']} → 📌 {u['new_status']}" for u in updated])
        await update.message.reply_text("✅ Sync completed:\n" + reply)
    else:
        await update.message.reply_text("⚠️ No new updates found.")

async def add_application(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: /add <company_name> <status>\nExample: /add Google Applied")
        return

    company = context.args[0]
    status = " ".join(context.args[1:])

    db: Session = get_db()
    new_app = models.Application(company_name=company, status=status)
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    db.close()

    await update.message.reply_text(f"✅ Added new application:\n🏢 {company} → 📌 {status}")

async def update_application(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: /update <company_name> <new_status>\nExample: /update Google Interview Scheduled")
        return

    company = context.args[0]
    new_status = " ".join(context.args[1:])

    db: Session = get_db()
    app = db.query(models.Application).filter(models.Application.company_name.ilike(f"%{company}%")).first()

    if not app:
        db.close()
        await update.message.reply_text(f"❌ No application found for {company}.")
        return

    app.status = new_status
    db.commit()
    db.refresh(app)
    db.close()

    await update.message.reply_text(f"✅ Updated:\n🏢 {app.company_name} → 📌 {app.status}")

async def delete_application(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("❌ Usage: /delete <company_name>\nExample: /delete Google")
        return

    company = " ".join(context.args)
    db: Session = get_db()
    app = db.query(models.Application).filter(models.Application.company_name.ilike(f"%{company}%")).first()

    if not app:
        db.close()
        await update.message.reply_text(f"❌ No application found for {company}.")
        return

    db.delete(app)
    db.commit()
    db.close()

    await update.message.reply_text(f"🗑️ Deleted application for {company}.")

# ------------------- Main ------------------- #
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("list", list_applications))
    app.add_handler(CommandHandler("sync", sync))
    app.add_handler(CommandHandler("add", add_application))
    app.add_handler(CommandHandler("update", update_application))
    app.add_handler(CommandHandler("delete", delete_application))  # ⬅️ NEW

    print("🤖 Telegram Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
