# Milestone Links — M1 → M2 → M3

This document provides traceability between project milestones:

- Milestone 1 (M1): Data ingestion & preprocessing — raw text sources and cleaned text artifacts.
- Milestone 2 (M2): Indexing & RAG — vector index, retrieval artifacts, and RAG outputs.
- Milestone 3 (M3): Packaging & Deliverables — PDFs, consolidated reports, and linkage artifacts.

Purpose
-------
Keep a clear mapping from M3 deliverables (PDFs, reports) back to the original M1 sources and the M2 index/RAG evidence used to create findings.

How to use
----------
Each entry below maps a single asset (contract/regulation) across milestones. Fields recorded:

- Asset ID: human-friendly identifier (e.g., `contract-001-v1`)
- Original TXT (M1): path to the source text file
- PDF (M3): path to the generated PDF
- Index entries (M2): pointer to vector index files or mapping file (e.g., `faiss_index/index.faiss`, with vector ids or mapping in `processed_results.json`)
- RAG findings (M2): file and location of RAG evidence (e.g., `rag_results.txt`, `processed_results.json`)
- Notes: preprocessing steps or redactions applied in M1

Example entry
-------------
- **Asset ID:** `contract-001-v1`
- **Original TXT (M1):** `data/contracts/contract-001-v1.txt`
- **PDF (M3):** `pdf_output/data/contracts/contract-001-v1.pdf`
- **Index entries (M2):** `faiss_index/index.faiss` — see `processed_results.json` for mapping (vector id: 12345)
- **RAG findings (M2):** `rag_results.txt` (excerpt at lines 45–58)
- **Notes:** normalized whitespace, lowercased dates, no redaction applied

Next steps to regenerate mapping
-------------------------------
1. Regenerate PDFs: run `python .\scripts\convert_txt_to_pdf.py --source data Dataset --output pdf_output`.
2. Rebuild or inspect the index with existing tooling (see `rag_system.py` and `faiss_index/`).
3. Update this document (or produce a `milestone_links.json`) by programmatically reading `contracts_index.json`, `processed_results.json`, and `rag_results.txt` to populate per-asset fields.

If you want, I can generate a `milestone_links.json` automatically by scanning `data/`, `Dataset/`, and `processed_results.json` to produce complete per-asset mappings.
