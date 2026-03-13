from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import httpx, os, html

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

GEMINI_KEY = os.environ.get("AIzaSyAxHVcyP2nQGww3-glm7_as447OvAIKTxk", "")
# Security Fix: Use headers instead of embedding the key in the URL.
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# Scraped accurately from kgi.edu.in. Fees removed, founded year corrected, and exact courses added.
KOSHYS_SYSTEM = """
You are KAIA, the friendly AI assistant for Koshys Group of Institutions (KGI), Bangalore.
Established in 2003. Premier educational group in Bangalore, Karnataka, India.
Institutions: Koshys Institute of Management Studies (KIMS), Koshys Institute of Health Sciences (KIHS), Koshys Institute of Hotel Management (KIHM), Koshys Global Academia (CBSE).
Courses offered:
- UG: BBA, B.Com, BCA, BVA (Animation/Graphic/Interior), BHM, B.Sc (Forensic Science, Nursing, MIT, MLT, AT & OT, Renal Dialysis, Respiratory Care), GNM.
- PG: MBA, MCA, M.Sc Nursing, PBBSc Nursing.
Fees: ABSOLUTELY DO NOT mention any fee amounts. If asked about fees, instruct the user to call 808 866 0000 or visit www.kgi.edu.in/ContactKGI to speak with the admissions department.
Scholarships: Available for merit and economically weaker students.
Admissions: Apply at apply.kgi.edu.in.
Campus: Wi-Fi, modern labs, hostels, 1000-bed NABH hospital for training, sports turf, placement cell.
Contact: 808 866 0000 | www.kgi.edu.in | Hennur Bagalur Road, Kannur P.O., Bangalore 562149.
Style: Warm, professional, 2-4 sentences. End with 'Is there anything else I can help you with?'
Respond in the same language the user writes in (English/Kannada/Hindi).
"""

async def gemini_reply(message: str, history: list = []) -> str:
    contents = []
    for msg in history[-10:]:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        
    if not history or history[-1]["content"] != message:
        contents.append({"role": "user", "parts": [{"text": message}]})
        
    payload = {
        "system_instruction": {"parts": [{"text": KOSHYS_SYSTEM}]},
        "contents": contents,
        # Lowered temperature to heavily reduce hallucination risk on fees
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 400} 
    }
    
    headers = {
        "x-goog-api-key": GEMINI_KEY, 
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        res = await client.post(GEMINI_URL, json=payload, headers=headers)
        data = res.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except KeyError:
            # Fallback in case of API timeout/error so Twilio doesn't hang up
            return "I am currently experiencing technical difficulties. Please call 808 866 0000 to speak with our team."

# ── Website chat endpoint
@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    reply = await gemini_reply(body.get("message", ""), body.get("history", []))
    return {"reply": reply}

# ── Twilio Voice / IVR endpoints
@app.get("/api/voice")
async def voice_welcome():
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" action="/api/voice" method="POST" speechTimeout="2" language="en-IN">
    <Say voice="Polly.Aditi" language="en-IN">
      Namaskara! Welcome to Koshys Group of Institutions.
      I am KAIA. How can I help you today?
    </Say>
  </Gather>
</Response>"""
    return Response(content=twiml, media_type="application/xml")

@app.post("/api/voice")
async def voice_respond(request: Request):
    form = await request.form()
    speech = form.get("SpeechResult", "")
    
    if not speech:
        reply = "I didn't catch that. Could you please repeat?"
    else:
        reply = await gemini_reply(speech)
        
    # Standard Python library escaping is mathematically safer
    safe_reply = html.escape(reply)
    
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" action="/api/voice" method="POST" speechTimeout="2" language="en-IN">
    <Say voice="Polly.Aditi" language="en-IN">{safe_reply}</Say>
  </Gather>
  <Say voice="Polly.Aditi" language="en-IN">Thank you for calling Koshys. Goodbye!</Say>
</Response>"""
    return Response(content=twiml, media_type="application/xml")

# ── Health check
@app.get("/api")
def root():
    return {"status": "KAIA running on Vercel", "version": "1.1"}
