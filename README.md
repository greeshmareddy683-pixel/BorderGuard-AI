# BORDERGUARD AI — Fake Identity & Document Screening System

**Application Name:** BORDERGUARD AI  
**Subtitle:** AI-Powered Identity & Document Screening System  
**Tagline:** Secure Border Checkpoint Screening Environment  

---

## 📌 Executive Summary

**BORDERGUARD AI** is an intelligent, multi-stage document and identity screening platform designed for border security checkpoints, airport immigration counters, and law enforcement command centers. 

It addresses critical border challenges including fake passports/visas, altered photographs, modified birth dates, tampered stamps, identity impersonation, and blacklisted traveler document use.

---

## ⚡ Core Pipeline Architecture

The application executes a 6-stage automated screening pipeline:

```
DOCUMENT UPLOAD ➔ IMAGE PREPROCESSING ➔ OCR EXTRACTION ➔ DOCUMENT VALIDATION ➔ TAMPERING ANALYSIS ➔ FACE VERIFICATION ➔ RISK ENGINE ➔ FINAL DECISION ➔ AUDIT REPORT (PDF)
```

1. **OCR EXTRACTION (`modules/ocr.py`):** Passport (ICAO 9303 MRZ), Visa, National ID field parsing and text extraction with confidence scoring.
2. **DOCUMENT VALIDATION (`modules/validation.py`):** MRZ modulo-10 checksum verification, expiration date checks, format regex rules, and SQLite watchlist database lookup.
3. **TAMPERING & FORGERY ANALYSIS (`modules/tampering.py`, `modules/metadata.py`):** Error Level Analysis (ELA) compression map generation, high-frequency noise variance inspection, portrait edge anomaly detection, and EXIF editing software scanning.
4. **BIOMETRIC FACE VERIFICATION (`modules/face_verification.py`):** Frontal face bounding box detection and multi-channel biometric feature similarity matching between document portrait and live traveler capture (via webcam or file upload).
5. **EXPLAINABLE RISK ENGINE (`modules/risk_engine.py`):** Multi-factor weighted score calculation (0–100) providing clear factor attribution (`+30 Blacklisted record`, `+20 ELA photo anomaly`, `-5 Valid MRZ`).
6. **AUDIT TRAIL & REPORTING (`modules/report_generator.py`):** Persistent SQLite database logging with unique Screening IDs (`BG-2026-XXXXXX`) and instant downloadable PDF audit reports.

---

## 🛠️ Technology Stack

* **Frontend / Dashboard:** Streamlit + Custom Command Center Dark Theme CSS
* **Computer Vision:** OpenCV (`opencv-python-headless`), Pillow (`PIL`), NumPy, SciPy
* **OCR & Field Parsing:** EasyOCR / Pytesseract + ICAO 9303 MRZ Algorithm
* **Local Security Database:** SQLite3 (`borderguard.db`)
* **PDF Report Generator:** ReportLab
* **Analytics & Charts:** Plotly

---

## 🚀 Installation & Local Execution

```bash
# 1. Navigate to project directory
cd C:\Users\grees\.gemini\antigravity\scratch\borderguard-ai

# 2. Install required Python packages
pip install -r requirements.txt

# 3. Launch Streamlit Command Center
python -m streamlit run app.py
```

The application will automatically open in your browser at `http://localhost:8501`.
