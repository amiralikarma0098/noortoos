import json
from datetime import datetime
from .database import execute_query

class AnalysisModel:
    """مدل تحلیل‌های عمومی CRM"""
    
    @staticmethod
    def save(file_info, analysis_data):
        """ذخیره تحلیل جدید با مدیریت خطا"""
        
        # اطمینان از دیکشنری بودن analysis_data
        if not isinstance(analysis_data, dict):
            analysis_data = {}
        
        # استخراج داده‌ها با مدیریت خطا
        nums = analysis_data.get('فیلدهای_عددی', {})
        if not isinstance(nums, dict):
            nums = {}
            
        text = analysis_data.get('فیلدهای_متنی', {})
        if not isinstance(text, dict):
            text = {}
            
        lists = analysis_data.get('لیست_ها', {})
        if not isinstance(lists, dict):
            lists = {}
            
        stats = analysis_data.get('آمار', {})
        if not isinstance(stats, dict):
            stats = {}
            
        best = analysis_data.get('بهترین_ها', {})
        if not isinstance(best, dict):
            best = {}
        
        # مهم: بررسی و تبدیل دلایل کاهش امتیازها
        reasons_dec = analysis_data.get('دلایل_کاهش_امتیازها', {})
        if not isinstance(reasons_dec, dict):
            # اگه لیست بود، تبدیل به دیکشنری کن
            if isinstance(reasons_dec, list):
                new_dict = {}
                for item in reasons_dec:
                    if isinstance(item, dict):
                        new_dict.update(item)
                reasons_dec = new_dict
            else:
                reasons_dec = {}
        
        # بررسی و تبدیل دلایل کسب امتیازها
        reasons_inc = analysis_data.get('دلایل_کسب_امتیازها', {})
        if not isinstance(reasons_inc, dict):
            if isinstance(reasons_inc, list):
                new_dict = {}
                for item in reasons_inc:
                    if isinstance(item, dict):
                        new_dict.update(item)
                reasons_inc = new_dict
            else:
                reasons_inc = {}
        
        # حالا با خیال راحت از get استفاده کن
        query = """
        INSERT INTO analyses (
            file_name, file_path, file_size, file_type, analyzed_at,
            score_total, score_rapport, score_needs, score_value, 
            score_objection, score_price, score_closing, score_followup,
            score_empathy, score_listening,
            lead_quality_percent, open_questions_count, objections_count,
            objection_success_percent, closing_attempts_count, customer_feeling_score,
            closing_readiness_percent, seller_technical_density_percent,
            customer_technical_density_percent, customer_price_sensitivity_percent,
            customer_risk_sensitivity_percent, customer_time_sensitivity_percent,
            yes_ladder_count,
            disc_d, disc_i, disc_s, disc_c,
            seller_name, seller_code, customer_name, call_duration,
            call_direction, call_stage, call_warmth, call_nature,
            product, seller_level, disc_type, disc_evidence, disc_interaction_guide,
            preferred_channel, customer_awareness_level,
            customer_talk_ratio, seller_talk_ratio,
            summary, customer_personality_analysis, seller_individual_performance,
            call_type_readiness, next_action,
            rapport_decrease_reasons, needs_decrease_reasons, value_decrease_reasons,
            objection_decrease_reasons, price_decrease_reasons, closing_decrease_reasons,
            followup_decrease_reasons, empathy_decrease_reasons, listening_decrease_reasons,
            rapport_increase_reasons, needs_increase_reasons, value_increase_reasons,
            objection_increase_reasons, price_increase_reasons, closing_increase_reasons,
            followup_increase_reasons, empathy_increase_reasons, listening_increase_reasons,
            total_calls, successful_calls, no_answer_calls, referred_calls,
            best_seller, best_seller_reason, best_customer, best_customer_reason,
            full_analysis
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s
        )
        """
        
        # استخراج مقادیر با مدیریت خطا
        values = (
            file_info.get('name', ''), 
            file_info.get('path', ''), 
            file_info.get('size', 0), 
            file_info.get('type', ''),
            datetime.now(),
            nums.get('امتیاز_کل', 0),
            nums.get('امتیاز_برقراری_ارتباط', 0),
            nums.get('امتیاز_نیازسنجی', 0),
            nums.get('امتیاز_ارزش_فروشی', 0),
            nums.get('امتیاز_مدیریت_اعتراض', 0),
            nums.get('امتیاز_شفافیت_قیمت', 0),
            nums.get('امتیاز_بستن_فروش', 0),
            nums.get('امتیاز_پیگیری', 0),
            nums.get('امتیاز_همسویی_احساسی', 0),
            nums.get('امتیاز_شنوندگی', 0),
            nums.get('کیفیت_لید_درصد', 0),
            nums.get('تعداد_سوالات_باز', 0),
            nums.get('تعداد_اعتراض', 0),
            nums.get('درصد_پاسخ_موفق_به_اعتراض', 0),
            nums.get('تعداد_تلاش_برای_بستن', 0),
            nums.get('امتیاز_احساس_مشتری', 0),
            nums.get('آمادگی_بستن_درصد', 0),
            nums.get('چگالی_اطلاعات_فنی_فروشنده_درصد', 0),
            nums.get('چگالی_اطلاعات_فنی_مشتری_درصد', 0),
            nums.get('حساسیت_قیمت_مشتری_درصد', 0),
            nums.get('حساسیت_ریسک_مشتری_درصد', 0),
            nums.get('حساسیت_زمان_مشتری_درصد', 0),
            nums.get('تعداد_بله_پله_ای', 0),
            nums.get('disc_d', 0),
            nums.get('disc_i', 0),
            nums.get('disc_s', 0),
            nums.get('disc_c', 0),
            text.get('نام_فروشنده'),
            text.get('کد_فروشنده'),
            text.get('نام_مشتری'),
            text.get('مدت_تماس'),
            text.get('نوع_تماس_جهت'),
            text.get('نوع_تماس_مرحله'),
            text.get('نوع_تماس_گرمی'),
            text.get('نوع_تماس_ماهیت'),
            text.get('محصول'),
            text.get('سطح_فروشنده'),
            text.get('disc_تیپ'),
            json.dumps(text.get('disc_شواهد', []), ensure_ascii=False),
            text.get('disc_راهنما'),
            text.get('ترجیح_کانال'),
            text.get('سطح_آگاهی_مشتری'),
            text.get('نسبت_زمان_صحبت_مشتری_به_فروشنده'),
            text.get('نسبت_زمان_صحبت_فروشنده_به_مشتری'),
            text.get('خلاصه'),
            text.get('تحلیل_شخصیت_مشتری'),
            text.get('ارزیابی_عملکرد_فردی_فروشنده'),
            text.get('تشخیص_آمادگی'),
            text.get('اقدام_بعدی'),
            json.dumps(reasons_dec.get('برقراری_ارتباط', []), ensure_ascii=False),
            json.dumps(reasons_dec.get('نیازسنجی', []), ensure_ascii=False),
            json.dumps(reasons_dec.get('ارزش_فروشی', []), ensure_ascii=False),
            json.dumps(reasons_dec.get('مدیریت_اعتراض', []), ensure_ascii=False),
            json.dumps(reasons_dec.get('شفافیت_قیمت', []), ensure_ascii=False),
            json.dumps(reasons_dec.get('بستن_فروش', []), ensure_ascii=False),
            json.dumps(reasons_dec.get('پیگیری', []), ensure_ascii=False),
            json.dumps(reasons_dec.get('همسویی_احساسی', []), ensure_ascii=False),
            json.dumps(reasons_dec.get('شنوندگی', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('برقراری_ارتباط', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('نیازسنجی', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('ارزش_فروشی', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('مدیریت_اعتراض', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('شفافیت_قیمت', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('بستن_فروش', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('پیگیری', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('همسویی_احساسی', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('شنوندگی', []), ensure_ascii=False),
            stats.get('تعداد_کل_تماس_ها', 0),
            stats.get('تماس_های_موفق', 0),
            stats.get('تماس_های_بی_پاسخ', 0),
            stats.get('تماس_های_ارجاعی', 0),
            best.get('بهترین_فروشنده', {}).get('نام') if isinstance(best.get('بهترین_فروشنده'), dict) else best.get('بهترین_فروشنده'),
            best.get('بهترین_فروشنده', {}).get('دلیل') if isinstance(best.get('بهترین_فروشنده'), dict) else '',
            best.get('بهترین_مشتری', {}).get('نام') if isinstance(best.get('بهترین_مشتری'), dict) else best.get('بهترین_مشتری'),
            best.get('بهترین_مشتری', {}).get('دلیل') if isinstance(best.get('بهترین_مشتری'), dict) else '',
            json.dumps(analysis_data, ensure_ascii=False)
        )
        
        analysis_id = execute_query(query, values, commit=True)
        
        # ذخیره جزئیات اضافی
        if analysis_id:
            AnalysisModel._save_details(analysis_id, stats, lists)
        
        return analysis_id
    
    @staticmethod
    def _save_details(analysis_id, stats, lists):
        """ذخیره جزئیات در جداول مرتبط"""
        # اطمینان از دیکشنری بودن
        if not isinstance(stats, dict):
            stats = {}
        if not isinstance(lists, dict):
            lists = {}
        
        # ذخیره کاربران فعال
        users = stats.get('کاربران_فعال', [])
        if isinstance(users, list):
            for user in users:
                if isinstance(user, dict):
                    execute_query(
                        "INSERT INTO active_users (analysis_id, user_name, call_count, performance_note) VALUES (%s, %s, %s, %s)",
                        (analysis_id, user.get('نام'), user.get('تعداد_تماس', 1), user.get('یادداشت_عملکرد')),
                        commit=True
                    )
        
        # ذخیره مشتریان پرتماس
        customers = stats.get('مشتریان_پرتماس', [])
        if isinstance(customers, list):
            for customer in customers:
                if isinstance(customer, dict):
                    execute_query(
                        "INSERT INTO top_customers (analysis_id, customer_name, contact_count, interaction_quality) VALUES (%s, %s, %s, %s)",
                        (analysis_id, customer.get('نام'), customer.get('تعداد_تماس', 1), customer.get('کیفیت_تعامل')),
                        commit=True
                    )
        
        # ذخیره لیست‌ها
        list_mappings = [
            ('نقاط_قوت', 'strengths', 'strength'),
            ('نقاط_ضعف', 'weaknesses', 'weakness'),
            ('اعتراضات', 'objections', 'objection'),
            ('تکنیکها', 'techniques', 'technique'),
            ('کلمات_مثبت', 'positive_keywords', 'keyword'),
            ('کلمات_منفی', 'negative_keywords', 'keyword'),
            ('ریسک_ها', 'risks', 'risk'),
            ('پارامترهای_رعایت_نشده', 'missed_parameters', 'parameter'),
            ('اشتباهات_رایج', 'common_mistakes', 'mistake')
        ]
        
        for list_key, table, field in list_mappings:
            items = lists.get(list_key, [])
            if isinstance(items, list):
                for item in items:
                    if item:  # فقط اگه خالی نباشه
                        execute_query(
                            f"INSERT INTO {table} (analysis_id, {field}) VALUES (%s, %s)",
                            (analysis_id, item),
                            commit=True
                        )
    
    @staticmethod
    def get_all():
        """دریافت لیست تمام تحلیل‌ها"""
        query = """
        SELECT 
            id, file_name, analyzed_at,
            score_total, seller_name, customer_name, product,
            total_calls, successful_calls
        FROM analyses
        ORDER BY analyzed_at DESC
        """
        return execute_query(query, fetch_all=True)
    
    @staticmethod
    def get_by_id(analysis_id):
        """دریافت یک تحلیل با ID"""
        query = "SELECT * FROM analyses WHERE id = %s"
        return execute_query(query, (analysis_id,), fetch_one=True)
    
    @staticmethod
    def get_latest():
        """دریافت آخرین تحلیل"""
        query = """
        SELECT 
            id, file_name, analyzed_at, full_analysis
        FROM analyses 
        ORDER BY analyzed_at DESC 
        LIMIT 1
        """
        return execute_query(query, fetch_one=True)


class ReferralAnalysisModel:
    """مدل تحلیل‌های ارجاعیات"""
    
    @staticmethod
    def save(file_info, analysis_data):
        """ذخیره تحلیل ارجاعیات"""
        
        # اطمینان از دیکشنری بودن
        if not isinstance(analysis_data, dict):
            analysis_data = {}
        
        # استخراج داده‌ها
        status = analysis_data.get('status_analysis', {})
        if not isinstance(status, dict):
            status = {}
            
        dist = status.get('status_distribution', {})
        if not isinstance(dist, dict):
            dist = {}
        
        total = sum(dist.values()) if isinstance(dist, dict) else 0
        completed = dist.get('اتمام کار', 0)
        pending = dist.get('بررسی نشده', 0)
        in_progress = dist.get('درحال پیگیری', 0)
        seen = dist.get('رویت شده', 0)
        accepted = dist.get('قبول ارجاع', 0)
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        pending_rate = (pending / total * 100) if total > 0 else 0
        
        query = """
        INSERT INTO referral_analyses (
            file_name, file_path, file_size, analyzed_at,
            total_referrals, completed_count, pending_count,
            in_progress_count, seen_count, accepted_count,
            completion_rate, pending_rate, full_analysis
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            file_info.get('name', ''), 
            file_info.get('path', ''), 
            file_info.get('size', 0), 
            datetime.now(),
            total, completed, pending, in_progress, seen, accepted,
            completion_rate, pending_rate,
            json.dumps(analysis_data, ensure_ascii=False)
        )
        
        return execute_query(query, values, commit=True)
    
    @staticmethod
    def get_all():
        """دریافت لیست تحلیل‌های ارجاعیات"""
        query = """
        SELECT 
            id, file_name, analyzed_at,
            total_referrals, completed_count, pending_count,
            completion_rate
        FROM referral_analyses
        ORDER BY analyzed_at DESC
        """
        return execute_query(query, fetch_all=True)
    
    @staticmethod
    def get_by_id(analysis_id):
        """دریافت یک تحلیل ارجاعیات با ID"""
        query = "SELECT * FROM referral_analyses WHERE id = %s"
        return execute_query(query, (analysis_id,), fetch_one=True)
    
    @staticmethod
    def get_latest():
        """دریافت آخرین تحلیل ارجاعیات"""
        query = """
        SELECT id, file_name, analyzed_at, full_analysis
        FROM referral_analyses 
        ORDER BY analyzed_at DESC 
        LIMIT 1
        """
        return execute_query(query, fetch_one=True)