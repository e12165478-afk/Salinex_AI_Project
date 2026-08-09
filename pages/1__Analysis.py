# pages/1__Analysis.py - پلتفرم جامع تحلیل علمی تطبیقی و سیستم تحلیل یکپارچه Salinex AI
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import yaml
from datetime import datetime
from utils.model_utils import MultiSourcePredictor

# --- تنظیمات صفحه ---
st.set_page_config(page_title="Salinex AI - Integrated Comparative Analysis", layout="wide")

# --- کلاس موتور تحلیل یکپارچه Salinex AI ---
class AdaptiveAnalysis:
    """
    کلاس مدیریت تحلیل تطبیقی یکپارچه، کانفیگ وزن‌ها، امتیاز ترکیبی،
    هشدارهای هوشمند و توليد گزارش جامع تحلیلی
    """
    def __init__(self, df: pd.DataFrame, config_path: str = "data/config/kpi_weights.yaml"):
        self.df = df
        self.config_path = config_path
        self.weights_config = self._load_config()
        self.brine_type = self._detect_brine_type()

    def _load_config(self) -> dict:
        """بارگذاری پویا فایل YAML تنظیمات وزن‌دهی"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            return {
                "Seawater RO Brine": {
                    "weights": {"Li_recovery": 0.35, "Mg_recovery": 0.20, "Ca_recovery": 0.15, "Energy_cost": 0.15, "ROI": 0.15},
                    "benchmarks": {"Li_recovery_target": 90.0, "Energy_cost_target": 0.50, "ROI_target": 6.0}
                },
                "High-Mg Salar Brine": {
                    "weights": {"Li_recovery": 0.40, "Mg_recovery": 0.25, "Ca_recovery": 0.10, "Energy_cost": 0.15, "ROI": 0.10},
                    "benchmarks": {"Li_recovery_target": 85.0, "Energy_cost_target": 0.80, "ROI_target": 4.0}
                },
                "Standard Brine": {
                    "weights": {"Li_recovery": 0.30, "Mg_recovery": 0.20, "Ca_recovery": 0.20, "Energy_cost": 0.15, "ROI": 0.15},
                    "benchmarks": {"Li_recovery_target": 80.0, "Energy_cost_target": 0.60, "ROI_target": 5.0}
                }
            }

    def _detect_brine_type(self) -> str:
        """تشخیص خودکار نوع شورابه بر اساس نسبت عناصر، دما و TDS"""
        import streamlit as st
        
        # ۱. ابتدا بررسی حافظه اصلی برنامه برای همگام‌سازی کامل
        if 'auto_brine' in st.session_state and st.session_state['auto_brine']:
            return st.session_state['auto_brine']

        # ۲. منطق پشتیبان در صورت عدم وجود داده در session_state
        if self.df is None or self.df.empty:
            return "Seawater RO Brine"
        
        tds_col = next((c for c in self.df.columns if 'TDS' in c.upper()), None)
        li_col = next((c for c in self.df.columns if 'LI' in c.upper()), None)
        mg_col = next((c for c in self.df.columns if 'MG' in c.upper()), None)
        temp_col = next((c for c in self.df.columns if 'TEMP' in c.upper()), None)

        avg_tds = self.df[tds_col].mean() if tds_col else 85000.0
        avg_li = self.df[li_col].mean() if li_col else 150.0
        avg_mg = self.df[mg_col].mean() if mg_col else 2500.0
        avg_temp = self.df[temp_col].mean() if temp_col else 30.0
        
        mg_li_ratio = avg_mg / max(avg_li, 1e-5)

        if avg_tds < 45000.0:
            return "Seawater RO Brine"
        elif avg_temp >= 50.0 or (avg_tds > 200000.0 and mg_li_ratio < 10.0):
            return "Deep Geothermal Brine"
        elif mg_li_ratio >= 8.0 or avg_li > 80.0:
            return "High-Mg Salar Brine"
        else:
            return "Standard Brine"
    def calculate_kpis(self) -> dict:
        """محاسبه یکپارچه KPIها و امتیاز کلی وزن‌دار (با مکانیزم ضد خطا)"""
        kpis = {"brine_type": self.brine_type}
        
        if self.df is None or self.df.empty:
            return kpis

        # استخراج ایمن میانگین غلظت لیتیوم
        li_mean = self.df['Li_ppm'].mean() if 'Li_ppm' in self.df.columns else self.df.select_dtypes(include=[np.number]).iloc[:, 0].mean() if not self.df.empty else 15.0

        if self.brine_type in ["Seawater RO Brine", "Seawater_RO"]:
            kpis['Li_recovery'] = min(95.0, (li_mean / 15.0) * 85.0) if li_mean > 0 else 61.8
            kpis['Mg_recovery'] = 92.4
            kpis['Ca_recovery'] = 88.1
            kpis['Energy_cost'] = 0.54  # $/m3
            kpis['ROI'] = 5.0  # Years
        else:
            kpis['Treatment_cost'] = 1.45  # $/m3
            # FIXME: kpis['Compliance'] was hardcoded 99.2. Replace with real calculation from data.
            kpis['Li_recovery'] = min(98.0, (li_mean / 50.0) * 90.0) if li_mean > 0 else 61.8
            # FIXME: kpis['Purity'] was hardcoded 99.5. Replace with real calculation from data.

        composite_score = self._compute_composite_score(kpis)
        kpis['Composite_Score'] = composite_score

        return kpis
    def _compute_composite_score(self, kpis: dict) -> float:
        """محاسبه امتیاز جامع Salinex Index (با کنترل کامل خطاهای Key و ZeroDivision)"""
        cfg = self.weights_config.get(self.brine_type, {})
        weights = cfg.get("weights", {})
        benchmarks = cfg.get("benchmarks", {})

        if self.brine_type in ["Seawater RO Brine", "Seawater_RO"]:
            li_rec = kpis.get('Li_recovery', 60.0)
            mg_rec = kpis.get('Mg_recovery', 90.0)
            ca_rec = kpis.get('Ca_recovery', 85.0)
            energy_cost = max(kpis.get('Energy_cost', 0.54), 0.01)
            roi = max(kpis.get('ROI', 5.0), 0.1)

            s_li = min(100.0, (li_rec / max(benchmarks.get('Li_recovery_target', 90.0), 1.0)) * 100)
            s_mg = mg_rec
            s_ca = ca_rec
            s_energy = min(100.0, (benchmarks.get('Energy_cost_target', 0.50) / energy_cost) * 100)
            s_roi = min(100.0, (benchmarks.get('ROI_target', 6.0) / roi) * 100)

            score = (
                s_li * weights.get('Li_recovery', 0.35) +
                s_mg * weights.get('Mg_recovery', 0.20) +
                s_ca * weights.get('Ca_recovery', 0.15) +
                s_energy * weights.get('Energy_cost', 0.15) +
                s_roi * weights.get('ROI', 0.15)
            )
            return round(score, 1)
        else:
            treat_cost = max(kpis.get('Treatment_cost', 1.45), 0.01)
            comp = kpis.get('Compliance', 99.0)
            li_rec = kpis.get('Li_recovery', 60.0)
            pur = kpis.get('Purity', 99.0)

            s_treat = min(100.0, (benchmarks.get('Treatment_cost_target', 1.50) / treat_cost) * 100)
            s_comp = comp
            s_li = min(100.0, (li_rec / max(benchmarks.get('Li_recovery_target', 85.0), 1.0)) * 100)
            s_pur = pur

            score = (
                s_treat * weights.get('Treatment_cost', 0.30) +
                s_comp * weights.get('Compliance', 0.25) +
                s_li * weights.get('Li_recovery', 0.25) +
                s_pur * weights.get('Purity', 0.20)
            )
            return round(score, 1)
    def generate_dynamic_insights(self) -> str:
        """تولید توضیحات پویای تحلیلی (با شناسایی هوشمند ستون‌ها)"""
        if self.df is None or self.df.empty:
            return "داده‌ای برای تحلیل یافت نشد."

        mg_col = next((c for c in self.df.columns if 'MG' in c.upper()), None)
        li_col = next((c for c in self.df.columns if 'LI' in c.upper()), None)

        avg_mg = float(self.df[mg_col].mean()) if mg_col else 0.0
        avg_li = float(self.df[li_col].mean()) if li_col else 0.0
        mg_li_ratio = avg_mg / max(avg_li, 1e-5) if avg_li > 0 else 0.0

        if self.brine_type in ["Seawater RO Brine", "Seawater_RO"]:
            insight = f"💡 **تحلیل تخصصی شورابه شیرین‌سازی:** نسبت Mg/Li برابر با **{mg_li_ratio:.1f}** محاسبه گردید. "
            if mg_li_ratio > 50:
                insight += "به دلیل بالا بودن غلظت منیزیم، استفاده از **واحد پیش‌تصفیه رسوبی یا نانو‌فیلتراسیون (NF)** جهت جداسازی منیزیم پیش از DLE الزامی است."
            else:
                insight += "نسبت Mg/Li در محدوده مطلوب جهت استخراج مستقیم لیتیوم (DLE) قرار دارد."
        elif self.brine_type == "High-Mg Salar Brine":
            insight = f"💡 **تحلیل تخصصی شورابه Salar (منیزیم بالا):** میانگین غلظت لیتیوم **{avg_li:.1f} ppm** و نسبت Mg/Li برابر با **{mg_li_ratio:.1f}** ثبت شده است. "
            insight += "به دلیل غلظت بسیار بالای منیزیم، ترکیب واحد **ادسرپشن/نانوفیلتراسیون (NF)** با **کریستالیزاسیون تبخیری** جهت آزادسازی لیتیوم و دستیابی به خلوص گرید باتری پیشنهاد می‌شود."
        else:
            insight = f"💡 **تحلیل تخصصی شورابه استاندارد:** میانگین غلظت لیتیوم **{avg_li:.1f} ppm** ثبت شده است. "
            insight += "جهت دستیابی به خلوص باتری، ترکیب واحد DLE با **کریستالیزاسیون حرارتی** پیشنهاد می‌شود."

        return insight
    def generate_smart_alerts(self, kpis: dict) -> list:
        """تولید هشدارهای هوشمند با رنگ‌بندی (سبز/زرد/قرمز) و پیشنهادات اصلاحی"""
        alerts = []
        if self.df is None or self.df.empty:
            return alerts

        # استخراج هوشمند ستون‌های Mg و Li
        mg_col = next((c for c in self.df.columns if 'MG' in c.upper()), None)
        li_col = next((c for c in self.df.columns if 'LI' in c.upper()), None)

        avg_mg = float(self.df[mg_col].mean()) if mg_col else 0.0
        avg_li = float(self.df[li_col].mean()) if li_col else 0.0
        mg_li_ratio = avg_mg / max(avg_li, 1e-5) if avg_li > 0 else 0.0

        # ۱. هشدار نسبت Mg/Li
        if mg_li_ratio > 60:
            alerts.append({
                "level": "red",
                "title": "🚨 بحران نسبت Mg/Li بالا",
                "message": f"نسبت Mg/Li بحرانی است ({mg_li_ratio:.1f} > 60). احتمال گرفتگی (Fouling) شدید در جاذب‌های DLE.",
                "recommendation": "پیشنهاد اصلاحی: نرخ دوزینگ شیرآهک/کربنات را افزایش داده و مد پیش‌تصفیه رسوبی را روی حالت حداکثری قرار دهید."
            })
        elif mg_li_ratio > 40:
            alerts.append({
                "level": "yellow",
                "title": "⚠️ هشدار نسبت Mg/Li متوسط",
                "message": f"نسبت Mg/Li در محدوده هشدار قرار دارد ({mg_li_ratio:.1f}). نیاز به پایش افت فشار غشاها.",
                "recommendation": "پیشنهاد اصلاحی: سیستم نانو‌فیلتراسیون (NF) را فعال کنید تا نسبت قبل از ورود به ستون‌های جذب به زیر ۳۰ برسد."
            })
        else:
            alerts.append({
                "level": "green",
                "title": "✅ نسبت Mg/Li ایده‌آل",
                "message": f"نسبت Mg/Li مطلوب است ({mg_li_ratio:.1f} < 40). شرایط عملیاتی برای DLE بهینه می‌باشد.",
                "recommendation": "پیشنهاد اصلاحی: تنظیمات جریان ورود به DLE را در حالت نامی (Nominal Flow) حفظ کنید."
            })

        # ۲. هشدار هزینه انرژی / تصفیه
        if self.brine_type in ["Seawater RO Brine", "Seawater_RO"]:
            energy_cost = kpis.get('Energy_cost')
            if energy_cost is not None:
                if energy_cost > 0.70:
                    alerts.append({
                        "level": "red",
                        "title": "🚨 مصرف انرژی بحرانی",
                        "message": f"هزینه انرژی (${energy_cost:.2f}/m³) بیش از حد مجاز پروژه است.",
                        "recommendation": "پیشنهاد اصلاحی: راندمان بازیافت انرژی (ERD) را بررسی کرده و بازرسی توربوشارژر/PX را انجام دهید."
                    })
                elif energy_cost > 0.50:
                    alerts.append({
                        "level": "yellow",
                        "title": "⚠️ مصرف انرژی نسبتاً بالا",
                        "message": f"هزینه انرژی (${energy_cost:.2f}/m³) بالاتر از تارگت ۰.۵۰$/m³ قرار دارد.",
                        "recommendation": "پیشنهاد اصلاحی: نقطه کار پمپ‌های فشار بالا (HP Pumps) را به محدوده BEP منتقل کنید."
                    })
                else:
                    alerts.append({
                        "level": "green",
                        "title": "✅ راندمان انرژی مطلوب",
                        "message": f"هزینه انرژی (${energy_cost:.2f}/m³) در محدوده کاملاً اقتصادی است.",
                        "recommendation": "پیشنهاد اصلاحی: عملکرد فعلی ERD و پمپ‌ها تثبیت شده است."
                    })
        else:
            treat_cost = kpis.get('Treatment_cost')
            if treat_cost is not None:
                if treat_cost > 2.00:
                    alerts.append({
                        "level": "red",
                        "title": "🚨 هزینه تصفیه بالا",
                        "message": f"هزینه تصفیه (${treat_cost:.2f}/m³) بالاتر از حد اقتصادی است.",
                        "recommendation": "پیشنهاد اصلاحی: فرایند بازبازی مواد شیمیایی (Chemical Recovery) را بهینه‌سازی کنید."
                    })

        # ۳. هشدار دوره بازگشت سرمایه (ROI)
        roi = kpis.get('ROI')
        if roi is not None and roi > 0:
            if roi <= 5.0:
                alerts.append({
                    "level": "green",
                    "title": "✅ بازدهی مالی عالی (ROI)",
                    "message": f"دوره بازگشت سرمایه ({roi:.1f} سال) بسیار سریع و مطلوب است.",
                    "recommendation": "پیشنهاد اصلاحی: ظرفیت خوراک‌دهی برای افزایش سودآوری روزانه تا ۱۰٪ قابل افزایش است."
                })
            else:
                alerts.append({
                    "level": "yellow",
                    "title": "⚠️ بازدهی مالی نیازمند بهینه‌سازی",
                    "message": f"دوره بازگشت سرمایه ({roi:.1f} سال) طولانی‌تر از حد انتظار است.",
                    "recommendation": "پیشنهاد اصلاحی: استخراج محصولات جانبی (مانند MgOH2 پودری) برای تقویت جریان درآمدی توصیه می‌شود."
                })

        return alerts
    def generate_full_report_text(self, kpis: dict, alerts: list) -> str:
        """تولید خروجی متنی گزارش تحلیلی جامع جهت ذخیره‌سازی و دانلود"""
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        lines = [
            "=" * 60,
            "     گزارش جامع تحلیلی پلتفرم Salinex AI - نسخه ۳.۹.۵",
            "     سیستم: Salinex AI",
            f"     تاریخ گزارش: {report_time}",
            "=" * 60,
            "",
            "[1. مشخصات و شاخص ترکیبی]",
            f" - نوع شورابه تشخیص داده‌شده: {self.brine_type or 'نامشخص'}",
        ]
        
        comp_score = kpis.get('Composite_Score', 0)
        lines.append(f" - امتیاز جامع Salinex Index: {comp_score:.1f} / 100" if isinstance(comp_score, (int, float)) else f" - امتیاز جامع Salinex Index: {comp_score} / 100")
        lines.append("")

        lines.append("[2. KPIهای عملیاتی و مالی]")
        has_kpis = False
        for k, v in kpis.items():
            if k not in ['brine_type', 'Composite_Score']:
                has_kpis = True
                if isinstance(v, float):
                    lines.append(f" - {k}: {v:.2f}")
                else:
                    lines.append(f" - {k}: {v}")
        
        if not has_kpis:
            lines.append(" - هیچ شاخص کلیدی عملکردی ثبت نشده است.")
        lines.append("")

        lines.append("[3. تحلیل پویای فرایند]")
        insights = self.generate_dynamic_insights() if hasattr(self, 'generate_dynamic_insights') else "تحلیل پویا در دسترس نیست."
        lines.append(f" {insights}")
        lines.append("")

        lines.append("[4. هشدارهای سیستم و پیشنهادات اصلاحی]")
        if alerts:
            for idx, alt in enumerate(alerts, 1):
                lines.append(f" {idx}. {alt.get('title', 'هشدار بدون عنوان')}")
                lines.append(f"    توضیح: {alt.get('message', '-')}")
                lines.append(f"    راه‌کار: {alt.get('recommendation', '-')}")
                lines.append("")
        else:
            lines.append(" - هیچ هشداری برای این مجموعه داده ثبت نشده است.\n")

        lines.append("=" * 60)
        lines.append(" پایان گزارش - Salinex AI Adaptive Analysis Suite")
        lines.append("=" * 60)

        return "\n".join(lines)

# --- رابط کاربری صفحه تحلیل (Streamlit UI) ---
st.title("📊 سیستم تحلیل یکپارچه و علمی تطبیقی")
st.markdown("**ENGINEER:** Mirzaee | **MODULE:** Integrated Adaptive Analysis Engine")
st.divider()

# دریافت داده‌های واقعی کاربر از Session State به روش ایمن
df = st.session_state.get('df', None)

# بررسی وجود داده بارگذاری‌شده و غیرخالی بودن آن
if df is None or (isinstance(df, pd.DataFrame) and df.empty):
    st.warning("⚠️ هنوز هیچ فایل داده‌ای بارگذاری نشده است!")
    st.info("👈 لطفاً ابتدا به صفحه اصلی (**app**) بروید و فایل داده‌های شورابه (CSV) خود را بارگذاری کنید تا تحلیل تطبیقی و KPIها محاسبه شوند.")
    st.stop()  # توقف اجرای ادامه صفحه تا زمان بارگذاری فایل

# آنالیزور
analyzer = AdaptiveAnalysis(df)
kpi_data = analyzer.calculate_kpis()

# --- نمایش امتیاز کلی وزن‌دار ---
detected_brine = kpi_data.get('brine_type', 'نامشخص')
brine_name = str(detected_brine).replace('_', ' ')
st.subheader(f"🏷️ نوع شورابه: {brine_name}")

col_score, col_details = st.columns([1, 2])

with col_score:
    score = kpi_data.get('Composite_Score', 0)
    score_val = float(score) if isinstance(score, (int, float)) else 0.0
    st.metric(
        label="🎯 امتیاز جامع عملیاتی-مالی (Salinex Index)",
        value=f"{score_val:.1f} / 100",
        delta="عالی (A+)" if score_val >= 90 else ("مطلوب (B)" if score_val >= 75 else "نیازمند بهینه‌سازی")
    )

with col_details:
    st.info("⚖️ **سیستم وزن‌دهی پویا:** این امتیاز حاصل ترکیب وزن‌دار نرخ بازیابی عناصر ($Li, Mg, Ca$)، هزینه انرژی و دوره بازگشت سرمایه بر اساس استانداردهای `kpi_weights.yaml` است.")

st.divider()
# --- کارت‌های KPI ---
if detected_brine in ["Seawater RO Brine", "Seawater_RO"]:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("بازیافت لیتیوم (Li)", f"{float(kpi_data.get('Li_recovery', 0.0) or 0.0):.1f}%")
    c2.metric("بازیافت منیزیم (Mg)", f"{float(kpi_data.get('Mg_recovery', 0.0) or 0.0):.1f}%")
    c3.metric("بازیافت کلسیم (Ca)", f"{float(kpi_data.get('Ca_recovery', 0.0) or 0.0):.1f}%")
    c4.metric("هزینه انرژی", f"${float(kpi_data.get('Energy_cost', 0.0) or 0.0):.2f} /m³")
    c5.metric("دوره بازگشت سرمایه", f"{float(kpi_data.get('ROI', 0.0) or 0.0):.1f} Years")
else:
    c1, c2, c3, c4 = st.columns(4)
    cost_val = float(kpi_data.get('Treatment_cost', kpi_data.get('Energy_cost', 0.0)) or 0.0)
    c1.metric("هزینه کل", f"${cost_val:.2f} /m³")
    c2.metric("انطباق زیست‌محیطی", f"{float(kpi_data.get('Compliance', 0.0) or 0.0):.1f}%")
    c3.metric("بازیافت لیتیوم", f"{float(kpi_data.get('Li_recovery', 0.0) or 0.0):.1f}%")
    c4.metric("خلوص محصول نهایی", f"{float(kpi_data.get('Purity', 0.0) or 0.0):.1f}%")

st.divider()
# --- فراخوانی موتور پیش‌بینی هوشمند (ML Predictive Engine) ---
st.divider()
st.subheader("🤖 پیش‌بینی هوشمند و شاخص اطمینان مدل (ML Prediction Engine)")

# ۱. دریافت ایمن نوع شورابه و دمای ورودی
brine_type = kpi_data.get('brine_type', 'Seawater_RO') if 'kpi_data' in locals() and isinstance(kpi_data, dict) else 'Seawater_RO'

# دریافت ایمن دمای دستی از Session State یا متغیر محلی
manual_temp_val = st.session_state.get('manual_temp', None)
if manual_temp_val is None and 'manual_temp' in locals():
    manual_temp_val = manual_temp

# ۲. فراخوانی مدل و محاسبه پیش‌بینی با محافظت کامل در برابر خطا (Try-Except)
try:
    if 'MultiSourcePredictor' not in locals() and 'MultiSourcePredictor' not in globals():
        raise NameError("کلاس MultiSourcePredictor تعریف نشده یا ایمپورت نشده است.")
    
    predictor = MultiSourcePredictor(brine_type=brine_type)
    
    # بررسی وجود داتافریم معتبر
    safe_df = df if 'df' in locals() and isinstance(df, pd.DataFrame) else pd.DataFrame()
    pred_results = predictor.predict_recovery_and_confidence(safe_df, manual_temp=manual_temp_val)
    
    # اطمینان از اینکه خروجی حتماً دیکشنری است
    if not isinstance(pred_results, dict):
        pred_results = {'status': 'error', 'message': 'خروجی پیش‌بینی مدل نامعتبر است.'}
    elif 'status' not in pred_results:
        # اگر کلید status در خروجی نبود اما داده‌ها موجود بودند، آن را موفق در نظر می‌گیریم
        if 'recovery' in pred_results or 'confidence' in pred_results:
            pred_results['status'] = 'success'
        
except Exception as e:
    import traceback
    pred_results = {
        'status': 'error', 
        'message': f"خطا در اجرای محاسبات پیش‌بینی:لغو یا عدم تطابق داده‌ها ({str(e)})",
        'detail': traceback.format_exc()
    }

# ۳. رندر بصری کارت‌ها و وضعیت اطمینان مدل
if isinstance(pred_results, dict) and pred_results.get('status') == 'success':
    p_col1, p_col2, p_col3 = st.columns(3)
    
    # استخراج ایمن داده‌ها با پشتیبانی از نام‌گذاری‌های مختلف خروجی مدل شما
    pred_li_raw = pred_results.get('predicted_Li_recovery', pred_results.get('recovery', 0.0))
    conf_score_raw = pred_results.get('confidence_score', pred_results.get('confidence', 0.0))
    
    # تبدیل ایمن به عدد با مدیریت مقادیر رشته‌ای احتمالی یا None
    try:
        pred_li = float(pred_li_raw) if pred_li_raw is not None else 0.0
    except (ValueError, TypeError):
        pred_li = 0.0
        
    try:
        conf_score = float(conf_score_raw) if conf_score_raw is not None else 0.0
    except (ValueError, TypeError):
        conf_score = 0.0
        
    samples_cnt = pred_results.get('samples_count', len(df) if 'df' in locals() and isinstance(df, pd.DataFrame) else 1)
    
    used_temp = pred_results.get('used_temperature', pred_results.get('temperature', 25.0))
    temp_src = pred_results.get('temp_source', 'پیش‌فرض سیستم')
    
    p_col1.metric(
        label="🎯 درصد بازیافت پیش‌بینی‌شده (Predicted Li Recovery)",
        value=f"{pred_li:.1f}%",
        delta="برآورد مدل ML"
    )
    
    p_col2.metric(
        label="🛡️ شاخص اطمینان مدل (Confidence Score)",
        value=f"{conf_score:.1f}%",
        delta="بسیار بالا" if conf_score >= 85 else "متوسط"
    )
    
    p_col3.metric(
        label="📊 تعداد نمونه‌های پردازش‌شده",
        value=f"{samples_cnt} داده"
    )
    
    st.write("**میزان پایداری و دقت داده‌ها برای مدلسازی:**")
    # اطمینان از قرارگیری عدد بین ۰ تا ۱۰۰ جهت جلوگیری از خطای progress
    progress_val = max(0, min(100, int(conf_score)))
    st.progress(progress_val)
    
    # هشدار عدم قطعیتی دما
    if pred_results.get("is_temp_assumed"):
        st.warning(f"⚠️ **اطلاعیه عدم قطعیتی:** ستون دما در فایل CSV یافت نشد. محاسبات بر اساس {temp_src} انجام شده و ۵٪ از شاخص اطمینان مدل کسر گردید.")
    else:
        st.info(f"🌡️ دمای مبنای محاسبات: {used_temp}°C ({temp_src})")

else:
    err_msg = pred_results.get('message', 'خطا در اجرای محاسبات پیش‌بینی') if isinstance(pred_results, dict) else 'خطای ناشناخته در خروجی مدل'
    st.error(f"⚠️ {err_msg}")
    
    if isinstance(pred_results, dict):
        if 'detail' in pred_results:
            with st.expander("🔍 جزئیات فنی خطای سیستمی"):
                st.code(pred_results['detail'], language="python")

st.divider()
# --- سیستم هشدارهای هوشمند KPI ---
st.subheader("🛡️ سیستم هشدارهای هوشمند و پیشنهادات اصلاحی (KPI Smart Alerts)")

# فراخوانی ایمن هشدارهای تحلیل‌گر
alerts = []
if 'analyzer' in locals() and hasattr(analyzer, 'generate_smart_alerts'):
    alerts = analyzer.generate_smart_alerts(kpi_data if 'kpi_data' in locals() and isinstance(kpi_data, dict) else {})

# نمایش کارت‌های هشدار در ستون‌های مجزا با چیدمان ایمن
if alerts:
    # جلوگیری از شکستگی UI در صورت زیاد بودن تعداد هشدارها (حداکثر ۴ ستون در هر ردیف)
    num_cols = min(len(alerts), 4)
    alert_cols = st.columns(num_cols)
    for idx, alert in enumerate(alerts):
        with alert_cols[idx % num_cols]:
            if alert.get('level') == 'red':
                st.error(f"**{alert.get('title', 'هشدار')}**\n\n{alert.get('message', '')}\n\n🛠️ *{alert.get('recommendation', '')}*")
            elif alert.get('level') == 'yellow':
                st.warning(f"**{alert.get('title', 'هشدار')}**\n\n{alert.get('message', '')}\n\n🛠️ *{alert.get('recommendation', '')}*")
            else:
                st.success(f"**{alert.get('title', 'اطلاعیه')}**\n\n{alert.get('message', '')}\n\n🛠️ *{alert.get('recommendation', '')}*")
else:
    st.info("✅ هیچ هشدار بحرانی یا انحرافی در شاخص‌های KPI ثبت نشده است.")

st.divider()
# --- نمودار وزن‌ها ---
st.subheader("⚙️ سهم وزن هر KPI در ارزیابی نهایی")

# دریافت وزن‌ها با پشتیبانی از تمامی انواع شورابه
brine_t = kpi_data.get('brine_type', '') if 'kpi_data' in locals() and isinstance(kpi_data, dict) else ''

# دسترسی ایمن به weights_config
weights_cfg_dict = getattr(analyzer, 'weights_config', {}) if 'analyzer' in locals() else {}
cfg_weights = weights_cfg_dict.get(brine_t, {}).get('weights', {}) if isinstance(weights_cfg_dict, dict) else {}

if not cfg_weights:
    if brine_t in ["Seawater RO Brine", "Seawater_RO"]:
        cfg_weights = {"Li_recovery": 0.35, "Mg_recovery": 0.20, "Ca_recovery": 0.15, "Energy_cost": 0.15, "ROI": 0.15}
    elif brine_t == "High-Mg Salar Brine":
        cfg_weights = {"Treatment_cost": 0.30, "Compliance": 0.25, "Li_recovery": 0.25, "Purity": 0.20}
    else:
        cfg_weights = {"Treatment_cost": 0.30, "Compliance": 0.25, "Li_recovery": 0.25, "Purity": 0.20}

# رسم ایمن نمودار دونات Plotly
try:
    import plotly.graph_objects as go
    fig_weights = go.Figure(data=[
        go.Pie(labels=list(cfg_weights.keys()), values=list(cfg_weights.values()), hole=.4)
    ])
    fig_weights.update_layout(template="plotly_dark", height=380, title="توزیع وزن شاخص‌های کلیدی (YAML Config)")
    st.plotly_chart(fig_weights, use_container_width=True)
except Exception as e:
    st.error(f"⚠️ خطای غیرمنتظره در رسم نمودار وزن‌ها: {str(e)}")

st.divider()
# --- تجسم‌سازی هوشمند و نمودارهای تطبیقی ---
st.subheader("📈 تجسم‌سازی هوشمند و تحلیل بصری (Visual Analytics)")

# کنترل حالت نمایش نمودار
col_mode, _ = st.columns([1, 2])
with col_mode:
    chart_mode = st.radio(
        "انتخاب حالت نمایش نمودار:",
        ["حالت ساده (Simple)", "حالت پیشرفته (Advanced)"],
        horizontal=True
    )

col_chart, col_insight = st.columns([2, 1])

with col_chart:
    if 'df' in locals() and isinstance(df, pd.DataFrame) and not df.empty:
        # نگاشت هوشمند ستون‌ها برای تطبیق با نام‌های مختلف احتمالی در فایل CSV
        cols_lower = {str(c).lower(): c for c in df.columns}
        
        target_mapping = {
            'Li_ppm': cols_lower.get('li_ppm') or cols_lower.get('li') or cols_lower.get('lithium'),
            'Mg_ppm': cols_lower.get('mg_ppm') or cols_lower.get('mg') or cols_lower.get('magnesium'),
            'Ca_ppm': cols_lower.get('ca_ppm') or cols_lower.get('ca') or cols_lower.get('calcium'),
            'TDS_ppm': cols_lower.get('tds_ppm') or cols_lower.get('tds')
        }
        
        # استخراج نام ستون‌های واقعی موجود در داتافریم
        elements_map = {k: v for k, v in target_mapping.items() if v is not None}
        elements = list(elements_map.keys())
    else:
        elements_map = {}
        elements = []

    if not elements:
        st.warning("⚠️ ستون‌های غلظت عناصر (Li_ppm, Mg_ppm, Ca_ppm, TDS_ppm) در فایل بارگذاری‌شده یافت نشدند.")
    else:
        try:
            import plotly.express as px
            import plotly.graph_objects as go
            
            if "ساده" in chart_mode:
                # نمودار ساده: میانگین غلظت عناصر اصلی با استفاده از ستون‌های نگاشت‌شده
                means_data = {k: df[v].mean() for k, v in elements_map.items()}
                avg_vals = pd.DataFrame(list(means_data.items()), columns=['Element', 'Mean_ppm'])

                fig_bar = px.bar(
                    avg_vals,
                    x='Element',
                    y='Mean_ppm',
                    text_auto='.1f',
                    color='Element',
                    title="نمودار ساده: میانگین غلظت عناصر (ppm)",
                    template="plotly_dark"
                )
                fig_bar.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)

            else:
                # نمودار پیشرفته: روند و نوسانات غلظت در نمونه‌ها
                fig_line = go.Figure()
                for el_key, col_name in elements_map.items():
                    if el_key in ['Li_ppm', 'Mg_ppm', 'Ca_ppm']:
                        fig_line.add_trace(go.Scatter(
                            y=df[col_name],
                            mode='lines+markers',
                            name=el_key,
                            line=dict(width=2)
                        ))

                fig_line.update_layout(
                    title="نمودار پیشرفته: روند نوسانات آنی غلظت عناصر در نمونه‌ها",
                    xaxis_title="شماره نمونه / سری زمانی",
                    yaxis_title="غلظت (ppm)",
                    template="plotly_dark",
                    height=400
                )
                st.plotly_chart(fig_line, use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ خطای غیرمنتظره در رسم نمودارهای بصری: {str(e)}")

with col_insight:
    st.markdown("### 💬 توضیحات پویای تحلیلی")
    dynamic_text = "اطلاعات تحلیلی در دسترس نیست."
    if 'analyzer' in locals() and hasattr(analyzer, 'generate_dynamic_insights'):
        try:
            dynamic_text = analyzer.generate_dynamic_insights()
        except Exception as e:
            dynamic_text = f"خطا در تولید تحلیل پویا: {str(e)}"
            
    st.success(dynamic_text)
    st.caption("📌 **راهنما:** رندر نمودارها متناسب با نوع شورابه ورودی به‌روزرسانی می‌شود.")

st.divider()

# --- بخش جدید روز پنجم: سیستم گزارش‌دهی تحلیلی یکپارچه ---
st.subheader("📄 دانلود گزارش تحلیلی یکپارچه (Integrated Analysis Report)")

col_rep_text, col_rep_btn = st.columns([2, 1])

with col_rep_text:
    st.write("گزارش جامع شامل تمامی محاسبات، هشدارهای فعال، شاخص Salinex Index و راه‌کارهای مهندسی آماده دریافت می‌باشد.")

with col_rep_btn:
    # ایمپورت ایمن datetime جهت جلوگیری از خطای NameError
    try:
        from datetime import datetime
        time_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    except Exception:
        import time
        time_str = time.strftime('%Y%m%d_%H%M%S')

    # استخراج ایمن محتوای گزارش
    report_content = "گزارشی تولید نشد."
    if 'analyzer' in locals() and hasattr(analyzer, 'generate_full_report_text'):
        try:
            safe_kpi = kpi_data if 'kpi_data' in locals() and isinstance(kpi_data, dict) else {}
            safe_alerts = alerts if 'alerts' in locals() and isinstance(alerts, list) else []
            report_content = analyzer.generate_full_report_text(safe_kpi, safe_alerts)
        except Exception as e:
            report_content = f"خطا در تولید گزارش جامع: {str(e)}"

    st.download_button(
        label="📥 دانلود گزارش تحلیلی (.txt)",
        data=report_content,
        file_name=f"Salinex_Analysis_Report_{time_str}.txt",
        mime="text/plain",
        use_container_width=True
    )