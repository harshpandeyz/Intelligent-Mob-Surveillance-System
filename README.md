# Criminal Activity Detection using CCTV with Blockchain-Based Security

AI-powered CCTV surveillance system that detects criminal activities in real-time, encrypts evidence, and stores tamper-proof hashes on blockchain.

## Problem Statement

Traditional CCTV systems rely on manual monitoring and lack secure evidence storage. Video footage can be altered or deleted, compromising investigations.

This project automates crime detection using AI and ensures evidence integrity using blockchain technology.

## Key Features

- Real-time CCTV monitoring
- AI-based criminal activity detection (YOLOv8)
- Video clip extraction and encryption (AES-256)
- Blockchain-based hash storage
- Tamper-proof evidence verification
- Secure dashboard with authentication

## System Architecture

CCTV Camera  
↓  
AI Detection Module  
↓  
Video Clip Extraction  
↓  
AES Encryption  
↓  
SHA-256 Hash Generation  
↓  
Blockchain Logging  
↓  
Dashboard & Evidence Verification

## Technology Stack

### AI & ML
- YOLOv8
- MediaPipe
- OpenCV

### Backend
- Python
- FastAPI
- MongoDB
- JWT Authentication

### Blockchain
- Ethereum (Ganache)
- Solidity
- Web3.py

### Frontend
- React
- Vite

## Project Structure

CCTV-AI-Blockchain/
├── backend/
├── ai/
├── frontend/
├── contracts/
├── storage/
├── docs/
├── .env
└── README.md

## Setup Instructions

### 1. Clone Repository
git clone https://github.com/Aanshtiwari/CCTV-AI-Blockchain.git
cd CCTV-AI-Blockchain

### 2. Backend Setup
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload

### 3. Blockchain Setup
- Start Ganache
- Deploy smart contract

### 4. AI Detection
python ai/detect_and_send.py

### 5. Frontend Setup
cd frontend
npm install
npm run dev

## Authentication Flow

- User logs in
- JWT token generated
- Token used for secured API calls
- Role-based access enforced

## Evidence Verification

1. Encrypted clip hash generated
2. Hash stored on blockchain
3. Investigator recalculates hash
4. Hash matched with blockchain record

## Future Enhancements

- Multi-camera RTSP support
- Facial recognition
- Cloud deployment
- SMS/Email alerts
- Permissioned blockchain
