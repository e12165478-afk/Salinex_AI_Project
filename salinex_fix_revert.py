#!/usr/bin/env python3
"""Revert all changes made by salinex_critical_fix.py"""
import shutil
from pathlib import Path
backup_dir = Path('salinex_fix_backups')
for bf in backup_dir.rglob('*'):
    if bf.is_file():
        target = Path('.') / bf.relative_to(backup_dir)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(bf, target)
        print(f'Reverted: {target}')
print('
All files reverted to pre-patch state.')
