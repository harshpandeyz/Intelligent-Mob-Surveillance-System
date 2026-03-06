from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from backend.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password,
    ensure_admin,
    get_current_admin_user,
)
from backend.database import users_collection, events_collection
from backend.blockchain import log_event_on_chain

import json
import os
import aiofiles
import uuid
from datetime import datetime
from AI.detect_clip_upload import analyze_clip_full

app = FastAPI(title="CCTV-AI Blockchain API")

# ----------------------------
# CORS for frontend
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Auth Models & Endpoints
# ----------------------------
class UserSignup(BaseModel):
    username: str
    password: str

@app.post("/signup")
async def signup(user: UserSignup):
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pw = hash_password(user.password)
    await users_collection.insert_one({
        "username": user.username,
        "hashed_password": hashed_pw,
        "role": "user"
    })
    return {"status": "success", "message": "User created successfully"}

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(data={"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

# ----------------------------
# AI-Powered Upload + Log
# ----------------------------
@app.post("/classify_upload")
async def classify_and_log_event(
    camera_id: str = Form(...),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    try:
        raw_filename = f"{camera_id}_{uuid.uuid4().hex}.mp4"
        raw_path = os.path.join("storage", raw_filename)

        async with aiofiles.open(raw_path, "wb") as f:
            await f.write(await file.read())

        result = analyze_clip_full(camera_id, raw_path, skip_post=True)
        print("[AI Result]", result)

        # Direct DB + Blockchain logging
        metadata = json.dumps(result)
        tx_hash = log_event_on_chain(result["hash"], metadata, enc_file_path=result["enc_path"])

        record = result.copy()
        record["tx_hash"] = tx_hash
        record["user"] = user["username"]
        await events_collection.insert_one(record)

        return {
            "status": "success",
            "event_type": record.get("event_type", "unknown"),
            "tx_hash": tx_hash,
            "confidence": record.get("confidence"),
            "start_time": record.get("start_time"),
        }

    except Exception as e:
        print("[ERROR] classify_upload failed:", e)
        return {"status": "error", "message": str(e)}

# ----------------------------
# Manual Event Log
# ----------------------------
class EventModel(BaseModel):
    camera_id: str
    event_type: str
    confidence: float
    start_time: str
    end_time: str
    clip_path: str
    enc_path: str
    hash: str

@app.post("/event")
async def log_event(event: EventModel, user: dict = Depends(get_current_user)):
    try:
        metadata = json.dumps(event.dict())
        tx_hash = log_event_on_chain(event.hash, metadata, enc_file_path=event.enc_path)

        record = event.dict()
        record["tx_hash"] = tx_hash
        record["user"] = user["username"]
        await events_collection.insert_one(record)

        return {"status": "success", "tx_hash": tx_hash}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/events")
async def get_all_events(user: dict = Depends(get_current_user)):
    query = {} if user["role"] == "admin" else {"user": user["username"]}
    events = []
    async for doc in events_collection.find(query, {"_id": 0}):
        events.append(doc)
    return {"count": len(events), "events": events}

@app.get("/admin-dashboard")
async def get_admin_dashboard(user: dict = Depends(get_current_admin_user)):
    return {"message": f"Welcome, Admin {user['username']}"}

@app.on_event("startup")
async def startup_event():
    await ensure_admin()


from backend.routes import live_stream
app.include_router(live_stream.router)
