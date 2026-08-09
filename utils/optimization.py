import numpy as np
try:
    from scipy.optimize import minimize
except ImportError:
    minimize = None

class AdaptiveMultiObjectiveOptimizer:
    """
    موتور بهینه‌سازی چندهدفه تطبیقی برای پلتفرم Salinex AI
    وظیفه: یافتن نقطه کارکرد بهینه و تحلیل مرز پارتو (Pareto Front)
    """
    def __init__(self, brine_type="Seawater_RO", weights=None):
        self.brine_type = brine_type
        self.weights = weights if weights is not None else {
            'recovery_weight': 0.6,
            'energy_weight': 0.4
        }
        
    def _check_constraints(self, flow, ph, est_cost):
        """
        بررسی محدودیت‌های فرآیندی و اعمال جریمه (Penalty) برای نقاط خطرناک
        """
        penalty = 0.0
        
        # ۱. محدودیت سقف هزینه (حداکثر 2.0 دلار)
        max_cost = 2.0
        if est_cost > max_cost:
            penalty += (est_cost - max_cost) * 2.0
            
        # ۲. محدودیت خطر رسوب منیزیم (pH بالا در شورابه منیزیم‌دار)
        if self.brine_type == "High-Mg Salar Brine" and ph > 7.2:
            penalty += (ph - 7.2) * 1.5
            
        # ۳. محدودیت خطر خفگی غشا (دبی بیش از حد مجاز)
        max_flow = 850.0
        if flow > max_flow:
            penalty += ((flow - max_flow) / 100.0) * 0.5
            
        return penalty

    def _find_pareto_frontier(self, evaluated_points):
        """
        تشخیص و استخراج نقاط مرز پارتو (Pareto Front) از بین تمام نقاط ارزیابی‌شده
        منطق: نقطه‌ای پارتو است که هیچ نقطه دیگری هم‌زمان هم بازیافت بیشتر و هم هزینه کمتر نداشته باشد.
        """
        pareto_points = []
        
        for p1 in evaluated_points:
            is_dominated = False
            for p2 in evaluated_points:
                # اگر p2 در هر دو معیار (بازیافت بالاتر و هزینه کمتر یا مساوی) از p1 بهتر بود، یعنی p1 مغلوب شده است
                if (p2['predicted_recovery'] >= p1['predicted_recovery'] and p2['estimated_cost'] <= p1['estimated_cost']) and \
                   (p2['predicted_recovery'] > p1['predicted_recovery'] or p2['estimated_cost'] < p1['estimated_cost']):
                    is_dominated = True
                    break
            if not is_dominated:
                pareto_points.append(p1)
                
        # مرتب‌سازی نقاط پارتو بر اساس هزینه صعودی
        pareto_points = sorted(pareto_points, key=lambda x: x['estimated_cost'])
        return pareto_points

    def optimize(self, current_data=None, manual_temp=25.0):
        """
        متد اصلی برای اجرای بهینه‌سازی چندهدفه، اعمال محدودیت‌ها و استخراج مرز پارتو
        """
        try:
            best_score = -999.0
            best_params = {
                'optimal_flow_rate': 720.0,
                'optimal_ph': 6.5,
                'predicted_recovery': 58.5,
                'estimated_cost': 1.25
            }
            
            all_evaluated_points = []
            
            flow_range = np.linspace(500.0, 900.0, 15)
            ph_range = np.linspace(5.5, 8.0, 10)
            
            w_rec = self.weights.get('recovery_weight', 0.6)
            w_cost = self.weights.get('energy_weight', 0.4)
            
            for flow in flow_range:
                for ph in ph_range:
                    if self.brine_type == "High-Mg Salar Brine":
                        est_recovery = min(75.0, 45.0 + (flow / 100.0) * 1.5 - abs(ph - 6.5) * 3.0)
                        est_cost = 1.0 + (flow / 500.0) * 0.4 + abs(ph - 7.0) * 0.05
                    else:
                        est_recovery = min(80.0, 50.0 + (flow / 120.0) * 1.2 - abs(ph - 7.0) * 2.0)
                        est_cost = 0.8 + (flow / 600.0) * 0.3
                    
                    penalty = self._check_constraints(flow, ph, est_cost)
                    
                    norm_rec = est_recovery / 100.0
                    norm_cost = max(0.0, 1.0 - (est_cost / 2.5))
                    
                    total_score = (w_rec * norm_rec) + (w_cost * norm_cost) - penalty
                    
                    point_data = {
                        'optimal_flow_rate': float(flow),
                        'optimal_ph': float(ph),
                        'predicted_recovery': float(est_recovery),
                        'estimated_cost': float(est_cost),
                        'score': float(total_score)
                    }
                    
                    all_evaluated_points.append(point_data)
                    
                    if total_score > best_score:
                        best_score = total_score
                        best_params = point_data
            
            # استخراج مرز پارتو از میان کل نقاط ارزیابی‌شده
            pareto_front = self._find_pareto_frontier(all_evaluated_points)
            
            optimized_results = {
                'status': 'success',
                'optimal_flow_rate': round(best_params['optimal_flow_rate'], 1),
                'optimal_ph': round(best_params['optimal_ph'], 2),
                'predicted_recovery': round(best_params['predicted_recovery'], 1),
                'estimated_cost': round(best_params['estimated_cost'], 2),
                'pareto_front': pareto_front, # لیست نقاط مرز پارتو برای تحلیل‌های پیشرفته
                'message': 'بهینه‌سازی چندهدفه، اعمال محدودیت‌ها و تحلیل پارتو با موفقیت انجام شد.'
            }
            return optimized_results
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"خطا در محاسبات بهینه‌سازی: {str(e)}"
            }