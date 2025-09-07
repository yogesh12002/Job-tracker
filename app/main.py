from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from apscheduler.schedulers.background import BackgroundScheduler
from . import models, schemas, database
from . import gmail_service, email_parser, email_summary
from .database import Base
from dotenv import load_dotenv
import os
load_dotenv()

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Job Application Tracker")

# ------------------- DB Dependency ------------------- #
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------- CORE ENDPOINTS ------------------- #
@app.post("/applications", response_model=schemas.ApplicationOut)
def create_application(application: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    db_app = models.Application(**application.dict())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.get("/applications", response_model=List[schemas.ApplicationOut])
def get_applications(db: Session = Depends(get_db)):
    return db.query(models.Application).all()

@app.put("/applications/{app_id}", response_model=schemas.ApplicationOut)
def update_status(app_id: int, update: schemas.ApplicationUpdate, db: Session = Depends(get_db)):
    db_app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    db_app.status = update.status
    db.commit()
    db.refresh(db_app)
    return db_app

@app.get("/applications/status/{company}", response_model=List[schemas.ApplicationOut])
def get_status_by_company(company: str, db: Session = Depends(get_db)):
    return db.query(models.Application).filter(models.Application.company_name.ilike(f"%{company}%")).all()

# ------------------- EMAIL SYNC LOGIC ------------------- #
def sync_emails_job():
    """Sync emails from Gmail and update application statuses"""
    try:
    db = database.SessionLocal()
    service = gmail_service.get_gmail_service()
        
        gmail_query = os.getenv("GMAIL_QUERY", "from:(linkedin.com OR naukri.com OR internshala.com OR indeed.com)")
        results = service.users().messages().list(
            userId='me',
            q=gmail_query
        ).execute()

        messages = results.get('messages', [])
        updated_apps = []

        for m in messages[:10]:  # Process last 10 emails
            msg = service.users().messages().get(userId='me', id=m['id']).execute()
            parsed = email_parser.parse_email(msg)

            # Try to match email with existing applications
            db_app = db.query(models.Application).filter(
                models.Application.company_name.ilike(f"%{parsed['subject']}%")
            ).first()

            if db_app and db_app.status != parsed["status"]:
                old_status = db_app.status
                db_app.status = parsed["status"]
                db.commit()
                db.refresh(db_app)
                updated_apps.append({
                    "company": db_app.company_name,
                    "old_status": old_status,
                    "new_status": db_app.status,
                    "email_subject": parsed["subject"]
                })

        db.close()
        print("✅ Gmail Sync Completed:", updated_apps)
        return updated_apps
    except Exception as e:
        print(f"❌ Gmail Sync Error: {str(e)}")
        return []

@app.post("/sync-emails")
def manual_sync():
    """Run Gmail sync manually via API"""
    return {"updated": sync_emails_job()}

# ------------------- SCHEDULER ------------------- #
scheduler = BackgroundScheduler()
scheduler.add_job(sync_emails_job, "interval", hours=12, id="email_sync")  # run every 12 hours
scheduler.add_job(email_summary.send_daily_summary, "cron", hour=9, id="daily_summary")

@app.on_event("startup")
async def startup_event():
    scheduler.start()
    print("✅ Scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    print("✅ Scheduler stopped")
