# scan_project.py - اسکریپت بررسی محتویات پوشه پروژه Salinex AI
import os

project_dir = r"C:\Users\Mirzaee\Desktop\Salinex_AI_Project"

print("=" * 60)
print(f"📂 در حال اسکن پوشه پروژه: {project_dir}")
print("=" * 60)

if os.path.exists(project_dir):
    items = os.listdir(project_dir)
    for item in sorted(items):
        item_path = os.path.join(project_dir, item)
        if os.path.isdir(item_path):
            # اگر پوشه بود
            sub_items = len(os.listdir(item_path))
            print(f"📁 [پوشه]  {item:<30} (تعداد فایل/پوشه درون آن: {sub_items})")
        else:
            # اگر فایل بود
            size_kb = os.path.getsize(item_path) / 1024
            print(f"📄 [فایل]  {item:<30} (حجم: {size_kb:.2f} KB)")
print("=" * 60)