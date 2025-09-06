import yagmail
import database, models

EMAIL_USER = "your_email@gmail.com"
EMAIL_PASS = "your_app_password"
TO_EMAIL = "your_email@gmail.com"

def send_daily_summary():
    db = database.SessionLocal()
    apps = db.query(models.Application).all()
    db.close()

    if not apps:
        body = "No applications tracked yet."
    else:
        body = "\n".join([f"{a.company_name} - {a.role} ({a.platform}) → {a.status}" for a in apps])

    yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASS)
    yag.send(TO_EMAIL, "📊 Daily Job Application Summary", body)
    print("✅ Daily summary email sent!")
