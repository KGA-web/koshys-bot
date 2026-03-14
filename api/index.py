from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import httpx, os

app = FastAPI(title="Koshys AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

KGI_SYSTEM = """
You are KGI Assistant for Koshys Group of Institutions, Bangalore, India.

IMPORTANT FACTS:
- Established: 2003 (23+ years)
- Location: #31/1, Hennur-Bagalur Road, Kannur P.O., Bengaluru, Karnataka 562149
- Phone: 808 866 0000
- Email: info@kgi.edu.in
- Website: kgi.edu.in

INSTITUTIONS:
1. Koshys Institute of Management Studies (KIMS) - kimsbengaluru.edu.in
2. Koshys Institute of Health Sciences (KIHS) - kgi.edu.in/KIHS
3. Koshys Institute of Hotel Management
4. Koshys Global Academia (CBSE School) - koshysglobalacademia.com

COURSES:
UG: BBA, BBA Aviation, BCA, BCA Advanced, B.Com, B.Com Logistics, B.Com Advanced, BVA (Animation, Applied Arts, Interior Design), B.Sc Forensic Science
PG: MBA, MCA
NURSING: GNM, B.Sc Nursing, PBBSc, M.Sc Nursing
ALLIED HEALTH: B.Sc Renal Dialysis, B.Sc Respiratory, B.Sc AT & OT, B.Sc MIT, B.Sc MLT

RULES:
- For fee questions: "For fee details, please contact our admission team at 808 866 0000 or click the Contact button."
- For admissions: Direct to apply.kgi.edu.in
- Keep responses short (2-4 sentences)
- Be warm and helpful
- End with "Is there anything else I can help you with?"
"""


async def get_openai_response(message: str, history: list = None) -> str:
    if not OPENAI_KEY:
        return "API key not configured. Please set OPENAI_API_KEY in Vercel environment variables."

    messages = [{"role": "system", "content": KGI_SYSTEM}]

    if history:
        for msg in history[-10:]:
            role = "user" if msg.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": msg.get("content", "")})

    messages.append({"role": "user", "content": message})

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 400,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"I'm experiencing technical issues. Please call 808 866 0000 for immediate assistance."


@app.get("/")
async def root():
    return {"status": "KGI AI Running", "version": "2.0"}


@app.get("/api")
async def api_check():
    return {"api": "working", "key_configured": bool(OPENAI_KEY)}


@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message", "")
    history = body.get("history", [])
    reply = await get_openai_response(message, history)
    return {"reply": reply}
