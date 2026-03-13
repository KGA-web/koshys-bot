from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import httpx, os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Koshys AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_KEY = os.environ.get("AIzaSyAxHVcyP2nQGww3-glm7_as447OvAIKTxk", "")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"

# Twilio credentials (for IVR)
TWILIO_ACCOUNT = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN   = os.environ.get("TWILIO_AUTH_TOKEN", "")

KOSHYS_SYSTEM = """
You are KAIA, the friendly AI assistant for Koshys Group of Institutions, Bangalore, India.
Founded in 1988, Koshys is one of Bangalore's premier educational groups.

Courses offered:
- Pre-University (PUC): Science, Commerce, Arts streams
- Undergraduate: B.Com, BBA, BCA, BA, B.Sc (Computer Science, Maths)
- Postgraduate: MBA, M.Com, MCA

Fee structure (approximate per year):
- PUC: Rs 15,000 - 30,000
- UG (B.Com/BBA/BA): Rs 25,000 - 45,000
- UG (BCA/B.Sc): Rs 30,000 - 55,000
- PG (MBA/M.Com/MCA): Rs 60,000 - 1,00,000
Scholarships available for merit students and economically weaker sections.

Admissions:
- Academic year starts in June
- Apply online at www.koshys.edu.in
- Documents: 10th & 12th marks cards, TC, Aadhaar, passport photos
- Email: admissions@koshys.edu.in

Campus facilities:
- Smart classrooms, computer labs, central library, Wi-Fi campus
- Sports ground, auditorium, boys & girls hostel
- Active placement cell with 200+ company tie-ups
- NSS, NCC, cultural clubs, annual fest

Contact:
- Phone: +91-80-XXXXXXXX
- Email: info@koshys.edu.in
- Website: www.koshys.edu.in
- Address: Bangalore, Karnataka, India

Response style:
- Be warm, helpful, and professional
- Keep answers concise (2-4 sentences)
- Always end with "Is there anything else I can help you with?"
- Respond in the same language the user writes in (English, Kannada, or Hindi)
"""

async def get_gemini_reply(message: str, history: list = None) -> str:
    contents = []
    if history:
        for msg in history[-10:]:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    if not history or history[-1]["content"] != message:
        contents.append({"role": "user", "parts": [{"text": message}]})

    payload = {
        "system_instruction": {"parts": [{"text": KOSHYS_SYSTEM}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 400}
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        res = await client.post(GEMINI_URL, json=payload)
        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


# ── HEALTH CHECK ──────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "KAIA backend running", "version": "1.0"}


# ── WEBSITE CHAT ──────────────────────────────────────────────
@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message", "")
    history = body.get("history", [])
    reply = await get_gemini_reply(message, history)
    return {"reply": reply}


# ── VOICE / IVR (Twilio) ──────────────────────────────────────
@app.get("/voice")
async def voice_welcome():
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/voice" method="POST" speechTimeout="auto" language="en-IN">
        <Say voice="Polly.Aditi" language="en-IN">
            Welcome to Koshys Group of Institutions! I am KAIA, your AI assistant.
            Please speak your question about courses, admissions, or fees now.
        </Say>
    </Gather>
</Response>"""
    return Response(content=twiml, media_type="application/xml")


@app.post("/voice")
async def voice_call(request: Request):
    form = await request.form()
    speech = form.get("SpeechResult", "Hello, I need information about Koshys.")
    reply = await get_gemini_reply(speech)
    # Sanitize reply for XML
    reply_safe = reply.replace("&", "and").replace("<", "").replace(">", "").replace('"', "")
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/voice" method="POST" speechTimeout="auto" language="en-IN">
        <Say voice="Polly.Aditi" language="en-IN">{reply_safe}</Say>
    </Gather>
    <Say voice="Polly.Aditi" language="en-IN">Thank you for calling Koshys. Goodbye!</Say>
</Response>"""
    return Response(content=twiml, media_type="application/xml")
