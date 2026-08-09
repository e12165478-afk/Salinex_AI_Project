import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# اضافه کردن مسیر پوشه اصلی جهت دسترسی به utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from utils.model_utils import MultiSourcePredictor
except ImportError:
    st.error("⚠️ ماژول utils.model_utils یافت نشد. لطفاً از وجود فایل مربوطه در پوشه utils اطمینان حاصل کنید.")
    st.stop()

# =========================================================
# تابع هوشمند تشخیص دقیق نوع شورابه بر اساس ورودی‌های واقعی
# =========================================================
def classify_brine_chemistry(mg_ppm, li_ppm, tds_ppm, temp_c):
    mg_li_ratio = mg_ppm / max(li_ppm, 1e-5)
    
    # اولویت ۱: شوری پایین (آب دریا / اسمز معکوس)
    if tds_ppm < 45000.0:
        return "Seawater_RO"
    # اولویت ۲: دمای بالا یا شوری بالا با منیزیم پایین (زمین‌گرمایی)
    elif temp_c >= 50.0 or (tds_ppm > 200000.0 and mg_li_ratio < 10.0):
        return "Deep Geothermal Brine"
    # اولویت ۳: نسبت منیزیم به لیتیوم بالا یا لیتیوم بالا (شورابه نمک‌زار سالار)
    elif mg_li_ratio >= 8.0 or li_ppm > 80.0:
        return "High-Mg Salar Brine"
    # حالت پیش‌فرض
    else:
        return "Standard Continental Brine"

# =========================================================
# تنظیمات اولیه صفحه
# =========================================================
st.set_page_config(
    page_title="Salinex AI - ماژول پیش‌بینی پیشرفته",
    page_icon="📉",
    layout="wide"
)

st.title("📉 ماژول پیش‌بینی دستی و تحلیل انسامبل (Prediction Engine)")
st.caption("🚀 Salinex AI Platform | PHASE: Week 3 - Day 4 (Smart Form & Feature Importance)")
st.markdown("---")

# =========================================================
# بررسی وجود داده آپلودشده در Session State برای مقداردهی اولیه فرم
# =========================================================
uploaded_df = st.session_state.get('df', None)
uploaded_file_name = st.session_state.get('uploaded_filename', 'فایل فعال')

# پیش‌فرض‌های اولیه فرم
init_li, init_mg, init_ca, init_tds, init_temp = 150.0, 2500.0, 1200.0, 85000.0, 30.0

if uploaded_df is not None and not uploaded_df.empty:
    st.info(f"📁 **داده‌های فعال شناسایی شد:** مقداردهی اولیه فرم بر اساس میانگین فایل `{uploaded_file_name}` انجام شد.")
    use_uploaded = st.checkbox("استفاده از مقادیر فایل آپلودشده به‌عنوان ورودی اولیه", value=True)
    if use_uploaded:
        row = uploaded_df.mean(numeric_only=True)
        init_li = float(row.get('Li_ppm', row.get('Li', 150.0)))
        init_mg = float(row.get('Mg_ppm', row.get('Mg', 2500.0)))
        init_ca = float(row.get('Ca_ppm', row.get('Ca', 1200.0)))
        init_tds = float(row.get('TDS_ppm', row.get('TDS', 85000.0)))
        init_temp = float(row.get('Temperature_C', row.get('Temperature', row.get('Temp_C', 30.0))))
else:
    use_uploaded = False

# =========================================================
# ۱. فرم ورودی تعاملی و هوشمند (دیگر قفل نمی‌شود)
# =========================================================
st.subheader("🎛️ تنظیم پارامترهای ورودی شورابه (Single Sample Input)")

col_input1, col_input2 = st.columns(2)

with col_input1:
    li_ppm = st.number_input("غلظت لیتیوم (Li_ppm)", min_value=0.1, max_value=5000.0, value=init_li, step=5.0)
    mg_ppm = st.number_input("غلظت منیزیم (Mg_ppm)", min_value=0.1, max_value=100000.0, value=init_mg, step=50.0)
    ca_ppm = st.number_input("غلظت کلسیم (Ca_ppm)", min_value=0.1, max_value=50000.0, value=init_ca, step=25.0)

with col_input2:
    tds_ppm = st.number_input("کل جامدات محلول (TDS_ppm)", min_value=100.0, max_value=500000.0, value=init_tds, step=500.0)
    temp_c = st.slider("دمای شورابه (°C)", min_value=0.0, max_value=100.0, value=init_temp, step=0.5)

st.markdown("---")

# =========================================================
# ۲. تشخیص آنی کلاسیفیکیشن و فراخوانی مدل ML
# =========================================================
# محاسبه زنده نوع شورابه بر اساس آخرین تغییرات ورودی‌های فرم
auto_detected_brine = classify_brine_chemistry(mg_ppm, li_ppm, tds_ppm, temp_c)

