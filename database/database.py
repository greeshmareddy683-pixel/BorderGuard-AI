import sqlite3
import json
import logging
import sys
from pathlib import Path

# Add project root to sys.path at index 0
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import DB_PATH, DATABASE_DIR

try:
    from database.demo_data import SYNTHETIC_WATCHLIST, SYNTHETIC_SCREENINGS
except (ImportError, ModuleNotFoundError):
    try:
        from demo_data import SYNTHETIC_WATCHLIST, SYNTHETIC_SCREENINGS
    except (ImportError, ModuleNotFoundError):
        from .demo_data import SYNTHETIC_WATCHLIST, SYNTHETIC_SCREENINGS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BORDERGUARD_DB")

def safe_json_dumps(obj):
    """Robust JSON serializer that handles sqlite3.Row, numpy arrays, and custom objects."""
    def default(o):
        if isinstance(o, sqlite3.Row):
            return dict(o)
        if hasattr(o, 'tolist'):
            return o.tolist()
        if hasattr(o, '__dict__'):
            return o.__dict__
        return str(o)
    try:
        return json.dumps(obj, default=default)
    except Exception as e:
        logger.warning(f"JSON serialization fallback used: {e}")
        return json.dumps(str(obj))

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

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            with open(schema_path, "r", encoding="utf-8") as f:
                cursor.executescript(f.read())
            
            cursor.execute("SELECT COUNT(*) FROM watchlist")
            if cursor.fetchone()[0] == 0:
                logger.info("Seeding Security Watchlist database...")
                for item in SYNTHETIC_WATCHLIST:
                    cursor.execute("""
                        INSERT INTO watchlist 
                        (document_number, document_type, holder_name, status, issue_date, expiry_date, risk_level, reason)
                        VALUES (:document_number, :document_type, :holder_name, :status, :issue_date, :expiry_date, :risk_level, :reason)
                    """, item)
            
            cursor.execute("SELECT COUNT(*) FROM screenings")
            if cursor.fetchone()[0] == 0:
                logger.info("Seeding historical screening audit logs...")
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
    except Exception as e:
        logger.error(f"Database initialization error (proceeding in-memory): {e}")

def search_watchlist(document_number):
    """Searches the Security Database for a document number."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM watchlist WHERE UPPER(document_number) = UPPER(?)", (document_number.strip(),))
            row = cursor.fetchone()
            if row:
                return dict(row)
    except Exception as e:
        logger.error(f"Watchlist search error: {e}")
    return None

def save_screening(data):
    """Saves a new screening audit trail record safely."""
    try:
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
                safe_json_dumps(data.get("extracted_fields", {})),
                safe_json_dumps(data.get("validation_results", {})),
                safe_json_dumps(data.get("tampering_results", {})),
                data.get("face_match_score", 0.0),
                data.get("face_status", "UNKNOWN"),
                data.get("risk_score", 0),
                data.get("risk_level", "LOW"),
                data.get("final_decision", "CLEAR"),
                data.get("processing_time_sec", 0.0),
                safe_json_dumps(data.get("contributing_factors", []))
            ))
            conn.commit()
    except Exception as e:
        logger.error(f"Save screening database log warning: {e}")

def get_all_screenings():
    """Retrieves all past screening records sorted by timestamp descending."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM screenings ORDER BY timestamp DESC")
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Get screenings error: {e}")
        return []

def get_screening_by_id(screening_id):
    """Retrieves a single screening record by Screening ID."""
    try:
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
    except Exception as e:
        logger.error(f"Get screening by ID error: {e}")
    return None

def get_dashboard_stats():
    """Returns aggregated stats for the main dashboard header cards."""
    try:
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
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return {"total": 0, "high": 0, "medium": 0, "low": 0, "avg_time": 0.0}

if __name__ == "__main__":
    init_db()
