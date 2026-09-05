import json
from datetime import datetime, timedelta

SYNTHETIC_WATCHLIST = [
    {
        "document_number": "J8392014",
        "document_type": "PASSPORT",
        "holder_name": "VIKTOR KORNEV",
        "status": "BLACKLISTED",
        "issue_date": "2019-03-15",
        "expiry_date": "2029-03-14",
        "risk_level": "HIGH",
        "reason": "Interpol Red Notice #IN-90214 for international financial fraud"
    },
    {
        "document_number": "Z9920184",
        "document_type": "PASSPORT",
        "holder_name": "MARIA GONZALEZ",
        "status": "SUSPICIOUS",
        "issue_date": "2021-06-10",
        "expiry_date": "2031-06-09",
        "risk_level": "HIGH",
        "reason": "Multiple entry attempts with altered Date of Birth logged in border network"
    },
    {
        "document_number": "X7728190",
        "document_type": "PASSPORT",
        "holder_name": "AHMED AL-MANSOORI",
        "status": "REVOKED",
        "issue_date": "2018-11-01",
        "expiry_date": "2028-10-31",
        "risk_level": "HIGH",
        "reason": "Reported lost/stolen by legitimate owner on 2025-11-12"
    },
    {
        "document_number": "V-882910",
        "document_type": "VISA",
        "holder_name": "JEAN-LUC DUBOIS",
        "status": "EXPIRED",
        "issue_date": "2023-01-01",
        "expiry_date": "2024-01-01",
        "risk_level": "MEDIUM",
        "reason": "Tourist Visa expired over 12 months ago"
    },
    {
        "document_number": "L4892011",
        "document_type": "PASSPORT",
        "holder_name": "SERGEI PETROV",
        "status": "BLACKLISTED",
        "issue_date": "2020-02-20",
        "expiry_date": "2030-02-19",
        "risk_level": "HIGH",
        "reason": "Flagged document series associated with counterfeit syndicate"
    },
    {
        "document_number": "P1234567",
        "document_type": "PASSPORT",
        "holder_name": "JOHNATHAN DOE",
        "status": "VALID",
        "issue_date": "2022-05-10",
        "expiry_date": "2032-05-09",
        "risk_level": "LOW",
        "reason": "Verified genuine document record"
    }
]

SYNTHETIC_SCREENINGS = [
    {
        "screening_id": "BG-2026-000181",
        "timestamp": (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
        "document_type": "Passport",
        "holder_name": "VIKTOR KORNEV",
        "document_number": "J8392014",
        "mrz_data": "P<UTOKORNEV<<VIKTOR<<<<<<<<<<<<<<<<<<<<<<<<<<\nJ8392014<0UTO8504128M2903142<<<<<<<<<<<<<<02",
        "ocr_confidence": 0.94,
        "extracted_fields": json.dumps({
            "Full Name": "VIKTOR KORNEV",
            "Passport Number": "J8392014",
            "Nationality": "UTO",
            "Date of Birth": "1985-04-12",
            "Gender": "M",
            "Date of Expiry": "2029-03-14"
        }),
        "validation_results": json.dumps({
            "status": "FAILED",
            "anomalies": ["Matched Blacklisted Database Record"]
        }),
        "tampering_results": json.dumps({
            "tampering_risk": 75,
            "indicators": ["Compression anomaly around portrait", "Metadata indicates editing software"]
        }),
        "face_match_score": 38.5,
        "face_status": "NO_MATCH",
        "risk_score": 78,
        "risk_level": "HIGH",
        "final_decision": "REFER FOR SECONDARY INSPECTION",
        "processing_time_sec": 2.4,
        "contributing_factors": json.dumps([
            "+30 Blacklisted document number",
            "+20 Portrait region manipulation anomaly",
            "+18 Biometric face mismatch (38.5%)",
            "+10 Metadata editing software detected"
        ])
    },
    {
        "screening_id": "BG-2026-000182",
        "timestamp": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
        "document_type": "Passport",
        "holder_name": "JOHNATHAN DOE",
        "document_number": "P1234567",
        "mrz_data": "P<USADOE<<JOHNATHAN<<<<<<<<<<<<<<<<<<<<<<<<<\nP1234567<4USA9001015M3205090<<<<<<<<<<<<<<00",
        "ocr_confidence": 0.98,
        "extracted_fields": json.dumps({
            "Full Name": "JOHNATHAN DOE",
            "Passport Number": "P1234567",
            "Nationality": "USA",
            "Date of Birth": "1990-01-01",
            "Gender": "M",
            "Date of Expiry": "2032-05-09"
        }),
        "validation_results": json.dumps({
            "status": "PASSED",
            "anomalies": []
        }),
        "tampering_results": json.dumps({
            "tampering_risk": 8,
            "indicators": []
        }),
        "face_match_score": 96.2,
        "face_status": "MATCH",
        "risk_score": 12,
        "risk_level": "LOW",
        "final_decision": "PASS / CLEAR",
        "processing_time_sec": 1.9,
        "contributing_factors": json.dumps([
            "-5 Valid MRZ Checksum",
            "-3 High OCR Confidence (98%)",
            "-5 High Biometric Face Match (96.2%)"
        ])
    },
    {
        "screening_id": "BG-2026-000183",
        "timestamp": (datetime.now() - timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
        "document_type": "Visa",
        "holder_name": "JEAN-LUC DUBOIS",
        "document_number": "V-882910",
        "mrz_data": "V<FRADUBOIS<<JEAN<LUC<<<<<<<<<<<<<<<<<<<<<<<\nV-882910<8FRA7809204M2401018<<<<<<<<<<<<<<04",
        "ocr_confidence": 0.91,
        "extracted_fields": json.dumps({
            "Full Name": "JEAN-LUC DUBOIS",
            "Visa Number": "V-882910",
            "Nationality": "FRA",
            "Date of Birth": "1978-09-20",
            "Valid Until": "2024-01-01"
        }),
        "validation_results": json.dumps({
            "status": "WARNING",
            "anomalies": ["Visa Expiry Date Past"]
        }),
        "tampering_results": json.dumps({
            "tampering_risk": 32,
            "indicators": ["Text region edge noise inconsistency"]
        }),
        "face_match_score": 82.0,
        "face_status": "MATCH",
        "risk_score": 48,
        "risk_level": "MEDIUM",
        "final_decision": "VERIFICATION RECOMMENDED",
        "processing_time_sec": 2.1,
        "contributing_factors": json.dumps([
            "+25 Expired document status in security DB",
            "+15 Minor text region anomaly detected",
            "-5 High Biometric Face Match (82.0%)"
        ])
    }
]
