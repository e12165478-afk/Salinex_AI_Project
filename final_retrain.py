import pandas as pd
import joblib
import os
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

# ۱. مسیر دقیق فایل در پوشه data
file_path = r'Path(__file__).resolve().parent.parent\data\Combined_Real_Brine_Data_cleaned.csv'

# ۲. خواندن داده‌ها
df = pd.read_csv(file_path)

# ۳. انتخاب ستون‌های ورودی و خروجی (دقیقاً طبق لیست شما)
# ورودی‌ها: شوری، مقدار لیتیوم اولیه، منیزیم و کلسیم
X = df[['TDS_ppm', 'Li_ppm', 'Mg_ppm', 'Ca_ppm']] 

# خروجی: درصد بازیابی لیتیوم (که قبلاً 0.17 می‌داد)
y = df['Li_Recovery_%']

# ۴. ساختن مدل هوشمند
model = Pipeline([
    ('scaler', RobustScaler()), # برای مدیریت اعداد بزرگ مثل TDS
    ('regressor', GradientBoostingRegressor(n_estimators=100))
])

# ۵. آموزش و ذخیره
print("🔄 در حال آموزش مغز جدید با داده‌های واقعی...")
model.fit(X, y)
joblib.dump(model, 'brine_model_v2.pkl')
print("✅ مدل جدید با نام 'brine_model_v2.pkl' ساخته شد و آماده استفاده است!")