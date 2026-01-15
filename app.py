from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from anthropic import Anthropic
from dotenv import load_dotenv
from pathlib import Path
import os
import uuid
import shutil

# --------------------
# Setup
# --------------------
load_dotenv()

client = Anthropic()  # reads ANTHROPIC_API_KEY automatically

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "sessions.jsonl"

app = FastAPI(title="Claude HTML UI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# --------------------
# In-memory sessions (dev-safe)
# --------------------
SESSIONS = {}

def get_session(session_id: str):
    if session_id not in SESSIONS:
        SESSIONS[session_id] = []
    return SESSIONS[session_id]

ALLOWED_MODELS = {
    "claude-opus-4-5",
    "claude-sonnet-4-5",
    "claude-haiku-4-5",
}

MODEL_PRICING = {
    "claude-opus-4-5": {
        "input": 5.00,
        "output": 25.00,
    },
    "claude-opus-4-1": {
        "input": 15.00,
        "output": 75.00,
    },
    "claude-opus-4": {
        "input": 15.00,
        "output": 75.00,
    },
    "claude-sonnet-4-5": {
        "input": 3.00,
        "output": 15.00,
    },
    "claude-sonnet-4": {
        "input": 3.00,
        "output": 15.00,
    },
    "claude-haiku-4-5": {
        "input": 1.00,
        "output": 5.00,
    },
    "claude-haiku-3-5": {
        "input": 0.80,
        "output": 4.00,
    },
    "claude-haiku-3": {
        "input": 0.25,
        "output": 1.25,
    },
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> dict:
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return {
            "input_cost": 0.0,
            "output_cost": 0.0,
            "total_cost": 0.0,
        }

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]

    return {
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "total_cost": round(input_cost + output_cost, 6),
    }

import json
from datetime import datetime

def log_interaction(entry: dict):
    entry["timestamp"] = datetime.utcnow().isoformat()

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

# --------------------
# UI
# --------------------
@app.get("/", response_class=HTMLResponse)
def serve_ui():
    return (BASE_DIR / "index.html").read_text(encoding="utf-8")

# --------------------
# Chat
# --------------------
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message")
    session_id = data.get("session_id")
    use_web_search = data.get("use_web_search", False)
    use_research = data.get("use_research", False)
    model = data.get("model", "claude-sonnet-4-5")

    if not message or not session_id:
        raise HTTPException(status_code=400, detail="Missing message or session_id")
    if model not in ALLOWED_MODELS:
        raise HTTPException(400, "Invalid model selected")
    
    messages = get_session(session_id)
    messages.append({"role": "user", "content": message})

    # Build tools array if web search enabled
    tools = []
    if use_web_search or use_research:
        tools.append({
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5
        })

    # Optional extra prompt tweak if research is requested
    if use_research:
        messages.append({
            "role": "system",
            "content": "Please conduct deep research using web search as needed and "
                       "provide citations when available."
        })

    response = client.messages.create(
        model=model,
        messages=messages,
        max_tokens=1024,
        tools=tools
    )

    usage = getattr(response, "usage", None)

    input_tokens = usage.input_tokens if usage else 0
    output_tokens = usage.output_tokens if usage else 0

    # Extract text safely
    assistant_text = []

    for block in response.content:
        if block.type == "text":
            assistant_text.append(block.text)

    assistant_text = "\n".join(assistant_text)

    messages.append({"role": "assistant", "content": assistant_text})

    costs = calculate_cost(
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )

    log_entry = {
        "session_id": session_id,
        "model": model,
        "prompt": message,
        "response": assistant_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "costs": costs,
        "flags": {
            "web_search": use_web_search,
            "research": use_research,
        }
    }

    log_interaction(log_entry)
    
    return {
        "reply": assistant_text,
        "model": model,
        "usage": {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": costs,
    }
    }

# --------------------
# Uploads (files / screenshots)
# --------------------
@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    stored = []

    for file in files:
        filename = f"{uuid.uuid4()}_{file.filename}"
        dest = UPLOAD_DIR / filename

        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        stored.append(filename)

    return {"files": stored}