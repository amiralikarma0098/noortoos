from openai import OpenAI
import json
from .config import Config

class OpenAIClient:
    """کلاینت OpenAI برای تحلیل‌های مختلف"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
    
    def analyze_crm(self, content):
        """تحلیل فایل CRM عمومی با پرامپت کامل"""
        prompt = self._build_crm_prompt(content)
        return self._call_api(prompt, "CRM analyst")
    
    def analyze_referral(self, content):
        """تحلیل فایل ارجاعیات"""
        prompt = self._build_referral_prompt(content)
        return self._call_api(prompt, "workflow analyst specializing in Persian CRM data")
    
    def _call_api(self, prompt, system_message):
        """فراخوانی API با مدیریت خطا"""
        try:
            print(f"📤 ارسال به OpenAI...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are a {system_message}. Return ONLY valid JSON with no markdown or explanation."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=8000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            print(f"✅ دریافت پاسخ - طول: {len(response_text)} کاراکتر")
            
            # حذف markdown اگر وجود داشت
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip() == '```json' or line.strip() == '```':
                        in_json = not in_json
                        continue
                    if in_json or (line.strip().startswith('{') or json_lines):
                        json_lines.append(line)
                response_text = '\n'.join(json_lines).strip()
            
            # Parse JSON
            analysis = json.loads(response_text)
            
            print(f"✅ JSON پارس شد")
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"❌ خطا در JSON: {str(e)}")
            print(f"📄 متن مشکل‌دار (500 کاراکتر اول): {response_text[:500]}")
            return {
                "error": True,
                "message": "خطا در پردازش پاسخ هوش مصنوعی"
            }
        except Exception as e:
            print(f"❌ خطا در فراخوانی API: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "error": True,
                "message": str(e)
            }
    
    def _build_crm_prompt(self, content):
        """ساخت پرامپت کامل برای تحلیل CRM - نسخه اصلی"""
        
        print(f"\n{'='*50}")
        print(f"📊 طول محتوا: {len(content)} کاراکتر")
        print(f"{'='*50}\n")
        
        prompt = f"""این گزارش CRM است. تحلیل کن و **فقط JSON برگردون** (بدون توضیح).

**ستون‌ها:**
ردیف | اشتراک | نام | نام موسسه | تلفن | کاربر | ثبت | نوع | وضعیت

**متن:**
{content}

**برای خلاصه:**
- بگو چند تماس انجام شده (موفق، بی‌پاسخ)
- چه کارشناسانی فعال بودن
- برترین مشتریان کدومن
- محصولات اصلی چی بودن
- نقاط قوت و ضعف

**مثال خلاصه:**
"گزارش شامل 150 تماس: 90 موفق (60%) و 30 بی‌پاسخ. کارشناس 'پایان' با 40 تماس برترین بود. مشتریان کلیدی: اداره کل دادگستری و تابلوفرمان پار. محصولات: APC، UPS، دوربین. نقاط قوت: پیگیری منظم و خدمات تعمیراتی. نقاط ضعف: تماس‌های بی‌پاسخ."

