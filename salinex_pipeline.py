import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from catboost import CatBoostRegressor
from sklearn.metrics import r2_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

print("۱. در حال ساخت لایه محافظ ورودی و آماده‌سازی سیستم...")

# ==========================================
# بخش ۱: کلاس بررسی و ساخت ستون‌های غایب
# ==========================================
class SchemaValidator(BaseEstimator, TransformerMixin):
    def __init__(self, expected_columns):
        self.expected_columns = expected_columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_df = pd.DataFrame(X).copy()
        for col in self.expected_columns:
            if col not in X_df.columns:
                X_df[col] = np.nan
        return X_df[self.expected_columns]

# ==========================================
# بخش ۲: کلاس پرکردن هوشمند داده‌های خالی (Imputer)
# ==========================================
class SmartFactoryImputer(BaseEstimator, TransformerMixin):
    def __init__(self, sensor_cols, ion_cols, n_neighbors=5):
        self.sensor_cols = sensor_cols
        self.ion_cols = ion_cols
        self.n_neighbors = n_neighbors
        self.knn_imputer = KNNImputer(n_neighbors=self.n_neighbors)

    def fit(self, X, y=None):
        X_df = pd.DataFrame(X)
        valid_cols = [c for c in (self.ion_cols + self.sensor_cols) if c in X_df.columns]
        if valid_cols:
            self.knn_imputer.fit(X_df[valid_cols])
        return self

    def transform(self, X):
        X_df = pd.DataFrame(X).copy()
        # پرکردن حسگرهای وابسته به زمان (مثل دما و pH)
        for col in self.sensor_cols:
            if col in X_df.columns:
                X_df[col] = X_df[col].ffill().bfill()
        
        # پرکردن یون‌ها با الگوریتم KNN
        valid_cols = [c for c in (self.ion_cols + self.sensor_cols) if c in X_df.columns]
        if valid_cols:
            imputed_data = self.knn_imputer.transform(X_df[valid_cols])
            X_df[valid_cols] = imputed_data
            
        return X_df

# ==========================================
# بخش ۳: محاسبه خودکار نسبت‌های شیمیایی
# ==========================================
class BrineFeatureExtractor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_df = pd.DataFrame(X).copy()
        
        mg_col = [c for c in X_df.columns if 'Mg' in c and 'Recovery' not in c and 'Revenue' not in c]
        ca_col = [c for c in X_df.columns if 'Ca' in c]
        na_col = [c for c in X_df.columns if 'Na' in c]
        k_col  = [c for c in X_df.columns if 'K' in c and 'Cost' not in c]
        
        if mg_col and ca_col:
            X_df['Feature_Mg_Ca_Ratio'] = X_df[mg_col[0]] / (X_df[ca_col[0]] + 1e-6)
            
        ion_cols = mg_col + ca_col + na_col + k_col
        if ion_cols:
            X_df['Feature_Total_Ions'] = X_df[ion_cols].sum(axis=1)
            if mg_col:
                X_df['Feature_Mg_Fraction'] = X_df[mg_col[0]] / (X_df['Feature_Total_Ions'] + 1e-6)
                
        return X_df

# ==========================================
# بخش اصلی اجرای آزمایشی روی داده‌های نویزدار
# ==========================================
noisy_data_path = 'Combined_Real_Brine_Data_noisy.csv'
df_noisy = pd.read_csv(noisy_data_path)

target_col = 'Mg_Recovery_%'
drop_cols = [
    target_col,
    'Energy_Cost_USD_m3', 'Chemical_Cost_USD_m3', 
    'Mg_Revenue_USD_m3', 'Total_Revenue_USD_m3', 'Profit_USD_m3', 'ROI_%'
]

# جداسازی ویژگی‌های ورودی
numeric_df = df_noisy.drop(columns=[c for c in drop_cols if c in df_noisy.columns], errors='ignore')
feature_cols = list(numeric_df.select_dtypes(include=[np.number]).columns)

# ایجاد لایه محافظ Pipeline
salinex_pipeline = Pipeline([
    ('schema_validator', SchemaValidator(expected_columns=feature_cols)),
    ('smart_imputer', SmartFactoryImputer(sensor_cols=['Temperature_C', 'pH'], ion_cols=feature_cols)),
    ('feature_extractor', BrineFeatureExtractor())
])

print("۲. عبور داده‌ها از لایه محافظ و ساخت خودکار ویژگی‌ها...")
X_processed = salinex_pipeline.fit_transform(df_noisy[feature_cols])
y = df_noisy[target_col]

# تقسیم داده‌ها به آموزش و تست
X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

print("۳. آموزش مدل CatBoost روی داده‌های بازسازی‌شده...")
model = CatBoostRegressor(random_state=42, verbose=0)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("=" * 65)
print("نتایج اجرای پلتفرم Salinex AI با لایه محافظ ورودی:")
print(f"  -> R2 Score: {r2 * 100:.2f}%")
print(f"  -> RMSE:     {rmse:.4f}")
print("=" * 65)