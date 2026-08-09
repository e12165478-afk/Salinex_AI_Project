import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# تنظیمات صفحه و استایل اختصاصی
# ==============================================================================
st.set_page_config(
    page_title="Salinex AI - Local Economic Calculator",
    page_icon="💰",
    layout="wide"
)

# ==============================================================================
# کلاس موتور محاسباتی اقتصادی تطبیقی (Adaptive EconomicCalculator)
# ==============================================================================
class AdaptiveEconomicCalculator:
    def __init__(self, brine_type):
        self.brine_type = brine_type

    def calculate_economics(self, flow_rate, recovery_pct, li_ppm, elec_price, chemical_cost_base, li_price, ca_ppm=0, mg_ppm=0):
        """
        محاسبه OPEX، درآمد و ROI بر اساس نوع شورابه و پارامترهای عملیاتی
        """
        # فرض بر این است که هر مترمکعب شورابه معادل مشخصی انرژی مصرف می‌کند (با فرض میانگین فشار عملیاتی)
        # برای آب‌شیرین‌کن‌ها تمرکز روی انرژی است، برای شورابه‌های High-Mg تمرکز روی مواد شیمیایی پیش‌تصفیه و رسوب‌زدایی است
        specific_energy_kwh = 4.68 if "Seawater" in self.brine_type else 3.85
        
        # ۱. محاسبه هزینه‌های عملیاتی متغیر (OPEX - $/m³)
        energy_opex_unit = specific_energy_kwh * elec_price
        
        # ضریب تعدیل مواد شیمیایی بر اساس نوع شورابه (شورابه‌های حاوی منیزیم بالا نیاز به اسید/باز و رسوب‌زدایی بیشتری دارند)
        if "High-Mg" in self.brine_type:
            chemical_opex_unit = chemical_cost_base * (1.0 + (mg_ppm / 5000.0) if mg_ppm > 0 else 1.5)
        else:
            chemical_opex_unit = chemical_cost_base * 0.8
            
        membrane_replacement_unit = 0.35  # هزینه ثابت استهلاک غشاها و تجهیزات
        
        total_opex_m3 = energy_opex_unit + chemical_opex_unit + membrane_replacement_unit
        
        # ۲. محاسبه درآمد ناخالص (Revenue - $/m³)
        # تبدیل ppm به ton در m^3
        li_tons_per_m3 = (li_ppm * (recovery_pct / 100.0)) / 1_000_000.0
        li_revenue_m3 = li_tons_per_m3 * li_price
        
        # ارزش‌افزوده محصول جانبی (مانند منیزیم در شورابه‌های High-Mg)
        byproduct_revenue_m3 = 2.40 if "High-Mg" in self.brine_type else 0.80
        
        total_revenue_m3 = li_revenue_m3 + byproduct_revenue_m3
        
        # ۳. محاسبه سود کل روزانه و سالانه
        hourly_net = (total_revenue_m3 - total_opex_m3) * flow_rate
        daily_profit = hourly_net * 24.0
        annual_profit = daily_profit * 350.0  # ۳۵۰ روز کاری در سال
        
        return {
            "energy_unit": energy_opex_unit,
            "chem_unit": chemical_opex_unit,
            "total_opex_m3": total_opex_m3,
            "total_revenue_m3": total_revenue_m3,
            "daily_profit": daily_profit,
            "annual_profit": annual_profit,
            "specific_energy": specific_energy_kwh
        }

