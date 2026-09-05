import sqlite3
import json
import logging
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import DB_PATH, DATABASE_DIR
try:
    from database.demo_data import SYNTHETIC_WATCHLIST, SYNTHETIC_SCREENINGS
except ModuleNotFoundError:
    from demo_data import SYNTHETIC_WATCHLIST, SYNTHETIC_SCREENINGS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BORDERGUARD_DB")

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema and seeds synthetic demo data if empty."""
    schema_path = DATABASE_DIR / "schema.sql"
    
    if not schema_path.exists():
        logger.error(f"Schema file not found at {schema_path}")
        return

    with get_connection() as conn:
        cursor = conn.cursor()
        with open(schema_path, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        
        # Seed watchlist if empty
        cursor.execute("SELECT COUNT(*) FROM watchlist")
        if cursor.fetchone()[0] == 0:
            logger.info("Seeding synthetic Demo Security Database watchlist...")
            for item in SYNTHETIC_WATCHLIST:
                cursor.execute("""
                    INSERT INTO watchlist 
                    (document_number, document_type, holder_name, status, issue_date, expiry_date, risk_level, reason)
                    VALUES (:document_number, :document_type, :holder_name, :status, :issue_date, :expiry_date, :risk_level, :reason)
                """, item)
        
        # Seed historical screenings if empty
        cursor.execute("SELECT COUNT(*) FROM screenings")
        if cursor.fetchone()[0] == 0:
            logger.info("Seeding synthetic historical screening audit logs...")
            for item in SYNTHETIC_SCREENINGS:
                cursor.execute("""
                    INSERT INTO screenings 
                    (screening_id, timestamp, document_type, holder_name, document_number, mrz_data, 
                     ocr_confidence, extracted_fields, validation_results, tampering_results, 
                     face_match_score, face_status, risk_score, risk_level, final_decision, 
                     processing_time_sec, contributing_factors)
                    VALUES (:screening_id, :timestamp, :document_type, :holder_name, :document_number, :mrz_data, 
                     :ocr_confidence, :extracted_fields, :validation_results, :tampering_results, 
                     :face_match_score, :face_status, :risk_score, :risk_level, :final_decision, 
                     :processing_time_sec, :contributing_factors)
                """, item)
        conn.commit()
    logger.info("Database initialized successfully.")

def search_watchlist(document_number):
    """Searches the Demo Security Database for a document number."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM watchlist WHERE UPPER(document_number) = UPPER(?)", (document_number.strip(),))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def save_screening(data):
    """Saves a new screening audit trail record."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO screenings 
            (screening_id, timestamp, document_type, holder_name, document_number, mrz_data, 
             ocr_confidence, extracted_fields, validation_results, tampering_results, 
             face_match_score, face_status, risk_score, risk_level, final_decision, 
             processing_time_sec, contributing_factors)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("screening_id"),
            data.get("timestamp"),
            data.get("document_type"),
            data.get("holder_name"),
            data.get("document_number"),
            data.get("mrz_data", ""),
            data.get("ocr_confidence", 0.0),
            json.dumps(data.get("extracted_fields", {})),
            json.dumps(data.get("validation_results", {})),
            json.dumps(data.get("tampering_results", {})),
            data.get("face_match_score", 0.0),
            data.get("face_status", "UNKNOWN"),
            data.get("risk_score", 0),
            data.get("risk_level", "LOW"),
            data.get("final_decision", "CLEAR"),
            data.get("processing_time_sec", 0.0),
            json.dumps(data.get("contributing_factors", []))
        ))
        conn.commit()

def get_all_screenings():
    """Retrieves all past screening records sorted by timestamp descending."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM screenings ORDER BY timestamp DESC")
        return [dict(row) for row in cursor.fetchall()]

def get_screening_by_id(screening_id):
    """Retrieves a single screening record by Screening ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM screenings WHERE screening_id = ?", (screening_id,))
        row = cursor.fetchone()
        if row:
            d = dict(row)
            d["extracted_fields"] = json.loads(d["extracted_fields"]) if d["extracted_fields"] else {}
            d["validation_results"] = json.loads(d["validation_results"]) if d["validation_results"] else {}
            d["tampering_results"] = json.loads(d["tampering_results"]) if d["tampering_results"] else {}
            d["contributing_factors"] = json.loads(d["contributing_factors"]) if d["contributing_factors"] else []
            return d
        return None

def get_dashboard_stats():
    """Returns aggregated stats for the main dashboard header cards."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM screenings")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM screenings WHERE risk_level = 'HIGH'")
        high = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM screenings WHERE risk_level = 'MEDIUM'")
        medium = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM screenings WHERE risk_level = 'LOW'")
        low = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(processing_time_sec) FROM screenings")
        avg_time = cursor.fetchone()[0] or 0.0
        
        return {
            "total": total,
            "high": high,
            "medium": medium,
            "low": low,
            "avg_time": round(avg_time, 1)
        }

if __name__ == "__main__":
    init_db()
