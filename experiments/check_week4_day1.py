import os
import re

def inspect_week4_day1():
    print("==================================================")
    print("🔍 بررسی دقیق وضعیت کارهای روز اول هفته چهارم")
    print("==================================================\n")

    project_root = "."
    pages_dir = os.path.join(project_root, "pages")
    
    # ۱. بررسی وجود پوشه pages
    if not os.path.exists(pages_dir):
        print("❌ پوشه 'pages/' در پروژه یافت نشد.")
        return

    # ۲. پیدا کردن فایل مربوط به Scenario
    page_files = os.listdir(pages_dir)
    scenario_file = None
    for f in page_files:
        if "scenario" in f.lower():
            scenario_file = f
            break

    print("📌 [۱] وضعیت فایل صفحه سناریو:")
    if scenario_file:
        print(f"   ✅ فایل یافت شد: pages/{scenario_file}")
    else:
        print("   ❌ فایل 'pages/3_Scenario.py' هنوز ساخته نشده است.")

    print("\n--------------------------------------------------")
    print("📌 [۲] بررسی وجود کلاس AdaptiveScenarioManager در کدهای پروژه:")

    class_found = False
    target_class = "AdaptiveScenarioManager"

    # اسکن تمام فایل‌های پایتون پروژه برای پیدا کردن نام کلاس
    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith(".py") and not file.startswith("check_"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if target_class in content:
                            class_found = True
                            print(f"   ✅ کلاس '{target_class}' در فایل '{file_path}' یافت شد.")
                            
                            # بررسی تعاریف متدها
                            methods = re.findall(r"def\s+(\w+)", content)
                            print(f"      • توابع/متدهای موجود: {methods}")
                except Exception as e:
                    pass

    if not class_found:
        print(f"   ❌ کلاس '{target_class}' در هیچ‌یک از فایل‌های پایتون یافت نشد.")

    print("\n==================================================")
    print("📊 نتیجه‌گیری کارهای روز اول هفته ۴:")
    if scenario_file and class_found:
        print("🎉 تمام موارد روز اول هفته چهارم پیاده‌سازی شده‌اند.")
    elif scenario_file or class_found:
        print("⚠️ بخشی از کارهای روز اول هفته چهارم انجام شده اما ناقص است.")
    else:
        print("🛑 کارهای روز اول هفته چهارم هنوز آغاز نشده‌اند.")
    print("==================================================")

if __name__ == "__main__":
    inspect_week4_day1()