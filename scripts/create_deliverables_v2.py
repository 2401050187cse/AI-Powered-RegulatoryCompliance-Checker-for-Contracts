#!/usr/bin/env python3
"""
Create updated deliverables.zip with separate system PDFs and project-based amendments
"""

import os
import zipfile
import hashlib
import json
from datetime import datetime

PROJECT_ROOT = r"D:\AI-Powered-RegulatoryCompliance-Checker-for-Contracts"
OUTPUT_ZIP = os.path.join(PROJECT_ROOT, "deliverables_v2.zip")

# Files to include in deliverables
deliverables_manifest = {
    # System-specific PDF reports (NEW)
    "system_reports": [
        ("pdf_output/app_analysis_report.pdf", "AI-Powered Regulatory Compliance - APP.PY Analysis Report"),
        ("pdf_output/rag_analysis_report.pdf", "AI-Powered Regulatory Compliance - RAG System Analysis Report"),
        ("pdf_output/regulatory_system_report.pdf", "AI-Powered Regulatory Compliance - Regulatory System Analysis Report"),
    ],
    # Existing reference reports
    "reference_reports": [
        ("pdf_output/final_report.pdf", "Consolidated compliance summary report"),
        ("pdf_output/regulatory_result_pdf.pdf", "Regulatory system difference report"),
    ],
    # Contract PDFs
    "contract_pdfs": [
        ("pdf_output/data/contracts/contract-001-v1.pdf", "Contract 001 Version 1"),
        ("pdf_output/data/contracts/contract-002-v1.pdf", "Contract 002 Version 1"),
        ("pdf_output/Dataset/contracts/CT001-v1.pdf", "CT001 Version 1"),
        ("pdf_output/Dataset/contracts/CT001-v2.pdf", "CT001 Version 2"),
        ("pdf_output/Dataset/contracts/CT002-v1.pdf", "CT002 Version 1"),
        ("pdf_output/Dataset/contracts/CT002-v2.pdf", "CT002 Version 2"),
    ],
    # Metadata and documentation
    "metadata": [
        ("milestone_links.json", "Asset traceability with SHA256 hashes"),
        ("README.md", "Project documentation"),
    ],
    # Project-based amendments (NEW structure)
    "amendments_by_system": [
        ("data/amendments/SUMMARY.json", "Amendments organization summary"),
        ("data/amendments/app/amendments.json", "App.py system amendments"),
        ("data/amendments/rag/amendments.json", "RAG system amendments"),
        ("data/amendments/regulatory/amendments.json", "Regulatory system amendments"),
    ]
}

print("🔄 Creating updated deliverables package...")
print(f"Output: {OUTPUT_ZIP}")

# Create zip file
with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
    files_added = 0
    total_size = 0
    
    # Add all deliverables
    for category, files_list in deliverables_manifest.items():
        print(f"\n📁 {category}:")
        for file_path, description in files_list:
            full_path = os.path.join(PROJECT_ROOT, file_path)
            if os.path.exists(full_path):
                arcname = file_path.replace("\\", "/")
                zipf.write(full_path, arcname)
                size = os.path.getsize(full_path)
                total_size += size
                files_added += 1
                print(f"  ✅ {file_path} ({size} bytes) - {description}")
            else:
                print(f"  ⚠️  {file_path} - NOT FOUND")
    
    # Create manifest file
    manifest = {
        "version": "v2.0",
        "created": datetime.now().isoformat(),
        "description": "AI-Powered Regulatory Compliance Checker - Complete Deliverables",
        "contents": {
            "system_reports": {
                "description": "Separate PDF reports from each analysis system",
                "files": [
                    {"name": "app_analysis_report.pdf", "system": "app.py (Groq LLM)", "purpose": "Compliance analysis via large language model"},
                    {"name": "rag_analysis_report.pdf", "system": "rag_system.py (FAISS+HF)", "purpose": "Retrieval-augmented generation analysis"},
                    {"name": "regulatory_system_report.pdf", "system": "regulatory.py (Rules)", "purpose": "Rule-based compliance engine analysis"}
                ]
            },
            "amendments": {
                "description": "Project-based amendments structure (not combined)",
                "organization": "Separate JSON per system: app/, rag/, regulatory/",
                "summary": "data/amendments/SUMMARY.json"
            },
            "contract_pdfs": {
                "description": "All converted contract PDFs",
                "count": 6,
                "format": "PDF (from TXT conversion)"
            }
        },
        "key_features": [
            "Three independent compliance analysis systems with separate reports",
            "Project-based amendments organization (not combined into single file)",
            "Full contract PDF conversion (TXT to PDF)",
            "SHA256 integrity tracking for all assets",
            "Regulatory framework analysis (GDPR, HIPAA, PCI DSS, AI Act)",
            "Vector search semantic analysis (FAISS + HuggingFace)",
            "LLM-based compliance reasoning (Groq API)"
        ]
    }
    
    manifest_json = json.dumps(manifest, indent=2)
    zipf.writestr("MANIFEST.json", manifest_json)
    files_added += 1
    
    print(f"\n  ✅ MANIFEST.json - Package manifest and contents description")

print(f"\n✅ Deliverables package created successfully!")
print(f"   Files added: {files_added}")
print(f"   Total size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
print(f"   Output: {OUTPUT_ZIP}")
print(f"   Size: {os.path.getsize(OUTPUT_ZIP):,} bytes ({os.path.getsize(OUTPUT_ZIP)/1024/1024:.2f} MB)")
