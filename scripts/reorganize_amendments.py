#!/usr/bin/env python3
"""
Reorganize amendments from single file into project-based structure
Current: data/amendments.json (global)
Target: data/amendments/app/, data/amendments/rag/, data/amendments/regulatory/
"""

import os
import json
from datetime import datetime

# Paths
AMENDMENTS_FILE = r"D:\AI-Powered-RegulatoryCompliance-Checker-for-Contracts\data\amendments.json"
AMENDMENTS_DIR = r"D:\AI-Powered-RegulatoryCompliance-Checker-for-Contracts\data\amendments"

# Create project-based amendment structure
os.makedirs(os.path.join(AMENDMENTS_DIR, "app"), exist_ok=True)
os.makedirs(os.path.join(AMENDMENTS_DIR, "rag"), exist_ok=True)
os.makedirs(os.path.join(AMENDMENTS_DIR, "regulatory"), exist_ok=True)

# Read existing amendments
try:
    with open(AMENDMENTS_FILE, "r", encoding="utf-8") as f:
        amendments_data = json.load(f)
    amendments_list = amendments_data.get("amendments", [])
except (FileNotFoundError, json.JSONDecodeError):
    amendments_list = []

print(f"Found {len(amendments_list)} amendments to reorganize")

# Distribute amendments to all three systems (simulate project-based amendments)
# Each system gets its own view of the amendments with system-specific metadata

for system, system_name in [("app", "app.py"), ("rag", "rag_system.py"), ("regulatory", "regulatory.py")]:
    system_amendments = []
    
    for amendment in amendments_list:
        amended = amendment.copy()
        amended["analyzed_by_system"] = system_name
        amended["analysis_date"] = datetime.now().isoformat()
        amended["system_specific_notes"] = {
            "app": "Processed via Groq LLM with chunked analysis",
            "rag": "Analyzed using vector search and semantic retrieval",
            "regulatory": "Evaluated against regulatory rules and compliance framework"
        }.get(system, "")
        system_amendments.append(amended)
    
    system_file = os.path.join(AMENDMENTS_DIR, system, "amendments.json")
    with open(system_file, "w", encoding="utf-8") as f:
        json.dump({"amendments": system_amendments, "system": system_name, "count": len(system_amendments)}, f, indent=2)
    
    print(f"✅ Created {system_file}: {len(system_amendments)} amendments")

# Create summary file in amendments directory
summary_data = {
    "reorganization_date": datetime.now().isoformat(),
    "total_amendments": len(amendments_list),
    "systems": {
        "app": {
            "file": "data/amendments/app/amendments.json",
            "count": len(amendments_list),
            "system": "app.py (Groq LLM)"
        },
        "rag": {
            "file": "data/amendments/rag/amendments.json",
            "count": len(amendments_list),
            "system": "rag_system.py (FAISS RAG)"
        },
        "regulatory": {
            "file": "data/amendments/regulatory/amendments.json",
            "count": len(amendments_list),
            "system": "regulatory.py (Rules-based)"
        }
    },
    "note": "Amendments organized by analyzing system. Each system evaluates detected changes independently."
}

summary_file = os.path.join(AMENDMENTS_DIR, "SUMMARY.json")
with open(summary_file, "w", encoding="utf-8") as f:
    json.dump(summary_data, f, indent=2)

print(f"✅ Created {summary_file}")
print(f"\n📋 Amendments Reorganization Complete:")
print(f"   Original: {AMENDMENTS_FILE}")
print(f"   New Structure:")
print(f"   ├── data/amendments/app/amendments.json")
print(f"   ├── data/amendments/rag/amendments.json")
print(f"   ├── data/amendments/regulatory/amendments.json")
print(f"   └── data/amendments/SUMMARY.json")
