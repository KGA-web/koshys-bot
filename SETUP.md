# KGI Chatbot - Setup Guide

## Overview
- **Platform**: Website Widget (kgi.edu.in)
- **Data Storage**: Google Sheets
- **Tech**: Vercel + Next.js + OpenAI (free tier)
- **Cost**: FREE (OpenAI $5 credit = thousands of chats)

---

## Step 1: Push to GitHub (Already Done ✓)

---

## Step 2: Deploy on Vercel

1. Go to: https://vercel.com
2. Sign up with GitHub
3. Click "Add New" → "Project"
4. Import "koshys-bot" from GitHub
5. Click "Deploy"

---

## Step 3: Configure Environment Variables

In Vercel dashboard, go to Settings → Environment Variables and add:

| Variable | Value |
|----------|-------|
| `OPENAI_API_KEY` | Your OpenAI key (see below) |
| `GOOGLE_SERVICE_ACCOUNT_EMAIL` | `kgi-947@koshys-bot.iam.gserviceaccount.com` |
| `GOOGLE_PRIVATE_KEY` | Your private key (see below) |
| `GOOGLE_SHEET_ID` | Your sheet ID (see below) |

---

## Step 4: Get OpenAI API Key

1. Go to: https://platform.openai.com
2. Sign up (free $5 credit)
3. API Keys → Create new secret key
4. Copy the key
5. Add to Vercel as `OPENAI_API_KEY`

---

## Step 5: Setup Google Sheets

1. Create new sheet: https://sheet.new
2. Rename to "KGI Enquiries"
3. Row 1 headers:
   ```
   A1: Timestamp
   B1: Name
   C1: Type
   D1: Phone
   E1: Course
   F1: Inquiry
   G1: Status
   ```
4. Click Share → Add: `kgi-947@koshys-bot.iam.gserviceaccount.com`
5. Get Sheet ID from URL (between /d/ and /edit)
6. Add to Vercel as `GOOGLE_SHEET_ID`

---

## Step 6: Get Private Key

From your downloaded JSON file (koshys-bot-c4c482fa16bd.json):
- Copy the `private_key` value
- Add to Vercel as `GOOGLE_PRIVATE_KEY`

---

## Step 7: Add Widget to Website

In kgi.edu.in HTML, add before `</body>`:
```html
<script src="https://your-vercel-app.vercel.app/widget.js"></script>
```
Or embed the ChatWidget component in your Next.js page.

---

## Features Included

- AI-powered chat with KGI knowledge base
- Auto-collects: Name, Phone, User Type (Student/Parent), Course
- Saves all enquiries to Google Sheets
- Quick buttons: Call 808 866 0000, Apply Now
- Fee queries → Contact button (no pricing shown)

---

## Need Help?

- Phone: 808 866 0000
- Email: info@kgi.edu.in
- Website: kgi.edu.in