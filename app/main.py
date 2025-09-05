from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from apscheduler.schedulers.background import BackgroundScheduler
import models, schemas, database
import gmail_service
import email_parser
import email_summary


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
    db = database.SessionLocal()
    service = gmail_service.get_gmail_service()
    results = service.users().messages().list(
        userId='me',
        q="from:(linkedin.com OR naukri.com OR internshala.com OR indeed.com)"
    ).execute()

    messages = results.get('messages', [])
    updated_apps = []

    for m in messages[:10]:
        msg = service.users().messages().get(userId='me', id=m['id']).execute()
        parsed = email_parser.parse_email(msg)

        db_app = db.query(models.Application).filter(
            models.Application.company_name.ilike(f"%{parsed['subject']}%")
        ).first()

        if db_app:
            db_app.status = parsed["status"]
            db.commit()
            db.refresh(db_app)
            updated_apps.append({
                "company": db_app.company_name,
                "new_status": db_app.status,
                "email_subject": parsed["subject"]
            })

    db.close()
    print("✅ Gmail Sync Completed:", updated_apps)
    return updated_apps

@app.post("/sync-emails")
def manual_sync():
    """Run Gmail sync manually via API"""
    return {"updated": sync_emails_job()}

# ------------------- SCHEDULER ------------------- #
scheduler = BackgroundScheduler()
scheduler.add_job(sync_emails_job, "interval", hours=12)  # run every 12 hours
scheduler.add_job(email_summary.send_daily_summary, "cron", hour=9)

scheduler.start()
