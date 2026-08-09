#!/usr/bin/env python3

"""
Salinex AI - Final Fix Patch (3 Issues)
==========================================
1. Remove  watermark
2. Change ROI to payback in decision_engine.py
3. Fix Brine Type detection using Source_Type column

Run inside project root:
    python salinex_final_fix.py
"""

import shutil
from pathlib import Path

BACKUP_DIR = 'salinex_fix_backups_v2'

def backup_and_write(filepath, content):
    backup_path = Path(BACKUP_DIR) / filepath.name
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(filepath, backup_path)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  OK: {filepath}')

def main():
    project_root = Path('.').resolve()
    print('SALINEX AI - FINAL FIX PATCH')
    print('=' * 50)
    (project_root / BACKUP_DIR).mkdir(exist_ok=True)

    # [1/3] Remove 
    print('\n[1/3] Removing  watermark...')
    py_files = list(project_root.rglob('*.py'))
    _removed = 0
    for py_file in py_files:
        if 'salinex_env' in str(py_file) or BACKUP_DIR in str(py_file):
            continue
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            original = content
            content = content.replace('', '')
            content = content.replace('', '')
            content = content.replace('', '')
            if content != original:
                backup_and_write(py_file, content)
                _removed += 1
        except Exception as e:
            print(f'  SKIP: {py_file} ({e})')
    print(f'  Done. Modified {_removed} files.')

    # [2/3] Fix decision_engine.py
    print('\n[2/3] Fixing ROI references in decision_engine.py...')
    decision_file = project_root / 'decision_engine.py'
    if decision_file.exists():
        with open(decision_file, 'r', encoding='utf-8') as f:
            content = f.read()
        original = content
        content = content.replace('بهینه‌سازی ROI', 'بهینه‌سازی بازگشت سرمایه')
        content = content.replace('ROI', 'بازگشت سرمایه')
        if content != original:
            backup_and_write(decision_file, content)
            print('  Done.')
        else:
            print('  No ROI text found.')
    else:
        print('  WARNING: decision_engine.py not found.')

    # [3/3] Fix Brine Type in app.py
    print('\n[3/3] Fixing Brine Type detection in app.py...')
    app_file = project_root / 'app.py'
    if app_file.exists():
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        old_block = '''        if tds_col and li_col:
            _mean_tds = df[tds_col].mean()
            _mean_li = df[li_col].mean()
            
            if _mean_tds < 50000 and _mean_li < 5.0:
                auto_brine = "Seawater RO Brine"
            elif _mean_li >= 10.0 or _mean_tds >= 100000:
                auto_brine = "High-Mg Salar Brine"
            else:
                auto_brine = "Standard Brine"
        else:
            auto_brine = "Standard Brine"'''
        new_block = '''        # FIXED: Use Source_Type column from uploaded data
        if 'Source_Type' in df.columns:
            source_counts = df['Source_Type'].value_counts()
            dominant_source = source_counts.index[0]
            source_map = {
                'seawater': 'Seawater RO Brine',
                'brackish': 'Brackish Water',
                'produced': 'Produced Water (High-Mg)'
            }
            auto_brine = source_map.get(dominant_source, 'Standard Brine')
        elif tds_col and li_col:
            _mean_tds = df[tds_col].mean()
            _mean_li = df[li_col].mean()
            
            if _mean_tds < 50000 and _mean_li < 5.0:
                auto_brine = "Seawater RO Brine"
            elif _mean_li >= 10.0 or _mean_tds >= 100000:
                auto_brine = "High-Mg Salar Brine"
            else:
                auto_brine = "Standard Brine"
        else:
            auto_brine = "Standard Brine"'''
        if old_block in content:
            content = content.replace(old_block, new_block)
            backup_and_write(app_file, content)
            print('  Done. Brine detection now uses Source_Type column.')
        else:
            print('  WARNING: Could not find old brine detection block.')
    else:
        print('  WARNING: app.py not found.')

    print('\n' + '=' * 50)
    print('PATCH COMPLETE')
    print('=' * 50)
    print('\nBackups saved in:', project_root / BACKUP_DIR)

if __name__ == '__main__':
    main()