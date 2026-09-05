from config import DEFAULT_RISK_WEIGHTS, RISK_LEVELS

def calculate_risk_score(ocr_res, val_res, tamp_res, face_res, weights=None):
    """
    Calculates explainable risk score (0-100) based on weighted multi-factor analysis.
    Returns score, risk level, final recommendation, and factor attributions list.
    """
    if weights is None:
        weights = DEFAULT_RISK_WEIGHTS

    risk_points = 0
    factors = []

    # 1. Database Check & Watchlist Status (Weight: 25%)
    db_record = val_res.get("db_record")
    if db_record:
        db_status = db_record.get("status", "UNKNOWN")
        reason = db_record.get("reason", "No reason specified")
        if db_status == "BLACKLISTED":
            risk_points += 35
            factors.append(f"+35 Blacklisted record match: {reason}")
        elif db_status == "REVOKED":
            risk_points += 30
            factors.append(f"+30 Revoked document match: {reason}")
        elif db_status == "SUSPICIOUS":
            risk_points += 25
            factors.append(f"+25 Suspicious watchlist flag: {reason}")
        elif db_status == "EXPIRED":
            risk_points += 18
            factors.append(f"+18 Expired status in database")
        elif db_status == "VALID":
            risk_points -= 5
            factors.append("-5 Validated against security watchlist DB")

    # 2. Tampering & CV Forgery Indicators (Weight: 25%)
    tamp_risk = tamp_res.get("tampering_risk", 0)
    tamp_points = int(tamp_risk * weights["tampering_analysis"])
    risk_points += tamp_points
    if tamp_risk > 60:
        factors.append(f"+{tamp_points} Photo/Text manipulation risk detected ({tamp_risk}%)")
    elif tamp_risk > 30:
        factors.append(f"+{tamp_points} Minor image compression anomalies flagged")

    for ind in tamp_res.get("indicators", []):
        factors.append(f"+5 {ind}")
        risk_points += 5

    # 3. Biometric Face Match Verification (Weight: 20%)
    match_score = face_res.get("match_score", 90.0)
    face_status = face_res.get("status", "MATCH")

    if face_status == "NO MATCH" or match_score < 55.0:
        pts = int((100 - match_score) * weights["face_verification"])
        risk_points += max(pts, 18)
        factors.append(f"+{max(pts, 18)} Biometric face mismatch ({match_score}%)")
    elif face_status == "POSSIBLE MATCH":
        risk_points += 10
        factors.append(f"+10 Moderate face match score ({match_score}%)")
    else:
        risk_points -= 5
        factors.append(f"-5 High biometric face match score ({match_score}%)")

    # 4. Document Validation Anomalies (Weight: 20%)
    anomalies = val_res.get("anomalies", [])
    for anomaly in anomalies:
        if "EXPIRED" in anomaly.upper():
            risk_points += 15
            factors.append(f"+15 Document date expired")
        elif "CHECKSUM" in anomaly.upper():
            risk_points += 12
            factors.append(f"+12 MRZ checksum calculation failed")
        elif "FORMAT" in anomaly.upper():
            risk_points += 8
            factors.append(f"+8 Document number format irregularity")

    if not anomalies and val_res.get("status") == "PASSED":
        risk_points -= 5
        factors.append("-5 Valid MRZ checksums & date sanity verified")

    # 5. OCR Confidence Score (Weight: 10%)
    ocr_conf = ocr_res.get("ocr_confidence", 0.90)
    if ocr_conf < 0.70:
        risk_points += 10
        factors.append(f"+10 Low OCR extraction confidence ({int(ocr_conf * 100)}%)")
    else:
        risk_points -= 3
        factors.append(f"-3 High OCR confidence score ({int(ocr_conf * 100)}%)")

    # Clamp total risk score between 0 and 100
    final_score = int(min(max(risk_points, 0), 100))

    # Determine Risk Level & Action Recommendation
    if final_score >= RISK_LEVELS["HIGH"][0]:
        risk_level = "HIGH"
        final_decision = "REFER FOR SECONDARY INSPECTION"
    elif final_score >= RISK_LEVELS["MEDIUM"][0]:
        risk_level = "MEDIUM"
        final_decision = "VERIFICATION RECOMMENDED"
    else:
        risk_level = "LOW"
        final_decision = "PASS / CLEAR"

    return {
        "risk_score": final_score,
        "risk_level": risk_level,
        "final_decision": final_decision,
        "contributing_factors": factors
    }
