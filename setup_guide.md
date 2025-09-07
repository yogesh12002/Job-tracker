# 🚀 Job Tracker Bot Setup Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Create Telegram Bot

1. **Open Telegram** and search for `@BotFather`
2. **Start a chat** with BotFather
3. **Send** `/newbot`
4. **Choose a name** for your bot (e.g., "My Job Tracker Bot")
5. **Choose a username** (must end with 'bot', e.g., "myjobtracker_bot")
6. **Copy the token** that BotFather gives you

Example interaction:
```
You: /newbot
BotFather: Alright, a new bot. How are we going to call it?
You: My Job Tracker Bot
BotFather: Good. Now let's choose a username for your bot.
You: myjobtracker_bot
BotFather: Done! Congratulations on your new bot. You will find it at t.me/myjobtracker_bot. You can now add a description...

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

## Step 3: Set up Gmail API

### 3.1 Enable Gmail API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Gmail API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### 3.2 Create OAuth2 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop application"
4. Download the JSON file
5. Rename it to `credentials.json` and place it in your project root

### 3.3 Set up Gmail App Password (for email summaries)
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Security > 2-Step Verification (enable if not already)
3. Security > App passwords
4. Generate an app password for "Mail"
5. Copy the 16-character password

## Step 4: Configure Environment Variables

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your credentials:
   ```env
   # Telegram Bot Configuration
   TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

   # Gmail Configuration
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASS=your_16_char_app_password
   TO_EMAIL=your_email@gmail.com

   # Database Configuration
   DATABASE_URL=sqlite:///./applications.db

   # Gmail API Configuration
   GMAIL_QUERY=from:(linkedin.com OR naukri.com OR internshala.com OR indeed.com)
   ```

## Step 5: Run the Application

### Option 1: Run Both Services Separately

**Terminal 1 - FastAPI Server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Telegram Bot:**
```bash
python bot.py
```

### Option 2: Run with Docker (Production)

```bash
# Build and run API
docker build -f Dockerfile.api -t job-tracker-api .
docker run -p 8000:10000 --env-file .env job-tracker-api

# Build and run Bot
docker build -f Dockerfile.bot -t job-tracker-bot .
docker run --env-file .env job-tracker-bot
```

## Step 6: Test the Setup

### Test FastAPI
1. Open browser: http://localhost:8000/docs
2. Try creating an application via the API

### Test Telegram Bot
1. Find your bot on Telegram
2. Send `/start`
3. Try commands like:
   - `/add Google Software Engineer`
   - `/list`
   - `/status Google`

### Test Gmail Integration
1. Send a test email from LinkedIn/Indeed to yourself
2. Use `/sync` command in Telegram
3. Or call API: `POST http://localhost:8000/sync-emails`

## Step 7: First Time Gmail OAuth

When you first run the application:
1. It will open a browser window
2. Sign in to your Google account
3. Grant permissions to read Gmail
4. The app will save `token.json` for future use

## Troubleshooting

### Common Issues:

1. **"Module not found" errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **Gmail API quota exceeded**
   - Wait a few minutes and try again
   - Check your Google Cloud Console quotas

3. **Telegram bot not responding**
   - Check if BOT_TOKEN is correct
   - Ensure bot is running (`python bot.py`)

4. **Database errors**
   - Delete `applications.db` and restart
   - Check file permissions

### Logs to Check:
- FastAPI logs: Look for "✅ Scheduler started"
- Bot logs: Look for "🤖 Telegram Bot running..."
- Gmail sync: Look for "✅ Gmail Sync Completed"

## Next Steps

Once everything is working:
1. **Deploy to production** using the provided `render.yaml`
2. **Set up webhooks** for real-time updates
3. **Add more job platforms** to the Gmail query
4. **Customize status keywords** in `email_parser.py`

## Support

If you encounter issues:
1. Check the logs for error messages
2. Verify all environment variables are set
3. Test each component individually
4. Check network connectivity for API calls