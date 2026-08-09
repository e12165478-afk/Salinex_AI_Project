import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

def train_and_save_ensemble_model(data_path: str = "data/Combine_cleaned.csv", model_dir: str = "models"):
    print("🚀 شروع فرآیند آموزش مدل‌های علمی-تطبیقی Salinex AI...")
    
    # ۱. بررسی و بارگذاری داده‌ها
    if not os.path.exists(data_path):
        print(f"❌ خطا: فایل داده در مسیر {data_path} یافت نشد.")
        return False
    
    df = pd.read_csv(data_path)
    feature_cols = ['Li_ppm', 'Mg_ppm', 'Ca_ppm', 'TDS_ppm']
    
    if 'Temperature_C' in df.columns:
        feature_cols.append('Temperature_C')
    
    if 'Li_Recovery' not in df.columns:
        mg_li_ratio = df['Mg_ppm'] / np.maximum(df['Li_ppm'], 0.1)
        temp_effect = (df['Temperature_C'] - 25.0) * 0.1 if 'Temperature_C' in df.columns else 0
        df['Li_Recovery'] = np.clip(94.0 - (mg_li_ratio * 0.07) - (df['TDS_ppm'] / 150000.0) + temp_effect, 60.0, 98.0)
    
    X = df[feature_cols]
    y = df['Li_Recovery']
    
    # ۲. تقسیم داده‌ها
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # ۳. آموزش Random Forest
    print("🌲 در حال آموزش مدل Random Forest...")
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    
    # ۴. آموزش Gradient Boosting
    print("⚡ در حال آموزش مدل Gradient Boosting...")
    gb_model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.05, max_depth=5, random_state=42)
    gb_model.fit(X_train, y_train)
    gb_pred = gb_model.predict(X_test)
    
    # ۵. ارزیابی مدل ترکیبی (Ensemble)
    ensemble_pred = 0.5 * rf_pred + 0.5 * gb_pred
    r2 = r2_score(y_test, ensemble_pred)
    rmse = np.sqrt(mean_squared_error(y_test, ensemble_pred))
    
    print(f"✅ آموزش با موفقیت انجام شد!")
    print(f"📊 ضریب تبیین (R² Score): {r2:.4f}")
    print(f"📉 خطای ریشه میانگین مربعات (RMSE): {rmse:.4f}%")
    
    # ۶. ذخیره‌سازی مدل‌ها و متادیتا
    os.makedirs(model_dir, exist_ok=True)
    
    metadata = {
        "feature_names": feature_cols,
        "has_temperature": 'Temperature_C' in feature_cols,
        "r2_score": float(r2),
        "rmse": float(rmse),
        "feature_means": X.mean().to_dict(),
        "feature_stds": X.std().to_dict()
    }
    
    joblib.dump(rf_model, os.path.join(model_dir, "rf_model.pkl"))
    joblib.dump(gb_model, os.path.join(model_dir, "gb_model.pkl"))
    joblib.dump(metadata, os.path.join(model_dir, "model_metadata.pkl"))
    
    print(f"💾 مدل‌ها و متادیتا در پوشه '{model_dir}' ذخیره شدند.")
    return True

if __name__ == "__main__":
    train_and_save_ensemble_model(data_path="data/Combined_Real_Brine_Data_cleaned.csv")