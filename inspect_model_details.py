import os
import joblib
import numpy as np

def inspect_models():
    print("==================================================")
    print("🔍 استخراج مشخصات و پارامترهای فنی مدل‌های Salinex AI")
    print("==================================================\n")

    model_paths = {
        "Random Forest": "./models/rf_model.pkl",
        "Gradient Boosting": "./models/gb_model.pkl",
        "Brine Base Model": "./models/brine_model.pkl",
        "Brine Model V2": "./brine_model_v2.pkl",
        "Metadata": "./models/model_metadata.pkl"
    }

    feature_names = ['Li_ppm', 'Mg_ppm', 'Ca_ppm', 'TDS_ppm', 'Temperature']

    for name, path in model_paths.items():
        if not os.path.exists(path):
            print(f"⚠️ فایل یافت نشد: {path}")
            continue

        size_kb = os.path.getsize(path) / 1024
        print(f"📦 [{name}] -> {path} ({size_kb:.2f} KB)")

        try:
            obj = joblib.load(path)
            
            # اگر فایل متادیتا باشد
            if isinstance(obj, dict):
                print("   📌 نوع: دیکشنری متادیتا / تنظیمات")
                print("   🔑 کلیدهای موجود:")
                for k, v in obj.items():
                    print(f"      - {k}: {v}")

            # اگر مدل رگرسیون یا درخت تصمیم باشد
            else:
                print(f"   🤖 نوع مدل: {type(obj).__name__}")
                
                # استخراج تعداد پارامترها / درخت‌ها
                if hasattr(obj, 'n_estimators'):
                    print(f"   🌲 تعداد درخت‌ها (n_estimators): {obj.n_estimators}")
                if hasattr(obj, 'max_depth'):
                    print(f"   📏 حداکثر عمق (max_depth): {obj.max_depth}")
                if hasattr(obj, 'n_features_in_'):
                    print(f"   📊 تعداد ویژگی‌های ورودی (n_features): {obj.n_features_in_}")

                # استخراج اهمیّت ویژگی‌ها (Feature Importances)
                if hasattr(obj, 'feature_importances_'):
                    importances = obj.feature_importances_
                    print("   🎯 درصد اهمیت ویژگی‌ها در پیش‌بینی (Feature Importance):")
                    for idx, imp in enumerate(importances):
                        feat = feature_names[idx] if idx < len(feature_names) else f"Feature_{idx}"
                        print(f"      • {feat}: {imp * 100:.2f}%")

                # برای مدل‌های Random Forest (تعداد کل گره‌ها)
                if hasattr(obj, 'estimators_'):
                    total_nodes = sum(e.tree_.node_count for e in obj.estimators_)
                    print(f"   🧠 مجموع گره‌های تصمیم‌گیری (Total Decision Nodes): {total_nodes:,}")

        except Exception as e:
            print(f"   ❌ خطایی در باز کردن فایل رخ داد: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    inspect_models()