#!/usr/bin/env python3
"""Create a public archive from an explicit allowlist; exclude all private data."""
from pathlib import Path
import sys
import zipfile

root = Path(__file__).resolve().parents[1]
output = Path(sys.argv[1]) if len(sys.argv)>1 else root.parent/'UK_International_Tracker_GitHub_Ready.zip'
selected = [root/'README.md', root/'.gitignore']
for folder in ['skills','examples','tools','tests']:
    selected.extend(p for p in (root/folder).rglob('*') if p.is_file() and not p.is_symlink()
                    and '__pycache__' not in p.parts and p.suffix in ['.md','.py','.json','.yaml','.mjs'])
private_bank=root/'private/evidence_bank.json'
profile={}
if private_bank.exists():
    import json
    profile=json.loads(private_bank.read_text()).get('profile',{})
sensitive=[str(profile[k]).casefold() for k in ['name','email','phone','portfolio'] if profile.get(k)]
for p in selected:
    content=p.read_text()
    local_home_prefix='/'+'users'+'/'
    if any(needle in content.casefold() for needle in sensitive) or local_home_prefix in content.casefold():
        raise ValueError('Personal data found in public file: '+str(p.relative_to(root)))
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(set(selected)):
        z.write(p, 'UK_International_Tracker/'+str(p.relative_to(root)))
with zipfile.ZipFile(output) as z:
    assert not any('/private/' in n or '/node_modules/' in n or '/tmp/' in n for n in z.namelist())
    print(f'Created {output} with {len(z.namelist())} public files; private data excluded')
