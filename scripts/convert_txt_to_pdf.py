#!/usr/bin/env python3
"""Convert .txt files to PDF while preserving directory structure.

Searches the provided source directories (default: `data`, `Dataset`) for
`.txt` files and writes corresponding PDFs under an output root
(`pdf_output/` by default) keeping the same relative paths.

Requires: reportlab (install with `pip install reportlab`).

Usage (PowerShell):
    python .\scripts\convert_txt_to_pdf.py --source data Dataset --output pdf_output
"""
from pathlib import Path
import argparse

try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.units import inch
    from reportlab.lib import colors
except Exception:
    raise SystemExit("Missing dependency: reportlab. Install with: pip install reportlab")


def make_header_footer(title):
    def draw(canvas, doc):
        canvas.saveState()
        width, height = doc.pagesize
        # header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(inch * 0.5, height - inch * 0.5 + 6, title)
        # footer (page number)
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.gray)
        page_num = f"Page {doc.page}"
        canvas.drawRightString(width - inch * 0.5, inch * 0.5 - 6, page_num)
        canvas.restoreState()
    return draw


def txt_to_pdf(src_path: Path, dst_path: Path, pagesize=LETTER):
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(dst_path), pagesize=pagesize,
                            rightMargin=48, leftMargin=48, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    heading = styles.get('Heading1', styles['Normal'])

    # read file and split into paragraphs by blank lines
    text = src_path.read_text(encoding='utf-8', errors='replace')
    paras = [p.strip() for p in text.split('\n\n') if p.strip()]

    story = []
    title = src_path.name
    story.append(Paragraph(title, heading))
    story.append(Spacer(1, 12))

    for p in paras:
        # replace single newlines with spaces for better flow
        p_clean = ' '.join([line.strip() for line in p.splitlines()])
        story.append(Paragraph(p_clean.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), normal))
        story.append(Spacer(1, 6))

    # build PDF with header/footer
    doc.build(story, onFirstPage=make_header_footer(title), onLaterPages=make_header_footer(title))


def convert_tree(source_dirs, output_root):
    source_dirs = [Path(d) for d in source_dirs]
    output_root = Path(output_root)
    converted = []
    for src_dir in source_dirs:
        if not src_dir.exists():
            print(f"Source directory not found: {src_dir} (skipping)")
            continue
        for txt_path in src_dir.rglob('*.txt'):
            try:
                rel = txt_path.relative_to(src_dir)
            except Exception:
                rel = txt_path.name
            out_pdf = output_root / src_dir.name / rel.with_suffix('.pdf')
            try:
                txt_to_pdf(txt_path, out_pdf)
                converted.append((txt_path, out_pdf))
                print(f"Converted: {txt_path} -> {out_pdf}")
            except Exception as e:
                print(f"Failed converting {txt_path}: {e}")
    return converted


def main():
    p = argparse.ArgumentParser(description='Convert .txt files to PDF')
    p.add_argument('--source', '-s', nargs='+', default=['data', 'Dataset'], help='Source directories to scan')
    p.add_argument('--output', '-o', default='pdf_output', help='Output root for PDFs')
    args = p.parse_args()
    converted = convert_tree(args.source, args.output)
    print(f"Conversion complete — {len(converted)} files converted. Output root: {args.output}")


if __name__ == '__main__':
    main()
