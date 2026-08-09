import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
from sklearn.model_selection import train_test_split
from catboost import CatBoostRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

print("۱. در حال بارگذاری داده‌های نویزدار...")
noisy_data_path = 'Combined_Real_Brine_Data_noisy.csv'
clean_data_path = 'Combined_Real_Brine_Data_cleaned.csv'

df_noisy = pd.read_csv(noisy_data_path)
df_clean = pd.read_csv(clean_data_path)

target_col = 'Mg_Recovery_%'
drop_cols = [
    target_col,
    'Energy_Cost_USD_m3', 'Chemical_Cost_USD_m3', 
    'Mg_Revenue_USD_m3', 'Total_Revenue_USD_m3', 'Profit_USD_m3', 'ROI_%'
]

# انتخاب ستون‌های عددی
numeric_df = df_noisy.drop(columns=[c for c in drop_cols if c in df_noisy.columns], errors='ignore')
features = list(numeric_df.select_dtypes(include=[np.number]).columns)

# ۲. ساخت نسخه فیلترشده داده‌های نویزدار
df_filtered_sg = df_noisy.copy()
df_filtered_ma = df_noisy.copy()

# اعمال فیلترها روی ویژگی‌های نویزی
window_length = 7  # طول پنجره فیلتر
poly_order = 2     # درجه چندجمله‌ای Savitzky-Golay

for col in features:
    # فیلتر Savitzky-Golay
    df_filtered_sg[col] = savgol_filter(df_noisy[col], window_length=window_length, polyorder=poly_order)
    # فیلتر میانگین متحرک (Moving Average)
    df_filtered_ma[col] = df_noisy[col].rolling(window=3, min_periods=1).mean()

# آماده‌سازی ماتریس‌های داده
X_clean = df_clean[features].fillna(df_clean[features].mean())
y_clean = df_clean[target_col]

X_noisy = df_noisy[features].fillna(df_noisy[features].mean())
y_noisy = df_noisy[target_col]

X_sg = df_filtered_sg[features].fillna(df_filtered_sg[features].mean())
X_ma = df_filtered_ma[features].fillna(df_filtered_ma[features].mean())

# تقسیم داده‌ها به آموزش و تست
X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)
X_train_n, X_test_n, y_train_n, y_test_n = train_test_split(X_noisy, y_noisy, test_size=0.2, random_state=42)
X_train_sg, X_test_sg, y_train_sg, y_test_sg = train_test_split(X_sg, y_noisy, test_size=0.2, random_state=42)
X_train_ma, X_test_ma, y_train_ma, y_test_ma = train_test_split(X_ma, y_noisy, test_size=0.2, random_state=42)

print("=" * 65)
print("۲. ارزیابی تأثیر فیلترهای نویز روی مدل CatBoost")
print("=" * 65)

# مدل ۱: بدون فیلتر (حالت خام نویزدار)
cb_raw = CatBoostRegressor(random_state=42, verbose=0)
cb_raw.fit(X_train_n, y_train_n)
r2_raw = r2_score(y_test_n, cb_raw.predict(X_test_n))
rmse_raw = np.sqrt(mean_squared_error(y_test_n, cb_raw.predict(X_test_n)))

# مدل ۲: با فیلتر Savitzky-Golay
cb_sg = CatBoostRegressor(random_state=42, verbose=0)
cb_sg.fit(X_train_sg, y_train_sg)
r2_sg = r2_score(y_test_n, cb_sg.predict(X_test_sg))
rmse_sg = np.sqrt(mean_squared_error(y_test_n, cb_sg.predict(X_test_sg)))

# مدل ۳: با فیلتر Moving Average
cb_ma = CatBoostRegressor(random_state=42, verbose=0)
cb_ma.fit(X_train_ma, y_train_ma)
r2_ma = r2_score(y_test_n, cb_ma.predict(X_test_ma))
rmse_ma = np.sqrt(mean_squared_error(y_test_n, cb_ma.predict(X_test_ma)))

print(f" [داده نویزدار خام - بدون فیلتر]:  R2 = {r2_raw * 100:.2f}%  |  RMSE = {rmse_raw:.4f}")
print(f" [پس از فیلتر Savitzky-Golay]:    R2 = {r2_sg * 100:.2f}%  |  RMSE = {rmse_sg:.4f}")
print(f" [پس از فیلتر Moving Average]:    R2 = {r2_ma * 100:.2f}%  |  RMSE = {rmse_ma:.4f}")

print("=" * 65)