# ==============================================================================
# رندر رابط کاربری صفحه اقتصادی
# ==============================================================================
def render_economics_page():
    st.title("💰 Local Economic Calculator & ROI Analysis")
    st.markdown("##### Industrial Decision Support: Cost Optimization, OPEX Breakdown & Revenue Estimation")
    st.markdown("---")

    # ۱. بازیابی داده‌ها از حافظه مشترک سشن (متصل به app.py)
    active_df = st.session_state.get('df', None)
    
    if active_df is None or active_df.empty:
        st.warning("⚠️ هیچ فایل شورابه‌ای در حافظه سیستم یافت نشد.")
        st.info("💡 لطفاً ابتدا از طریق صفحه اصلی (`app.py`) فایل CSV داده‌های شورابه را بارگذاری کنید تا محاسبات اقتصادی بر اساس آن انجام شود.")
        return

    # ۲. تشخیص پویا یا بازیابی نوع شورابه
    detected_brine = st.session_state.get('auto_brine', 'High-Mg Salar Brine')
    
    # استخراج میانگین پارامترها از فایل فعال
    li_avg = active_df['Li_ppm'].mean() if 'Li_ppm' in active_df.columns else 450.0
    mg_avg = active_df['Mg_ppm'].mean() if 'Mg_ppm' in active_df.columns else 1200.0
    ca_avg = active_df['Ca_ppm'].mean() if 'Ca_ppm' in active_df.columns else 400.0
    
    # دبی جریان پیش‌فرض یا دریافتی
    flow_rate = st.session_state.get('f_rate', 100.0)
    for col in active_df.columns:
        if 'flow' in col.lower() or 'دبی' in col:
            try:
                flow_rate = float(active_df[col].mean())
                break
            except:
                pass

    # ۳. نمایش هدر وضعیت هماهنگ فرآیند
    st.markdown("### 📊 وضعیت پایه فرآیند (متصل به موتور مرکزی Salinex)")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("شورابه فعال (منطبق با App)", detected_brine)
    with col2:
        st.metric("دبی جریان متوسط", f"{flow_rate:.1f} m³/h")
    with col3:
        st.metric("حجم دیتابیس فعال", f"{len(active_df):,} ردیف")
    with col4:
        st.metric("وضعیت همگام‌سازی", "✅ متصل و فعال")

    st.markdown("---")

    # ۴. تنظیم عوامل و تعرفه‌های محلی (Regional Economic Factors)
    st.markdown("### 🎛️ تنظیم عوامل و تعرفه‌های محلی (Regional Economic Factors)")
    
    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        elec_price = st.number_input("⚡ قیمت برق ($/kWh)", min_value=0.01, max_value=0.50, value=0.12, step=0.01, help="تعرفه محلی انرژی الکتریکی جهت پمپاژ و تجهیزات")
    with col_in2:
        chem_cost_base = st.number_input("🧪 هزینه پایه مواد پیش‌تصفیه ($/m³)", min_value=0.0, max_value=2.0, value=0.15, step=0.01, help="هزینه مواد تنظیم pH و ضد رسوب")
    with col_in3:
        li_market_price = st.number_input("💎 ارزش فروش معادل لیتیوم ($/ton Li-Eq)", min_value=5000.0, max_value=50000.0, value=22000.0, step=500.0, help="قیمت بازار جهانی/منطقه‌ای لیتیوم")

    st.markdown("---")

    # ۵. اجرای محاسبات اقتصادی تطبیقی
    calculator = AdaptiveEconomicCalculator(brine_type=detected_brine)
    econ_results = calculator.calculate_economics(
        flow_rate=flow_rate,
        recovery_pct=76.7, # درصد بازیابی پیش‌فرض یا مدل
        li_ppm=li_avg,
        elec_price=elec_price,
        chemical_cost_base=chem_cost_base,
        li_price=li_market_price,
        ca_ppm=ca_avg,
        mg_ppm=mg_avg
    )

    # ۶. نمایش داشبورد تحلیل مالی و OPEX
    st.markdown("### 📈 نتایج تحلیل اقتصادی لحظه‌ای و تفکیک هزینه‌ها")
    
    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
    with col_res1:
        st.metric("هزینه عملیاتی کل (OPEX)", f"${econ_results['total_opex_m3']:.2f} /m³")
    with col_res2:
        st.metric("درآمد ناخالص (Revenue)", f"${econ_results['total_revenue_m3']:.2f} /m³")
    with col_res3:
        st.metric("سود خالص روزانه", f"${econ_results['daily_profit']:,.0f}")
    with col_res4:
        st.metric("سود خالص سالانه", f"${econ_results['annual_profit']:,.0f}")

    # تفکیک استراتژیک بر اساس نوع شورابه (منطبق با درخواست شما)
    st.markdown("---")
    st.markdown("### 🔍 تحلیل ساختاری هزینه‌ها بر اساس نوع شورابه")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if "High-Mg" in detected_brine:
            st.info("🔹 **تحلیل تمرکز هزینه‌ای (High-Mg Salar Brine):** به دلیل غلظت بالای منیزیم در این شورابه، بیشترین وزن هزینه‌ای روی **مواد شیمیایی پیش‌تصفیه و حوضچه‌های رسوب‌زدایی** قرار دارد. ارزش‌افزوده استخراج منیزیم به عنوان محصول جانبی، بخشی از هزینه‌ها را جبران می‌کند.")
        else:
            st.info("🔹 **تحلیل تمرکز هزینه‌ای (Seawater RO Brine):** تمرکز اصلی هزینه‌ها در این پساب روی **مصرف انرژی الکتریکی پمپ‌های فشارقوی** است و سیستم‌های بازیابی انرژی (ERD) نقش کلیدی در کاهش OPEX دارند.")
    
    with col_s2:
        st.write(f"- **سهم هزینه انرژی:** `${econ_results['energy_unit']:.2f} /m³`")
        st.write(f"- **سهم هزینه مواد شیمیایی:** `${econ_results['chem_unit']:.2f} /m³`")
        st.write(f"- **مصرف ویژه انرژی:** `{econ_results['specific_energy']:.2f} kWh/m³`")

    st.markdown("---")
    st.success("✅ صفحه اقتصادی با موفقیت و به صورت کاملاً پویا به داده‌های زنده پلتفرم و فایل آپلودشده متصل شد.")

if __name__ == "__main__":
    render_economics_page()