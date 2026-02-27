# ai/detect_and_send.py
import os
import cv2
import time
import json
import base64
import hashlib
import requests
from collections import deque
from datetime import datetime, timedelta
from dotenv import load_dotenv
from ultralytics import YOLO
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import numpy as np
import mediapipe as mp

# Load env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
CAMERA_ID = os.getenv("CAMERA_ID", "cam1")
AES_KEY_B64 = os.getenv("AES_KEY")  # base64 encoded 32-byte key
BUFFER_SECONDS = float(os.getenv("BUFFER_SECONDS", 8))
COOLDOWN_SECONDS = float(os.getenv("COOLDOWN_SECONDS", 30))

if AES_KEY_B64 is None:
    raise RuntimeError("Set AES_KEY in .env (base64 encoded 256-bit key).")

AES_KEY = base64.b64decode(AES_KEY_B64)

# Parameters
FPS = 20                          # fallback fps if camera doesn't provide
BUFFER_SIZE = int(BUFFER_SECONDS * FPS)
PERSON_CLASS_ID = 0               # COCO person class
MELEE_MIN_PERSONS = 2
MELEE_SPEED_THRESHOLD = 12.0      # pixels/frame (tune per camera)
MOB_MIN_PERSONS = 5
MOB_AREA_RATIO_THRESHOLD = 0.2    # cluster area ratio (tune)
COOLDOWN = COOLDOWN_SECONDS

STORAGE_DIR = os.path.join(os.path.dirname(__file__), '..', 'storage')
os.makedirs(STORAGE_DIR, exist_ok=True)

# init YOLO and Mediapipe
model = YOLO("yolov8n.pt")  # will download if not present
mp_pose = mp.solutions.pose
pose_detector = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)

# helper functions
def save_clip(frames, path, fps=FPS):
    h, w = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, fps, (w, h))
    for f in frames:
        out.write(f)
    out.release()

def encrypt_file(in_path, out_path, key=AES_KEY):
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    with open(in_path, "rb") as f:
        plaintext = f.read()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    with open(out_path, "wb") as f:
        f.write(nonce + ciphertext)   # store nonce + ciphertext
    return out_path

def compute_sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            data = f.read(65536)
            if not data: break
            h.update(data)
    return h.hexdigest()

def is_valid_hex(s):
    """Check if string s is valid hexadecimal"""
    try:
        bytes.fromhex(s)
        return True
    except ValueError:
        return False

def post_event(payload):
    # Ensure hash is valid hex before sending
    hash_hex = payload.get("hash", "")
    if not is_valid_hex(hash_hex):
        print(f"[WARN] Invalid hex hash, regenerating from encrypted file: {payload.get('enc_path')}")
        hash_hex = compute_sha256_file(payload.get("enc_path"))
        payload["hash"] = hash_hex

    token = os.getenv("ACCESS_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        resp = requests.post(f"{BACKEND_URL}/event", json=payload, headers=headers, timeout=10)
        return resp.status_code, resp.text
    except Exception as e:
        return None, str(e)


# main loop
def main(camera_source=0, device='cpu'):
    cap = cv2.VideoCapture(camera_source)
    cam_fps = cap.get(cv2.CAP_PROP_FPS) or 0
    if cam_fps > 0:
        fps = int(cam_fps)
    else:
        fps = FPS

    buf = deque(maxlen=BUFFER_SIZE)
    last_centroids = {}   # id => (x,y)
    last_event_time = 0

    print("Starting detection. Press 'q' to quit.")
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame read failed, exiting.")
            break
        frame_idx += 1
        buf.append(frame.copy())

        # Run YOLO (every frame)
        results = model(frame, imgsz=640, device=device)[0]  # CPU/GPU inference
        boxes = results.boxes
        persons = []
        centroids = []

        for box in boxes:
            cls = int(box.cls[0])
            if cls == PERSON_CLASS_ID:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                persons.append((x1, y1, x2, y2))
                centroids.append((cx, cy))
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

        # compute speeds
        speeds = []
        for i, c in enumerate(centroids):
            if i in last_centroids:
                px, py = last_centroids[i]
                dist = np.linalg.norm(np.array([c[0]-px, c[1]-py]))
                speeds.append(dist)
        avg_speed = float(np.mean(speeds)) if speeds else 0.0

        # crowd / mob detection
        event_type = None
        event_confidence = 0.0
        now = time.time()
        P = len(persons)
        h, w = frame.shape[:2]
        frame_area = h * w

        if P >= MOB_MIN_PERSONS:
            xs = [p[0] for p in persons] + [p[2] for p in persons]
            ys = [p[1] for p in persons] + [p[3] for p in persons]
            minx, maxx = min(xs), max(xs)
            miny, maxy = min(ys), max(ys)
            cluster_area = max(1, (maxx-minx)*(maxy-miny))
            area_ratio = cluster_area / frame_area
            if area_ratio < MOB_AREA_RATIO_THRESHOLD:
                event_type = "mob_formation"
                event_confidence = 0.8

        # melee detection
        if event_type is None and P >= MELEE_MIN_PERSONS:
            if avg_speed > MELEE_SPEED_THRESHOLD:
                event_type = "melee"
                event_confidence = 0.9

        # suspicious pose
        suspicious_pose = False
        if P > 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = pose_detector.process(rgb)
            if res.pose_landmarks:
                lm = res.pose_landmarks.landmark
                lw = lm[15]; rw = lm[16]; ls = lm[11]; rs = lm[12]
                if lw.y < ls.y or rw.y < rs.y:
                    suspicious_pose = True
                    if event_type is None:
                        event_type = "suspicious_body_language"
                        event_confidence = 0.6

        last_centroids = {i: c for i, c in enumerate(centroids)}

        # Cooldown
        if event_type and (now - last_event_time) > COOLDOWN:
            start_ts = datetime.utcnow() - timedelta(seconds=BUFFER_SECONDS) if BUFFER_SECONDS else datetime.utcnow()
            end_ts = datetime.utcnow()
            ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            clip_name = f"{CAMERA_ID}_{event_type}_{ts}.mp4"
            clip_path = os.path.join(STORAGE_DIR, clip_name)
            frames_to_save = list(buf)
            save_clip(frames_to_save, clip_path, fps=fps)
            print(f"[EVENT] {event_type} detected. Saved clip: {clip_path}")

            # Encrypt clip
            enc_name = clip_name + ".enc"
            enc_path = os.path.join(STORAGE_DIR, enc_name)
            encrypt_file(clip_path, enc_path)
            print(f"Encrypted -> {enc_path}")

            # Compute SHA256 hash
            hash_hex = compute_sha256_file(enc_path)
            print(f"SHA256 (encrypted): {hash_hex}")

            # Post metadata
            payload = {
                "camera_id": CAMERA_ID,
                "event_type": event_type,
                "confidence": event_confidence,
                "start_time": start_ts.isoformat(),
                "end_time": end_ts.isoformat(),
                "clip_path": clip_path,
                "enc_path": enc_path,
                "hash": hash_hex
            }
            status, resp_text = post_event(payload)
            print("POST /event ->", status, resp_text)

            last_event_time = now

        cv2.imshow("Detect (press q to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main(camera_source=0, device='cpu')
