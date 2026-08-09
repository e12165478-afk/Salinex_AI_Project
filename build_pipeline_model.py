import os
import joblib
import pandas as pd
import numpy as np
from catboost import CatBoostRegressor

# تعریف کلاس لایه محافظ ورودی و مهندسی ویژگی‌ها
class SalinexPipeline:
    def __init__(self):
        self.model = CatBoostRegressor(iterations=300, depth=6, learning_rate=0.05, verbose=0)
        self.is_fitted = False

    def transform_features(self, df):
        """اعمال لایه محافظ: تمیزکاری، فیلتر نویز و ساخت ویژگی‌های شیمیایی"""
        data = df.copy()

        # مطمئن شدن از وجود ستون‌های اصلی
        required_cols = ['Li_ppm', 'Mg_ppm', 'Ca_ppm', 'TDS_ppm', 'Temperature']
        for col in required_cols:
            if col not in data.columns:
                if col == 'Temperature':
                    data[col] = 25.0
                else:
                    data[col] = 100.0

        # فیلتر مقادیر پرت و نویزی (Clipping)
        data['Li_ppm'] = data['Li_ppm'].clip(lower=0.1)
        data['Mg_ppm'] = data['Mg_ppm'].clip(lower=0.1)

        # ساخت ویژگی‌های مهندسی شیمی/شورابه
        data['Mg_Li_Ratio'] = data['Mg_ppm'] / data['Li_ppm']
        data['Ca_Li_Ratio'] = data['Ca_ppm'] / data['Li_ppm']
        data['TDS_Density_Proxy'] = data['TDS_ppm'] / 10000.0

        return data

    def fit(self, X, y):
        X_trans = self.transform_features(X)
        self.model.fit(X_trans, y)
        self.is_fitted = True
        return self

    def predict(self, X):
        X_trans = self.transform_features(X)
        if not self.is_fitted:
            # در صورتی که مدل مستقل بارگذاری شود
            return self.model.predict(X_trans)
        return self.model.predict(X_trans)


def train_and_save_pipeline():
    print("🔄 در حال آماده‌سازی و آموزش پایپ‌لاین لایه محافظ Salinex...")

    # تلاش برای خواندن داده‌های نویزی واقعی پروژه
    data_path = "Combined_Brine_Dataset_noisy.csv"
    if not os.path.exists(data_path):
        data_path = os.path.join("data", "Combined_Brine_Dataset_noisy.csv")

    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        print(f"📊 داده‌ها از فایل {data_path} با {len(df)} ردیف بارگذاری شدند.")
    else:
        print("⚠️ فایل داده نویزی یافت نشد؛ ساخت داده شبیه‌سازی‌شده برای ساخت پایپ‌لاین...")
        np.random.seed(42)
        n = 1000
        df = pd.DataFrame({
            'Li_ppm': np.random.uniform(50, 300, n),
            'Mg_ppm': np.random.uniform(500, 3000, n),
            'Ca_ppm': np.random.uniform(100, 1000, n),
            'TDS_ppm': np.random.uniform(50000, 250000, n),
            'Temperature': np.random.uniform(15, 45, n),
            'Recovery_Rate': np.random.uniform(60, 90, n)
        })

    # تفکیک ویژگی‌ها و هدف
    target_col = 'Recovery_Rate' if 'Recovery_Rate' in df.columns else df.columns[-1]
    X = df.drop(columns=[target_col]) if target_col in df.columns else df
    y = df[target_col] if target_col in df.columns else np.random.uniform(65, 85, len(df))

    # آموزش پایپ‌لاین لایه محافظ
    pipeline = SalinexPipeline()
    pipeline.fit(X, y)

    # ذخیره‌سازی شیء کامل پایپ‌لاین
    output_path = "salinex_pipeline_model.pkl"
    joblib.dump(pipeline, output_path)
    print(f"✅ فایل با موفقیت در مسیر زیر ذخیره شد:\n 💾 {os.path.abspath(output_path)}")


if __name__ == "__main__":
    train_and_save_pipeline()