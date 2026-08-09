import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from catboost import CatBoostRegressor
from sklearn.ensemble import RandomForestRegressor
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

# تابع ساخت ویژگی‌های شیمیایی (فقط سطر به سطر - کاملاً ایمن)
def add_chemical_features(df):
    df_out = df.copy()
    
    # پیدا کردن ستون‌های مربوط به یون‌ها بر اساس نام
    mg_col = [c for c in df.columns if 'Mg' in c and 'Recovery' not in c and 'Revenue' not in c]
    ca_col = [c for c in df.columns if 'Ca' in c]
    na_col = [c for c in df.columns if 'Na' in c]
    k_col  = [c for c in df.columns if 'K' in c and 'Cost' not in c]
    
    # ۱. ساخت نسبت Mg به Ca (با اضافه کردن مقدار بسیار کوچک برای جلوگیری از تقسیم بر صفر)
    if mg_col and ca_col:
        df_out['Feature_Mg_Ca_Ratio'] = df_out[mg_col[0]] / (df_out[ca_col[0]] + 1e-6)
        
    # ۲. محاسبه شاخص مجموع بار یونی تقریبی
    ion_cols = mg_col + ca_col + na_col + k_col
    if ion_cols:
        df_out['Feature_Total_Ions'] = df_out[ion_cols].sum(axis=1)
        if mg_col:
            # ۳. سهم منیزیم از کل یون‌ها
            df_out['Feature_Mg_Fraction'] = df_out[mg_col[0]] / (df_out['Feature_Total_Ions'] + 1e-6)
            
    return df_out

print("۲. در حال اعمال مهندسی ویژگی‌ها روی داده‌ها...")
df_clean_fe = add_chemical_features(df_clean)
df_noisy_fe = add_chemical_features(df_noisy)

# انتخاب ستون‌های عددی ورودی
numeric_df = df_clean_fe.drop(columns=[c for c in drop_cols if c in df_clean_fe.columns], errors='ignore')
features = list(numeric_df.select_dtypes(include=[np.number]).columns)

print(f"تعداد کل ویژگی‌ها (همراه با ویژگی‌های جدید مهندسی‌شده): {len(features)}")

# آماده‌سازی ماتریس‌ها
X_clean = df_clean_fe[features].fillna(df_clean_fe[features].mean())
y_clean = df_clean_fe[target_col]

X_noisy = df_noisy_fe[features].fillna(df_noisy_fe[features].mean())
y_noisy = df_noisy_fe[target_col]

# تقسیم داده‌ها
X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)
X_train_n, X_test_n, y_train_n, y_test_n = train_test_split(X_noisy, y_noisy, test_size=0.2, random_state=42)

print("=" * 65)
print("۳. ارزیابی مدل CatBoost با ویژگی‌های جدید شیمیایی")
print("=" * 65)

# آموزش روی داده نویزدار مهندسی‌شده
cb_model = CatBoostRegressor(random_state=42, verbose=0)
cb_model.fit(X_train_n, y_train_n)

y_pred_n = cb_model.predict(X_test_n)
r2_n = r2_score(y_test_n, y_pred_n)
rmse_n = np.sqrt(mean_squared_error(y_test_n, y_pred_n))

print(f" [CatBoost روی داده نویزدار + Feature Engineering]:")
print(f"   -> R2 Score:  {r2_n * 100:.2f}%")
print(f"   -> RMSE:      {rmse_n:.4f}")
print("=" * 65)