import os
import inspect

print("🔍 --- ۱. جستجوی فایل‌های ذخیره‌شده مدل روی هارد ---")
found_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(('.pkl', '.joblib', '.sav', '.h5', '.pt', '.onnx')):
            full_path = os.path.join(root, file)
            found_files.append(full_path)
            print(f"  [FOUND FILE] 💾 {full_path}")

if not found_files:
    print("  ❌ هیچ فایل مدلی با پسوندهای رایج (.pkl یا .joblib) روی هارد یافت نشد.")

print("\n🔍 --- ۲. بررسی کلاس MultiSourcePredictor در پلتفرم ---")
try:
    # تلاش برای فراخوانی کلاس از ماژول‌های پروژه
    try:
        from ml_engine import MultiSourcePredictor
    except ImportError:
        try:
            from app import MultiSourcePredictor
        except ImportError:
            # اگر فایل دیگری دارید اسم آن را اینجا قرار دهید
            from salinex_ml import MultiSourcePredictor

    print(f"  ✅ کلاس MultiSourcePredictor با موفقیت یافت شد.")
    
    # نمونه‌سازی آزمایشی
    pred = MultiSourcePredictor(brine_type="Standard Brine")
    
    print("\n📋 ویژگی‌ها و متدهای موجود در این کلاس:")
    for attr in dir(pred):
        if not attr.startswith("__"):
            val = getattr(pred, attr)
            print(f"  🔹 {attr}: {type(val)}")
            
except Exception as e:
    print(f"  ⚠️ خطایی هنگام بررسی کلاس رخ داد: {e}")

print("\n-------------------------------------------------")