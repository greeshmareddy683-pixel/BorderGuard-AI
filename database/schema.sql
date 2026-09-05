-- BORDERGUARD AI - Database Schema

CREATE TABLE IF NOT EXISTS watchlist (
    document_number TEXT PRIMARY KEY,
    document_type TEXT NOT NULL,
    holder_name TEXT NOT NULL,
    status TEXT NOT NULL, -- VALID, EXPIRED, BLACKLISTED, REVOKED, SUSPICIOUS
    issue_date TEXT,
    expiry_date TEXT,
    risk_level TEXT NOT NULL, -- LOW, MEDIUM, HIGH
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS screenings (
    screening_id TEXT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    document_type TEXT NOT NULL,
    holder_name TEXT,
    document_number TEXT,
    mrz_data TEXT,
    ocr_confidence REAL,
    extracted_fields TEXT,      -- Stored as JSON
    validation_results TEXT,    -- Stored as JSON
    tampering_results TEXT,     -- Stored as JSON
    face_match_score REAL,
    face_status TEXT,
    risk_score INTEGER,
    risk_level TEXT,
    final_decision TEXT,
    processing_time_sec REAL,
    contributing_factors TEXT   -- Stored as JSON
);
