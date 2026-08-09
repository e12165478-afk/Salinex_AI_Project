import os

# مسیر پوشه پروژه خود را اینجا وارد کنید (مثلا مسیر جاری: '.')
project_dir = '.' 

# پوشه‌هایی که معمولا نباید اسکن شوند
exclude_dirs = {'venv', '.git', '__pycache__', '.idea', 'site-packages', 'build', 'dist'}

for root, dirs, files in os.walk(project_dir):
    # حذف پوشه‌های اضافی از پیمایش
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    
    level = root.replace(project_dir, '').count(os.sep)
    indent = ' ' * 4 * level
    print(f"{indent}📂 {os.path.basename(root) or project_dir}")
    sub_indent = ' ' * 4 * (level + 1)
    for f in files:
        if not f.endswith(('.pyc', '.pyo')):
            print(f"{sub_indent}📄 {f}")