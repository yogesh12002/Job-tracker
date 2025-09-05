import base64
import re
from bs4 import BeautifulSoup

STATUS_KEYWORDS = {
    "rejected": "Rejected",
    "declined": "Rejected",
    "shortlisted": "In Review",
    "viewed": "In Review",
    "interview": "Interview Scheduled",
    "hired": "Offer",
    "offer": "Offer"
}

def parse_email(msg):
    payload = msg['payload']
    headers = payload['headers']

    subject = ""
    for h in headers:
        if h['name'] == 'Subject':
            subject = h['value']

    body = ""
    if 'data' in payload['body']:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    else:
        parts = payload.get('parts', [])
        if parts:
            data = parts[0]['body'].get('data')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')

    soup = BeautifulSoup(body, "html.parser")
    text_body = soup.get_text()

    status = "Applied"
    for k, v in STATUS_KEYWORDS.items():
        if re.search(k, subject.lower()) or re.search(k, text_body.lower()):
            status = v
            break

    return {
        "subject": subject,
        "body": text_body[:500],  # preview
        "status": status
    }