{{
  "فیلدهای_عددی": {{
    "امتیاز_کل": 7,
    "امتیاز_برقراری_ارتباط": 7,
    "امتیاز_نیازسنجی": 6,
    "امتیاز_ارزش_فروشی": 5,
    "امتیاز_مدیریت_اعتراض": 5,
    "امتیاز_شفافیت_قیمت": 6,
    "امتیاز_بستن_فروش": 5,
    "امتیاز_پیگیری": 8,
    "امتیاز_همسویی_احساسی": 6,
    "امتیاز_شنوندگی": 7,
    "کیفیت_لید_درصد": 70,
    "تعداد_سوالات_باز": 0,
    "تعداد_اعتراض": 5,
    "درصد_پاسخ_موفق_به_اعتراض": 60,
    "تعداد_تلاش_برای_بستن": 10,
    "امتیاز_احساس_مشتری": 6,
    "آمادگی_بستن_درصد": 50,
    "چگالی_اطلاعات_فنی_فروشنده_درصد": 75,
    "چگالی_اطلاعات_فنی_مشتری_درصد": 60,
    "disc_d": 6,
    "disc_i": 7,
    "disc_s": 6,
    "disc_c": 5,
    "حساسیت_قیمت_مشتری_درصد": 65,
    "حساسیت_ریسک_مشتری_درصد": 55,
    "حساسیت_زمان_مشتری_درصد": 60,
    "تعداد_بله_پله_ای": 3
  }},
  "فیلدهای_متنی": {{
    "نام_فروشنده": "پایان، کارگر، حسینی",
    "کد_فروشنده": "",
    "نام_مشتری": "اداره کل دادگستری مشهد، تابلوفرمان پار",
    "مدت_تماس": "",
    "نوع_تماس_جهت": "خروجی",
    "نوع_تماس_مرحله": "پشتیبانی و فروش",
    "نوع_تماس_گرمی": "متوسط",
    "نوع_تماس_ماهیت": "پشتیبانی و فروش",
    "محصول": "APC، UPS، دوربین، سانترال",
    "سطح_فروشنده": "متوسط",
    "disc_تیپ": "I",
    "disc_شواهد": ["تعامل زیاد", "پیگیری مستمر"],
    "disc_راهنما": "تعامل مستمر و پیگیری",
    "ترجیح_کانال": "تلفن",
    "سطح_آگاهی_مشتری": "متوسط",
    "نسبت_زمان_صحبت_مشتری_به_فروشنده": "40:60",
    "نسبت_زمان_صحبت_فروشنده_به_مشتری": "60:40",
    "خلاصه": "خلاصه کامل مطابق مثال - با اعداد و جزئیات",
    "تحلیل_شخصیت_مشتری": "مشتریان سازمانی و دولتی با نیاز به پشتیبانی مستمر",
    "ارزیابی_عملکرد_فردی_فروشنده": "تیم فعال با پیگیری منظم",
    "تشخیص_آمادگی": "آمادگی متوسط برای خرید",
    "اقدام_بعدی": "پیگیری تماس‌های بی‌پاسخ و بستن فروش‌ها"
  }},
  "دلایل_کاهش_امتیازها": {{
    "برقراری_ارتباط": ["تماس‌های بی‌پاسخ"],
    "نیازسنجی": ["عدم شناسایی کامل نیاز"],
    "ارزش_فروشی": ["عدم توضیح کامل ارزش"],
    "مدیریت_اعتراض": ["برخی اعتراضات بدون پاسخ"],
    "شفافیت_قیمت": ["تاخیر در ارسال قیمت"],
    "بستن_فروش": ["عدم بستن فروش‌های آماده"],
    "پیگیری": ["ختم زودهنگام"],
    "همسویی_احساسی": [],
    "شنوندگی": []
  }},
  "دلایل_کسب_امتیازها": {{
    "برقراری_ارتباط": ["تماس‌های منظم"],
    "نیازسنجی": ["شناسایی نیازهای فنی"],
    "ارزش_فروشی": ["ارائه محصولات متنوع"],
    "مدیریت_اعتراض": ["رسیدگی به مشکلات"],
    "شفافیت_قیمت": ["ارائه قیمت"],
    "بستن_فروش": ["فاکتورهای موفق"],
    "پیگیری": ["Reminder منظم"],
    "همسویی_احساسی": ["رفتار محترمانه"],
    "شنوندگی": ["توجه به نیازها"]
  }},
  "لیست_ها": {{
    "کلمات_مثبت": ["تایید", "موفق", "انجام شد", "قبول"],
    "کلمات_منفی": ["بی‌پاسخ", "خاتمه", "مشکل", "تاخیر"],
    "ریسک_ها": ["از دست دادن مشتری", "تاخیر در پاسخ"],
    "نقاط_قوت": ["پیگیری منظم", "تنوع خدمات", "تعمیرات فعال"],
    "نقاط_ضعف": ["تماس‌های بی‌پاسخ", "ختم زودهنگام"],
    "اعتراضات": ["تاخیر در پاسخ", "مشکل در تحویل"],
    "تکنیکها": ["Reminder", "ارجاع به حسابداری", "پیگیری تلفنی"],
    "پارامترهای_رعایت_نشده": ["زمان پاسخ"],
    "اشتباهات_رایج": ["عدم پاسخ به موقع"]
  }},
  "آمار": {{
    "تعداد_کل_تماس_ها": 150,
    "تماس_های_موفق": 90,
    "تماس_های_بی_پاسخ": 30,
    "تماس_های_ارجاعی": 20,
    "کاربران_فعال": [
      {{"نام": "پایان", "تعداد_تماس": 40, "یادداشت_عملکرد": "برترین کارشناس"}},
      {{"نام": "فنی-اداری1", "تعداد_تماس": 25, "یادداشت_عملکرد": "خوب"}},
      {{"نام": "حسینی", "تعداد_تماس": 20, "یادداشت_عملکرد": "فعال"}},
      {{"نام": "کارگر", "تعداد_تماس": 15, "یادداشت_عملکرد": "خوب"}},
      {{"نام": "رسولی", "تعداد_تماس": 10, "یادداشت_عملکرد": "متوسط"}}
    ],
    "مشتریان_پرتماس": [
      {{"نام": "اداره کل دادگستری مشهد", "تعداد_تماس": 12, "کیفیت_تعامل": "عالی"}},
      {{"نام": "تابلوفرمان پار", "تعداد_تماس": 8, "کیفیت_تعامل": "خوب"}},
      {{"نام": "شرکت گاز", "تعداد_تماس": 6, "کیفیت_تعامل": "متوسط"}}
    ],
    "انواع_تماس": {{
      "پایان": 50,
      "Reminder": 40,
      "Erja": 20,
      "تعمیرات": 30,
      "Repair": 10
    }}
  }},
  "بهترین_ها": {{
    "بهترین_فروشنده": {{
      "نام": "پایان",
      "دلیل": "40 تماس با نرخ موفقیت بالا"
    }},
    "بهترین_مشتری": {{
      "نام": "اداره کل دادگستری مشهد",
      "دلیل": "12 تماس با کیفیت عالی"
    }}
  }}
}}"""

        return prompt
    
    def _build_referral_prompt(self, content):
        """ساخت پرامپت برای تحلیل ارجاعیات"""
        return f"""You are a workflow analyst. Analyze this referral/excel data and return ONLY JSON with the analysis.

