#!/usr/bin/env python3
"""Detect amendments by scanning versioned .txt files and write data/amendments.json

Heuristic: files named like `NAME-v1.txt`, `NAME-v2.txt` are different versions.
For each newer version we create a simple amendment entry linking to the changed file.

Usage:
    python .\scripts\detect_amendments.py --roots data Dataset --output data/amendments.json
"""
from pathlib import Path
import argparse
import re
import datetime
import json


def detect(roots):
    pattern = re.compile(r"(?P<base>.+)-v(?P<ver>\d+)\.txt$", re.IGNORECASE)
    groups = {}
    for root in roots:
        for p in Path(root).rglob('*.txt'):
            m = pattern.match(p.name)
            if m:
                base = m.group('base')
                ver = int(m.group('ver'))
                groups.setdefault(base, []).append((ver, p))

    amendments = []
    for base, items in groups.items():
        items.sort(key=lambda x: x[0])
        # for each upgrade step (prev -> next) create amendment record for next
        for i in range(1, len(items)):
            ver, p = items[i]
            prev_ver, prev_p = items[i-1]
            stat = p.stat()
            amend = {
                'asset_id': base,
                'amendment_id': f'{base}-amend-v{ver}',
                'date': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'summary': f'Update from v{prev_ver} to v{ver}',
                'changed_files': [str(p)],
                'author': None
            }
            amendments.append(amend)

    return amendments


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--roots', nargs='+', default=['data', 'Dataset'])
    p.add_argument('--output', default='data/amendments.json')
    args = p.parse_args()

    amendments = detect(args.roots)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'amendments': amendments}, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Wrote {out} with {len(amendments)} amendments')


if __name__ == '__main__':
    main()
