from flask import Flask, render_template, request, jsonify, send_file
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from striprtf.striprtf import rtf_to_text
import pdfplumber
from docx import Document
import openpyxl
import mysql.connector
from mysql.connector import Error
import shutil

# بارگذاری متغیرهای محیطی
load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['UPLOAD_FOLDER'] = 'uploaded_files'



# تنظیم OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# تنظیمات MySQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'crm_analyzer'),
    'charset': 'utf8mb4'
}

def get_db_connection():
    """اتصال به دیتابیس"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"❌ خطا در اتصال به دیتابیس: {e}")
        return None

def save_analysis_to_db(file_info, analysis_data):
    """ذخیره تحلیل کامل در دیتابیس"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # استخراج داده‌ها
        nums = analysis_data.get('فیلدهای_عددی', {})
        text = analysis_data.get('فیلدهای_متنی', {})
        lists = analysis_data.get('لیست_ها', {})
        stats = analysis_data.get('آمار', {})
        best = analysis_data.get('بهترین_ها', {})
        reasons_dec = analysis_data.get('دلایل_کاهش_امتیازها', {})
        reasons_inc = analysis_data.get('دلایل_کسب_امتیازها', {})
        
        # Insert تحلیل اصلی
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
        
        values = (
            # فایل
            file_info['name'], file_info['path'], file_info['size'], file_info['type'],
            datetime.now(),
            # امتیازها
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
            # فیلدهای عددی اضافی
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
            # DISC
            nums.get('disc_d', 0),
            nums.get('disc_i', 0),
            nums.get('disc_s', 0),
            nums.get('disc_c', 0),
            # اطلاعات متنی
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
            # دلایل کاهش
            json.dumps(reasons_dec.get('برقراری_ارتباط', []), ensure_ascii=False),
            json.dumps(reasons_dec.get('نیازسنجی', []), ensure_ascii=False),
            json.dumps(reasons_dec.get('ارزش_فروشی', []), ensure_ascii=False),
            json.dumps(reasons_dec.get('مدیریت_اعتراض', []), ensure_ascii=False),
            json.dumps(reasons_dec.get('شفافیت_قیمت', []), ensure_ascii=False),
            json.dumps(reasons_dec.get('بستن_فروش', []), ensure_ascii=False),
            json.dumps(reasons_dec.get('پیگیری', []), ensure_ascii=False),
            json.dumps(reasons_dec.get('همسویی_احساسی', []), ensure_ascii=False),
            json.dumps(reasons_dec.get('شنوندگی', []), ensure_ascii=False),
            # دلایل کسب
            json.dumps(reasons_inc.get('برقراری_ارتباط', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('نیازسنجی', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('ارزش_فروشی', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('مدیریت_اعتراض', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('شفافیت_قیمت', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('بستن_فروش', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('پیگیری', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('همسویی_احساسی', []), ensure_ascii=False),
            json.dumps(reasons_inc.get('شنوندگی', []), ensure_ascii=False),
            # آمار
            stats.get('تعداد_کل_تماس_ها', 0),
            stats.get('تماس_های_موفق', 0),
            stats.get('تماس_های_بی_پاسخ', 0),
            stats.get('تماس_های_ارجاعی', 0),
            # بهترین‌ها
            best.get('بهترین_فروشنده', {}).get('نام'),
            best.get('بهترین_فروشنده', {}).get('دلیل'),
            best.get('بهترین_مشتری', {}).get('نام'),
            best.get('بهترین_مشتری', {}).get('دلیل'),
            # JSON کامل
            json.dumps(analysis_data, ensure_ascii=False)
        )
        
        cursor.execute(query, values)
        analysis_id = cursor.lastrowid
        
        # ذخیره کاربران فعال
        users = stats.get('کاربران_فعال', [])
        for user in users:
            if isinstance(user, dict):
                cursor.execute(
                    "INSERT INTO active_users (analysis_id, user_name, call_count, performance_note) VALUES (%s, %s, %s, %s)",
                    (analysis_id, user.get('نام'), user.get('تعداد_تماس', 1), user.get('یادداشت_عملکرد'))
                )
            else:
                cursor.execute(
                    "INSERT INTO active_users (analysis_id, user_name) VALUES (%s, %s)",
                    (analysis_id, user)
                )
        
        # ذخیره مشتریان
        customers = stats.get('مشتریان_پرتماس', [])
        for customer in customers:
            if isinstance(customer, dict):
                cursor.execute(
                    "INSERT INTO top_customers (analysis_id, customer_name, contact_count, interaction_quality) VALUES (%s, %s, %s, %s)",
                    (analysis_id, customer.get('نام'), customer.get('تعداد_تماس', 1), customer.get('کیفیت_تعامل'))
                )
            else:
                cursor.execute(
                    "INSERT INTO top_customers (analysis_id, customer_name) VALUES (%s, %s)",
                    (analysis_id, customer)
                )
        
        # ذخیره نقاط قوت
        for strength in lists.get('نقاط_قوت', []):
            cursor.execute(
                "INSERT INTO strengths (analysis_id, strength) VALUES (%s, %s)",
                (analysis_id, strength)
            )
        
        # ذخیره نقاط ضعف
        for weakness in lists.get('نقاط_ضعف', []):
            cursor.execute(
                "INSERT INTO weaknesses (analysis_id, weakness) VALUES (%s, %s)",
                (analysis_id, weakness)
            )
        
        # ذخیره اعتراضات
        for objection in lists.get('اعتراضات', []):
            cursor.execute(
                "INSERT INTO objections (analysis_id, objection) VALUES (%s, %s)",
                (analysis_id, objection)
            )
        
        # ذخیره تکنیک‌ها
        for technique in lists.get('تکنیکها', []):
            cursor.execute(
                "INSERT INTO techniques (analysis_id, technique) VALUES (%s, %s)",
                (analysis_id, technique)
            )
        
        # ذخیره کلمات مثبت
        for keyword in lists.get('کلمات_مثبت', []):
            cursor.execute(
                "INSERT INTO positive_keywords (analysis_id, keyword) VALUES (%s, %s)",
                (analysis_id, keyword)
            )
        
        # ذخیره کلمات منفی
        for keyword in lists.get('کلمات_منفی', []):
            cursor.execute(
                "INSERT INTO negative_keywords (analysis_id, keyword) VALUES (%s, %s)",
                (analysis_id, keyword)
            )
        
        # ذخیره ریسک‌ها
        for risk in lists.get('ریسک_ها', []):
            cursor.execute(
                "INSERT INTO risks (analysis_id, risk) VALUES (%s, %s)",
                (analysis_id, risk)
            )
        
        # ذخیره پارامترهای رعایت نشده
        for param in lists.get('پارامترهای_رعایت_نشده', []):
            cursor.execute(
                "INSERT INTO missed_parameters (analysis_id, parameter) VALUES (%s, %s)",
                (analysis_id, param)
            )
        
        # ذخیره اشتباهات
        for mistake in lists.get('اشتباهات_رایج', []):
            cursor.execute(
                "INSERT INTO common_mistakes (analysis_id, mistake) VALUES (%s, %s)",
                (analysis_id, mistake)
            )
        
        conn.commit()
        print(f"✅ تحلیل با ID {analysis_id} ذخیره شد")
        return analysis_id
        
    except Error as e:
        print(f"❌ خطا در ذخیره: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def get_all_analyses():
    """دریافت لیست تمام تحلیل‌ها"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT 
            id, file_name, created_at, analyzed_at,
            score_total, seller_name, customer_name, product,
            total_calls, successful_calls
        FROM analyses
        ORDER BY created_at DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        # تبدیل datetime به string
        for row in results:
            row['created_at'] = row['created_at'].isoformat() if row['created_at'] else None
            row['analyzed_at'] = row['analyzed_at'].isoformat() if row['analyzed_at'] else None
        
        return results
    except Error as e:
        print(f"❌ خطا در دریافت لیست: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_analysis_by_id(analysis_id):
    """دریافت یک تحلیل با ID"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # دریافت تحلیل اصلی
        cursor.execute("SELECT * FROM analyses WHERE id = %s", (analysis_id,))
        analysis = cursor.fetchone()
        
        if not analysis:
            return None
        
        # تبدیل datetime به string
        analysis['created_at'] = analysis['created_at'].isoformat() if analysis['created_at'] else None
        analysis['analyzed_at'] = analysis['analyzed_at'].isoformat() if analysis['analyzed_at'] else None
        
        # Parse JSON
        if analysis['full_analysis']:
            analysis['full_analysis'] = json.loads(analysis['full_analysis'])
        
        return analysis
        
    except Error as e:
        print(f"❌ خطا در دریافت تحلیل: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
  
  
def extract_text_from_file(file):
    """استخراج متن از فایل‌های مختلف - بدون striprtf"""
    filename = file.filename.lower()
    
    try:
        print(f"\n📁 فایل: {filename}")
        
        if filename.endswith('.rtf'):
            # خواندن محتوای خام
            raw_content = file.read()
            
            # استخراج متن بدون striprtf - روش مستقیم
            try:
                # تلاش با UTF-8
                content = raw_content.decode('utf-8', errors='ignore')
            except:
                try:
                    # تلاش با Windows-1256 (فارسی)
                    content = raw_content.decode('windows-1256', errors='ignore')
                except:
                    # آخرین تلاش با latin-1
                    content = raw_content.decode('latin-1', errors='ignore')
            
            # حذف دستورات RTF و استخراج متن خام
            import re
            
            # حذف header RTF
            content = re.sub(r'\\rtf\d', '', content)
            content = re.sub(r'\\ansi\\ansicpg\d+', '', content)
            content = re.sub(r'\\deff\d+', '', content)
            
            # حذف font table
            content = re.sub(r'\{\\fonttbl[^\}]*\}', '', content)
            
            # حذف color table
            content = re.sub(r'\{\\colortbl[^\}]*\}', '', content)
            
            # حذف stylesheet
            content = re.sub(r'\{\\stylesheet[^\}]*\}', '', content)
            
            # حذف تمام دستورات RTF (\xxx)
            content = re.sub(r'\\[a-z]+\d*[\s\-]?', '', content)
            
            # حذف پرانتزهای اضافی
            content = content.replace('{', '').replace('}', '')
            
            # حذف کاراکترهای خاص
            content = re.sub(r'[\\*]', '', content)
            
            # حذف خطوط خالی متعدد
            content = re.sub(r'\n\s*\n', '\n', content)
            
            text = content.strip()
            
            print(f"✅ RTF استخراج شد: {len(text)} کاراکتر")
            return text
        
        elif filename.endswith('.txt'):
            raw_content = file.read()
            
            # تلاش با encoding‌های مختلف
            encodings = ['utf-8', 'cp1256', 'windows-1256', 'iso-8859-1', 'latin-1']
            
            for encoding in encodings:
                try:
                    text = raw_content.decode(encoding)
                    print(f"✅ TXT استخراج شد ({encoding}): {len(text)} کاراکتر")
                    return text
                except:
                    continue
            
            text = raw_content.decode('utf-8', errors='ignore')
            print(f"✅ TXT استخراج شد (fallback): {len(text)} کاراکتر")
            return text
        
        elif filename.endswith('.pdf'):
            text = ""
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            print(f"✅ PDF استخراج شد: {len(text)} کاراکتر")
            return text
        
        elif filename.endswith('.docx'):
            doc = Document(file)
            text = "\n".join([para.text for para in doc.paragraphs])
            print(f"✅ DOCX استخراج شد: {len(text)} کاراکتر")
            return text
        
        elif filename.endswith(('.xlsx', '.xls')):
            wb = openpyxl.load_workbook(file)
            text = ""
            for sheet in wb.worksheets:
                for row in sheet.iter_rows(values_only=True):
                    text += " ".join([str(cell) for cell in row if cell]) + "\n"
            print(f"✅ XLSX استخراج شد: {len(text)} کاراکتر")
            return text
        
        else:
            # فایل عمومی
            raw_content = file.read()
            encodings = ['utf-8', 'cp1256', 'windows-1256', 'iso-8859-1', 'latin-1']
            
            for encoding in encodings:
                try:
                    text = raw_content.decode(encoding)
                    print(f"✅ فایل استخراج شد ({encoding}): {len(text)} کاراکتر")
                    return text
                except:
                    continue
            
            text = raw_content.decode('utf-8', errors='ignore')
            print(f"✅ فایل استخراج شد (fallback): {len(text)} کاراکتر")
            return text
            
    except Exception as e:
        print(f"❌ خطا در خواندن فایل: {str(e)}")
        raise Exception(f"خطا در خواندن فایل: {str(e)}")





def analyze_with_ai(content):
    """تحلیل CRM - نسخه نهایی کاری"""
    
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

    try:
        print(f"📤 ارسال...")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a CRM analyst. Return ONLY JSON with this exact structure. Make the summary detailed with specific numbers. No markdown, no explanation."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        response_text = response.choices[0].message.content.strip()
        
        print(f"✅ دریافت شد")
        print(f"\n{'='*50}")
        print(f"🤖 پاسخ:")
        print(response_text[:500] + "...")
        print(f"{'='*50}\n")
        
        # حذف markdown
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
        
        # Parse
        analysis = json.loads(response_text)
        
        print(f"✅ JSON پارس شد")
        print(f"  امتیاز: {analysis['فیلدهای_عددی']['امتیاز_کل']}")
        print(f"  تماس‌ها: {analysis['آمار']['تعداد_کل_تماس_ها']}")
        print(f"  خلاصه: {analysis['فیلدهای_متنی']['خلاصه'][:80]}...")
        print()
        
        return analysis
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON خطا: {str(e)}")
        print(f"📄 متن:")
        print(response_text[:1000])
        return {"error": True, "message": "خطا در JSON"}
        
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": True, "message": str(e)}



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    return render_template('history.html')


@app.route('/users')
def users_page():
    """صفحه تحلیل کارشناسان"""
    return render_template('users.html')


@app.route('/referral-history')
def referral_history_page():
    """صفحه تاریخچه ارجاعیات"""
    return render_template('referral_history.html')


@app.route('/api/referral-history')
def get_referral_history():
    """دریافت تاریخچه تحلیل‌های ارجاعیات"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify([])
        
        cursor = conn.cursor(dictionary=True)
        
        # بررسی وجود جدول
        cursor.execute("SHOW TABLES LIKE 'referral_analyses'")
        if not cursor.fetchone():
            print("⚠️ جدول referral_analyses وجود ندارد")
            return jsonify([])
        
        query = """
        SELECT 
            id,
            file_name,
            DATE_FORMAT(analyzed_at, '%%Y-%%m-%%d %%H:%%i:%%s') as analyzed_at,
            total_referrals,
            completed_count,
            pending_count,
            ROUND(completion_rate, 1) as completion_rate,
            JSON_UNQUOTE(JSON_EXTRACT(full_analysis, '$.status_analysis.worst_sender_pending.unit')) as bottleneck_unit
        FROM referral_analyses
        ORDER BY analyzed_at DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"✅ {len(results)} رکورد از تاریخچه ارجاعیات دریافت شد")
        
        cursor.close()
        conn.close()
        
        return jsonify(results)
        
    except Exception as e:
        print(f"❌ خطا در get_referral_history: {str(e)}")
        return jsonify([])


@app.route('/api/referral-analysis/<int:analysis_id>')
def get_referral_analysis(analysis_id):
    """دریافت جزئیات یک تحلیل"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "خطا در اتصال"}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT 
            id,
            file_name,
            analyzed_at,
            total_referrals,
            completed_count,
            pending_count,
            completion_rate,
            full_analysis
        FROM referral_analyses
        WHERE id = %s
        """
        
        cursor.execute(query, (analysis_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            return jsonify({"error": "یافت نشد"}), 404
        
        # تبدیل JSON
        if result['full_analysis']:
            result['full_analysis'] = json.loads(result['full_analysis'])
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        return jsonify({"error": str(e)}), 500




@app.route('/api/referral-report/<int:analysis_id>')
def download_referral_report(analysis_id):
    """دانلود گزارش Excel از تحلیل ارجاعیات"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "خطا در اتصال"}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM referral_analyses WHERE id = %s", (analysis_id,))
        analysis = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not analysis:
            return jsonify({"error": "یافت نشد"}), 404
        
        # ایجاد گزارش Excel
        import pandas as pd
        from io import BytesIO
        
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # برگه خلاصه
            summary_df = pd.DataFrame([{
                'نام فایل': analysis['file_name'],
                'تاریخ تحلیل': analysis['analyzed_at'],
                'کل ارجاعات': analysis['total_referrals'],
                'اتمام یافته': analysis['completed_count'],
                'بررسی نشده': analysis['pending_count'],
                'درصد موفقیت': f"{analysis['completion_rate']:.1f}%"
            }])
            summary_df.to_excel(writer, sheet_name='خلاصه', index=False)
            
            # برگه جزئیات (از full_analysis)
            if analysis['full_analysis']:
                full = json.loads(analysis['full_analysis'])
                
                # وضعیت‌ها
                status_dist = full.get('status_analysis', {}).get('status_distribution', {})
                if status_dist:
                    status_df = pd.DataFrame([
                        {'وضعیت': k, 'تعداد': v} 
                        for k, v in status_dist.items()
                    ])
                    status_df.to_excel(writer, sheet_name='وضعیت‌ها', index=False)
                
                # موضوعات
                subjects = full.get('subject_analysis', {}).get('unique_subjects', [])
                if subjects:
                    subject_df = pd.DataFrame(subjects)
                    subject_df.to_excel(writer, sheet_name='موضوعات', index=False)
                
                # توصیه‌ها
                recs = full.get('comprehensive_insights', {}).get('recommendations_fa', [])
                if recs:
                    rec_df = pd.DataFrame({'توصیه‌ها': recs})
                    rec_df.to_excel(writer, sheet_name='توصیه‌ها', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name=f"referral_report_{analysis_id}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"❌ خطا در download_referral_report: {str(e)}")
        return jsonify({"error": str(e)}), 500




def save_referral_analysis(file_info, analysis_data):
    """ذخیره تحلیل ارجاعیات در دیتابیس با دیباگ کامل"""
    conn = get_db_connection()
    if not conn:
        print("❌ اتصال به دیتابیس برقرار نشد")
        return None
    
    try:
        cursor = conn.cursor()
        
        # دیباگ - چاپ ساختار دریافتی
        print("\n" + "="*60)
        print("📊 STRUCTURE RECEIVED FROM OPENAI:")
        print(json.dumps(analysis_data, indent=2, ensure_ascii=False)[:1000])
        print("="*60 + "\n")
        
        # استخراج داده‌ها با دسترسی ایمن
        status = analysis_data.get('status_analysis', {})
        if not status:
            print("⚠️ status_analysis پیدا نشد، از کل داده استفاده می‌کنم")
            status = analysis_data
        
        dist = status.get('status_distribution', {})
        
        # محاسبه آمار
        total = 0
        completed = 0
        pending = 0
        in_progress = 0
        seen = 0
        accepted = 0
        
        # اگر dist دیکشنری بود
        if isinstance(dist, dict):
            total = sum(dist.values())
            completed = dist.get('اتمام کار', 0)
            pending = dist.get('بررسی نشده', 0)
            in_progress = dist.get('درحال پیگیری', 0)
            seen = dist.get('رویت شده', 0)
            accepted = dist.get('قبول ارجاع', 0)
        else:
            print(f"⚠️ dist از نوع {type(dist)} است، نه دیکشنری")
            # تلاش برای استخراج از جای دیگر
            if isinstance(analysis_data, dict):
                for key in ['status_distribution', 'distribution', 'statuses']:
                    if key in analysis_data and isinstance(analysis_data[key], dict):
                        dist = analysis_data[key]
                        total = sum(dist.values())
                        completed = dist.get('اتمام کار', 0)
                        pending = dist.get('بررسی نشده', 0)
                        break
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        pending_rate = (pending / total * 100) if total > 0 else 0
        
        print(f"📈 آمار محاسبه شده:")
        print(f"   total: {total}")
        print(f"   completed: {completed}")
        print(f"   pending: {pending}")
        print(f"   in_progress: {in_progress}")
        print(f"   seen: {seen}")
        print(f"   accepted: {accepted}")
        print(f"   completion_rate: {completion_rate:.1f}%")
        print(f"   pending_rate: {pending_rate:.1f}%")
        
        # بررسی وجود جدول
        cursor.execute("SHOW TABLES LIKE 'referral_analyses'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ جدول referral_analyses وجود ندارد!")
            print("🔄 در حال ایجاد جدول...")
            
            # ایجاد جدول
            cursor.execute("""
                CREATE TABLE referral_analyses (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    file_name VARCHAR(255),
                    file_path VARCHAR(500),
                    file_size INT,
                    analyzed_at DATETIME,
                    total_referrals INT,
                    completed_count INT,
                    pending_count INT,
                    in_progress_count INT,
                    seen_count INT,
                    accepted_count INT,
                    completion_rate FLOAT,
                    pending_rate FLOAT,
                    full_analysis JSON,
                    created_at DATETIME DEFAULT NOW()
                )
            """)
            print("✅ جدول referral_analyses ایجاد شد")
        
        # درج داده
        query = """
        INSERT INTO referral_analyses (
            file_name, file_path, file_size, analyzed_at,
            total_referrals, completed_count, pending_count,
            in_progress_count, seen_count, accepted_count,
            completion_rate, pending_rate, full_analysis
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            file_info['name'], file_info['path'], file_info['size'], datetime.now(),
            total, completed, pending, in_progress, seen, accepted,
            completion_rate, pending_rate,
            json.dumps(analysis_data, ensure_ascii=False)
        )
        
        print("📤 اجرای query...")
        cursor.execute(query, values)
        analysis_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ تحلیل ارجاعیات با ID {analysis_id} در دیتابیس ذخیره شد")
        
        # ذخیره جزئیات در جداول وابسته (اختیاری)
        try:
            # ذخیره موضوعات
            subjects = analysis_data.get('subject_analysis', {}).get('unique_subjects', [])
            if subjects and analysis_id:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS referral_subjects (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        analysis_id INT,
                        subject_name VARCHAR(255),
                        frequency INT,
                        FOREIGN KEY (analysis_id) REFERENCES referral_analyses(id) ON DELETE CASCADE
                    )
                """)
                for subj in subjects:
                    cursor.execute(
                        "INSERT INTO referral_subjects (analysis_id, subject_name, frequency) VALUES (%s, %s, %s)",
                        (analysis_id, subj.get('subject'), subj.get('count'))
                    )
                conn.commit()
                print(f"✅ {len(subjects)} موضوع ذخیره شد")
        except Exception as e:
            print(f"⚠️ خطا در ذخیره جزئیات: {e}")
        
        return analysis_id
        
    except Exception as e:
        print(f"❌ خطا در ذخیره: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()



# ========================================
# REFERRAL ANALYSIS MODULE
# ========================================
@app.route('/api/analyze-referral', methods=['POST'])
def analyze_referral():
    """API برای تحلیل فایل ارجاعیات - نسخه کامل با ذخیره‌سازی"""
    file_path = None
    
    try:
        # بررسی وجود فایل
        if 'file' not in request.files:
            return jsonify({"error": "فایلی آپلود نشده است"}), 400
        
        file = request.files['file']
        
        if file.filename == '':            return jsonify({"error": "فایل انتخاب نشده است"}), 400
        
        # ذخیره فایل
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"referral_{timestamp}_{file.filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        file.save(file_path)
        print(f"✅ فایل ذخیره شد: {file_path}")
        
        # استخراج متن
        with open(file_path, 'rb') as f:
            from io import BytesIO
            file_obj = BytesIO(f.read())
            file_obj.filename = file.filename
            
            content = extract_text_from_file(file_obj)
        
        if not content or len(content.strip()) < 50:
            os.remove(file_path)
            return jsonify({"error": "محتوای فایل خالی یا ناقص است"}), 400
        
        # تحلیل با AI
        analysis = analyze_referral_with_ai(content)
        
        if analysis.get('error'):
            os.remove(file_path)
            return jsonify(analysis), 400
        
        # آماده‌سازی اطلاعات فایل برای ذخیره
        file_info = {
            'name': file.filename,
            'path': file_path,
            'size': os.path.getsize(file_path),
            'type': file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'unknown'
        }
        
        # ذخیره در دیتابیس
        analysis_id = save_referral_analysis(file_info, analysis)
        
        if analysis_id:
            analysis['id'] = analysis_id
            print(f"✅ تحلیل با ID {analysis_id} در دیتابیس ذخیره شد")
        else:
            print("⚠️ خطا در ذخیره‌سازی تحلیل در دیتابیس")
        
        return jsonify(analysis)
        
    except Exception as e:
        print(f"\n❌❌❌ خطای CRITICAL در analyze_referral: {type(e).__name__}")
        print(f"پیام: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # حذف فایل در صورت خطا
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({
            "error": True,
            "message": f"{type(e).__name__}: {str(e)}"
        }), 500





def analyze_referral_with_ai(content):
    """تحلیل فایل ارجاعیات با OpenAI - پرامپت کامل با تمام سوالات"""
    
    print(f"\n{'='*50}")
    print(f"📊 تحلیل ارجاعیات - طول محتوا: {len(content)} کاراکتر")
    print(f"{'='*50}\n")
    
    # پرامپت کامل با تمام 50+ سوال
    prompt = f"""You are a workflow analyst. Analyze this referral/excel data and return ONLY JSON with the analysis.

**Input Data:**
{content[:15000]}

**COMPLETE ANALYSIS QUESTIONS (50+ Metrics):**

1. STATUS ANALYSIS (وضعیت ارجاعیات):
   - What percentage of referrals are in "بررسی نشده" status?
   - Which status has the highest frequency?
   - Average time in "بررسی نشده" status (based on due date)?
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
   - What is the trend between 28th and 29th?
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
   - Top 5 recommendations in Persian

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
  
  "temporal_analysis": {{
    "busiest_date": "1404/11/28",
    "daily_counts": {{"1404/11/28": 23, "1404/11/29": 4}},
    "avg_days_to_due": 0,
    "percent_overdue": 0,
    "hourly_distribution": {{"08-10": 15, "10-12": 8, "12-14": 3, "14-16": 1}},
    "trend_description": "بیشترین ارجاعات در تاریخ 28 بهمن با 23 مورد ثبت شده است"
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
    "subject_to_unit": {{
      "خرید باتری": ["پورحسین", "امور خدمات"],
      "اعزام کارشناس": ["تعمیرات", "امور خدمات"],
      "فاکتور شود و تحویل": ["کمک-حسابدار1", "امور خدمات"]
    }},
    "subjects_no_description": [],
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
    ],
    "receiver_pending": {{"امور خدمات": 5, "تعمیرات": 3}},
    "sender_least_description": "مومنی",
    "most_collaborative_unit": "امور خدمات",
    "collaboration_count": 8
  }},
  
  "institution_analysis": {{
    "top_institutions": [
      {{"name": "سیمان بجنورد", "count": 3, "subs": 28, "completion_rate": 100}},
      {{"name": "بیمارستان نهم دی تربت حیدریه", "count": 3, "subs": 92, "completion_rate": 100}},
      {{"name": "موقوفات ملک", "count": 3, "subs": 184, "completion_rate": 0}}
    ],
    "institution_subjects": {{
      "سیمان بجنورد": ["ارسال باتری", "فاکتور شود و تحویل"],
      "دانشگاه علوم پزشکی مشهد": ["فاکتور شود و تحویل"],
      "جایگاه سوخت کوه سفید": ["اعزام کارشناس"]
    }},
    "subscription_correlation": 0.3,
    "institutions_no_description": [],
    "institution_with_most_pending": "موقوفات ملک",
    "pending_count": 3
  }},
  
  "description_analysis": {{
    "percent_with_description": 65.4,
    "avg_description_length": 45.2,
    "max_description_length": 120,
    "top_describers": ["پورحسین", "رسولی"],
    "status_without_desc": {{"بررسی نشده": 3, "رویت شده": 2}},
    "top_keywords": [
      {{"word": "باتری", "count": 6, "completion_rate": 50.0}},
      {{"word": "فاکتور", "count": 5, "completion_rate": 80.0}},
      {{"word": "تحویل", "count": 4, "completion_rate": 75.0}},
      {{"word": "ارسال", "count": 3, "completion_rate": 66.7}},
      {{"word": "کارشناس", "count": 2, "completion_rate": 0.0}}
    ],
    "all_keywords": ["باتری", "فاکتور", "تحویل", "ارسال", "کارشناس", "پیش‌فاکتور", "تست"]
  }},
  
  "tracking_analysis": {{
    "duplicate_trackings": [
      {{"tracking": 23781, "count": 2, "statuses": ["بررسی نشده", "رویت شده"]}},
      {{"tracking": 23768, "count": 2, "statuses": ["رویت شده", "قبول ارجاع"]}},
      {{"tracking": 23766, "count": 2, "statuses": ["اتمام کار", "اتمام کار"]}}
    ],
    "avg_followups": 1.2,
    "max_followups": 2,
    "tracking_with_most_changes": 23781
  }},
  
  "subscription_analysis": {{
    "highest_subscription": {{"institution": "موقوفات ملک", "subs": 184}},
    "lowest_subscription": {{"institution": "سیمان بجنورد", "subs": 28}},
    "avg_subscription_pending": 156,
    "avg_subscription_completed": 89,
    "correlation_coefficient": 0.3,
    "correlation_description": "همبستگی ضعیف بین اشتراک و تعداد ارجاع"
  }},
  
  "comprehensive_insights": {{
    "completion_factors": [
      "توضیحات کامل",
      "ارجاع مستقیم به واحد مناسب",
      "پیگیری منظم",
      "ثبت دقیق اطلاعات مشتری"
    ],
    "top_bottlenecks": [
      {{"bottleneck": "واحد امور خدمات", "pending_count": 5, "impact": "بالا"}},
      {{"bottleneck": "واحد تعمیرات", "pending_count": 3, "impact": "متوسط"}},
      {{"bottleneck": "فرآیند تایید تعمیر", "pending_count": 2, "impact": "پایین"}}
    ],
    "top_strengths": [
      "پیگیری منظم توسط پورحسین",
      "سرعت عمل در فاکتور",
      "هماهنگی بین واحدها"
    ],
    "top_risks": [
      {{"risk": "مشتری جایگاه سوخت کوه سفید", "severity": "بالا", "reason": "تکرار درخواست بدون رسیدگی"}},
      {{"risk": "موقوفات ملک", "severity": "متوسط", "reason": "سه درخواست همزمان"}}
    ],
    "collaborating_units": [
      {{"units": ["تعمیرات", "امور خدمات"], "success_rate": 0.8, "collaboration_count": 3}},
      {{"units": ["پورحسین", "کمک-حسابدار1"], "success_rate": 1.0, "collaboration_count": 2}}
    ],
    "description_impact": true,
    "description_impact_details": "توضیحات کامل‌تر باعث افزایش ۳۰٪ در نرخ تکمیل می‌شود",
    "recurring_patterns": [
      {{"pattern": "درخواست باتری", "frequency": 4, "trend": "افزایشی"}},
      {{"pattern": "درخواست فاکتور", "frequency": 6, "trend": "ثابت"}},
      {{"pattern": "اعزام کارشناس", "frequency": 2, "trend": "تکراری با تاخیر"}}
    ],
    "workflow_health_score": 68.5,
    "health_description": "وضعیت متوسط - نیاز به بهبود در پیگیری و هماهنگی",
    "summary_fa": "از مجموع ۲۷ ارجاع، ۱۲ مورد به اتمام رسیده (۴۴٪) و ۷ مورد بررسی نشده (۲۶٪). گلوگاه اصلی در واحد امور خدمات با ۸ ارجاع دریافتی و ۵ مورد مانده است. مشتریان استراتژیک: سیمان بجنورد، بیمارستان نهم دی و موقوفات ملک. هشدار: جایگاه سوخت کوه سفید با درخواست مکرر اعزام کارشناس.",
    "recommendations_fa": [
      "پیگیری فوری ارجاعات معطل‌مانده در امور خدمات (۵ مورد) - حداکثر تا ۲۴ ساعت آینده",
      "تماس با جایگاه سوخت کوه سفید و عذرخواهی + اعزام کارشناس امروز",
      "ثبت توضیحات کامل‌تر برای ارجاعات (۳۵٪ بدون توضیح هستند)",
      "بهبود هماهنگی بین تعمیرات و امور خدمات (۳ ارجاع مشترک)",
      "برگزاری جلسه هماهنگی برای رسیدگی به درخواست‌های تکراری"
    ]
  }}
}}"""
    
    try:
        print(f"📤 ارسال به OpenAI...")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a workflow analyst specializing in Persian CRM data. Return ONLY valid JSON with no markdown or explanation. Make sure to include ALL fields in the exact structure provided."
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
        print(f"  وضعیت‌ها: {analysis['status_analysis']['status_distribution']}")
        print(f"  امتیاز سلامت: {analysis['comprehensive_insights']['workflow_health_score']}")
        print(f"  خلاصه: {analysis['comprehensive_insights']['summary_fa'][:100]}...")
        
        return analysis
        
    except json.JSONDecodeError as e:
        print(f"❌ خطا در JSON: {str(e)}")
        print(f"📄 متن مشکل‌دار (500 کاراکتر اول): {response_text[:500]}")
        return {
            "error": True,
            "message": "خطا در پردازش پاسخ هوش مصنوعی"
        }
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "error": True,
            "message": str(e)
        }


@app.route('/referral')
def referral_page():
    """صفحه تحلیل ارجاعیات"""
    return render_template('referral.html')



@app.route('/api/referral/latest')
def get_latest_referral_analysis():
    """دریافت آخرین تحلیل ارجاعیات"""
    try:
        # اینجا باید از دیتابیس بخونید
        # فعلاً نمونه برمی‌گردانیم
        
        sample_analysis = {
            "status_analysis": {
                "percent_pending": 25.9,
                "most_frequent_status": "اتمام کار",
                "frequent_status_count": 12,
                "avg_days_pending": 1.5,
                "worst_sender_pending": {"unit": "تعمیرات", "count": 3},
                "percent_completed": 44.4,
                "receiver_with_most_in_progress": {"receiver": "امور خدمات", "count": 2},
                "status_distribution": {
                    "بررسی نشده": 7,
                    "رویت شده": 3,
                    "درحال پیگیری": 2,
                    "اتمام کار": 12,
                    "قبول ارجاع": 1
                }
            },
            "comprehensive_insights": {
                "summary_fa": "از مجموع ۲۷ ارجاع، ۱۲ مورد به اتمام رسیده (۴۴٪) و ۷ مورد بررسی نشده (۲۶٪). گلوگاه اصلی در واحد امور خدمات با ۸ ارجاع دریافتی و ۵ مورد مانده است. مشتریان استراتژیک: سیمان بجنورد، بیمارستان نهم دی و موقوفات ملک. هشدار: جایگاه سوخت کوه سفید با درخواست مکرر اعزام کارشناس.",
                "recommendations_fa": [
                    "پیگیری فوری ارجاعات معطل‌مانده در امور خدمات (۵ مورد)",
                    "تماس با جایگاه سوخت کوه سفید و عذرخواهی + اعزام کارشناس",
                    "ثبت توضیحات کامل‌تر برای ارجاعات (۳۵٪ بدون توضیح)",
                    "بهبود هماهنگی بین تعمیرات و امور خدمات (۳ ارجاع مشترک)"
                ]
            }
        }
        
        return jsonify(sample_analysis)
        
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        return jsonify({"error": True, "message": str(e)}), 500


# ========================================
# USERS ANALYSIS ROUTES
# ========================================


@app.route('/api/analysis/latest')
def get_latest_analysis():
    """آخرین تحلیل انجام شده"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': True, 'message': 'خطا در اتصال به دیتابیس'}), 500
            
        cursor = conn.cursor()
        
        # دریافت آخرین تحلیل
        cursor.execute('''
            SELECT 
                id, 
                file_name, 
                analyzed_at,
                full_analysis
            FROM analyses 
            ORDER BY analyzed_at DESC 
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': True, 'message': 'تحلیلی یافت نشد'}), 404
        
        # Parse کردن JSON کامل
        full_analysis = json.loads(row[3]) if row[3] else {}
        
        # ساخت response
        analysis = {
            'id': row[0],
            'file_name': row[1],
            'analyzed_at': row[2].isoformat() if row[2] else None,
            'فیلدهای_عددی': full_analysis.get('فیلدهای_عددی', {}),
            'فیلدهای_متنی': full_analysis.get('فیلدهای_متنی', {}),
            'آمار': full_analysis.get('آمار', {}),
            'بهترین_ها': full_analysis.get('بهترین_ها', {}),
            'دلایل_کاهش_امتیازها': full_analysis.get('دلایل_کاهش_امتیازها', {}),
            'دلایل_کسب_امتیازها': full_analysis.get('دلایل_کسب_امتیازها', {}),
            'لیست_ها': full_analysis.get('لیست_ها', {})
        }
        
        return jsonify(analysis)
        
    except Exception as e:
        print(f"❌ خطا در get_latest_analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': True, 'message': str(e)}), 500



@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API برای تحلیل فایل"""
    file_path = None
    
    try:
        # بررسی وجود فایل
        if 'file' not in request.files:
            return jsonify({"error": "فایلی آپلود نشده است"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "فایل انتخاب نشده است"}), 400
        
        # ذخیره فایل
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        file.save(file_path)  # ⬅️⬅️⬅️ این خط را اضافه کنید!
        
        # باز کردن مجدد برای استخراج متن
        with open(file_path, 'rb') as f:
            from io import BytesIO
            file_obj = BytesIO(f.read())
            file_obj.filename = file.filename
            
            content = extract_text_from_file(file_obj)
        
        if not content or len(content.strip()) < 50:
            os.remove(file_path)
            return jsonify({"error": "محتوای فایل خالی یا ناقص است"}), 400
        
        # تحلیل با AI
        analysis = analyze_with_ai(content)
        
        if analysis.get('error'):
            os.remove(file_path)
            return jsonify(analysis), 400
        
        analysis['analyzed_at'] = datetime.now().isoformat()
        analysis['file_name'] = file.filename
        
        # ذخیره در دیتابیس
        file_info = {
            'name': file.filename,
            'path': file_path,
            'size': os.path.getsize(file_path),
            'type': file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'unknown'
        }
        
        analysis_id = save_analysis_to_db(file_info, analysis)
        
        if analysis_id:
            analysis['id'] = analysis_id
        
        return jsonify(analysis)
        
    except Exception as e:
        # پرینت خطای دقیق
        print(f"\n❌❌❌ خطای CRITICAL: {type(e).__name__}")
        print(f"پیام: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # حذف فایل در صورت خطا
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({
            "error": True,
            "message": f"{type(e).__name__}: {str(e)}"
        }), 500




@app.route('/api/history')
def api_history():
    """API دریافت لیست تحلیل‌ها"""
    analyses = get_all_analyses()
    return jsonify(analyses)

@app.route('/api/analysis/<int:analysis_id>')
def api_analysis_detail(analysis_id):
    """API دریافت جزئیات یک تحلیل"""
    analysis = get_analysis_by_id(analysis_id)
    if analysis:
        return jsonify(analysis)
    return jsonify({"error": "تحلیل یافت نشد"}), 404

@app.route('/api/file/<int:analysis_id>')
def download_file(analysis_id):
    """دانلود فایل مربوط به یک تحلیل"""
    analysis = get_analysis_by_id(analysis_id)
    if analysis and os.path.exists(analysis['file_path']):
        return send_file(
            analysis['file_path'],
            as_attachment=True,
            download_name=analysis['file_name']
        )
    return jsonify({"error": "فایل یافت نشد"}), 404

@app.route('/api/health')
def health():
    """بررسی سلامت API"""
    api_key = os.getenv('OPENAI_API_KEY')
    db_conn = get_db_connection()
    
    return jsonify({
        "status": "ok",
        "api_configured": bool(api_key and api_key.startswith('sk-')),
        "db_connected": bool(db_conn)
    })

if __name__ == '__main__':
    # ایجاد پوشه‌های ضروری
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    print(f"✅ پوشه آپلود: {app.config['UPLOAD_FOLDER']}")
    
    # بررسی API Key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  هشدار: کلید OpenAI در فایل .env تنظیم نشده است!")
    else:
        print("✅ OpenAI API Key تنظیم شده")
    
    # بررسی اتصال به دیتابیس
    conn = get_db_connection()
    if conn:
        print("✅ اتصال به دیتابیس برقرار است")
        conn.close()
    else:
        print("❌ خطا در اتصال به دیتابیس!")
    
    print("\n" + "="*60)
    print("🚀 سرور Flask آماده است")
    print("📍 آدرس: http://127.0.0.1:5001")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
