import pandas as pd
import os

# مسیر پوشه داده‌ها
data_folder = r'Path(__file__).resolve().parent.parent\data'

try:
    # لیست کردن فایل‌های داخل پوشه data
    files = os.listdir(data_folder)
    csv_files = [f for f in files if f.endswith('.csv')]
    
    if csv_files:
        # فرض می‌کنیم اولین فایل CSV همان فایل مدنظر ماست
        target_file = os.path.join(data_folder, csv_files[0])
        df = pd.read_csv(target_file)
        
        print(f"✅ فایل پیدا شد: {csv_files[0]}")
        print("\n--- لیست ستون‌های این فایل ---")
        for col in df.columns:
            print(f"- {col}")
        print("----------------------------")
    else:
        print("❌ در پوشه data هیچ فایل CSV پیدا نشد.")
        print(f"فایل‌های موجود در پوشه data: {files}")

except Exception as e:
    print(f"❌ خطا: {e}")