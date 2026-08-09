import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error

# ۱. بارگذاری هر دو فایل (پاک و نویزدار)
clean_data_path = 'Combined_Real_Brine_Data_cleaned.csv'
noisy_data_path = 'Combined_Real_Brine_Data_noisy.csv'

df_clean = pd.read_csv(clean_data_path)
df_noisy = pd.read_csv(noisy_data_path)

# ۲. مشخص کردن ستون هدف
target_col = 'Mg_Recovery_%'

# ستون‌های مالی و غیرمرتبط جهت حذف
drop_cols = [
    target_col,
    'Energy_Cost_USD_m3', 'Chemical_Cost_USD_m3', 
    'Mg_Revenue_USD_m3', 'Total_Revenue_USD_m3', 'Profit_USD_m3', 'ROI_%'
]

# ۳. انتخاب «فقط ستون‌های عددی» برای جلوگیری از خطای متنی
numeric_df = df_clean.drop(columns=[col for col in drop_cols if col in df_clean.columns])
numeric_df = numeric_df.select_dtypes(include=[np.number])

features = list(numeric_df.columns)

# ۴. آماده‌سازی داده‌های Clean و Noisy
X_clean = df_clean[features]
y_clean = df_clean[target_col]

X_noisy = df_noisy[features]
y_noisy = df_noisy[target_col]

# تقسیم داده‌ها به آموزش و تست با seed ثابت
X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)
X_train_n, X_test_n, y_train_n, y_test_n = train_test_split(X_noisy, y_noisy, test_size=0.2, random_state=42)

print("=" * 60)
print("ارزیابی رفتار مدل در ۳ سناریوی متفاوت")
print("=" * 60)

# --------------------------------------------------
# سناریو ۱: آموزش پاک -> تست پاک
# --------------------------------------------------
model_clean = RandomForestRegressor(random_state=42)
model_clean.fit(X_train_c, y_train_c)

y_pred_s1 = model_clean.predict(X_test_c)
r2_s1 = r2_score(y_test_c, y_pred_s1)
rmse_s1 = np.sqrt(mean_squared_error(y_test_c, y_pred_s1))

print(f"\n[سناریو ۱] آموزش: پاک | تست: پاک")
print(f"  -> R2 Score:  {r2_s1 * 100:.2f}%")
print(f"  -> RMSE:      {rmse_s1:.4f}")

# --------------------------------------------------
# سناریو ۲: آموزش پاک -> تست نویزدار (شوک واقعی)
# --------------------------------------------------
y_pred_s2 = model_clean.predict(X_test_n)
r2_s2 = r2_score(y_test_n, y_pred_s2)
rmse_s2 = np.sqrt(mean_squared_error(y_test_n, y_pred_s2))

print(f"\n[سناریو ۲] آموزش: پاک | تست: نویزدار (شوک واقعی)")
print(f"  -> R2 Score:  {r2_s2 * 100:.2f}%")
print(f"  -> RMSE:      {rmse_s2:.4f}")

# --------------------------------------------------
# سناریو ۳: آموزش نویزدار -> تست نویزدار (مدل مقاوم شده)
# --------------------------------------------------
model_robust = RandomForestRegressor(random_state=42)
model_robust.fit(X_train_n, y_train_n)

y_pred_s3 = model_robust.predict(X_test_n)
r2_s3 = r2_score(y_test_n, y_pred_s3)
rmse_s3 = np.sqrt(mean_squared_error(y_test_n, y_pred_s3))

print(f"\n[سناریو ۳] آموزش: نویزدار | تست: نویزدار (مدل مقاوم شده)")
print(f"  -> R2 Score:  {r2_s3 * 100:.2f}%")
print(f"  -> RMSE:      {rmse_s3:.4f}")
print("=" * 60)