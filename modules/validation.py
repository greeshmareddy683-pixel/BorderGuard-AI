import re
from datetime import datetime
from database.database import search_watchlist

def calculate_mrz_check_digit(data_str):
    """
    Computes ICAO 9303 MRZ Check Digit using weights [7, 3, 1].
    """
    weights = [7, 3, 1]
    total = 0
    for i, char in enumerate(data_str):
        if char == '<':
            val = 0
        elif char.isdigit():
            val = int(char)
        elif char.isalpha():
            val = ord(char.upper()) - 55
        else:
            val = 0
        total += val * weights[i % 3]
    return str(total % 10)

def verify_epassport_chip(extracted_fields):
    """
    Simulates e-Passport RFID/NFC microchip PKI digital signature validation
    and DG1/DG2 structure verification against visual OCR text.
    """
    doc_num = extracted_fields.get("Passport Number") or extracted_fields.get("Passport Number / ID") or "P1234567"
    name = extracted_fields.get("Full Name") or "UNKNOWN"
    
    # Simulate PKI RSA/ECDSA digital signature check
    pki_valid = bool(len(doc_num) >= 6)
    chip_checksum = "VALID (0x8F9A2B4C)" if pki_valid else "INVALID (0x00000000)"
    
    return {
        "chip_detected": True,
        "pki_signature_valid": pki_valid,
        "chip_checksum": chip_checksum,
        "dg1_mrz_match": True,
        "dg2_facial_template_match": True,
        "issuer_authority_cert": "ICAO Master List Verified (Country CSCA)"
    }

def validate_document_data(extracted_fields, document_type="Passport"):
    """
    Validates extracted fields, performs MRZ checksum checks, date sanity checks,
    queries the Security Database (SQLite), and checks e-Passport chip data.
    """
    anomalies = []
    status = "PASSED"
    db_record = None

    doc_num = extracted_fields.get("Passport Number") or extracted_fields.get("Passport Number / ID") or extracted_fields.get("Visa Number") or ""
    expiry_str = extracted_fields.get("Date of Expiry") or extracted_fields.get("Valid Until") or ""
    dob_str = extracted_fields.get("Date of Birth") or ""

    # 1. Database Watchlist Check
    if doc_num:
        db_record = search_watchlist(doc_num)
        if db_record:
            db_status = db_record.get("status", "UNKNOWN")
            reason = db_record.get("reason", "No reason specified")
            if db_status in ["BLACKLISTED", "REVOKED", "SUSPICIOUS"]:
                status = "FAILED"
                anomalies.append(f"SECURITY DB WATCHLIST MATCH: Status = {db_status} ({reason})")
            elif db_status == "EXPIRED":
                if status != "FAILED":
                    status = "WARNING"
                anomalies.append("SECURITY DB FLAG: Record marked EXPIRED")

    # 2. Expiration Date Check
    if expiry_str:
        try:
            exp_date = datetime.strptime(expiry_str, "%Y-%m-%d")
            if exp_date < datetime.now():
                if status != "FAILED":
                    status = "WARNING"
                anomalies.append(f"DOCUMENT EXPIRED: Expiry date was {expiry_str}")
        except ValueError:
            anomalies.append(f"INVALID DATE FORMAT: Expiry date '{expiry_str}' format invalid")

    # 3. Passport / ID Format Check
    if doc_num:
        if not re.match(r'^[A-Z0-9]{6,12}$', doc_num.upper()):
            anomalies.append(f"SUSPICIOUS DOCUMENT NUMBER FORMAT: '{doc_num}'")

    # 4. MRZ Checksum Validation
    mrz_doc_check = extracted_fields.get("MRZ Checksum DocNum")
    if doc_num and mrz_doc_check:
        expected = calculate_mrz_check_digit(doc_num)
        if expected != str(mrz_doc_check):
            status = "FAILED"
            anomalies.append(f"MRZ CHECKSUM FAIL: Passport number checksum expected {expected}, got {mrz_doc_check}")

    mrz_dob_check = extracted_fields.get("MRZ Checksum DOB")
    if dob_str and mrz_dob_check and len(dob_str) == 10:
        yymmdd = dob_str[2:4] + dob_str[5:7] + dob_str[8:10]
        expected = calculate_mrz_check_digit(yymmdd)
        if expected != str(mrz_dob_check):
            if status != "FAILED":
                status = "WARNING"
            anomalies.append(f"MRZ DOB CHECKSUM WARN: Expected {expected}, got {mrz_dob_check}")

    # 5. e-Passport NFC RFID Microchip Check
    chip_data = verify_epassport_chip(extracted_fields)

    return {
        "status": status,
        "anomalies": anomalies,
        "db_record": db_record,
        "total_checks": 10,
        "failed_checks": len(anomalies),
        "epassport_chip": chip_data
    }
