import os
import cv2
import json
import base64
import hashlib
import requests
from datetime import datetime
from dotenv import load_dotenv
from ultralytics import YOLO
import numpy as np
import mediapipe as mp
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pathlib import Path

# Load .env
root_path = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=root_path / ".env")

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
CAMERA_ID = os.getenv("CAMERA_ID", "sim")
AES_KEY_B64 = os.getenv("AES_KEY")

if not AES_KEY_B64:
    raise RuntimeError("Set AES_KEY in .env (base64 encoded 256-bit key)")
AES_KEY = base64.b64decode(AES_KEY_B64)

# ------------------ Token Fetch ------------------
def fetch_new_token():
    try:
        res = requests.post(
            f"{BACKEND_URL}/login",
            data={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        res.raise_for_status()
        return res.json().get("access_token")
    except Exception as e:
        print("[ERROR] Failed to fetch token:", e)
        return None

ACCESS_TOKEN = fetch_new_token()

# Load models
model = YOLO(str(root_path / "ai" / "yolov8n.pt"))
mp_pose = mp.solutions.pose
pose_detector = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)

def encrypt_file(in_path, out_path, key=AES_KEY):
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    with open(in_path, "rb") as f:
        plaintext = f.read()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    with open(out_path, "wb") as f:
        f.write(nonce + ciphertext)
    return out_path

def compute_sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def post_event(payload):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"} if ACCESS_TOKEN else {}
    if not ACCESS_TOKEN:
        print("[ERROR] ACCESS_TOKEN missing")
        return None, "Missing access token"
    try:
        print(f"[INFO] Sending POST /event with token")
        resp = requests.post(f"{BACKEND_URL}/event", json=payload, headers=headers, timeout=30)
        print(f"[INFO] POST /event -> {resp.status_code}: {resp.text}")
        return resp.status_code, resp.text
    except Exception as e:
        print("[ERROR] post_event failed:", e)
        return None, str(e)

def analyze_clip(path):
    print(f"[DEBUG] Analyzing clip: {path}")
    cap = cv2.VideoCapture(path)
    persons, speeds, centroids = 0, [], []
    frame_area = None
    suspicious = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, imgsz=640)[0]
        if frame_area is None:
            frame_area = frame.shape[0] * frame.shape[1]

        local_centroids, p_count = [], 0
        for box in results.boxes:
            if int(box.cls[0]) == 0:
                p_count += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                local_centroids.append((cx, cy))

        if len(local_centroids) > 1:
            dists = [np.linalg.norm(np.array(c1) - np.array(c2)) for c1, c2 in zip(local_centroids, local_centroids[1:])]
            speeds.extend(dists)

        if p_count > 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = pose_detector.process(rgb)
            if res.pose_landmarks:
                lm = res.pose_landmarks.landmark
                lw = lm[15]; rw = lm[16]; ls = lm[11]; rs = lm[12]
                if lw.y < ls.y or rw.y < rs.y:
                    suspicious = True

        persons += p_count
        centroids.extend(local_centroids)

    cap.release()

    avg_speed = np.mean(speeds or [0])
    print(f"[DEBUG] Persons: {persons}, Speed: {avg_speed:.2f}, Suspicious: {suspicious}")

    if persons >= 5:
        xs, ys = [c[0] for c in centroids], [c[1] for c in centroids]
        area_ratio = ((max(xs) - min(xs)) * (max(ys) - min(ys))) / frame_area
        print(f"[DEBUG] Crowd area ratio: {area_ratio:.3f}")
        if area_ratio < 0.2:
            return "mob_formation", 0.8

    if persons >= 2 and avg_speed > 12:
        return "melee", 0.9

    if suspicious:
        return "suspicious_body_language", 0.6

    return "unknown", 0.0

def analyze_clip_full(camera_id, clip_path, skip_post=False):
    clip_path = str(Path(clip_path).resolve())
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    enc_name = f"{camera_id}_{ts}.mp4.enc"
    enc_path = str(root_path / "storage" / enc_name)
    os.makedirs(os.path.dirname(enc_path), exist_ok=True)

    encrypt_file(clip_path, enc_path)
    file_hash = compute_sha256_file(enc_path)
    event_type, confidence = analyze_clip(clip_path)

    payload = {
        "camera_id": camera_id,
        "event_type": event_type,
        "confidence": confidence,
        "start_time": datetime.utcnow().isoformat(),
        "end_time": datetime.utcnow().isoformat(),
        "clip_path": clip_path,
        "enc_path": enc_path,
        "hash": file_hash,
    }

    if not skip_post:
        status, msg = post_event(payload)
        try:
            msg_data = json.loads(msg)
            payload["tx_hash"] = msg_data.get("tx_hash", "pending")
        except Exception:
            payload["tx_hash"] = "pending"
    else:
        payload["tx_hash"] = "pending"

    print("[AI Result]", json.dumps(payload, indent=2))
    return payload

if __name__ == "__main__":
    result = analyze_clip_full("cam2", "../Storage/criminal activity clip 1.mp4")
    print("[FINAL]", result)
