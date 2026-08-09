#!/usr/bin/env python3

import re
import shutil
from pathlib import Path
from datetime import datetime

BACKUP_DIR = 'salinex_fix_backups'

# ============================================================
# FIX 1: Remove Hardcoded Compliance & Purity
# ============================================================

def fix_hardcoded_metrics(content, filepath):
    content = content.replace("kpis['Compliance'] = 99.2",
        "# FIXME: kpis['Compliance'] was hardcoded 99.2. Replace with real calculation from data.")
    content = content.replace("kpis['Purity'] = 99.5",
        "# FIXME: kpis['Purity'] was hardcoded 99.5. Replace with real calculation from data.")
    return content

# ============================================================
# FIX 2: Rename ROI to Payback Period
# ============================================================

def fix_roi_naming(content, filepath):
    if 'app.py' not in filepath:
        return content
    content = content.replace(
        'roi_years = (capex_val * 1000000) / (profit * 350)',
        'payback_years = (capex_val * 1000000) / (profit * 350)  # FIXED: Was incorrectly named roi_years')
    content = content.replace("roi_years != float('inf')", "payback_years != float('inf')")
    content = content.replace('roi_years', 'payback_years')
    content = content.replace('"ROI Current"', '"Payback Period (Years)"')
    content = content.replace('ROI Current', 'Payback Period')
    content = content.replace('بهینه‌سازی ROI:', 'بهینه‌سازی بازگشت سرمایه:')
    return content

# ============================================================
# FIX 3: Remove Personal Signature
# ============================================================

def fix_personal_signature(content, filepath):
    content = re.sub(r'ENGINEER:\s*Mirzaee\s*\|?\s*PHASE:[^\n]*',
        'SYSTEM: Salinex AI v3.9.5', content, flags=re.IGNORECASE)
    content = re.sub(r'SUPERVISING ENGINEER:\s*MIRZAEE',
        'SYSTEM GENERATED REPORT', content, flags=re.IGNORECASE)
    persian_greeting = 'مهندس میرزایی عزیز، لطفاً جهت شروع تحلیل، فایل CSV داده‌های شورابه را بارگذاری نمایید.'
    content = content.replace(persian_greeting,
        'لطفاً جهت شروع تحلیل، فایل CSV داده‌های شورابه را بارگذاری نمایید.')
    content = re.sub(r'مهندس مسئول:\s*Mirzaee', 'سیستم: Salinex AI', content, flags=re.IGNORECASE)
    content = re.sub(r'مسئول پروژه / مهندس ناظر:\s*Mirzaee',
        'سیستم مدیریت پروژه: Salinex AI', content, flags=re.IGNORECASE)
    content = re.sub(r'تایید مهندس ناظر \([^)]*Mirzaee[^)]*\)', 'تایید سیستمی', content, flags=re.IGNORECASE)
    content = re.sub(r'C:\\Users\\Mirzaee\\Desktop\\Salinex_AI_Project',
        'Path(__file__).resolve().parent.parent', content)
    content = re.sub(r'\(امضای مهندسی میرزایی\)', '(گزارش خودکار سیستم)', content)
    content = re.sub(r'^ENGINEER:\s*Mirzaee\s*\|?\s*PHASE:[^\n]*',
        'SYSTEM: Salinex AI', content, flags=re.IGNORECASE | re.MULTILINE)
    return content

# ============================================================
# FIX 4: Fix Hardcoded OPEX Formula
# ============================================================

def fix_hardcoded_opex(content, filepath):
    if 'app.py' not in filepath:
        return content
    marker = 'opex_m3 = 1.30 + (0.65 * actual_softening)'
    if marker in content:
        content = content.replace(marker,
            '# FIXME: OPEX was hardcoded. Use data-driven approach.\n'
            '# For uploaded data: opex_m3 = df[\'Total_Cost_USD_m3\'].mean()\n'
            '# Fallback formula for manual input:\n'
            + marker)
    return content

# ============================================================
# FIX 5: Remove Hardcoded Stability Index
# ============================================================

def fix_hardcoded_stability(content, filepath):
    content = content.replace(
        'st.metric("شاخص پایداری عملیاتی", "94.5 / 100 (A+)")',
        '# FIXME: st.metric("شاخص پایداری عملیاتی", "94.5 / 100 (A+)") was HARDCODED.')
    content = content.replace(
        'st.caption("✅ پایداری داده‌ها: تأییدشده")',
        'st.caption("✅ پایداری داده‌ها: بررسی شد")  # FIXME: Add real validation')
    return content

# ============================================================
# MAIN
# ============================================================

def main():
    project_root = Path('.').resolve()
    print('SALINEX AI - CRITICAL FIX PATCH v1.0')
    print('=' * 60)
    print(f'Project root: {project_root}')
    print(f'Timestamp: {datetime.now()}')
    (project_root / BACKUP_DIR).mkdir(exist_ok=True)

    fix_map = {
        'Remove Hardcoded Compliance & Purity': (["pages/1__Analysis.py"], fix_hardcoded_metrics),
        'Rename ROI to Payback Period': (["app.py", "pages/3__Scenario.py", "pages/4__Economics.py"], fix_roi_naming),
        'Remove Personal Signature': ([
            "app.py", "pages/1__Analysis.py", "pages/3__Scenario.py",
            "utils/scenario_utils.py", "final_retrain.py",
            "scan_project.py", "experiments/check_cols.py", "experiments/check_li.py"
        ], fix_personal_signature),
        'Fix Hardcoded OPEX Formula': (["app.py"], fix_hardcoded_opex),
        'Remove Hardcoded Stability Index': (["pages/3__Scenario.py", "app.py"], fix_hardcoded_stability),
    }

    all_changes = []
    all_errors = []

    for fix_name, (file_list, apply_func) in fix_map.items():
        print(f'\n▶ FIX: {fix_name}')
        for rel_path in file_list:
            full_path = project_root / rel_path
            if not full_path.exists():
                all_errors.append(f'  File not found: {rel_path}')
                continue
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    original = f.read()
                new_content = apply_func(original, rel_path)
                if new_content != original:
                    backup_path = project_root / BACKUP_DIR / rel_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(full_path, backup_path)
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    all_changes.append(f'  OK: {rel_path}')
                else:
                    all_changes.append(f'  No change: {rel_path}')
            except Exception as e:
                all_errors.append(f'  Error in {rel_path}: {e}')

    print('\n' + '=' * 60)
    print('PATCH SUMMARY')
    print('=' * 60)
    print('\nChanges Made:')
    for c in all_changes:
        print(c)
    if all_errors:
        print('\nErrors:')
        for e in all_errors:
            print(e)

    revert_script = '''#!/usr/bin/env python3
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
print('\nAll files reverted to pre-patch state.')
'''
    with open(project_root / 'salinex_fix_revert.py', 'w', encoding='utf-8') as f:
        f.write(revert_script)

    print('\nNEXT STEPS:')
    print('1. Review changed files in your IDE')
    print('2. Search for FIXME comments and implement real calculations')
    print('3. Test the app: streamlit run app.py')
    print('4. If anything breaks, revert: python salinex_fix_revert.py')
    print('\nRevert script created: salinex_fix_revert.py')

if __name__ == '__main__':
    main()