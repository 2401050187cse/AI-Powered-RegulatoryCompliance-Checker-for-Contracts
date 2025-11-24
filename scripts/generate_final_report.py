#!/usr/bin/env python3
"""Generate a consolidated final report PDF from milestone links and RAG outputs.

Usage:
    python .\scripts\generate_final_report.py --links milestone_links.json --processed processed_results.json --rag rag_results.txt --output pdf_output/final_report.pdf
"""
from pathlib import Path
import json
import argparse
import datetime

try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.units import inch
    from reportlab.lib import colors
except Exception:
    raise SystemExit("reportlab is required. Install with: pip install reportlab")


def load_text(path: Path):
    if not path.exists():
        return ""
    return path.read_text(encoding='utf-8', errors='replace')


def short_excerpt(big_text, terms, context=200):
    for t in terms:
        if not t:
            continue
        i = big_text.find(t)
        if i != -1:
            start = max(0, i - context)
            end = min(len(big_text), i + len(t) + context)
            return big_text[start:end].strip()
    return None


def build_report(mappings, processed_text, rag_text, out_path: Path):
    doc = SimpleDocTemplate(str(out_path), pagesize=LETTER, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    flow = []

    title = f"Final Report — Milestone 3 Packaging"
    flow.append(Paragraph(title, styles['Title']))
    flow.append(Spacer(1, 12))
    meta = f"Generated: {datetime.datetime.utcnow().isoformat()} UTC"
    flow.append(Paragraph(meta, styles['Normal']))
    flow.append(Spacer(1, 18))

    summary = f"Assets included: {len(mappings)}. PDFs are in `pdf_output/`. See per-asset sections for checksums and excerpts."
    flow.append(Paragraph(summary, styles['Normal']))
    flow.append(Spacer(1, 18))

    # Cover / Integrity summary
    flow.append(Paragraph("Integrity Summary", styles['Heading2']))
    flow.append(Spacer(1, 6))
    for m in mappings:
        aid = m.get('asset_id')
        parts = []
        if m.get('txt_sha256'):
            parts.append(f"TXT sha256: {m.get('txt_sha256')}")
        if m.get('txt_size_bytes') is not None:
            parts.append(f"TXT size: {m.get('txt_size_bytes')} bytes")
        if m.get('pdf_sha256'):
            parts.append(f"PDF sha256: {m.get('pdf_sha256')}")
        if m.get('pdf_size_bytes') is not None:
            parts.append(f"PDF size: {m.get('pdf_size_bytes')} bytes")
        line = f"{aid} — {' | '.join(parts) if parts else 'no integrity metadata available'}"
        flow.append(Paragraph(line, styles['Normal']))
        flow.append(Spacer(1, 4))
    flow.append(PageBreak())

    for m in mappings:
        aid = m.get('asset_id')
        flow.append(Paragraph(f"Asset: <b>{aid}</b>", styles['Heading2']))
        flow.append(Spacer(1, 6))

        info_lines = []
        info_lines.append(f"Source TXT: {m.get('source_txt')}")
        info_lines.append(f"PDF: {m.get('pdf_path')} (exists: {m.get('pdf_exists')})")
        if m.get('pdf_mtime'):
            info_lines.append(f"PDF mtime: {m.get('pdf_mtime')}")
        if m.get('pdf_sha256'):
            info_lines.append(f"PDF sha256: {m.get('pdf_sha256')}")
        if m.get('pdf_size_bytes') is not None:
            info_lines.append(f"PDF size (bytes): {m.get('pdf_size_bytes')}")
        if m.get('txt_size_bytes') is not None:
            info_lines.append(f"Source TXT size (bytes): {m.get('txt_size_bytes')}")
        if m.get('txt_sha256'):
            info_lines.append(f"Source TXT sha256: {m.get('txt_sha256')}")
        if m.get('notes'):
            info_lines.append(f"Notes: {', '.join(m.get('notes'))}")

        for l in info_lines:
            flow.append(Paragraph(l, styles['Normal']))
        flow.append(Spacer(1, 8))

        # include processed_results excerpt if available
        prex = m.get('processed_results_excerpt')
        if not prex:
            # attempt search
            terms = [aid, Path(m.get('source_txt')).name]
            prex = short_excerpt(processed_text, terms)
        if prex:
            flow.append(Paragraph("Processed Results Excerpt:", styles['Italic']))
            flow.append(Paragraph(prex.replace('\n', '<br/>'), styles['Code'] if 'Code' in styles else styles['BodyText']))
            flow.append(Spacer(1, 6))

        rex = m.get('rag_results_excerpt')
        if not rex:
            terms = [aid, Path(m.get('source_txt')).name]
            rex = short_excerpt(rag_text, terms)
        if rex:
            flow.append(Paragraph("RAG Excerpt:", styles['Italic']))
            flow.append(Paragraph(rex.replace('\n', '<br/>'), styles['BodyText']))
            flow.append(Spacer(1, 6))

        flow.append(PageBreak())

    doc.build(flow)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--links', default='milestone_links.json')
    p.add_argument('--processed', default='processed_results.json')
    p.add_argument('--rag', default='rag_results.txt')
    p.add_argument('--output', default='pdf_output/final_report.pdf')
    args = p.parse_args()

    links = json.loads(Path(args.links).read_text(encoding='utf-8'))
    mappings = links.get('mappings', [])
    processed_text = load_text(Path(args.processed))
    rag_text = load_text(Path(args.rag))

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    build_report(mappings, processed_text, rag_text, out_path)
    print(f"Wrote {out_path}")


if __name__ == '__main__':
    main()
