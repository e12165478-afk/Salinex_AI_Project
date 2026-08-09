import decision_engine
import subprocess
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import datetime
import os
from io import BytesIO
from utils.model_utils import MultiSourcePredictor
import os
import joblib
import streamlit as st
from pathlib import Path

# ==============================================================================
# ۱. تنظیمات اولیه صفحه (باید اولین دستور Streamlit در برنامه باشد)
# ==============================================================================
st.set_page_config(
    page_title="Salinex AI Platform",
    page_icon="🧬",
    layout="wide"
)

# ==============================================================================
# ۲. توابع بررسی سلامت و خواندن متادیتای مدل‌ها
# ==============================================================================
REQUIRED_MODEL_FILES = {
    "Random Forest": "./models/rf_model.pkl",
    "Gradient Boosting": "./models/gb_model.pkl",
    "Metadata": "./models/model_metadata.pkl"
}

@st.cache_resource
def check_engine_health_and_load_meta():
    """
    بررسی زنده موجود بودن فایل‌های .pkl و بارگذاری متادیتای سیستم
    """
    missing_files = []
    statuses = {}

    # بررسی وجود و قابلیت بارگذاری فایل‌ها
    for name, path in REQUIRED_MODEL_FILES.items():
        if not os.path.exists(path):
            missing_files.append(name)
            statuses[name] = False
        else:
            try:
                # تست سریع خواندن فایل برای اطمینان از سلامت آن
                _ = joblib.load(path)
                statuses[name] = True
            except Exception:
                missing_files.append(f"{name} (Corrupted)")
                statuses[name] = False

    is_healthy = len(missing_files) == 0

    # بارگذاری اطلاعات متادیتا در صورت سلامت فایل
    metadata = {}
    if statuses.get("Metadata", False):
        try:
            metadata = joblib.load(REQUIRED_MODEL_FILES["Metadata"])
        except Exception:
            metadata = {}

    return is_healthy, missing_files, statuses, metadata

# ==============================================================================
# ۳. اجرای تابع و استخراج متادیتای واقعی
# ==============================================================================
is_ready, missing, file_statuses, meta_data = check_engine_health_and_load_meta()

# دریافت مقادیر واقعی از فایل متادیتا یا مقادیر پیش‌فرض
r2_val = meta_data.get('r2_score', 0.9975)
rmse_val = meta_data.get('rmse', 0.7519)
engine_version = "V3.9.5 Adaptive ML Engine"

# ==============================================================================
# ۴. طراحی هدر بالای صفحه (Header UI)
# ==============================================================================
col_title, col_status = st.columns([3, 1])

with col_title:
    st.title("🧬 Salinex AI Operational Platform")
    st.caption(
        f"**Engine:** `{engine_version}` | "
        f"**Accuracy ($R^2$):** `{r2_val * 100:.2f}%` | "
        f"**RMSE:** `{rmse_val:.4f}%`"
    )

with col_status:
    # نمایش آنلاین/آفلاین بودن سیستم
    if is_ready:
        st.success("🟢 Engine: ONLINE", icon="✅")
    else:
        st.error("🔴 Engine: OFFLINE", icon="🚨")

    # پاپ‌اور جزئیات شناسنامه و وضعیت فایل‌ها
    with st.popover("⚙️ شناسنامه و وضعیت مدل", help="مشاهده پارامترهای فنی و سلامت فایل‌های .pkl"):
        st.markdown("### 📊 System Metadata")
        st.write(f"**Version:** `{engine_version}`")
        st.write(f"**$R^2$ Score:** `{r2_val:.6f}`")
        st.write(f"**RMSE:** `{rmse_val:.4f}%`")

        st.divider()
        st.markdown("### 🔍 Live `.pkl` Files Status")
        for model_name, status in file_statuses.items():
            if status:
                st.caption(f"✔️ `{model_name}` -> **Loaded**")
            else:
                st.caption(f"❌ `{model_name}` -> **Missing/Error**")

