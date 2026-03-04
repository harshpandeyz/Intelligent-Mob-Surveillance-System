# Intelligent Mob Surveillance System using AI and Blockchain

An AI-powered intelligent CCTV surveillance framework designed to automatically detect suspicious criminal activities in real-time and ensure tamper-proof storage of digital evidence using blockchain-based cryptographic security.

---

## Problem Statement

Traditional CCTV surveillance systems depend on continuous human monitoring and utilize centralized storage mechanisms where recorded video evidence can be modified, deleted, or tampered with. This compromises the reliability of digital forensic evidence during legal investigations.

The proposed Intelligent Mob Surveillance System (IMS) integrates Artificial Intelligence with Blockchain technology to automate criminal activity detection and ensure the integrity, confidentiality, and authenticity of surveillance evidence.

---

## Key Features

- Real-time CCTV monitoring  
- AI-based mob/criminal activity detection (YOLOv8)  
- Suspicious event-triggered video clip extraction  
- AES-256 encryption of extracted evidence  
- SHA-256 hash generation for integrity verification  
- Blockchain-based immutable hash logging  
- Tamper-proof evidence verification  
- Secure monitoring dashboard with authentication  

---

## System Architecture

CCTV Camera  
↓  
AI Detection Module (YOLOv8)  
↓  
Suspicious Activity Detection  
↓  
Video Clip Extraction  
↓  
AES-256 Encryption  
↓  
SHA-256 Hash Generation  
↓  
Ethereum Blockchain Logging  
↓  
Monitoring Dashboard & Evidence Verification  

---

## Technology Stack

### AI & Computer Vision
- YOLOv8
- OpenCV
- MediaPipe

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

---

## Project Structure
