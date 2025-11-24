# AI-Powered-RegulatoryCompliance-Checker-for-Contracts
This is demo

## Milestone 3 — PDF packaging

If your project contains text artifacts (`.txt`) under `data/` or `Dataset/`, you can convert them to PDF and produce traceability links with the included script.

Usage (PowerShell):

```
python .\scripts\convert_txt_to_pdf.py --source data Dataset --output pdf_output
```

This will create a `pdf_output/` directory with PDFs mirroring the source structure. See `milestone_links.md` for how M3 outputs map back to M1 and M2 artifacts.