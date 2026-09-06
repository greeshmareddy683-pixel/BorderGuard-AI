# 🛂 BORDERGUARD AI
### AI-Powered Identity & Document Screening System

**Secure Border Checkpoint Screening Environment**

Built by **Greeshma** · Team **Code Blockers**

[![Live Demo](https://img.shields.io/badge/🔗_Live_Demo-Streamlit-FF4B4B?style=for-the-badge)](https://borderguard-ai-jwse4nvphxjfmbykwuwydm.streamlit.app/)

---

## 🔗 Live Demo

👉 **[Launch BORDERGUARD AI](https://borderguard-ai-jwse4nvphxjfmbykwuwydm.streamlit.app/)**

> ⚠️ Hosted on Streamlit Community Cloud — the app may take 20–30 seconds to wake up on first load if it's been idle. If it's slow or unresponsive during a demo/review, see **[Run Locally](#-run-locally)** below to spin it up in under a minute.

---

## 📌 Executive Summary

BORDERGUARD AI is an intelligent, multi-stage document and identity screening platform designed for border security checkpoints, airport immigration counters, and law enforcement command centers.

It addresses critical border challenges including fake passports/visas, altered photographs, modified birth dates, tampered stamps, identity impersonation, and blacklisted traveler document use.

---

## ⚡ Core Pipeline Architecture

The application executes a 6-stage automated screening pipeline:

```
DOCUMENT UPLOAD ➔ IMAGE PREPROCESSING ➔ OCR EXTRACTION ➔ DOCUMENT VALIDATION
➔ TAMPERING ANALYSIS ➔ FACE VERIFICATION ➔ RISK ENGINE ➔ FINAL DECISION ➔ AUDIT REPORT (PDF)
```

| Stage | Module | What it does |
|---|---|---|
| **1. OCR Extraction** | `modules/ocr.py` | Passport (ICAO 9303 MRZ), Visa, and National ID field parsing and text extraction with confidence scoring |
| **2. Document Validation** | `modules/validation.py` | MRZ modulo-10 checksum verification, expiration date checks, format regex rules, SQLite watchlist database lookup |
| **3. Tampering & Forgery Analysis** | `modules/tampering.py`, `modules/metadata.py` | Error Level Analysis (ELA) compression map generation, high-frequency noise variance inspection, portrait edge anomaly detection, EXIF editing-software scanning |
| **4. Biometric Face Verification** | `modules/face_verification.py` | Frontal face bounding box detection and multi-channel biometric feature similarity matching between document portrait and live traveler capture |
| **5. Explainable Risk Engine** | `modules/risk_engine.py` | Multi-factor weighted score (0–100) with clear factor attribution, e.g. `+30 Blacklisted record`, `+20 ELA photo anomaly`, `-5 Valid MRZ` |
| **6. Audit Trail & Reporting** | `modules/report_generator.py` | Persistent SQLite logging with unique Screening IDs (`BG-2026-XXXXXX`) and instant downloadable PDF audit reports |

---

## 🛠️ Technology Stack

- **Frontend / Dashboard:** Streamlit + Custom Command Center Dark Theme CSS
- **Computer Vision:** OpenCV (`opencv-python-headless`), Pillow (`PIL`), NumPy, SciPy
- **OCR & Field Parsing:** EasyOCR / Pytesseract + ICAO 9303 MRZ Algorithm
- **Local Security Database:** SQLite3 (`borderguard.db`)
- **PDF Report Generator:** ReportLab
- **Analytics & Charts:** Plotly

---

## ⚠️ Limitations & Ethical Considerations

This project is a **prototype/demo system** built for evaluation purposes and is not deployed in any real screening environment. A few things worth being upfront about:

- **Accuracy is not independently benchmarked** against a large, diverse test set of genuine vs. tampered documents — results shown are indicative, not certified.
- **Face verification bias:** biometric matching systems can have measurable accuracy differences across skin tones, lighting conditions, and demographics. This system has not been audited for fairness and should not be treated as bias-free.
- **False positives vs. false negatives:** in a real border-security context, a false positive wrongly flags a legitimate traveler, while a false negative lets a fraudulent document through. The risk engine's weights are tunable and would need real-world calibration, not just demo defaults.
- **Data handling:** the demo is intended to run on sample/synthetic documents only. It is not built or hardened for storing real passport, visa, or biometric data, and does not implement production-grade encryption, access control, or retention policies.
- **"AI" vs. rule-based:** not every stage is machine learning — MRZ checksum validation, regex format checks, and watchlist lookups are deterministic rule-based logic. Only OCR and face similarity matching involve learned models.

We think naming these limitations openly is part of building responsible AI for high-stakes use cases, not a weakness of the project.

---

## 🚀 Run Locally

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd borderguard-ai

# 2. Install required Python packages
pip install -r requirements.txt

# 3. Launch the Streamlit Command Center
python -m streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## 👥 Team

**Code Blockers**
- Greeshma

---

<p align="center"><i>BORDERGUARD AI — built for Smart India Hackathon</i></p>
