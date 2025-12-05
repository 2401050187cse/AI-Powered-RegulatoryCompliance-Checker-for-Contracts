#!/usr/bin/env python3
"""
Generate PDF report for rag_system.py (RAG-based retrieval)
Outputs to: pdf_output/rag_analysis_report.pdf
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# Paths
RAG_RESULTS_FILE = r"D:\AI-Powered-RegulatoryCompliance-Checker-for-Contracts\rag_results.txt"
OUTPUT_DIR = r"D:\AI-Powered-RegulatoryCompliance-Checker-for-Contracts\pdf_output"
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "rag_analysis_report.pdf")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read RAG results
try:
    with open(RAG_RESULTS_FILE, "r", encoding="utf-8") as f:
        rag_text = f.read()
except FileNotFoundError:
    rag_text = "RAG system results not available. Run rag_system.py to generate results."

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
story.append(Paragraph("RAG System Analysis Report", heading_style))
story.append(Spacer(1, 0.1*inch))
story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
story.append(Spacer(1, 0.3*inch))

# System info
story.append(Paragraph("System Overview", heading_style))
story.append(Paragraph(
    "<b>Module:</b> rag_system.py - Retrieval Augmented Generation<br/>"
    "<b>Purpose:</b> Retrieve relevant contract clauses and analyze compliance using vector search<br/>"
    "<b>Approach:</b> FAISS-based semantic search with HuggingFace embeddings<br/>"
    "<b>Output:</b> Compliance-focused Q&A with source attribution<br/>"
    "<b>Model:</b> Llama 3.1 8B via Groq API",
    body_style
))
story.append(Spacer(1, 0.2*inch))

# Analysis section
story.append(PageBreak())
story.append(Paragraph("RAG Retrieval Results", heading_style))
story.append(Spacer(1, 0.1*inch))

# Process RAG content
lines = rag_text.split("\n")
for line in lines[:500]:  # Limit to first 500 lines
    if "Q:" in line or "A:" in line or "Sources:" in line:
        story.append(Paragraph(f"<b>{line}</b>", body_style))
    elif line.strip():
        story.append(Paragraph(line, body_style))
    if len(story) > 150:
        story.append(PageBreak())

# Summary
story.append(PageBreak())
story.append(Paragraph("RAG System Configuration", heading_style))
story.append(Spacer(1, 0.1*inch))

config_data = [
    ["Parameter", "Value"],
    ["Embedding Model", "sentence-transformers/all-MiniLM-L6-v2"],
    ["Chat Model", "llama-3.1-8b-instant"],
    ["Vector Database", "FAISS"],
    ["Chunk Size", "1000 characters"],
    ["Chunk Overlap", "200 characters"],
    ["Top-K Results", "4 per query"],
    ["Report Generated", datetime.now().strftime('%Y-%m-%d')]
]

config_table = Table(config_data, colWidths=[3*inch, 3*inch])
config_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 11),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))
story.append(config_table)

# Build PDF
doc.build(story)
print(f"✅ RAG Analysis PDF generated: {OUTPUT_PDF}")
print(f"   Size: {os.path.getsize(OUTPUT_PDF)} bytes")
