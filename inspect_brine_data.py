import os
import pandas as pd
import numpy as np

def inspect_data_file():
    print("==================================================")
    print("🔍 بازرسی آماری و ارزیابی دقت روی Combined_Real_Brine_Data_cleaned.csv")
    print("==================================================\n")

    # پیدا کردن مسیر فایل
    possible_paths = [
        "Combined_Real_Brine_Data_cleaned.csv",
        "./data/Combined_Real_Brine_Data_cleaned.csv",
        "../Combined_Real_Brine_Data_cleaned.csv"
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break

    if not file_path:
        print("❌ فایل Combined_Real_Brine_Data_cleaned.csv در مسیرهای رایج پیدا نشد.")
        return

    print(f"✅ فایل با موفقیت یافت شد: {file_path}")
    df = pd.read_csv(file_path)
    
    print(f"📊 تعداد کل نمونه‌ها (Rows): {len(df)}")
    print(f"📌 ستون‌های موجود: {list(df.columns)}\n")

    # نمایش ۵ ردیف اول
    print("--- 🔍 ۵ ردیف اول داده‌ها ---")
    print(df.head(), "\n")

    # ۱. بررسی همبستگی متغیرها با ستون خروجی (Target)
    target_col = None
    for col in df.columns:
        if "recovery" in col.lower() or "target" in col.lower() or "rec" in col.lower():
            target_col = col
            break

    if target_col:
        print(f"🎯 ستون خروجی (Target) شناسایی‌شده: '{target_col}'")
        
        # محاسبه همبستگی
        numeric_df = df.select_dtypes(include=[np.number])
        correlations = numeric_df.corr()[target_col].sort_values(ascending=False)
        print("\n📈 میزان همبستگی (Correlation) متغیرها با خروجی:")
        print(correlations)

        # بررسی احتمال نشت داده
        leaking_cols = correlations[abs(correlations) > 0.98].index.tolist()
        leaking_cols.remove(target_col)
        if leaking_cols:
            print(f"\n⚠️ **هشدار نشت داده (Data Leakage):** متغیرهای زیر همبستگی بالای ۹۸٪ با پاسخ دارند: {leaking_cols}")
        else:
            print("\n✅ هیچ متغیر تک‌عاملی که باعث Data Leakage مستقیم شود یافت نشد.")

    # ۲. بررسی میزان یکنواختی و نویز داده‌ها
    print("\n--- 📊 خلاصه وضعیت آماری (Mean, Std, Min, Max) ---")
    print(df.describe().T[['mean', 'std', 'min', '50%', 'max']])

    print("\n==================================================")

if __name__ == "__main__":
    inspect_data_file()