**Input Data:**
{content[:15000]}

**COMPLETE ANALYSIS QUESTIONS:**

1. STATUS ANALYSIS (وضعیت ارجاعیات):
   - What percentage of referrals are in "بررسی نشده" status?
   - Which status has the highest frequency?
   - Average time in "بررسی نشده" status?
   - Which sender unit has most "بررسی نشده" referrals?
   - Percentage of "اتمام کار" referrals vs total?
   - Which receiver has most "درحال پیگیری" referrals?
   - What is the distribution of all statuses?
   - Which status has the lowest frequency?
   - How many referrals are in "قبول ارجاع" status?

2. TEMPORAL ANALYSIS (تحلیل زمانی):
   - Which date had most referrals?
   - Average days between registration and due date?
   - Which day was busiest?
   - Percentage of overdue referrals still pending?
   - What is the hourly distribution of referrals?
   - What is the trend between dates?
   - Which time of day has most referrals?

3. SUBJECT ANALYSIS (تحلیل موضوعی):
   - Most frequent subject/topic?
   - Which subject has most "بررسی نشده"?
   - Average response time per subject?
   - Which subjects go to "تعمیرات" most?
   - Subjects with no descriptions?
   - Second most frequent subject?
   - Which subject has highest completion rate?
   - Which subject has lowest completion rate?
   - List all unique subjects with counts

4. SENDER/RECEIVER ANALYSIS:
   - Top sender by volume?
   - Top receiver by volume?
   - Most common sender-receiver pair?
   - Which receiver has most pending?
   - Which sender has least descriptions?
   - Second top sender?
   - Second top receiver?
   - Which unit collaborates with most others?
   - Sender with highest completion rate?
   - Receiver with highest completion rate?

5. INSTITUTION ANALYSIS:
   - Top institutions by referral count?
   - Most common subject for top institutions?
   - Do higher subscription numbers mean more referrals?
   - Institutions with no descriptions?
   - Which institution has most pending?
   - Which institution has highest completion rate?
   - List all institutions with their subscription codes
   - Correlation between subscription and completion?

6. DESCRIPTION ANALYSIS:
   - Percentage with descriptions?
   - Average description length?
   - Which units write most descriptions?
   - Status of referrals without descriptions?
   - Top keywords in descriptions (like باتری, فاکتور, etc.)?
   - List all unique keywords with frequencies
   - Which keywords correlate with completion?
   - Longest description length?

7. TRACKING ANALYSIS:
   - Which tracking numbers had multiple referrals?
   - Average follow-ups per tracking?
   - Maximum follow-ups for a single tracking?
   - Tracking numbers with most status changes?

8. SUBSCRIPTION ANALYSIS:
   - Highest subscription number?
   - Correlation between subscription and referral count?
   - Average subscription for completed referrals?
   - Average subscription for pending referrals?

9. COMPREHENSIVE INSIGHTS:
   - What factors lead to "اتمام کار"?
   - Which units collaborate most?
   - Do longer descriptions lead to faster completion?
   - Recurring patterns in referrals?
   - What are the top 3 bottlenecks?
   - What are the top 3 strengths?
   - What are the top 3 risks?
   - Overall health score of the workflow (0-100)?
   - Summary in Persian (minimum 3 sentences)
   - Top 5 recommendations in Persian (as an array)

