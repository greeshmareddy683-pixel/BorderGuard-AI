import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
REPORTS_DIR = BASE_DIR / "reports"
DEMO_DIR = BASE_DIR / "demo"
ASSETS_DIR = BASE_DIR / "assets"
DB_PATH = DATABASE_DIR / "borderguard.db"

# Ensure essential directories exist
for directory in [DATABASE_DIR, REPORTS_DIR, DEMO_DIR, ASSETS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Application Branding
APP_NAME = "BORDERGUARD AI"
APP_SUBTITLE = "AI-Powered Identity & Document Screening System"
APP_TAGLINE = "Secure Screening Environment"

# Default Risk Engine Weights (Must sum to 1.0 or 100%)
DEFAULT_RISK_WEIGHTS = {
    "ocr_confidence": 0.10,
    "doc_validity": 0.20,
    "database_status": 0.25,
    "tampering_analysis": 0.25,
    "face_verification": 0.20
}

# Risk Thresholds
RISK_LEVELS = {
    "LOW": (0, 25),
    "MEDIUM": (26, 60),
    "HIGH": (61, 100)
}

# UI Color Palette (SOC Command Center Dark Theme)
COLOR_PALETTE = {
    "background": "#0b0f19",
    "card_bg": "#131b2e",
    "sidebar_bg": "#090d16",
    "border": "#1e293b",
    "text_primary": "#f8fafc",
    "text_secondary": "#94a3b8",
    "accent_blue": "#38bdf8",
    "accent_cyan": "#06b6d4",
    "success_green": "#22c55e",
    "warning_amber": "#f59e0b",
    "danger_red": "#ef4444",
}
