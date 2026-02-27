from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import json
from backend.auth import authenticate_user, create_access_token, get_current_user, hash_password, ensure_admin
from backend.database import users_collection, events_collection
from backend.blockchain import log_event_on_chain

app = FastAPI(title="CCTV-AI Blockchain API")

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# User Signup/Login
# ======================
class UserSignup(BaseModel):
    username: str
    password: str

@app.post("/signup")
async def signup(user: UserSignup):
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pw = hash_password(user.password)
    await users_collection.insert_one({"username": user.username, "hashed_password": hashed_pw})
    return {"status": "success", "message": "User created successfully"}

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(data={"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

# ======================
# CCTV Event Handling
# ======================
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
    """Log event to blockchain and MongoDB (auth required)"""
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
    """Retrieve all events (auth required)"""
    events = []
    async for doc in events_collection.find({"user": user["username"]}, {"_id": 0}):
        events.append(doc)
    return {"count": len(events), "events": events}

# ======================
# Startup Event
# ======================
@app.on_event("startup")
async def startup_event():
    await ensure_admin()
