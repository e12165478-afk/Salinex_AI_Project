import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.metrics import r2_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

print("۱. در حال بارگذاری داده‌های پاک و نویزدار...")
clean_data_path = 'Combined_Real_Brine_Data_cleaned.csv'
noisy_data_path = 'Combined_Real_Brine_Data_noisy.csv'

df_clean = pd.read_csv(clean_data_path)
df_noisy = pd.read_csv(noisy_data_path)

target_col = 'Mg_Recovery_%'
drop_cols = [
    target_col,
    'Energy_Cost_USD_m3', 'Chemical_Cost_USD_m3', 
    'Mg_Revenue_USD_m3', 'Total_Revenue_USD_m3', 'Profit_USD_m3', 'ROI_%'
]

# انتخاب خودکار ستون‌های عددی برای جلوگیری از خطای String
numeric_df = df_clean.drop(columns=[c for c in drop_cols if c in df_clean.columns], errors='ignore')
features = list(numeric_df.select_dtypes(include=[np.number]).columns)

X_clean = df_clean[features].fillna(df_clean[features].mean())
y_clean = df_clean[target_col]

X_noisy = df_noisy[features].fillna(df_noisy[features].mean())
y_noisy = df_noisy[target_col]

# تقسیم داده‌ها
X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)
X_train_n, X_test_n, y_train_n, y_test_n = train_test_split(X_noisy, y_noisy, test_size=0.2, random_state=42)

# تعریف الگوریتم‌های مسیر دوم
models = {
    'Gradient Boosting Standard': GradientBoostingRegressor(random_state=42),
    'LightGBM Regressor': LGBMRegressor(random_state=42, verbose=-1),
    'CatBoost Regressor': CatBoostRegressor(random_state=42, verbose=0)
}

print("=" * 65)
print("۲. شروع ارزیابی الگوریتم‌های مسیر دوم در ۳ سناریو...")
print("=" * 65)

for name, model in models.items():
    print(f"\n<<< در حال بررسی الگوریتم: {name} >>>")
    
    # سناریو ۱: آموزش پاک | تست پاک
    model.fit(X_train_c, y_train_c)
    r2_s1 = r2_score(y_test_c, model.predict(X_test_c))
    rmse_s1 = np.sqrt(mean_squared_error(y_test_c, model.predict(X_test_c)))
    
    # سناریو ۲: آموزش پاک | تست نویزدار (شوک واقعی)
    r2_s2 = r2_score(y_test_n, model.predict(X_test_n))
    rmse_s2 = np.sqrt(mean_squared_error(y_test_n, model.predict(X_test_n)))
    
    # سناریو ۳: آموزش نویزدار | تست نویزدار (مدل مقاوم‌شده)
    model_noisy = model.__class__(**model.get_params())
    model_noisy.fit(X_train_n, y_train_n)
    r2_s3 = r2_score(y_test_n, model_noisy.predict(X_test_n))
    rmse_s3 = np.sqrt(mean_squared_error(y_test_n, model_noisy.predict(X_test_n)))
    
    print(f"  [سناریو ۱] آموزش پاک | تست پاک:     R2 = {r2_s1 * 100:.2f}%  |  RMSE = {rmse_s1:.4f}")
    print(f"  [سناریو ۲] آموزش پاک | تست نویزی:    R2 = {r2_s2 * 100:.2f}%  |  RMSE = {rmse_s2:.4f}")
    print(f"  [سناریو ۳] آموزش نویزی | تست نویزی:  R2 = {r2_s3 * 100:.2f}%  |  RMSE = {rmse_s3:.4f}")

print("\n" + "=" * 65)