#!/usr/bin/env python3
"""Generate milestone_links.json mapping M3 outputs back to M1 and M2 artifacts.

Scans the index files under `data/` and `Dataset/`, finds source `.txt` files,
computes the expected PDF output path under `pdf_output/`, and tries to attach
evidence pointers from `processed_results.json` and `rag_results.txt`.

Usage:
    python .\scripts\generate_milestone_links.py --output milestone_links.json
"""
from pathlib import Path
import json
import argparse
import hashlib
import datetime
import os


def load_json(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


def read_text(path: Path):
    if not path.exists():
        return ""
    return path.read_text(encoding='utf-8', errors='replace')


def find_excerpt(big_text: str, terms, context=120):
    for t in terms:
        if not t:
            continue
        idx = big_text.find(t)
        if idx != -1:
            start = max(0, idx - context)
            end = min(len(big_text), idx + len(t) + context)
            return big_text[start:end].strip()
    return None


def build_mappings(repo_root: Path):
    mappings = []
    proc = read_text(repo_root / 'processed_results.json')
    rag = read_text(repo_root / 'rag_results.txt')
    # load amendments manifest if present
    amendments_manifest = load_json(repo_root / 'data' / 'amendments.json')
    amendments_list = amendments_manifest.get('amendments', []) if amendments_manifest else []

    # index files to consider
    index_files = [repo_root / 'data' / 'contracts_index.json', repo_root / 'Dataset' / 'contracts_index.json']
    for idx_path in index_files:
        idx = load_json(idx_path)
        source_name = 'data' if 'data' in str(idx_path) else 'Dataset'
        for key, meta in idx.items():
            file_rel = meta.get('file') or meta.get('file_path') or ''
            source_txt = str(Path(source_name) / file_rel)
            pdf_path = str(Path('pdf_output') / source_name / Path(file_rel).with_suffix('.pdf'))
            # try to find excerpt in processed results and rag
            basename = Path(file_rel).name
            terms = [key, basename, meta.get('title') or meta.get('name') or '']
            proc_excerpt = find_excerpt(proc, terms)
            rag_excerpt = find_excerpt(rag, terms)

            # check PDF existence and compute mtime + sha256
            pdf_abs = repo_root / Path(pdf_path)
            pdf_exists = pdf_abs.exists()
            pdf_mtime = None
            pdf_sha256 = None
            pdf_size_bytes = None
            if pdf_exists:
                try:
                    stat = pdf_abs.stat()
                    pdf_mtime = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                    pdf_size_bytes = stat.st_size
                    # compute sha256
                    h = hashlib.sha256()
                    with pdf_abs.open('rb') as fh:
                        for chunk in iter(lambda: fh.read(8192), b''):
                            h.update(chunk)
                    pdf_sha256 = h.hexdigest()
                except Exception:
                    pdf_mtime = None
                    pdf_sha256 = None
                    pdf_size_bytes = None

            # compute source TXT sha256 and size
            txt_abs = repo_root / Path(source_txt)
            txt_sha256 = None
            txt_size_bytes = None
            if txt_abs.exists():
                try:
                    txt_stat = txt_abs.stat()
                    txt_size_bytes = txt_stat.st_size
                    h2 = hashlib.sha256()
                    with txt_abs.open('rb') as fh2:
                        for chunk in iter(lambda: fh2.read(8192), b''):
                            h2.update(chunk)
                    txt_sha256 = h2.hexdigest()
                except Exception:
                    txt_sha256 = None
                    txt_size_bytes = None

            mappings.append({
                'asset_id': key,
                'source_txt': source_txt,
                'pdf_path': pdf_path,
                'pdf_exists': pdf_exists,
                'pdf_mtime': pdf_mtime,
                'pdf_sha256': pdf_sha256,
                'pdf_size_bytes': pdf_size_bytes,
                'txt_size_bytes': txt_size_bytes,
                'txt_sha256': txt_sha256,
                'amendments': [a for a in amendments_list if (a.get('asset_id') == key or Path(a.get('changed_files', [''])[0]).stem.startswith(Path(file_rel).stem.split('-v')[0]))],
                'index_file': str(idx_path.relative_to(repo_root)),
                'processed_results': 'processed_results.json',
                'processed_results_excerpt': proc_excerpt,
                'rag_results': 'rag_results.txt',
                'rag_results_excerpt': rag_excerpt,
                'notes': meta.get('applied_regulations') or meta.get('applied') or []
            })

    return mappings


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo-root', default='.', help='Repository root (default: current dir)')
    p.add_argument('--output', default='milestone_links.json', help='Output JSON file')
    args = p.parse_args()
    repo_root = Path(args.repo_root)
    mappings = build_mappings(repo_root)
    out_path = repo_root / args.output
    out_path.write_text(json.dumps({'mappings': mappings}, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Wrote {out_path} with {len(mappings)} entries')


if __name__ == '__main__':
    main()
