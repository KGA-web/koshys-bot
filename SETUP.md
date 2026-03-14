# KGI Chatbot - Complete Setup Guide

## Quick Summary of Credentials

### From Google Service Account JSON:
- **Email**: kgi-947@koshys-bot.iam.gserviceaccount.com
- **Private Key**: (in .env file)

### What You Need to Get:

| Variable | Where to Get | Free? |
|----------|--------------|-------|
| OPENAI_API_KEY | platform.openai.com | $5 credit |
| GOOGLE_SHEET_ID | Create new sheet → get ID | Yes |
| VAPI_API_KEY | dashboard.vapi.ai | $5 credit |

---

## Step-by-Step: Google Sheets Setup

1. **Create Google Sheet**
   - Go to: https://sheet.new
   - Rename to: "KGI Enquiries"

2. **Add Headers in Row 1:**
   ```
   A1: Timestamp
   B1: Name
   C1: Type
   D1: Phone
   E1: Course
   F1: Inquiry
   G1: Status
   ```

3. **Share with Service Account:**
   - Click "Share" button
   - Add: `kgi-947@koshys-bot.iam.gserviceaccount.com`
   - Role: Viewer
   - Click "Send"

4. **Get Sheet ID:**
   - URL looks like: `https://docs.google.com/spreadsheets/d/ABC123XYZ/edit`
   - Sheet ID = `ABC123XYZ` (put in GOOGLE_SHEET_ID)

---

## Step-by-Step: Vapi.ai Setup

1. Go to: https://dashboard.vapi.ai
2. Sign up / Login
3. Copy your API Key from settings
4. Import the `vapi-assistant.json` file:
   - Go to Assistants
   - Click "Create Assistant"
   - Choose "Import from JSON"
   - Upload `vapi-assistant.json`

5. Get a phone number:
   - Click "Phone Numbers"
   - Get a virtual number
   - Point it to your Vercel API

---

## Deployment Checklist

- [ ] Push to GitHub
- [ ] Import to Vercel
- [ ] Add all env variables in Vercel
- [ ] Deploy
- [ ] Test chat widget
- [ ] Test voice call
- [ ] Check Google Sheet for data

---

## Need Help?

- Email: info@kgi.edu.in
- Phone: 808 866 0000
- Website: kgi.edu.in