Return JSON with this exact structure:
{{
  "status_analysis": {{
    "percent_pending": 25.5,
    "most_frequent_status": "بررسی نشده",
    "frequent_status_count": 7,
    "avg_days_pending": 2.3,
    "worst_sender_pending": {{"unit": "تعمیرات", "count": 3}},
    "percent_completed": 45.8,
    "receiver_with_most_in_progress": {{"receiver": "امور خدمات", "count": 2}},
    "status_distribution": {{
      "بررسی نشده": 7,
      "رویت شده": 3,
      "درحال پیگیری": 2,
      "اتمام کار": 12,
      "قبول ارجاع": 1
    }},
    "status_with_lowest_frequency": "قبول ارجاع",
    "lowest_frequency_count": 1
  }},
  
  "subject_analysis": {{
    "most_frequent_subject": "فاکتور شود و تحویل",
    "subject_frequency": 6,
    "second_most_frequent": "خرید باتری",
    "second_frequency": 3,
    "subject_pending": {{
      "فاکتور شود و تحویل": 2,
      "خرید باتری": 1,
      "اعزام کارشناس": 1
    }},
    "subject_response_time": {{
      "فاکتور شود و تحویل": 1.2,
      "خرید باتری": 2.1,
      "اعزام کارشناس": 3.5
    }},
    "unique_subjects": [
      {{"subject": "فاکتور شود و تحویل", "count": 6}},
      {{"subject": "خرید باتری", "count": 3}},
      {{"subject": "اعزام کارشناس", "count": 2}}
    ]
  }},
  
  "sender_receiver_analysis": {{
    "top_senders": [
      {{"sender": "تعمیرات", "count": 7, "completion_rate": 57.1}},
      {{"sender": "پورحسین", "count": 5, "completion_rate": 80.0}},
      {{"sender": "رسولی", "count": 3, "completion_rate": 66.7}}
    ],
    "top_receivers": [
      {{"receiver": "امور خدمات", "count": 8, "pending": 5}},
      {{"receiver": "کمک-حسابدار1", "count": 6, "pending": 1}},
      {{"receiver": "پورحسین", "count": 5, "pending": 1}}
    ],
    "common_pairs": [
      {{"from": "تعمیرات", "to": "امور خدمات", "count": 3}},
      {{"from": "پورحسین", "to": "کمک-حسابدار1", "count": 2}},
      {{"from": "رسولی", "to": "امور خدمات", "count": 2}}
    ]
  }},
  
  "institution_analysis": {{
    "top_institutions": [
      {{"name": "سیمان بجنورد", "count": 3, "subs": 28, "completion_rate": 100}},
      {{"name": "بیمارستان نهم دی تربت حیدریه", "count": 3, "subs": 92, "completion_rate": 100}},
      {{"name": "موقوفات ملک", "count": 3, "subs": 184, "completion_rate": 0}}
    ],
    "subscription_correlation": 0.3
  }},
  
  "description_analysis": {{
    "percent_with_description": 65.4,
    "avg_description_length": 45.2,
    "top_keywords": [
      {{"word": "باتری", "count": 6, "completion_rate": 50.0}},
      {{"word": "فاکتور", "count": 5, "completion_rate": 80.0}},
      {{"word": "تحویل", "count": 4, "completion_rate": 75.0}}
    ]
  }},
  
  "comprehensive_insights": {{
    "completion_factors": [
      "توضیحات کامل",
      "ارجاع مستقیم به واحد مناسب",
      "پیگیری منظم"
    ],
    "top_bottlenecks": [
      {{"bottleneck": "واحد امور خدمات", "pending_count": 5, "impact": "بالا"}},
      {{"bottleneck": "واحد تعمیرات", "pending_count": 3, "impact": "متوسط"}}
    ],
    "top_strengths": [
      "پیگیری منظم توسط پورحسین",
      "سرعت عمل در فاکتور"
    ],
    "workflow_health_score": 68.5,
    "summary_fa": "از مجموع ۲۷ ارجاع، ۱۲ مورد به اتمام رسیده (۴۴٪) و ۷ مورد بررسی نشده (۲۶٪). گلوگاه اصلی در واحد امور خدمات با ۸ ارجاع دریافتی و ۵ مورد مانده است.",
    "recommendations_fa": [
      "پیگیری فوری ارجاعات معطل‌مانده در امور خدمات (۵ مورد)",
      "تماس با جایگاه سوخت کوه سفید و عذرخواهی + اعزام کارشناس",
      "ثبت توضیحات کامل‌تر برای ارجاعات (۳۵٪ بدون توضیح هستند)",
      "بهبود هماهنگی بین تعمیرات و امور خدمات",
      "برگزاری جلسه هماهنگی برای رسیدگی به درخواست‌های تکراری"
    ]
  }}
}}"""