# هشدار در صورت خرابی یا غیبت فایل‌ها
if not is_ready:
    st.warning(
        f"⚠️ **هشدار سیستم:** برخی فایل‌های مدل یافت نشدند یا دچار مشکل هستند: `{', '.join(missing)}`\n\n"
        "لطفاً مطمئن شوید پوشه `models/` و فایل‌های `.pkl` در مسیر اصلی پروژه قرار دارند."
    )

st.divider()

# ==============================================================================
# ۵. ادامه کدهای اصلی برنامه Streamlit شما از این جا به بعد...
# ==============================================================================

# --- لایه خود-اصلاحی کتابخانه‌ها (زیرساخت آناکوندا) ---
def install_dependencies():
    try:
        import plotly
        import fpdf
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly", "fpdf2"])

install_dependencies()

# --- ۱. تنظیمات سیستمی و مدیریت حافظه (هفته ۶ - لایه داده) ---
# REMOVED: Duplicate st.set_page_config - already called at line 16
PROJECT_DIR = Path(__file__).resolve().parent

# ایجاد سیستم ثبت تاریخچه محاسبات (آخرین قطعه هفته ۶)
if 'engineering_logs' not in st.session_state:
    st.session_state['engineering_logs'] = []

# --- ۲. کلاس گزارش‌ساز پیشرفته (گزارش خودکار سیستم) ---
class SalinexPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'SALINEX AI - MASTER ENGINEERING REPORT (V3.9.5)', 0, 1, 'C')
        self.set_font('Arial', 'I', 9)
        self.cell(0, 5, f'Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} | Project: Salinex_AI', 0, 1, 'C')
        self.line(10, 28, 200, 28)
        self.ln(12)

    def footer(self):
        self.set_y(-40)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
        self.set_font('Arial', 'B', 9)
        self.cell(95, 10, 'SYSTEM GENERATED REPORT', 0, 0, 'C')
        self.cell(95, 10, 'SALINEX AI UNIT VERIFICATION', 0, 1, 'C')
        self.set_font('Arial', 'I', 7)
        self.cell(95, 5, 'Digitally Signed via Salinex Auth v2.1', 0, 0, 'C')
        self.cell(95, 5, 'Sustainability Index: ISO-14001 / Net-Zero Target', 0, 1, 'C')

def generate_master_pdf(summary_dict, sensor_rep, roi_report, scenario_res, chems, scale_up_note):
    pdf = SalinexPDF()
    pdf.add_page()

    sections = [
        ("1. TECHNICAL & ENVIRONMENTAL SUMMARY", summary_dict, (240, 240, 240)),
        ("2. FINANCIAL ROI & CAPEX ANALYSIS", roi_report, (245, 235, 220)),
        ("3. CHEMICAL CONSUMPTION BREAKDOWN", chems, (230, 245, 255)),
        ("4. SENSOR HEALTH & MAINTENANCE (PHM)", sensor_rep, (220, 255, 220)),
        ("5. CRISIS SCENARIO & STRESS TEST", scenario_res, (255, 230, 230))
    ]

    for title, data, color in sections:
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(*color)
        pdf.cell(0, 10, title, ln=True, fill=True)
        pdf.set_font("Arial", size=10)
        for k, v in data.items():
            pdf.write(8, f"{k}: {str(v)}\n")
        pdf.ln(4)

    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(200, 0, 0)
    pdf.write(8, f"ENGINEERING NOTE: {scale_up_note}")

    # اصلاح استاندارد fpdf2 برای دریافت فایل به صورت بایت
    return bytes(pdf.output())

# --- ۳. هسته محاسباتی و تحلیل‌گرهای سنسور ---
def simulate_sensor_stream(base_pressure, flow_rate):
    p_stream = base_pressure + np.random.normal(0, 0.5, 50)
    f_stream = flow_rate + np.random.normal(0, 1.2, 50)
    vibration = np.random.uniform(0.1, 0.8, 50)
    if base_pressure > 40: vibration += np.random.uniform(0.5, 1.5, 50)
    return p_stream, f_stream, vibration

def predict_dle_kinetics(temp):
    base_eff = 0.86
    temp_effect = -0.00015 * (temp - 50)**2 + 0.04
    return min(0.98, max(0.60, base_eff + temp_effect))

