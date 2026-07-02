import json
import sys
from pathlib import Path

nb_path = Path(sys.argv[1])
if not nb_path.exists():
    print('Notebook not found:', nb_path)
    sys.exit(2)

bak = nb_path.with_suffix(nb_path.suffix + '.bak')
print('Backing up', nb_path, 'to', bak)
with nb_path.open('rb') as f:
    data = json.load(f)

modified = 0
# Top-level metadata
if isinstance(data, dict) and 'metadata' in data:
    md = data['metadata']
    if isinstance(md, dict) and 'widgets' in md:
        w = md['widgets']
        if isinstance(w, dict) and 'state' not in w:
            w['state'] = {}
            modified += 1

# Cells
if 'cells' in data and isinstance(data['cells'], list):
    for cell in data['cells']:
        if not isinstance(cell, dict):
            continue
        md = cell.get('metadata')
        if isinstance(md, dict) and 'widgets' in md:
            w = md['widgets']
            if isinstance(w, dict) and 'state' not in w:
                w['state'] = {}
                modified += 1

# Also check outputs for widget metadata (commonly in nbformat)
if 'cells' in data and isinstance(data['cells'], list):
    for cell in data['cells']:
        outputs = cell.get('outputs')
        if not isinstance(outputs, list):
            continue
        for out in outputs:
            md = out.get('metadata')
            if isinstance(md, dict) and 'widgets' in md:
                w = md['widgets']
                if isinstance(w, dict) and 'state' not in w:
                    w['state'] = {}
                    modified += 1

if modified > 0:
    bak.write_bytes(nb_path.read_bytes())
    with nb_path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print('Patched', modified, "metadata.widgets entries (added empty 'state').")
    print('Backup written to', bak)
else:
    print('No metadata.widgets entries missing state were found.')
