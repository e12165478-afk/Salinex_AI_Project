# decision_engine.py - موتور تصمیم‌یار مستقل Salinex AI

def generate_prescriptive_advice(li_ppm, mg_ppm, ca_ppm, elec_price, current_flow, profit, roi_years):
    """
    تحلیل پارامترهای فنی و مالی و ارائه توصیه‌های هوشمند عملیاتی به اپراتور
    """
    advice_list = []
    
    # ۱. تحلیل نسبت منیزیم به لیتیوم
    mg_li_ratio = mg_ppm / li_ppm if li_ppm > 0 else 0
    if mg_li_ratio > 10:
        advice_list.append(
            f"💡 **توصیه استخراج چندماده‌ای:** غلظت منیزیم ({round(mg_ppm,1)} ppm) بسیار بالاتر از لیتیوم است. "
            f"پیشنهاد می‌شود مد پیش‌تصفیه رسوبی فعال بماند تا سود حاصل از فروش منیزیم حفظ شود."
        )
    
    # ۲. تحلیل نرخ بازگشت سرمایه (بازگشت سرمایه)
    if roi_years > 5.0:
        suggested_flow = round(current_flow * (roi_years / 5.0), 0)
        advice_list.append(
            f"⚠️ **بهینه‌سازی بازگشت سرمایه:** نرخ بازگشت سرمایه فعلی ({round(roi_years,1)} سال) بالاتر از تارگت ۵ ساله است. "
            f"توصیه هوشمند: دبی ورودی (Flow Rate) را به حدود **{suggested_flow} m3/hr** افزایش دهید تا بازگشت سرمایه زیر ۵ سال بیاید."
        )
    else:
        advice_list.append(
            f"✅ **وضعیت مطلوب مالی:** نرخ بازگشت سرمایه ({round(roi_years,1)} سال) در محدوده بسیار عالی قرار دارد."
        )
        
    # ۳. تحلیل ریسک انرژی
    if elec_price > 0.15:
        advice_list.append(
            f"⚡ **مدیریت هزینه برق:** قیمت برق بالا است ({elec_price} $/kWh). "
            f"اطمینان حاصل کنید که بازیابی انرژی (ERD) فعال باشد تا ۳۵٪ صرفه‌جویی ثبت شود."
        )
        
    return advice_list


def classify_brine_source(tds, li_ppm, mg_ppm, ca_ppm):
    """
    تشخیص هوشمند گروه و منبع شورابه ورودی بر اساس نسبت‌های شیمیایی یون‌ها
    """
    mg_li_ratio = mg_ppm / li_ppm if li_ppm > 0 else 0
    
    if li_ppm > 50 and mg_li_ratio < 20:
        return "🏔️ سالار / منابع طبیعی لیتیوم‌دار (Salar Brine)"
    elif ca_ppm > 2000 or tds > 100000:
        return "🏭 پساب صنعتی / پتروشیمی (Industrial Effluent)"
    elif mg_li_ratio >= 20:
        return "🌊 شورابه شیرین‌سازی آب دریا (Seawater RO Brine)"
    else:
        return "💧 شورابه معدنی / نامشخص (Standard Brine)"