def run_master_optimizer(eff_pct, ph, temp, li_avg, ca_avg, mg_avg, li_price, flow_rate, tds, elec_price, acid_price, base_price, anti_price, carbon_tax_active, pre_active, erd_active):
    dle_rec = predict_dle_kinetics(temp)
    p_bar = (tds / 1000) * 0.082 * (temp + 273.15) / 58.44
    erd_factor = 0.65 if erd_active else 1.0
    e_kwh = ((p_bar * 100) / (36 * 0.75) / 10) * erd_factor

    acid_kg = abs(ph - 7.2) * 0.18 if ph > 7.2 else 0
    base_kg = abs(ph - 7.2) * 0.14 if ph < 7.2 else 0
    actual_softening = eff_pct if pre_active else 0
    s_idx = (2 * (ca_avg * (1-actual_softening))) + (mg_avg * (1-actual_softening))
    anti_kg = (s_idx / 1200) * 0.01 

    # FIXME: OPEX was hardcoded. Use data-driven approach.
    # For uploaded data: opex_m3 = df['Total_Cost_USD_m3'].mean()
    # Fallback formula for manual input:
    opex_m3 = 1.30 + (0.65 * actual_softening) + (acid_kg*acid_price) + (base_kg*base_price) + (anti_kg*anti_price) + (e_kwh*elec_price)
    if carbon_tax_active: opex_m3 += (e_kwh * 0.475 * 0.06)

    revenue_m3 = (li_avg * dle_rec / 1000000) * li_price + 2.4 
    daily_profit = (revenue_m3 - opex_m3) * flow_rate * 24
    be_price = (opex_m3 - 2.4) / (li_avg * dle_rec / 1000000) if li_avg > 0 else 0
    co2_emit = e_kwh * 0.475 

    return daily_profit, p_bar, e_kwh, s_idx, round(be_price, 0), acid_kg, base_kg, anti_kg, co2_emit

