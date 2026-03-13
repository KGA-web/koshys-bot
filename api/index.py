from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, HTMLResponse
import httpx, os

app = FastAPI(title="Koshys KAIA Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AIzaSyARE5aXg63_CnfJ0kMC1xenGZsHg2A6blo}"

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
- PUC: Rs 15,000 – 30,000
- UG (B.Com/BBA/BA): Rs 25,000 – 45,000
- UG (BCA/B.Sc): Rs 30,000 – 55,000
- PG (MBA/M.Com/MCA): Rs 60,000 – 1,00,000
Scholarships available for merit and economically weaker students.

Admissions: Academic year starts June. Apply at www.koshys.edu.in
Email: admissions@koshys.edu.in | Phone: +91-80-XXXXXXXX

Campus: Smart classrooms, library, Wi-Fi, sports, auditorium, hostel, placement cell (200+ companies).

Response style:
- Warm, helpful, professional. 2–4 sentences max.
- End with "Is there anything else I can help you with?"
- Respond in the same language the user writes in (English/Kannada/Hindi).
- If unsure, direct to admissions@koshys.edu.in
"""

async def gemini_reply(message: str, history: list = None) -> str:
    contents = []
    if history:
        for msg in (history or [])[-10:]:
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
        res  = await client.post(GEMINI_URL, json=payload)
        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


# ── HEALTH CHECK ──────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "KAIA is running on Vercel ✅", "version": "1.0"}


# ── WEBSITE CHAT ──────────────────────────────────────────────
@app.post("/chat")
async def chat(request: Request):
    body    = await request.json()
    message = body.get("message", "")
    history = body.get("history", [])
    reply   = await gemini_reply(message, history)
    return {"reply": reply}


# ── VOICE / IVR (Twilio) ──────────────────────────────────────
@app.get("/voice")
async def voice_welcome():
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" action="/voice" method="POST" speechTimeout="auto" language="en-IN">
    <Say voice="Polly.Aditi" language="en-IN">
      Welcome to Koshys Group of Institutions! I am KAIA, your AI assistant.
      Please speak your question about admissions, courses, fees, or campus now.
    </Say>
  </Gather>
</Response>"""
    return Response(content=twiml, media_type="application/xml")


@app.post("/voice")
async def voice_call(request: Request):
    form   = await request.form()
    speech = form.get("SpeechResult", "Tell me about Koshys courses")
    reply  = await gemini_reply(speech)
    # Sanitise for TwiML
    safe = reply.replace("&", "and").replace("<", "").replace(">", "")
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" action="/voice" method="POST" speechTimeout="auto" language="en-IN">
    <Say voice="Polly.Aditi" language="en-IN">{safe}</Say>
  </Gather>
  <Say voice="Polly.Aditi" language="en-IN">Thank you for calling Koshys. Goodbye!</Say>
</Response>"""
    return Response(content=twiml, media_type="application/xml")
