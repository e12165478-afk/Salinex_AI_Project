"""
Salinex AI - Adaptive Scenario Manager Module
SYSTEM: Salinex AI v3.9.5
"""

class AdaptiveScenarioManager:
    def __init__(self, brine_type="High-Mg Salar Brine"):
        self.brine_type = brine_type

    def get_scenarios(self):
        """
        بازگرداندن سناریوهای متناسب با نوع شورابه ورودی
        """
        scenarios = {}

        if "Salar" in self.brine_type:
            scenarios = {
                "سناریوی ۱: حداکثر خلوص (Pre-Treatment Focus)": {
                    "description": "فعال‌سازی مد نانوفیلتراسیون (NF) جهت کاهش نسبت Mg/Li به زیر ۳۰ و جلوگیری از خفه شدن ستون جذب.",
                    "target_ph": 6.4,
                    "recommended_flow": 680.0,
                    "erd_active": False,
                    "expected_recovery_boost": "+15%",
                    "energy_impact": "متوسط (+0.12 kWh/m³)"
                },
                "سناریوی ۲: حداکثر بازیافت لیتیوم (Aggressive Li Extraction)": {
                    "description": "افزایش دبی و دما برای استخراج بیشترین میزان لیتیوم ممکن بدون توجه به مصرف انرژی.",
                    "target_ph": 5.8,
                    "recommended_flow": 850.0,
                    "erd_active": False,
                    "expected_recovery_boost": "+22%",
                    "energy_impact": "بالا (+0.35 kWh/m³)"
                },
                "سناریوی ۳: تولید چندماده‌ای (Li + Mg Co-Recovery)": {
                    "description": "حفظ غلظت منیزیم جهت استخراج هم‌زمان و تولید محصول جانبی منیزیم با سودآوری بالا.",
                    "target_ph": 7.2,
                    "recommended_flow": 720.0,
                    "erd_active": True,
                    "expected_recovery_boost": "+10%",
                    "energy_impact": "بهینه (-0.05 kWh/m³)"
                }
            }
        elif "Seawater" in self.brine_type or "RO" in self.brine_type:
            scenarios = {
                "سناریوی ۱: کاهش مصرف انرژی (Energy Efficiency - BEP)": {
                    "description": "تنظیم نقطه‌کار پمپ‌ها در محدوده BEP به همراه فعال‌سازی ERD جهت حداقل‌سازی هزینه برق.",
                    "target_ph": 6.8,
                    "recommended_flow": 950.0,
                    "erd_active": True,
                    "expected_recovery_boost": "+8%",
                    "energy_impact": "حداقل (-0.45 kWh/m³)"
                },
                "سناریوی ۲: دبی حداکثری (High-Throughput RO)": {
                    "description": "پردازش حداکثر حجم پساب ورودی جهت افزایش سود کل روزانه پروژه.",
                    "target_ph": 6.5,
                    "recommended_flow": 1200.0,
                    "erd_active": True,
                    "expected_recovery_boost": "+12%",
                    "energy_impact": "متوسط (+0.18 kWh/m³)"
                }
            }
        else:
            # سناریوهای عمومی برای سایر شورابه‌ها
            scenarios = {
                "سناریوی ۱: استاندارد عملیاتی (Balanced Baseline)": {
                    "description": "تنظیمات متعادل فرآیندی جهت حفظ نرخ بازیافت و پایداری تجهیزات.",
                    "target_ph": 6.5,
                    "recommended_flow": 750.0,
                    "erd_active": True,
                    "expected_recovery_boost": "+5%",
                    "energy_impact": "نرمال"
                }
            }

        return scenarios