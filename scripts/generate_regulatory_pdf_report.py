#!/usr/bin/env python3
"""
Generate PDF report for regulatory.py (Rules-based compliance analysis)
Outputs to: pdf_output/regulatory_system_report.pdf
"""

import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# Paths
PROCESSED_RESULTS_FILE = r"D:\AI-Powered-RegulatoryCompliance-Checker-for-Contracts\processed_results.json"
OUTPUT_DIR = r"D:\AI-Powered-RegulatoryCompliance-Checker-for-Contracts\pdf_output"
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "regulatory_system_report.pdf")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read processed results
try:
    with open(PROCESSED_RESULTS_FILE, "r", encoding="utf-8") as f:
        results_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    results_data = {"chunks": []}

# Create PDF
doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
styles = getSampleStyleSheet()
story = []

# Custom styles
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=18,
    textColor=colors.HexColor('#2d5aa8'),
    spaceAfter=6,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=13,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=4,
    spaceBefore=8,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['Normal'],
    fontSize=10,
    alignment=TA_JUSTIFY,
    spaceAfter=4,
    leading=12
)

# Cover page
story.append(Paragraph("AI-Powered Regulatory Compliance Checker", title_style))
story.append(Spacer(1, 0.2*inch))
story.append(Paragraph("Regulatory System Analysis Report", heading_style))
story.append(Spacer(1, 0.1*inch))
story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
story.append(Spacer(1, 0.3*inch))

# System info
story.append(Paragraph("System Overview", heading_style))
story.append(Paragraph(
    "<b>Module:</b> Regulatory.py - Rules-Based Compliance Analysis<br/>"
    "<b>Purpose:</b> Analyze contracts against regulatory frameworks and compliance rules<br/>"
    "<b>Approach:</b> Deterministic rule engine with structured contract parsing<br/>"
    "<b>Output:</b> Structured compliance analysis with risk categorization<br/>"
    "<b>Regulations:</b> GDPR, HIPAA, PCI DSS, AI Act, General Clauses",
    body_style
))
story.append(Spacer(1, 0.2*inch))

# Analysis section
story.append(PageBreak())
story.append(Paragraph("Compliance Analysis Results", heading_style))
story.append(Spacer(1, 0.1*inch))

# Get chunks data
chunks = results_data.get("chunks", [])
story.append(Paragraph(f"<b>Total Contracts Analyzed: {len(chunks)}</b>", body_style))
story.append(Spacer(1, 0.15*inch))

# Process chunks
contracts_processed = 0
for i, chunk in enumerate(chunks[:50]):  # Limit to first 50 chunks
    contract_id = chunk.get("contract_id", "Unknown")
    clauses = chunk.get("clauses", [])
    risks = chunk.get("risks", [])
    
    story.append(Paragraph(f"<b>Contract: {contract_id}</b>", heading_style))
    
    # Clauses section
    if clauses:
        clause_text = "<b>Identified Clauses:</b> " + ", ".join(clauses[:5])
        story.append(Paragraph(clause_text, body_style))
    
    # Risks section
    if risks:
        risk_text = "<b>Compliance Risks:</b><br/>"
        for risk in risks[:3]:
            risk_name = risk.get("risk_type", "Unknown") if isinstance(risk, dict) else str(risk)
            risk_text += f"• {risk_name}<br/>"
        story.append(Paragraph(risk_text, body_style))
    
    story.append(Spacer(1, 0.1*inch))
    contracts_processed += 1
    
    # Page break every 8 contracts
    if contracts_processed % 8 == 0:
        story.append(PageBreak())

# Summary statistics
story.append(PageBreak())
story.append(Paragraph("Analysis Summary", heading_style))
story.append(Spacer(1, 0.1*inch))

# Calculate statistics
total_clauses = set()
total_risks = set()
for chunk in chunks:
    for clause in chunk.get("clauses", []):
        total_clauses.add(clause)
    for risk in chunk.get("risks", []):
        risk_type = risk.get("risk_type", "Unknown") if isinstance(risk, dict) else str(risk)
        total_risks.add(risk_type)

summary_data = [
    ["Metric", "Count"],
    ["Contracts Analyzed", str(len(chunks))],
    ["Unique Clause Types", str(len(total_clauses))],
    ["Risk Categories Identified", str(len(total_risks))],
    ["Processing Method", "Rule-Based"],
    ["Database", "regulations.json"],
    ["Report Generated", datetime.now().strftime('%Y-%m-%d')]
]

summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
summary_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 11),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))
story.append(summary_table)

story.append(Spacer(1, 0.2*inch))
story.append(Paragraph("Identified Clause Types", heading_style))
story.append(Spacer(1, 0.1*inch))

clause_list = "<br/>".join([f"• {clause}" for clause in sorted(total_clauses)[:15]])
story.append(Paragraph(clause_list, body_style))

story.append(Spacer(1, 0.2*inch))
story.append(Paragraph("Risk Categories", heading_style))
story.append(Spacer(1, 0.1*inch))

risk_list = "<br/>".join([f"• {risk}" for risk in sorted(total_risks)[:15]])
story.append(Paragraph(risk_list, body_style))

# Build PDF
doc.build(story)
print(f"✅ Regulatory System PDF generated: {OUTPUT_PDF}")
print(f"   Size: {os.path.getsize(OUTPUT_PDF)} bytes")
print(f"   Contracts analyzed: {len(chunks)}")
print(f"   Unique risks identified: {len(total_risks)}")
