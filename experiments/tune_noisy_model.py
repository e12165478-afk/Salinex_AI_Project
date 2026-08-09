import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

print("۱. در حال بارگذاری داده‌ها...")
clean_data_path = 'Combined_Real_Brine_Data_cleaned.csv'
noisy_data_path = 'Combined_Real_Brine_Data_noisy.csv'

df_clean = pd.read_csv(clean_data_path)
df_noisy = pd.read_csv(noisy_data_path)

# ستون هدف
target_col = 'Mg_Recovery_%'

# ستون‌هایی که نباید در ورودی مدل باشند
drop_cols = [
    target_col,
    'Energy_Cost_USD_m3', 'Chemical_Cost_USD_m3', 
    'Mg_Revenue_USD_m3', 'Total_Revenue_USD_m3', 'Profit_USD_m3', 'ROI_%'
]

# انتخاب دقیق فقط ستون‌های عددی برای جلوگیری از خطای String
numeric_df = df_clean.drop(columns=[c for c in drop_cols if c in df_clean.columns], errors='ignore')
features = list(numeric_df.select_dtypes(include=[np.number]).columns)

X_clean = df_clean[features].fillna(df_clean[features].mean())
y_clean = df_clean[target_col]

X_noisy = df_noisy[features].fillna(df_noisy[features].mean())
y_noisy = df_noisy[target_col]

# تقسیم داده‌ها
X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)
X_train_n, X_test_n, y_train_n, y_test_n = train_test_split(X_noisy, y_noisy, test_size=0.2, random_state=42)

print(f"تعداد ویژگی‌های عددی ورودی: {len(features)}")
print("=" * 60)
print("۲. شروع جستجوی بهترین هایپرپارامترها برای Random Forest...")

# فضای جستجوی پارامترها برای RandomForest
rf_param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, 30, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

rf_search = RandomizedSearchCV(
    estimator=RandomForestRegressor(random_state=42),
    param_distributions=rf_param_grid,
    n_iter=10,
    cv=3,
    scoring='r2',
    random_state=42,
    n_jobs=-1
)

# آموزش روی داده‌های پاک برای یافتن بهترین هایپرپارامترها
rf_search.fit(X_train_c, y_train_c)
best_rf = rf_search.best_estimator_

print("\n[نتایج RandomForest بهینه‌شده]")
print(f"بهترین پارامترها: {rf_search.best_params_}")

# ارزیابی RF بهینه‌شده
r2_rf_c = r2_score(y_test_c, best_rf.predict(X_test_c))
r2_rf_n = r2_score(y_test_n, best_rf.predict(X_test_n))

print(f"  -> R2 روی داده پاک (سناریو ۱):    {r2_rf_c * 100:.2f}%")
print(f"  -> R2 روی داده نویزدار (سناریو ۲): {r2_rf_n * 100:.2f}%")

print("=" * 60)
print("۳. شروع جستجوی بهترین هایپرپارامترها برای XGBoost...")

# فضای جستجوی پارامترها برای XGBoost
xgb_param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 6, 10],
    'learning_rate': [0.01, 0.05, 0.1, 0.2],
    'subsample': [0.8, 1.0]
}

xgb_search = RandomizedSearchCV(
    estimator=XGBRegressor(random_state=42),
    param_distributions=xgb_param_grid,
    n_iter=10,
    cv=3,
    scoring='r2',
    random_state=42,
    n_jobs=-1
)

xgb_search.fit(X_train_c, y_train_c)
best_xgb = xgb_search.best_estimator_

print("\n[نتایج XGBoost بهینه‌شده]")
print(f"بهترین پارامترها: {xgb_search.best_params_}")

# ارزیابی XGB بهینه‌شده
r2_xgb_c = r2_score(y_test_c, best_xgb.predict(X_test_c))
r2_xgb_n = r2_score(y_test_n, best_xgb.predict(X_test_n))

print(f"  -> R2 روی داده پاک (سناریو ۱):    {r2_xgb_c * 100:.2f}%")
print(f"  -> R2 روی داده نویزدار (سناریو ۲): {r2_xgb_n * 100:.2f}%")
print("=" * 60)