import os

model_utils_path = os.path.join("utils", "model_utils.py")

new_code = '''import os
import joblib
import pandas as pd

# مسیر فایل مدل نهایی
MODEL_PATH = "brine_model_v2.pkl"

def load_salinex_model():
    """بارگذاری مدل هوشمند Salinex"""
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            return model, True
        except Exception as e:
            print(f"خطا در بارگذاری مدل: {e}")
            return None, False
    else:
        # اگر v2 نبود، مدل اصلی پوشه models را چک کند
        alt_path = os.path.join("models", "brine_model.pkl")
        if os.path.exists(alt_path):
            try:
                model = joblib.load(alt_path)
                return model, True
            except Exception as e:
                return None, False
        return None, False

def predict_recovery(input_df):
    """پیش‌بینی درصد بازیافت با مدل بارگذاری‌شده"""
    model, success = load_salinex_model()
    if success and model is not None:
        try:
            predictions = model.predict(input_df)
            return predictions
        except Exception as e:
            print(f"خطا در محاسبات پیش‌بینی: {e}")
            return None
    return None
'''

with open(model_utils_path, "w", encoding="utf-8") as f:
    f.write(new_code)

print("✅ فایل utils/model_utils.py با موفقیت به‌روزرسانی شد!")