import pandas as pd
import numpy as np

# ۱. تنظیم seed برای تکرارپذیری نتایج
np.random.seed(42)

# ۲. بارگذاری فایل داده‌های تمیز
input_filename = 'Combined_Real_Brine_Data_cleaned.csv'
output_filename = 'Combined_Real_Brine_Data_noisy.csv'

df = pd.read_csv(input_filename)
df_noisy = df.copy()

print("در حال ساخت داده‌های نویزدار...")

# ۳. اعمال نویز روی متغیرهای فیزیکی و حسگرها
if 'Temp_C' in df_noisy.columns:
    # خطای حسگر دما (+-1.5 درجه)
    df_noisy['Temp_C'] += np.random.normal(0, 1.5, size=len(df_noisy))

if 'pH' in df_noisy.columns:
    # خطای حسگر pH (+-0.15)
    df_noisy['pH'] += np.random.normal(0, 0.15, size=len(df_noisy))
    df_noisy['pH'] = df_noisy['pH'].clip(0, 14)

if 'Energy_kWh_m3' in df_noisy.columns:
    # نوسان ۳ درصدی حسگر انرژی
    df_noisy['Energy_kWh_m3'] *= (1 + np.random.normal(0, 0.03, size=len(df_noisy)))

# ۴. اعمال خطای ۷ درصدی آنالیز آزمایشگاهی روی تمام ستون‌های غلظت یون‌ها
ion_cols = [col for col in df_noisy.columns if '_ppm' in col]
for col in ion_cols:
    relative_noise = np.random.normal(0, 0.07, size=len(df_noisy))
    df_noisy[col] *= (1 + relative_noise)
    df_noisy[col] = df_noisy[col].clip(lower=0) # غلظت نمی‌تواند منفی شود

# ۵. ذخیره فایل جدید در همان پوشه
df_noisy.to_csv(output_filename, index=False)

print(f"فایل نویزدار با موفقیت ایجاد و ذخیره شد: {output_filename}")