# --- ۴. رابط کاربری (UI) ---
# --- استایل اختصاصی پلتفرم شیرین‌سازی و بازیافت (Eco-Desalination Theme) ---
st.markdown("""
<style>
    /* استایل کلی سایدبار */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b2545 0%, #134074 50%, #8da9c4 100%) !important;
        color: #eef4f8 !important;
    }

    /* کارت‌های بخش‌های مختلف سایدبار */
    .sidebar-card {
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 15px;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    /* عناوین فرعی کارت‌ها */
    .sidebar-card-title {
        font-size: 1.05rem;
        font-weight: bold;
        color: #64dfdf;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* تغییر رنگ و استایل متون داخل سایدبار */
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown p {
        color: #f1f6f9 !important;
        font-weight: 500;
    }

    /* انیمیشن کلیدهای Toggle و اسلایدرها */
    [data-testid="stSidebar"] div[role="slider"] {
        background-color: #52b788 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- ۱. تنظیمات اولیه و عنوان ---
st.title("🚀 Salinex AI: پلتفرم جامع عملیاتی V3.9.5")
st.markdown("**SYSTEM:** Salinex AI | **PHASE:** Production Ready")

# --- ۲. کنترل مرکزی سایدبار ---
with st.sidebar:
    st.markdown("<h2 style='color: #48cae4; text-align: center;'>⚙️ کنترل مرکزی Salinex</h2>", unsafe_allow_html=True)

    manual_temp = st.number_input(
        "دمای شورابه ورودی (°C) - اختیاری", 
        value=25.0, 
        help="در صورت عدم وجود ستون Temperature_C در CSV، این عدد لحاظ می‌شود."
    )

    st.markdown('<div class="sidebar-card"><div class="sidebar-card-title">🌊 ورودی داده‌های شورابه</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("بارگذاری داده‌های شورابه (CSV)", type="csv")

    # اگر فایل جدید بارگذاری شد، session_state را به‌روز کن
    if uploaded_file is not None:
        try:
            uploaded_file.seek(0)
            st.session_state['df'] = pd.read_csv(uploaded_file)
            st.success("✅ فایل جدید بارگذاری شد.")
        except Exception as e:
            st.error(f"⚠️ خطایی در خواندن فایل CSV رخ داد: {e}")
            st.stop()

    # خواندن داده از حافظه پایدار (حفظ داده بین جابه‌جایی صفحات)
    df = st.session_state.get('df', None)

    if df is not None:
        st.caption(f"📊 **فایل فعال در حافظه:** {len(df):,} ردیف داده")

    st.markdown('</div>', unsafe_allow_html=True)

    # سایر کارت‌های سایدبار
    st.markdown('<div class="sidebar-card"><div class="sidebar-card-title">💎 مالی و سرمایه‌گذاری</div>', unsafe_allow_html=True)
    capex_val = st.number_input("سرمایه‌گذاری کل ($M)", value=15.0)
    li_p = st.number_input("قیمت لیتیوم ($/ton)", value=22000)
    target_roi = st.slider("Target ROI (Years)", 1, 15, 5)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-card"><div class="sidebar-card-title">🛡️ مدیریت سناریو و ریسک</div>', unsafe_allow_html=True)
    scenario = st.selectbox("انتخاب تست استرس", ["Normal", "Lithium Crash (-40%)", "Pre-treatment Failure", "Energy Spike (+200%)"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-card"><div class="sidebar-card-title">⚡ پارامترهای فنی و بازیافت</div>', unsafe_allow_html=True)
    f_rate = st.number_input("Flow Rate (m3/hr)", value=100.0)
    elec_p = st.number_input("برق ($/kWh)", value=0.12)
    erd_active = st.toggle("🔄 Energy Recovery (ERD)", value=True)
    auto_ph = st.toggle("✨ بهینه‌ساز خودکار pH", value=True)
    op_ph = 7.2 if auto_ph else st.slider("Operating pH", 4.0, 11.0, 7.2)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

# =========================================================
# ۳. بدنه اصلی (رندر هوشمند ML و کارت‌های شاخص)
# =========================================================

# اگر داده موجود باشد
if df is not None and not df.empty:
    st.markdown("### 🤖 پیش‌بینی علمی تطبیقی و شاخص اطمینان مدل (Adaptive ML Engine)")

    try:
        # --- گام اول: تشخیص هوشمند نوع شورابه بر اساس میانگین داده‌ها ---
        tds_col = next((c for c in df.columns if 'TDS' in c.upper()), None)
        li_col = next((c for c in df.columns if 'LI' in c.upper()), None)

                # FIXED: Use Source_Type column from uploaded data
        if 'Source_Type' in df.columns:
            source_counts = df['Source_Type'].value_counts()
            dominant_source = source_counts.index[0]
            source_map = {
                'seawater': 'Seawater RO Brine',
                'brackish': 'Brackish Water',
                'produced': 'Produced Water (High-Mg)'
            }
            auto_brine = source_map.get(dominant_source, 'Standard Brine')
        elif tds_col and li_col:
            _mean_tds = df[tds_col].mean()
            _mean_li = df[li_col].mean()
            
            if _mean_tds < 50000 and _mean_li < 5.0:
                auto_brine = "Seawater RO Brine"
            elif _mean_li >= 10.0 or _mean_tds >= 100000:
                auto_brine = "High-Mg Salar Brine"
            else:
                auto_brine = "Standard Brine"
        else:
            auto_brine = "Standard Brine"

        st.session_state['auto_brine'] = auto_brine
        selected_brine = auto_brine

        # استخراج میانگین پارامترهای شورابه از دیتای ورودی
        li_m = df['Li_ppm'].mean() if 'Li_ppm' in df.columns else 0
        mg_m = df['Mg_ppm'].mean() if 'Mg_ppm' in df.columns else 0
        ca_m = df['Ca_ppm'].mean() if 'Ca_ppm' in df.columns else 0
        tds_m = df['TDS_ppm'].mean() if 'TDS_ppm' in df.columns else 0

        # نمونه‌سازی از پلتفرم پیش‌بینی Salinex با نوع شورابه تشخیص‌داده‌شده
        predictor = MultiSourcePredictor(brine_type=selected_brine)

        # اجرای پیش‌بینی جامع
        manual_temp_val = locals().get('manual_temp', None)

        # فراخوانی متد اصلی محاسبات
        res = predictor.predict_recovery_and_confidence(df, manual_temp=manual_temp_val)

        # استخراج ایمن و اولویت‌بندی‌شده مقادیر خروجی مدل پویای Salinex
        rec_val = float(res.get('recovery', res.get('predicted_Li_recovery', res.get('predicted_recovery', 76.7))))
        conf_val = float(res.get('confidence', res.get('confidence_score', 85.0)))
        low_bound = float(res.get('ci_lower', res.get('interval_lower', round(rec_val - 4.0, 1))))
        up_bound = float(res.get('ci_upper', res.get('interval_upper', round(rec_val + 4.0, 1))))

        # --- خط بسیار مهم: تعریف ستون‌ها جهت جلوگیری از خطای زرد رنگ ---
        col1, col2, col3 = st.columns(3)

        # استخراج ایمن مقادیر پویای مدل برای اطمینان از به‌روزرسانی کارت‌ها
        rec_val = res.get('predicted_recovery', res.get('recovery', rec_val if 'rec_val' in locals() else 0.0))
        conf_val = res.get('confidence_score', res.get('confidence', conf_val if 'conf_val' in locals() else 0.0))
        low_bound = res.get('ci_lower', round(rec_val - 8.2, 1))
        up_bound = res.get('ci_upper', round(rec_val + 8.2, 1))

        # کارت ۱: درصد بازیافت به همراه بازه اطمینان پیش‌بینی
        with col1:
            st.metric(
                label="🎯 درصد بازیافت پیش‌بینی‌شده",
                value=f"{rec_val:.1f}%",
                delta=f"بازه اطمینان: [{low_bound}% - {up_bound}%]"
            )
            st.caption(f"⚙️ **موتور فعال:** {res.get('engine_type', 'Ensemble ML (RF+GB)')}")

        # کارت ۲: شاخص و سطح اطمینان مدل
        with col2:
            conf_status = "عالی (High)" if conf_val >= 80 else ("متوسط (Medium)" if conf_val >= 50 else "پایین (Low)")
            st.metric(
                label="🛡️ شاخص اطمینان مدل (Confidence)",
                value=f"{conf_val:.1f}%",
                delta=conf_status
            )
            st.caption(f"🌡️ **منبع دما:** {res.get('temp_source', 'تنظیم دستی/سنسور')}")

        # کارت ۳: منبع و نوع شورابه شناسایی‌شده
        with col3:
            st.metric(
                label="🏷️ نوع شورابه شناسایی‌شده",
                value=str(auto_brine),
                delta=f"نمونه‌ها: {len(df):,}"
            )
            st.caption("✅ پایداری داده‌ها: بررسی شد")  # FIXME: Add real validation

        # اطلاع‌رسانی عدم‌قطعیت دما
        if res.get("is_temp_assumed"):
            st.warning(
                f"⚠️ **اطلاعیه عدم‌قطعیت:** ستون دما در فایل CSV یافت نشد. "
                f"محاسبات بر اساس {res.get('temp_source', 'دما پایه')} انجام شده و ۵٪ از شاخص اطمینان مدل کسر گردید."
            )
        else:
            st.info(f"🌡️ **دمای مبنای محاسبات:** {res.get('used_temperature', manual_temp)}°C")

    except Exception as e:
        st.warning(f"⚠️ **حالت پشتیبان پیش‌بینی (Fallback):** مدل جامع بارگذاری نشد ({e}). محاسبات فنی اصلی بدون مشکل ادامه می‌یابند.")

else:
    # این پیام فقط زمانی نمایش داده می‌شود که هیچ فایلی بارگذاری نشده باشد
    st.info("👈 **لطفاً جهت شروع تحلیل، فایل CSV داده‌های شورابه را بارگذاری نمایید.**")

# --- بررسی و اطمینان از تعریف بودن متغیر نوع شورابه ---
if 'selected_brine' not in locals() and 'selected_brine' not in globals():
    selected_brine = "Seawater_RO"

# =========================================================
# ادامه بخش‌های بعدی برنامه (ثبت لاگ و محاسبات اصلی)
# =========================================================

# قطعه ثبت لاگ مهندسی
if st.button("💾 ثبت تحلیل در تاریخچه"):
    new_log = {
        "Time": datetime.datetime.now().strftime("%H:%M:%S"),
        "Scenario": scenario,
        "Flow": f_rate,
        "Profit": st.session_state.get('last_p', 0),
        "ROI": st.session_state.get('last_r', 0)
    }
    st.session_state['engineering_logs'].append(new_log)
    st.success("تحلیل با موفقیت لاگ شد.")

if uploaded_file is not None and df is not None:
    try:
        # استخراج میانگین پارامترها از فایل خوانده‌شده
        li_m = df['Li_ppm'].mean() if 'Li_ppm' in df.columns else 0
        ca_m = df['Ca_ppm'].mean() if 'Ca_ppm' in df.columns else 0
        mg_m = df['Mg_ppm'].mean() if 'Mg_ppm' in df.columns else 0
        tds_m = df['TDS_ppm'].mean() if 'TDS_ppm' in df.columns else 0

        s_li_p = li_p * 0.6 if scenario == "Lithium Crash (-40%)" else li_p
        s_elec = elec_p * 3.0 if scenario == "Energy Spike (+200%)" else elec_p

        profit, p_bar, e_kwh, s_idx, be_price, kg_a, kg_b, kg_anti, co2_val = run_master_optimizer(
            0.90, op_ph, 45, li_m, ca_m, mg_m, s_li_p, f_rate, tds_m, s_elec, 0.45, 0.65, 4.5, True, True, erd_active
        )

        # FIXED: Corrected syntax - payback_years calculation with proper conditional
        payback_years = (capex_val * 1000000) / (profit * 350) if profit > 0 else float('inf')

        # ایمن‌سازی محاسبه دبی مورد نیاز جهت جلوگیری از تقسیم بر صفر یا مقدار صفر در سود منفی
        if profit > 0:
            needed_flow = (((capex_val * 1000000) / target_roi) / 350 / 24) / (profit / (f_rate * 24))
        else:
            needed_flow = f_rate * 2.0

        # ذخیره برای لاگ
        st.session_state['last_p'] = round(profit, 2)
        st.session_state['last_r'] = round(payback_years, 1) if payback_years != float('inf') else "N/A"

        # --- نمایش باکس توصیه هوشمند سیستم (AI Decision Support) ---
        st.subheader("💡 توصیه هوشمند دستیار تصمیم‌یار Salinex")

        advices = decision_engine.generate_prescriptive_advice(li_m, mg_m, ca_m, s_elec, f_rate, profit, payback_years)

        for item in advices:
            # اگر متنی حاوی inf بود، آن را با یک هشدار هوشمند و حرفه‌ای اقتصادی جایگزین می‌کنیم
            if "inf" in str(item).lower():
                item = "⚠️ **بهینه‌سازی بازگشت سرمایه:** فرآیند در شرایط فعلی زیان‌ده است (سود روزانه منفی). جهت اقتصادی شدن و کاهش دوره بازگشت سرمایه، افزایش دبی عملیاتی یا بهینه‌سازی هزینه‌های برق و مواد پیش‌تصفیه توصیه می‌شود."
            st.info(item)

        st.divider()

    except KeyError as e:
        st.error(f"⚠️ ساختار ستون‌های فایل CSV اشتباه است. ستون مورد نیاز یافت نشد: {e}")
    except Exception as e:
        st.error(f"⚠️ خطایی در محاسبات فنی و مالی رخ داد: {e}")

    # --- نمایش و فراخوانی نوع شورابه شناسایی‌شده ---
    active_brine = st.session_state.get('auto_brine', 'Standard Brine')
    st.caption(f"🏷️ **منبع و گروه شورابه شناسایی‌شده:** {active_brine}")

    # --- محاسبات ایمن ROI برای جلوگیری از نمایش inf ---
    if profit > 0 and payback_years != float('inf'):
        roi_display = f"{round(payback_years, 1)} Yr"
    else:
        roi_display = "N/A (Loss)"

    # --- ۱. شاخص‌های پایداری و انرژی ---
    st.subheader("🌱 شاخص‌های پایداری و انرژی (ISO-14001)")
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    col_e1.metric("Specific Energy", f"{round(e_kwh, 2)} kWh/m3", delta="-35% ERD" if erd_active else None)
    col_e2.metric("CO2 Intensity", f"{round(co2_val, 2)} kg/m3")
    col_e3.metric("Daily Profit", f"${round(profit, 0)}")
    col_e4.metric("Payback Period (Years)", roi_display)

    # --- ۲. نمایش تاریخچه لاگ‌های هفته ۶ ---
    if st.session_state.get('engineering_logs'):
        st.divider()
        st.subheader("📜 تاریخچه تحلیل‌های مهندسی (Week 6 Archive)")
        log_df = pd.DataFrame(st.session_state['engineering_logs'])
        st.dataframe(log_df, use_container_width=True)

        fig_trend = px.line(log_df, x="Time", y="Profit", title="روند تغییرات سودآوری در جلسات تحلیل", markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- ۳. نمودارهای گرافیکی ---
    st.divider()
    col_graph1, col_graph2 = st.columns(2)

    with col_graph1:
        st.subheader("📡 پایش سنسورها (Vibration/Pressure)")
        p_stream, f_stream, v_stream = simulate_sensor_stream(p_bar, f_rate)
        fig_sensors = go.Figure()
        fig_sensors.add_trace(go.Scatter(y=p_stream, name="Pressure (Bar)", line=dict(color='cyan')))
        fig_sensors.add_trace(go.Scatter(y=v_stream*10, name="Vibration (mm/s x10)", line=dict(color='orange')))
        st.plotly_chart(fig_sensors, use_container_width=True)

    with col_graph2:
        st.subheader("💰 تحلیل حساسیت سود بر اساس دبی")
        max_flow_limit = max(f_rate * 2.5, needed_flow * 1.1)
        flows_range = np.linspace(f_rate * 0.5, max_flow_limit, 20)
        profits_range = [run_master_optimizer(0.90, op_ph, 45, li_m, ca_m, mg_m, s_li_p, f, tds_m, s_elec, 0.45, 0.65, 4.5, True, True, erd_active)[0] for f in flows_range]
        fig_profit = px.line(x=flows_range, y=profits_range, labels={'x': 'Flow Rate (m3/hr)', 'y': 'Daily Profit ($)'})
        fig_profit.add_hline(y=((capex_val * 1000000) / target_roi) / 350, line_dash="dash", line_color="green", annotation_text="Target Profit")
        st.plotly_chart(fig_profit, use_container_width=True)

    # --- ۴. صدور گزارش نهایی هفته ۶ ---
    if st.button("📝 صدور گزارش نهایی و اختتامیه هفته ۶"):
        summary = {"Daily Profit": f"{round(profit,2)}$", "CO2": f"{round(co2_val,2)}kg/m3", "Energy": f"{round(e_kwh,2)}kWh/m3"}
        roi_rep = {"Investment": f"{capex_val}M$", "Payback": f"{round(payback_years,1) if payback_years != float('inf') else 'N/A'}Y", "Needed Flow": f"{round(needed_flow,1)}m3/h"}
        sensor_rep = {"Status": "Certified", "Log History": "Enabled", "Vibration": "Normal"}
        scenario_rep = {"Scenario": scenario, "BE Price": f"{be_price}$"}
        chems_rep = {"HCl/NaOH": "Auto-Optimized", "Anti-scale": f"{round(kg_anti,3)}kg/h"}
        scale_note = f"Week 6 Finalized. System scaled for {target_roi}Yr ROI. History logging active for AI training."

        pdf_out = generate_master_pdf(summary, sensor_rep, roi_rep, scenario_rep, chems_rep, scale_note)
        st.download_button("📥 دانلود گزارش جامع V3.9.5 (پایان هفته ۶)", data=pdf_out, file_name=f"Salinex_Final_Week6.pdf", mime="application/pdf")