import os

# لیست پوشه‌هایی که می‌خواهیم نادیده گرفته شوند
IGNORE_DIRS = {'salinex_env', 'venv', '.venv', '__pycache__', '.git', '.idea', '.vscode'}

def inspect_project_location(start_path='.'):
    current_dir = os.path.abspath(start_path)
    print(f"📍 موقعیت فعلی شما (Current Working Directory):\n{current_dir}\n")
    print("📁 ساختار فایل‌ها و پوشه‌های اصلی پروژه:\n" + "="*45)
    
    for root, dirs, files in os.walk(start_path):
        # حذف پوشه‌های نادیده‌گرفته‌شده از پیمایش
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        level = root.replace(start_path, '').count(os.sep)
        indent = ' ' * 4 * level
        folder_name = os.path.basename(root) if root != start_path else '.'
        print(f"{indent}📂 {folder_name}/")
        
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{sub_indent}📄 {f}")

if __name__ == "__main__":
    inspect_project_location()