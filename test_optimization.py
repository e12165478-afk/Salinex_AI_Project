from utils.optimization import AdaptiveMultiObjectiveOptimizer

def run_test():
    print("--- در حال تست ماژول بهینه‌سازی چندهدفه ---")
    
    # ۱. تست برای شورابه منیزیم بالا (High-Mg Salar Brine)
    print("\n[تست ۱] شورابه نوع: High-Mg Salar Brine")
    optimizer_salar = AdaptiveMultiObjectiveOptimizer(
        brine_type="High-Mg Salar Brine", 
        weights={'recovery_weight': 0.7, 'energy_weight': 0.3}
    )
    result_salar = optimizer_salar.optimize()
    print("نتیجه بهینه‌سازی Salar:", result_salar)
    
    # بررسی وجود مرز پارتو در خروجی
    if 'pareto_front' in result_salar:
        print(f"تعداد نقاط پارتو استخراج‌شده: {len(result_salar['pareto_front'])}")

    # ۲. تست برای شورابه اسمز معکوس (Seawater RO)
    print("\n[تست ۲] شورابه نوع: Seawater_RO")
    optimizer_ro = AdaptiveMultiObjectiveOptimizer(
        brine_type="Seawater_RO", 
        weights={'recovery_weight': 0.5, 'energy_weight': 0.5}
    )
    result_ro = optimizer_ro.optimize()
    print("نتیجه بهینه‌سازی RO:", result_ro)

if __name__ == "__main__":
    run_test()