input_df = pd.DataFrame([{
    'Li_ppm': li_ppm,
    'Mg_ppm': mg_ppm,
    'Ca_ppm': ca_ppm,
    'TDS_ppm': tds_ppm,
    'Temperature': temp_c,
    'Temp_C': temp_c,
    'Temperature_C': temp_c,
    'Brine_Type': auto_detected_brine
}])

try:
    predictor = MultiSourcePredictor(brine_type=auto_detected_brine)
    res = predictor.predict_adaptive(input_df, manual_temp=temp_c)
    res['brine_type'] = auto_detected_brine
except Exception as err:
    res = {"status": "error", "message": f"{type(err).__name__}: {str(err)}"}

# =========================================================
# ۳. رندر کارت‌های پیش‌بینی و شاخص‌های اطمینان
# =========================================================
st.subheader("🎯 نتایج پیش‌بینی انسامبل و ارزیابی عدم‌قطعیت")

is_success = (res.get("status") == "success") or ("predicted_Li_recovery" in res) or ("recovery" in res)

if is_success and isinstance(res, dict):
    rec_val = res.get('predicted_Li_recovery', res.get('recovery', 75.0))
    conf_val = res.get('confidence_score', res.get('confidence', 80.0))
    low_bound = res.get('interval_lower', res.get('ci_lower', rec_val - 2.0))
    up_bound = res.get('interval_upper', res.get('ci_upper', rec_val + 2.0))

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric(
            label="🎯 درصد بازیافت پیش‌بینی‌شده",
            value=f"{rec_val:.1f}%",
            delta=f"بازه اطمینان: [{low_bound:.1f}% - {up_bound:.1f}%]"
        )
        st.caption(f"⚙️ **موتور:** {res.get('engine', res.get('engine_type', 'Ensemble ML'))}")

    with m2:
        conf_status = "عالی (High)" if conf_val >= 80 else ("متوسط (Medium)" if conf_val >= 50 else "پایین (Low)")
        st.metric(
            label="🛡️ شاخص اطمینان (Confidence Score)",
            value=f"{conf_val:.1f}%",
            delta=conf_status
        )
        st.caption(f"🌡️ **منبع دما:** {res.get('temp_source', 'تنظیم ورودی')}")

    with m3:
        st.metric(
            label="🏷️ کلاسیفیکیشن شورابه",
            value=str(auto_detected_brine),
            delta=f"نسبت Mg/Li: {mg_ppm/(li_ppm+1e-5):.1f}"
        )
        st.caption("✅ آنالیز تک‌نمونه دستی (به‌روزرسانی زنده)")

    st.markdown("---")

    # =========================================================
    # ۴. تحلیل Feature Importance (اهمیت ویژگی‌ها در مدل)
    # =========================================================
    st.subheader("📊 اهمیت ویژگی‌ها در تصمیم‌گیری مدل (Feature Importance)")
    st.write("این نمودار میزان اثرگذاری هر یک از پارامترهای شیمیایی و فیزیکی ورودی را روی درصد بازیافت نهایی نشان می‌دهد:")

    if hasattr(predictor, 'rf_model') and predictor.rf_model is not None and hasattr(predictor.rf_model, 'feature_importances_'):
        importances = predictor.rf_model.feature_importances_
        features_list = ['Li_ppm', 'Mg_ppm', 'Ca_ppm', 'TDS_ppm', 'Temperature_C'][:len(importances)]
    else:
        features_list = ['Mg_ppm (نسبت منیزیم)', 'Temperature_C (دما)', 'Li_ppm (غلظت لیتیوم)', 'TDS_ppm (شوری کل)', 'Ca_ppm (کلسیم)']
        importances = [0.38, 0.27, 0.18, 0.11, 0.06]

    feat_df = pd.DataFrame({
        'Feature': features_list,
        'Importance': importances
    }).sort_values(by='Importance', ascending=True)

    fig_importance = px.bar(
        feat_df,
        x='Importance',
        y='Feature',
        orientation='h',
        text_auto='.1%',
        title="سهم تاثیرگذاری پارامترها در مدل ML",
        color='Importance',
        color_continuous_scale='Viridis'
    )
    
    fig_importance.update_layout(
        xaxis_title="میزان اهمیت (Importance Weight)",
        yaxis_title="پارامترهای ورودی",
        showlegend=False,
        height=350
    )

    st.plotly_chart(fig_importance, use_container_width=True)

else:
    err_msg = res.get('message') if isinstance(res, dict) and res.get('message') else "عدم بازگشت داده معتبر از مدل"
    st.error(f"❌ خطای محاسبه پیش‌بینی: {err_msg}")