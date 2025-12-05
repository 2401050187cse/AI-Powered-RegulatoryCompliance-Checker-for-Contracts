#!/usr/bin/env python3
"""Generate a PDF report showing differences between source TXT files and
the processed results (from `processed_results.json`).

Usage: python scripts/generate_diff_report.py --links milestone_links.json --processed processed_results.json --output pdf_output/diff_report.pdf
"""
import argparse
import json
import os
import re
import difflib
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted


def load_processed_text(processed_path):
    try:
        with open(processed_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # processed_results.json contains chunks; join them
        if isinstance(data, dict):
            parts = []
            for k in sorted(data.keys()):
                v = data[k]
                if isinstance(v, str):
                    parts.append(v)
            return "\n\n".join(parts)
        # fallback: stringify
        return json.dumps(data, indent=2)
    except Exception:
        with open(processed_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()


def excerpt_around(text, pat, chars=800):
    idx = text.lower().find(pat.lower())
    if idx == -1:
        return None
    start = max(0, idx - chars//3)
    end = min(len(text), idx + chars)
    return text[start:end]


def find_best_excerpt(processed_text, asset_id, source_text):
    # Try a few heuristics to find the relevant processed excerpt
    # 1) digits in asset id -> Contract #NNN
    digits = ''.join(re.findall(r"\d+", asset_id))
    if digits:
        pat = f"Contract #{int(digits):03d}" if len(digits) <= 3 else f"Contract #{digits}"
        e = excerpt_around(processed_text, pat)
        if e:
            return e

    # 2) try asset_id directly
    e = excerpt_around(processed_text, asset_id)
    if e:
        return e

    # 3) try searching for a few words from the source_text (title-like)
    first_line = source_text.strip().splitlines()[0] if source_text.strip() else ''
    if first_line:
        e = excerpt_around(processed_text, first_line[:80])
        if e:
            return e

    # 4) fallback: return a head excerpt of processed_text
    return processed_text[:1200]


def make_diff(a, b):
    a_lines = a.splitlines()
    b_lines = b.splitlines()
    diff = difflib.unified_diff(a_lines, b_lines, lineterm='')
    return '\n'.join(diff)


def build_pdf(mappings, processed_text, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    cover = Paragraph(f"Diff Report: input TXT vs regulatory results — {datetime.utcnow().isoformat()}Z", styles['Title'])
    story.append(cover)
    story.append(Spacer(1, 12))

    for m in mappings:
        asset = m.get('asset_id') or os.path.basename(m.get('source_txt',''))
        story.append(Paragraph(f"Asset: {asset}", styles['Heading2']))
        story.append(Spacer(1, 6))

        src_path = m.get('source_txt')
        try:
            with open(src_path, 'r', encoding='utf-8') as f:
                src_text = f.read()
        except Exception:
            src_text = f"(Could not read source file: {src_path})"

        proc_excerpt = find_best_excerpt(processed_text, asset, src_text)

        story.append(Paragraph('Source (excerpt)', styles['Heading3']))
        story.append(Preformatted('\n'.join(src_text.splitlines()[:40]), styles['Code']))
        story.append(Spacer(1, 6))

        story.append(Paragraph('Processed results (excerpt)', styles['Heading3']))
        story.append(Preformatted('\n'.join(proc_excerpt.splitlines()[:40]), styles['Code']))
        story.append(Spacer(1, 6))

        story.append(Paragraph('Unified diff (source -> processed)', styles['Heading3']))
        diff_text = make_diff(src_text, proc_excerpt)
        if not diff_text.strip():
            diff_text = '(No differences detected or unable to compute diff)'
        story.append(Preformatted(diff_text or '(empty diff)', styles['Code']))
        story.append(Spacer(1, 18))

    doc.build(story)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--links', default='milestone_links.json')
    ap.add_argument('--processed', default='processed_results.json')
    ap.add_argument('--output', default='pdf_output/regulatory_result_pdf.pdf')
    args = ap.parse_args()

    with open(args.links, 'r', encoding='utf-8') as f:
        links = json.load(f)

    mappings = links.get('mappings') if isinstance(links, dict) else links
    processed_text = load_processed_text(args.processed)

    build_pdf(mappings, processed_text, args.output)
    print(f"Wrote {args.output}")


if __name__ == '__main__':
    main()
