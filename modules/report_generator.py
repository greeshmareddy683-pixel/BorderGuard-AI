import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from config import REPORTS_DIR

def generate_pdf_report(screening_data, filename=None):
    """
    Generates an official PDF Audit Report for a given screening record.
    Returns absolute file path of the generated PDF.
    """
    sid = screening_data.get("screening_id", "BG-REPORT")
    if filename is None:
        filename = f"Screening_Report_{sid}.pdf"
    
    pdf_path = REPORTS_DIR / filename

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette for PDF
    c_primary = colors.HexColor("#0f172a")
    c_blue = colors.HexColor("#0284c7")
    c_red = colors.HexColor("#dc2626")
    c_amber = colors.HexColor("#d97706")
    c_green = colors.HexColor("#16a34a")

    risk_lvl = screening_data.get("risk_level", "LOW")
    risk_color = c_red if risk_lvl == "HIGH" else (c_amber if risk_lvl == "MEDIUM" else c_green)

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=c_primary
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748b")
    )

    heading2_style = ParagraphStyle(
        'DocHeading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_blue,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    elements = []

    # Header Banner
    elements.append(Paragraph("BORDERGUARD AI — SECURITY SCREENING AUDIT REPORT", title_style))
    elements.append(Paragraph(f"Official Border Checkpoint Inspection Record • Screening ID: {sid} • Date: {screening_data.get('timestamp')}", subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_blue, spaceBefore=2, spaceAfter=12))

    # Executive Summary Card Table
    summary_data = [
        [
            Paragraph("<b>FINAL RISK SCORE</b>", body_style),
            Paragraph(f"<font color='{risk_color.hexval()}'><b>{screening_data.get('risk_score')}/100 ({risk_lvl} RISK)</b></font>", body_style)
        ],
        [
            Paragraph("<b>RECOMMENDED ACTION</b>", body_style),
            Paragraph(f"<b>{screening_data.get('final_decision')}</b>", body_style)
        ],
        [
            Paragraph("<b>PROCESSING TIME</b>", body_style),
            Paragraph(f"{screening_data.get('processing_time_sec')} seconds", body_style)
        ]
    ]

    t_summary = Table(summary_data, colWidths=[160, 380])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BORDER', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(t_summary)
    elements.append(Spacer(1, 12))

    # Document & Holder Details
    elements.append(Paragraph("1. DOCUMENT & HOLDER INFORMATION", heading2_style))
    fields = screening_data.get("extracted_fields", {})
    doc_table_data = [
        [Paragraph("<b>Document Type:</b>", body_style), Paragraph(str(screening_data.get("document_type")), body_style),
         Paragraph("<b>Document Number:</b>", body_style), Paragraph(str(screening_data.get("document_number")), body_style)],
        [Paragraph("<b>Holder Name:</b>", body_style), Paragraph(str(screening_data.get("holder_name")), body_style),
         Paragraph("<b>Nationality:</b>", body_style), Paragraph(str(fields.get("Nationality", "N/A")), body_style)],
        [Paragraph("<b>Date of Birth:</b>", body_style), Paragraph(str(fields.get("Date of Birth", "N/A")), body_style),
         Paragraph("<b>Date of Expiry:</b>", body_style), Paragraph(str(fields.get("Date of Expiry", "N/A")), body_style)]
    ]
    t_doc = Table(doc_table_data, colWidths=[110, 160, 110, 160])
    t_doc.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t_doc)
    elements.append(Spacer(1, 10))

    # Contributing Factors
    elements.append(Paragraph("2. KEY SCREENING FINDINGS & CONTRIBUTING FACTORS", heading2_style))
    factors = screening_data.get("contributing_factors", [])
    if factors:
        for factor in factors:
            elements.append(Paragraph(f"• {factor}", body_style))
    else:
        elements.append(Paragraph("• No negative risk indicators detected during analysis.", body_style))

    elements.append(Spacer(1, 14))

    # Disclaimer Footer
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceBefore=10, spaceAfter=10))
    elements.append(Paragraph("<i>CONFIDENTIAL SECURITY AUDIT RECORD • BORDERGUARD AI COMMAND CENTER</i>", subtitle_style))

    doc.build(elements)
    return str(pdf_path)
