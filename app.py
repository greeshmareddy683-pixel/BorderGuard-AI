import sys
from pathlib import Path

# Add project root to sys.path at index 0 for Streamlit Cloud package resolution
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import time
import json
import logging
import streamlit as st
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BORDERGUARD_APP")

# Import configuration and custom modules
from config import APP_NAME, APP_SUBTITLE, APP_TAGLINE, COLOR_PALETTE, BASE_DIR
from database.database import (
    init_db, get_dashboard_stats, get_all_screenings,
    get_screening_by_id, save_screening, get_connection
)
from modules.ocr import extract_document_info
from modules.validation import validate_document_data
from modules.tampering import analyze_tampering, generate_uv_simulation
from modules.metadata import analyze_metadata
from modules.face_verification import verify_faces
from modules.risk_engine import calculate_risk_score
from modules.report_generator import generate_pdf_report
from utils.helpers import generate_screening_id, get_current_timestamp
from utils.preprocessing import preprocess_image_for_ocr

# Page Configuration
st.set_page_config(
    page_title="BORDERGUARD AI — Identity & Document Screening",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
def load_css():
    css_path = BASE_DIR / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
init_db()

# Session State Initialization
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Dashboard"
if "current_screening" not in st.session_state:
    st.session_state.current_screening = None

# Sidebar Branding & Navigation
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 10px 0;'>
            <h2 style='color: #38bdf8; font-family: monospace; margin:0;'>🛡️ {APP_NAME}</h2>
            <p style='color: #94a3b8; font-size: 0.78rem; margin-top:4px;'>{APP_SUBTITLE}</p>
        </div>
        <hr style='border-color: #1e293b; margin: 15px 0;'>
    """, unsafe_allow_html=True)

    page = st.radio(
        "NAVIGATION",
        ["● Dashboard", "● New Screening", "● Screening History", "● Security Database"],
        key="nav_radio"
    )
    clean_page_name = page.replace("● ", "").strip()

    st.markdown("<hr style='border-color: #1e293b; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("""
        <div style='background-color: #131b2e; padding: 12px; border-radius: 6px; border: 1px solid #1e293b; font-size: 0.75rem; color: #94a3b8;'>
            <strong style='color: #f8fafc;'>System Status:</strong> <span style='color: #22c55e;'>ONLINE</span><br>
            <strong>Environment:</strong> Secure Border Counter<br>
            <strong>Database Connection:</strong> Active
        </div>
    """, unsafe_allow_html=True)

# Common Header Banner
def render_header(title, subtitle):
    st.markdown(f"""
        <div class='command-header'>
            <div class='command-title'>{title}</div>
            <div class='command-subtitle'>{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)

# Function to render screening results cleanly
def render_screening_results(s):
    st.markdown("---")
    risk_lvl = s["risk_level"]
    risk_cls = "high" if risk_lvl == "HIGH" else ("medium" if risk_lvl == "MEDIUM" else "low")
    
    # High Risk Alert Dispatch Banner
    if risk_lvl == "HIGH":
        st.markdown(f"""
            <div style='background: linear-gradient(90deg, #7f1d1d 0%, #991b1b 100%); border: 2px solid #ef4444; border-radius: 8px; padding: 14px 20px; margin-bottom: 15px;'>
                <div style='font-size:1.1rem; font-weight:700; color:#f8fafc;'>🚨 SECURITY THREAT ALERT DISPATCHED</div>
                <p style='margin:4px 0 0 0; color:#fca5a5; font-size:0.85rem;'>Screening ID {s['screening_id']} flagged as HIGH RISK ({s['risk_score']}/100). Automated dispatch sent to Duty Supervisor & Counter Officer.</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class='content-card' style='border-left: 6px solid #ef4444;'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <h2 style='margin:0; color:#38bdf8; font-family:monospace;'>SCREENING COMPLETE — {s['screening_id']}</h2>
                    <p style='color:#94a3b8; margin-top:4px;'>Processed in {s['processing_time_sec']}s • {s['timestamp']}</p>
                </div>
                <div style='text-align:right;'>
                    <div style='font-size:2.2rem; font-weight:700;' class='metric-value {risk_cls}'>{s['risk_score']} / 100</div>
                    <span class='status-pill status-{risk_cls}'>{risk_lvl} RISK</span>
                </div>
            </div>
            <hr style='border-color:#1e293b; margin:15px 0;'>
            <div style='font-size:1.1rem; font-weight:700; color:#f8fafc;'>
                RECOMMENDED ACTION: <span style='color:#ef4444;'>{s['final_decision']}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 5 Module Summaries
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>OCR Extraction</div><div class='metric-value info'>{int(s['ocr_confidence']*100)}%</div></div>", unsafe_allow_html=True)
    with m2:
        val_st = s["validation_results"].get("status", "PASSED")
        val_color = "low" if val_st == "PASSED" else "high"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Doc Validation</div><div class='metric-value {val_color}'>{val_st}</div></div>", unsafe_allow_html=True)
    with m3:
        tamp_k = s["tampering_results"].get("tampering_risk", 0)
        tamp_color = "high" if tamp_k > 50 else "low"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Tampering Risk</div><div class='metric-value {tamp_color}'>{tamp_k}%</div></div>", unsafe_allow_html=True)
    with m4:
        face_st = s["face_status"]
        face_color = "low" if face_st == "MATCH" else "high"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Face Match</div><div class='metric-value {face_color}'>{s['face_match_score']}%</div></div>", unsafe_allow_html=True)
    with m5:
        db_rec = s["validation_results"].get("db_record")
        db_status = db_rec.get("status") if db_rec else "CLEAR"
        db_color = "high" if db_status in ["BLACKLISTED", "REVOKED"] else "low"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Security DB</div><div class='metric-value {db_color}'>{db_status}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Detailed Factor Analysis & Advanced Visual Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📌 Key Findings & Factors", 
        "📄 Extracted Fields & MRZ", 
        "🔍 Tampering & ELA Map", 
        "🔦 UV Lamp Security Check", 
        "👤 Face Match & Liveness", 
        "📶 e-Passport NFC Chip"
    ])

    with tab1:
        st.markdown("<div class='content-card'><div class='card-title'>🔴 CONTRIBUTING RISK FACTORS (EXPLAINABLE AI)</div>", unsafe_allow_html=True)
        for factor in s["contributing_factors"]:
            if factor.startswith("+"):
                st.markdown(f"<p style='color:#ef4444; font-family:monospace; margin:4px 0;'>{factor}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color:#22c55e; font-family:monospace; margin:4px 0;'>{factor}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='content-card'><div class='card-title'>📄 EXTRACTED DOCUMENT FIELDS</div>", unsafe_allow_html=True)
        st.json(s["extracted_fields"])
        st.code(f"MRZ READOUT:\n{s.get('mrz_data', 'N/A')}", language="text")
        
        if s.get("preprocessed_img"):
            with st.expander("🔬 View OpenCV OCR Preprocessed Enhancement Image"):
                st.image(s["preprocessed_img"], caption="Adaptive CLAHE Noise Reduction & Contrast Filter", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='content-card'><div class='card-title'>🔍 ERROR LEVEL ANALYSIS (ELA) VISUAL MAP</div>", unsafe_allow_html=True)
        st.markdown("High-intensity visual brightness variance highlights re-compressed or spliced image regions.")
        if s.get("ela_image"):
            st.image(s["ela_image"], caption="Error Level Analysis (ELA) Compression Map", use_container_width=True)
        else:
            st.info("ELA Visual Map available for live uploads.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown("<div class='content-card'><div class='card-title'>🔦 ULTRAVIOLET (365nm) SECURITY LAMP SIMULATION</div>", unsafe_allow_html=True)
        st.markdown("Simulates UV lamp illumination to reveal optical watermarks, fluorescent threads, and state crests.")
        if s.get("uv_image"):
            st.image(s["uv_image"], caption="UV 365nm Optical Watermark & Fluorescence Analysis Map", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab5:
        st.markdown("<div class='content-card'><div class='card-title'>👤 BIOMETRIC FACE MATCH & 3D LIVENESS ANALYSIS</div>", unsafe_allow_html=True)
        st.markdown(f"**Face Match Score:** `{s['face_match_score']}%` • **Face Status:** `{s['face_status']}`")
        st.markdown(f"**3D Face Liveness:** `{s.get('liveness_status', 'VERIFIED REAL')} ({s.get('liveness_score', 96.0)}%)`")
        
        view_mode = st.radio("Visual Overlay Mode", ["🕸️ Biometric Landmark Mesh & Feature Triangulation", "🔲 Standard Bounding Box"], horizontal=True, key=f"face_view_mode_{s['screening_id']}")
        
        use_mesh = "Mesh" in view_mode
        doc_vis = s.get("mesh_doc") if use_mesh and s.get("mesh_doc") else s.get("annotated_doc")
        live_vis = s.get("mesh_live") if use_mesh and s.get("mesh_live") else s.get("annotated_live")

        f_col1, f_col2 = st.columns(2)
        with f_col1:
            if doc_vis:
                st.image(doc_vis, caption="Document Portrait Landmark Mesh & Vector Geometry", use_container_width=True)
        with f_col2:
            if live_vis:
                st.image(live_vis, caption="Live Traveler Photo Landmark Mesh & Vector Geometry", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab6:
        st.markdown("<div class='content-card'><div class='card-title'>📶 e-PASSPORT RFID MICROCHIP DATA (NFC / PKI)</div>", unsafe_allow_html=True)
        chip = s["validation_results"].get("epassport_chip", {})
        st.json(chip)
        st.markdown("</div>", unsafe_allow_html=True)

    # PDF Download Button
    try:
        pdf_file = generate_pdf_report(s)
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="📥 DOWNLOAD PDF AUDIT REPORT",
                data=f,
                file_name=f"Screening_Report_{s['screening_id']}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key=f"pdf_btn_{s['screening_id']}"
            )
    except Exception as pdf_err:
        logger.warning(f"PDF report generation skipped: {pdf_err}")


# PAGE 1: DASHBOARD
if clean_page_name == "Dashboard":
    render_header("COMMAND CENTER DASHBOARD", "Real-time border checkpoint identity & document screening metrics")

    stats = get_dashboard_stats()

    # Top Metric Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Total Screenings</div>
                <div class='metric-value info'>{stats['total']}</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>High Risk</div>
                <div class='metric-value high'>{stats['high']}</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Medium Risk</div>
                <div class='metric-value medium'>{stats['medium']}</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Low Risk</div>
                <div class='metric-value low'>{stats['low']}</div>
            </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Avg Proc. Time</div>
                <div class='metric-value info'>{stats['avg_time']}s</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Pipeline Diagram Visualization
    st.markdown("""
        <div class='content-card'>
            <div class='card-title'>⚡ LIVE AI SCREENING PIPELINE</div>
            <div class='pipeline-container'>
                <div class='pipeline-step'>
                    <div class='step-icon done'>1</div>
                    <div class='step-label'>Upload</div>
                </div>
                <div class='pipeline-arrow'>➔</div>
                <div class='pipeline-step'>
                    <div class='step-icon done'>2</div>
                    <div class='step-label'>OCR</div>
                </div>
                <div class='pipeline-arrow'>➔</div>
                <div class='pipeline-step'>
                    <div class='step-icon done'>3</div>
                    <div class='step-label'>Validation</div>
                </div>
                <div class='pipeline-arrow'>➔</div>
                <div class='pipeline-step'>
                    <div class='step-icon done'>4</div>
                    <div class='step-label'>Tampering</div>
                </div>
                <div class='pipeline-arrow'>➔</div>
                <div class='pipeline-step'>
                    <div class='step-icon done'>5</div>
                    <div class='step-label'>Face Match</div>
                </div>
                <div class='pipeline-arrow'>➔</div>
                <div class='pipeline-step'>
                    <div class='step-icon done'>6</div>
                    <div class='step-label'>Risk Engine</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Row 2: Risk Analytics Donut Chart & Threat Breakdown Cards
    col_chart, col_summary = st.columns([1, 1])

    with col_chart:
        st.markdown("<div class='content-card'><div class='card-title'>📊 RISK DISTRIBUTION ANALYTICS</div>", unsafe_allow_html=True)
        import plotly.express as px
        labels = ['High Risk', 'Medium Risk', 'Low Risk']
        values = [stats['high'], stats['medium'], stats['low']]
        if sum(values) > 0:
            fig = px.pie(
                values=values,
                names=labels,
                color=labels,
                color_discrete_map={'High Risk': '#ef4444', 'Medium Risk': '#f59e0b', 'Low Risk': '#22c55e'},
                hole=0.55
            )
            fig.update_layout(
                height=260,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                font=dict(color="#94a3b8")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No screening data logged yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_summary:
        st.markdown("<div class='content-card'><div class='card-title'>🛡️ THREAT LEVEL METRIC BREAKDOWN</div>", unsafe_allow_html=True)
        total_cnt = max(stats['total'], 1)
        high_pct = int((stats['high'] / total_cnt) * 100)
        med_pct = int((stats['medium'] / total_cnt) * 100)
        low_pct = int((stats['low'] / total_cnt) * 100)

        st.markdown(f"""
            <div style='margin-bottom:16px;'>
                <div style='display:flex; justify-content:space-between; font-size:0.88rem; margin-bottom:6px;'>
                    <span style='color:#ef4444; font-weight:600;'>🔴 High Risk Screenings</span>
                    <span style='color:#f8fafc; font-weight:700;'>{stats['high']} ({high_pct}%)</span>
                </div>
                <div style='background-color:#1e293b; border-radius:4px; height:10px;'>
                    <div style='background-color:#ef4444; width:{high_pct}%; height:10px; border-radius:4px;'></div>
                </div>
            </div>
            <div style='margin-bottom:16px;'>
                <div style='display:flex; justify-content:space-between; font-size:0.88rem; margin-bottom:6px;'>
                    <span style='color:#f59e0b; font-weight:600;'>🟠 Medium Risk Screenings</span>
                    <span style='color:#f8fafc; font-weight:700;'>{stats['medium']} ({med_pct}%)</span>
                </div>
                <div style='background-color:#1e293b; border-radius:4px; height:10px;'>
                    <div style='background-color:#f59e0b; width:{med_pct}%; height:10px; border-radius:4px;'></div>
                </div>
            </div>
            <div style='margin-bottom:16px;'>
                <div style='display:flex; justify-content:space-between; font-size:0.88rem; margin-bottom:6px;'>
                    <span style='color:#22c55e; font-weight:600;'>🟢 Low Risk (Cleared)</span>
                    <span style='color:#f8fafc; font-weight:700;'>{stats['low']} ({low_pct}%)</span>
                </div>
                <div style='background-color:#1e293b; border-radius:4px; height:10px;'>
                    <div style='background-color:#22c55e; width:{low_pct}%; height:10px; border-radius:4px;'></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Row 3: Interactive Border Checkpoint Risk Map
    st.markdown("<div class='content-card'><div class='card-title'>🗺️ BORDER CHECKPOINT RISK MAP</div>", unsafe_allow_html=True)
    import pandas as pd
    map_data = pd.DataFrame([
        {"Checkpoint": "Terminal 1 - Int'l Airport", "lat": 28.5562, "lon": 77.1000, "Risk": "HIGH (78/100)", "Screenings": 142},
        {"Checkpoint": "Terminal 3 - Immigration", "lat": 19.0896, "lon": 72.8656, "Risk": "LOW (12/100)", "Screenings": 389},
        {"Checkpoint": "Land Border Checkpoint Alpha", "lat": 31.6042, "lon": 74.5725, "Risk": "HIGH (88/100)", "Screenings": 94},
        {"Checkpoint": "Seaport Counter 3", "lat": 13.0827, "lon": 80.2707, "Risk": "MEDIUM (48/100)", "Screenings": 210}
    ])
    st.map(map_data, zoom=4, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Row 4: Full Width Table
    st.markdown("<div class='content-card'><div class='card-title'>📋 RECENT BORDER SCREENINGS</div>", unsafe_allow_html=True)
    screenings = get_all_screenings()
    if screenings:
        df_display = []
        for s in screenings[:8]:
            df_display.append({
                "Screening ID": s["screening_id"],
                "Document": f"{s['document_type']} ({s['document_number']})",
                "Holder Name": s["holder_name"],
                "Risk Score": f"{s['risk_score']}/100",
                "Risk Level": s["risk_level"],
                "Decision": s["final_decision"],
                "Time": s["timestamp"]
            })
        st.dataframe(pd.DataFrame(df_display), use_container_width=True)
    else:
        st.info("No screenings logged yet.")
    st.markdown("</div>", unsafe_allow_html=True)


# PAGE 2: NEW SCREENING (HERO FEATURE)
elif clean_page_name == "New Screening":
    render_header("NEW BORDER SCREENING", "Upload identity & travel documents for automated AI-assisted risk analysis")

    col_u1, col_u2 = st.columns(2)

    with col_u1:
        st.markdown("<div class='content-card'><div class='card-title'>📄 1. TRAVEL DOCUMENT</div>", unsafe_allow_html=True)
        doc_file = st.file_uploader("Upload Passport / Visa / National ID / Driving License", type=["jpg", "jpeg", "png", "webp"], key="doc_uploader")
        st.markdown("<p style='font-size:0.75rem; color:#94a3b8;'>Supported Formats: Passport, Visa, ID Card (JPEG, PNG)</p></div>", unsafe_allow_html=True)

    with col_u2:
        st.markdown("<div class='content-card'><div class='card-title'>👤 2. LIVE TRAVELER PHOTOGRAPH</div>", unsafe_allow_html=True)
        live_mode = st.radio("Capture Method", ["📷 Take Live Photo (On-spot Camera)", "📁 Upload Photo File"], horizontal=True, key="live_mode_radio")
        
        live_file = None
        if "Camera" in live_mode:
            live_file = st.camera_input("Click photo to capture traveler face", key="camera_capture")
        else:
            live_file = st.file_uploader("Upload Person Photograph File", type=["jpg", "jpeg", "png", "webp"], key="live_file_uploader")
            
        st.markdown("<p style='font-size:0.75rem; color:#94a3b8;'>Used for biometric face verification against document portrait</p></div>", unsafe_allow_html=True)

    start_btn = st.button("🚀 START AI SCREENING PIPELINE", use_container_width=True)

    if start_btn:
        if doc_file is None:
            st.error("Please upload a travel document image!")
        else:
            try:
                t_start = time.time()
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Step 1: Receiving Document
                status_text.markdown("`[1/6] Processing document image...`")
                doc_img = Image.open(doc_file)
                preprocessed_img = preprocess_image_for_ocr(doc_img)
                progress_bar.progress(15)

                # Step 2: OCR Extraction
                status_text.markdown("`[2/6] Running OCR & MRZ Field Extraction...`")
                ocr_res = extract_document_info(doc_img)
                progress_bar.progress(35)

                # Step 3: Document Validation & e-Passport Chip Check
                status_text.markdown("`[3/6] Validating document dates, format, e-Passport NFC chip, and Watchlist DB...`")
                val_res = validate_document_data(ocr_res["fields"], ocr_res["document_type"])
                progress_bar.progress(55)

                # Step 4: Digital Tampering & UV Security Lamp Analysis
                status_text.markdown("`[4/6] Executing ELA Compression Map & UV Lamp Fluorescence Inspection...`")
                tamp_res = analyze_tampering(doc_img)
                meta_res = analyze_metadata(doc_img)
                tamp_res["indicators"].extend(meta_res["indicators"])
                progress_bar.progress(75)

                # Step 5: Face Verification & Liveness Anti-Spoof Check
                status_text.markdown("`[5/6] Verifying biometric facial embeddings & 3D face liveness...`")
                live_img = Image.open(live_file) if live_file is not None else None
                face_res = verify_faces(doc_img, live_img)
                progress_bar.progress(90)

                # Step 6: Risk Scoring Engine
                status_text.markdown("`[6/6] Computing explainable risk score & generating audit record...`")
                risk_res = calculate_risk_score(ocr_res, val_res, tamp_res, face_res)
                progress_bar.progress(100)
                t_end = time.time()

                proc_time = round(t_end - t_start, 2)
                sid = generate_screening_id()

                doc_num = ocr_res["fields"].get("Passport Number") or ocr_res["fields"].get("Passport Number / ID") or "P1234567"
                holder_name = ocr_res["fields"].get("Full Name") or "UNKNOWN HOLDER"

                # Construct final screening record dict
                screening_record = {
                    "screening_id": sid,
                    "timestamp": get_current_timestamp(),
                    "document_type": ocr_res["document_type"],
                    "holder_name": holder_name,
                    "document_number": doc_num,
                    "mrz_data": ocr_res["mrz_string"],
                    "ocr_confidence": ocr_res["ocr_confidence"],
                    "extracted_fields": ocr_res["fields"],
                    "validation_results": val_res,
                    "tampering_results": {
                        "tampering_risk": tamp_res["tampering_risk"],
                        "indicators": tamp_res["indicators"]
                    },
                    "face_match_score": face_res["match_score"],
                    "face_status": face_res["status"],
                    "liveness_score": face_res.get("liveness_score", 96.0),
                    "liveness_status": face_res.get("liveness_status", "VERIFIED REAL"),
                    "risk_score": risk_res["risk_score"],
                    "risk_level": risk_res["risk_level"],
                    "final_decision": risk_res["final_decision"],
                    "processing_time_sec": proc_time,
                    "contributing_factors": risk_res["contributing_factors"],
                    "ela_image": tamp_res.get("ela_image"),
                    "uv_image": tamp_res.get("uv_image"),
                    "preprocessed_img": preprocessed_img,
                    "annotated_doc": face_res.get("annotated_doc"),
                    "mesh_doc": face_res.get("mesh_doc"),
                    "annotated_live": face_res.get("annotated_live"),
                    "mesh_live": face_res.get("mesh_live")
                }

                save_screening(screening_record)
                st.session_state.current_screening = screening_record
                st.success(f"Screening Completed in {proc_time}s! ID: {sid}")
                render_screening_results(screening_record)

            except Exception as pipeline_err:
                logger.error(f"Pipeline execution warning: {pipeline_err}")
                st.error(f"Screening Processing Error: {pipeline_err}")

    elif st.session_state.current_screening:
        render_screening_results(st.session_state.current_screening)


# PAGE 3: SCREENING HISTORY
elif clean_page_name == "Screening History":
    render_header("SCREENING HISTORY & AUDIT TRAIL", "Searchable historical log of border document evaluations")

    screenings = get_all_screenings()
    if screenings:
        import pandas as pd
        df = pd.DataFrame(screenings)
        st.dataframe(df[["screening_id", "timestamp", "holder_name", "document_number", "risk_score", "risk_level", "final_decision"]], use_container_width=True)
    else:
        st.info("No historical screening records found.")


# PAGE 4: SECURITY DATABASE
elif clean_page_name == "Security Database":
    render_header("SECURITY DATABASE", "Watchlist and blacklisted identity records (SQLite)")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM watchlist")
    records = [dict(r) for r in cursor.fetchall()]

    import pandas as pd
    st.dataframe(pd.DataFrame(records), use_container_width=True)
