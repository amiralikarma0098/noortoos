# modules/academy/routes.py
from flask import Blueprint, render_template, jsonify, request, session
from modules.auth.decorators import login_required, manager_required, admin_required
from datetime import datetime
import openai
from modules.config import Config
import json
import pytz
from modules.database import execute_query, get_db_connection
from .product_search import ProductSearch

# ایمپورت پرامپت
from modules.academy.prompts.sales_master_prompt import get_sales_master_prompt

# تنظیم کلید OpenAI
openai.api_key = Config.OPENAI_API_KEY

# ایجاد شیء جستجوی محصولات
product_search = ProductSearch()

academy_bp = Blueprint('academy', __name__, url_prefix='/academy')

# ================ صفحات اصلی ================

@academy_bp.route('/')
@login_required
def index():
    """صفحه اصلی آموزشگاه"""
    return render_template('academy/index.html')


# ================ آموزشکاه فروش ================

@academy_bp.route('/sales/master')
@login_required
def sales_master():
    """صفحه اساتید فروش"""
    return render_template('academy/sales/master.html', department='sales')


@academy_bp.route('/sales/qa')
@login_required
def sales_qa():
    """صفحه پرسش و پاسخ با استاد فروش"""
    return render_template('academy/sales/qa_chat.html')


@academy_bp.route('/sales/assessment')
@login_required
def sales_assessment():
    """صفحه سنجش فروش"""
    return render_template('academy/sales/assessment.html', department='sales')


@academy_bp.route('/sales/workshop')
@login_required
def sales_workshop():
    """صفحه کارگاه‌های فروش"""
    return render_template('academy/sales/workshop.html', department='sales')


# ================ آموزشکاه خدمات ================

@academy_bp.route('/services/master')
@login_required
def services_master():
    """صفحه اساتید خدمات"""
    return render_template('academy/services/master.html', department='services')


@academy_bp.route('/services/assessment')
@login_required
def services_assessment():
    """صفحه سنجش خدمات"""
    return render_template('academy/services/assessment.html', department='services')


@academy_bp.route('/services/workshop')
@login_required
def services_workshop():
    """صفحه کارگاه‌های خدمات"""
    return render_template('academy/services/workshop.html', department='services')


# ================ API اساتید ================

@academy_bp.route('/api/master/list', methods=['GET'])
@login_required
def get_masters_list():
    """دریافت لیست اساتید"""
    department = request.args.get('department')
    
    masters = {
        'sales': [
            {
                'id': 1,
                'full_name': 'دکتر علی محمدی',
                'expertise': 'فروش و بازاریابی پیشرفته',
                'department': 'sales',
                'bio': 'دکترای مدیریت بازاریابی با ۱۵ سال سابقه تدریس در سازمان‌های بزرگ',
                'image_url': None,
                'courses_count': 12,
                'students_count': 450,
                'rating': 4.8
            },
            {
                'id': 2,
                'full_name': 'مهندس سارا احمدی',
                'expertise': 'مذاکرات فروش حرفه‌ای',
                'department': 'sales',
                'bio': 'مشاور فروش شرکت‌های بزرگ با سابقه بیش از ۱۰۰۰ ساعت کارگاه آموزشی',
                'image_url': None,
                'courses_count': 8,
                'students_count': 320,
                'rating': 4.9
            }
        ],
        'services': [
            {
                'id': 3,
                'full_name': 'دکتر رضا حسینی',
                'expertise': 'مدیریت ارتباط با مشتری',
                'department': 'services',
                'bio': 'دکترای مدیریت خدمات با سابقه اجرایی در شرکت‌های بین‌المللی',
                'image_url': None,
                'courses_count': 10,
                'students_count': 380,
                'rating': 4.7
            },
            {
                'id': 4,
                'full_name': 'مهندس مریم کریمی',
                'expertise': 'خدمات پس از فروش',
                'department': 'services',
                'bio': 'کارشناس ارشد مدیریت خدمات با ۱۲ سال سابقه در صنعت خودرو',
                'image_url': None,
                'courses_count': 6,
                'students_count': 210,
                'rating': 4.6
            }
        ]
    }
    
    if department and department in masters:
        return jsonify({
            'success': True,
            'masters': masters[department]
        })
    else:
        all_masters = masters['sales'] + masters['services']
        return jsonify({
            'success': True,
            'masters': all_masters
        })


@academy_bp.route('/api/master/<int:master_id>', methods=['GET'])
@login_required
def get_master(master_id):
    """دریافت اطلاعات یک استاد"""
    master = {
        'id': master_id,
        'full_name': 'دکتر علی محمدی',
        'expertise': 'فروش و بازاریابی پیشرفته',
        'department': 'sales',
        'bio': 'دکترای مدیریت بازاریابی از دانشگاه تهران با ۱۵ سال سابقه تدریس در سازمان‌های بزرگ کشور. نویسنده کتاب "فروش حرفه‌ای در عصر دیجیتال"',
        'image_url': None,
        'email': 'a.mohammadi@academy.ir',
        'phone': '0912xxxxxxx',
        'education': [
            {'degree': 'دکترای مدیریت بازاریابی', 'university': 'دانشگاه تهران', 'year': '1390'},
            {'degree': 'کارشناسی ارشد مدیریت اجرایی', 'university': 'دانشگاه صنعتی شریف', 'year': '1385'}
        ],
        'experience': [
            {'position': 'مدیر آموزش فروش', 'company': 'شرکت بازرگانی البرز', 'years': '1395-1400'},
            {'position': 'مشاور ارشد فروش', 'company': 'هلدینگ توسعه تجارت', 'years': '1400-اکنون'}
        ],
        'courses': [
            {'id': 1, 'title': 'کارگاه فروش حرفه‌ای', 'date': '1404/02/15', 'students': 45},
            {'id': 2, 'title': 'مذاکرات پیشرفته', 'date': '1404/03/10', 'students': 32}
        ]
    }
    
    return jsonify({
        'success': True,
        'master': master
    })


@academy_bp.route('/api/master', methods=['POST'])
@manager_required
def create_master():
    """ایجاد استاد جدید (فقط مدیران)"""
    data = request.json
    return jsonify({
        'success': True,
        'message': 'استاد با موفقیت ایجاد شد',
        'master_id': 5
    })


@academy_bp.route('/api/master/<int:master_id>', methods=['PUT'])
@manager_required
def update_master(master_id):
    """ویرایش اطلاعات استاد (فقط مدیران)"""
    return jsonify({
        'success': True,
        'message': 'اطلاعات استاد با موفقیت ویرایش شد'
    })


@academy_bp.route('/api/master/<int:master_id>', methods=['DELETE'])
@admin_required
def delete_master(master_id):
    """حذف استاد (فقط ادمین)"""
    return jsonify({
        'success': True,
        'message': 'استاد با موفقیت حذف شد'
    })


# ================ API کارگاه‌ها ================

@academy_bp.route('/api/workshop/list', methods=['GET'])
@login_required
def get_workshops_list():
    """دریافت لیست کارگاه‌ها"""
    department = request.args.get('department')
    workshop_type = request.args.get('type', 'all')
    status = request.args.get('status', 'all')
    
    workshops = [
        {
            'id': 1,
            'title': 'کارگاه فروش حرفه‌ای',
            'department': 'sales',
            'master_name': 'دکتر علی محمدی',
            'master_id': 1,
            'description': 'آموزش تکنیک‌های پیشرفته فروش و مذاکره',
            'start_date': '2025-03-15T10:00:00',
            'end_date': '2025-03-17T18:00:00',
            'capacity': 30,
            'registered_count': 15,
            'workshop_type': 'online',
            'status': 'upcoming',
            'price': 'رایگان',
            'location': 'آنلاین - اسکای روم'
        },
        {
            'id': 2,
            'title': 'مدیریت ارتباط با مشتری',
            'department': 'services',
            'master_name': 'دکتر رضا حسینی',
            'master_id': 3,
            'description': 'اصول و تکنیک‌های مدیریت ارتباط با مشتری',
            'start_date': '2025-03-20T09:00:00',
            'end_date': '2025-03-22T17:00:00',
            'capacity': 25,
            'registered_count': 22,
            'workshop_type': 'practical',
            'status': 'upcoming',
            'price': '450,000 تومان',
            'location': 'مشهد - بلوار وکیل‌آباد'
        },
        {
            'id': 3,
            'title': 'مذاکرات فروش پیشرفته',
            'department': 'sales',
            'master_name': 'مهندس سارا احمدی',
            'master_id': 2,
            'description': 'تکنیک‌های مذاکره در فروش B2B',
            'start_date': '2025-02-10T10:00:00',
            'end_date': '2025-02-12T18:00:00',
            'capacity': 20,
            'registered_count': 20,
            'workshop_type': 'online',
            'status': 'completed',
            'price': 'رایگان',
            'location': 'آنلاین - اسکای روم'
        }
    ]
    
    if department:
        workshops = [w for w in workshops if w['department'] == department]
    if status != 'all':
        workshops = [w for w in workshops if w['status'] == status]
    if workshop_type != 'all':
        workshops = [w for w in workshops if w['workshop_type'] == workshop_type]
    
    return jsonify({
        'success': True,
        'workshops': workshops
    })


@academy_bp.route('/api/workshop/<int:workshop_id>', methods=['GET'])
@login_required
def get_workshop(workshop_id):
    """دریافت اطلاعات یک کارگاه"""
    workshop = {
        'id': workshop_id,
        'title': 'کارگاه فروش حرفه‌ای',
        'department': 'sales',
        'master_name': 'دکتر علی محمدی',
        'master_id': 1,
        'master_bio': 'دکترای مدیریت بازاریابی با ۱۵ سال سابقه',
        'description': 'در این کارگاه با تکنیک‌های پیشرفته فروش، اصول مذاکره و روش‌های جذب مشتری آشنا خواهید شد.',
        'start_date': '2025-03-15T10:00:00',
        'end_date': '2025-03-17T18:00:00',
        'capacity': 30,
        'registered_count': 15,
        'workshop_type': 'online',
        'status': 'upcoming',
        'price': 'رایگان',
        'location': 'آنلاین - اسکای روم',
        'syllabus': [
            {'day': 1, 'title': 'مقدمات فروش حرفه‌ای', 'topics': ['شناخت مشتری', 'نیازسنجی', 'ارزش‌آفرینی']},
            {'day': 2, 'title': 'تکنیک‌های مذاکره', 'topics': ['اصول مذاکره', 'مدیریت اعتراضات', 'بستن قرارداد']},
            {'day': 3, 'title': 'فروش در عصر دیجیتال', 'topics': ['CRM', 'فروش آنلاین', 'تحلیل داده‌های فروش']}
        ],
        'prerequisites': ['آشنایی مقدماتی با مفاهیم فروش', 'گذراندن دوره مقدماتی'],
        'target_audience': ['مدیران فروش', 'کارشناسان فروش', 'بازاریابان']
    }
    
    return jsonify({
        'success': True,
        'workshop': workshop
    })


@academy_bp.route('/api/workshop/<int:workshop_id>/register', methods=['POST'])
@login_required
def register_workshop(workshop_id):
    """ثبت نام در کارگاه"""
    return jsonify({
        'success': True,
        'message': 'ثبت نام با موفقیت انجام شد'
    })


@academy_bp.route('/api/workshop/<int:workshop_id>/unregister', methods=['POST'])
@login_required
def unregister_workshop(workshop_id):
    """لغو ثبت نام در کارگاه"""
    return jsonify({
        'success': True,
        'message': 'ثبت نام با موفقیت لغو شد'
    })


@academy_bp.route('/api/workshop/<int:workshop_id>/sessions', methods=['GET'])
@login_required
def get_workshop_sessions(workshop_id):
    """دریافت جلسات کارگاه"""
    sessions = [
        {
            'id': 1,
            'title': 'جلسه اول - مقدمات فروش',
            'date': '2025-03-15T10:00:00',
            'duration': 180,
            'master_name': 'دکتر علی محمدی',
            'material_url': None,
            'video_url': None,
            'status': 'upcoming'
        },
        {
            'id': 2,
            'title': 'جلسه دوم - تکنیک‌های مذاکره',
            'date': '2025-03-16T10:00:00',
            'duration': 180,
            'master_name': 'دکتر علی محمدی',
            'material_url': None,
            'video_url': None,
            'status': 'upcoming'
        }
    ]
    
    return jsonify({
        'success': True,
        'sessions': sessions
    })


@academy_bp.route('/api/workshop', methods=['POST'])
@manager_required
def create_workshop():
    """ایجاد کارگاه جدید (فقط مدیران)"""
    return jsonify({
        'success': True,
        'message': 'کارگاه با موفقیت ایجاد شد',
        'workshop_id': 4
    })


# ================ API چت بات استاد ================

@academy_bp.route('/api/chat/history', methods=['GET'])
@login_required
def get_chat_history():
    """دریافت تاریخچه مکالمات کاربر از دیتابیس"""
    user_id = session.get('user_id')
    
    try:
        # دریافت آخرین 10 مکالمه کاربر
        query = """
            SELECT cs.*, 
                   (SELECT content FROM chat_messages WHERE session_id = cs.id ORDER BY created_at DESC LIMIT 1) as last_message
            FROM chat_sessions cs
            WHERE cs.user_id = %s
            ORDER BY cs.updated_at DESC
            LIMIT 10
        """
        sessions = execute_query(query, (user_id,), fetch_all=True)
        
        history = []
        for session_data in sessions or []:
            # عنوان مکالمه
            title = session_data.get('title')
            if not title:
                # اگر عنوان نداره، از اولین پیام کاربر استفاده کن
                first_msg_query = """
                    SELECT content FROM chat_messages 
                    WHERE session_id = %s AND role = 'user' 
                    ORDER BY created_at ASC LIMIT 1
                """
                first_msg = execute_query(first_msg_query, (session_data['id'],), fetch_one=True)
                if first_msg:
                    title = first_msg['content'][:30] + '...'
                else:
                    title = 'مکالمه جدید'
            
            # محاسبه زمان به فارسی
            from datetime import datetime
            now = datetime.now()
            diff = now - session_data['updated_at']
            
            if diff.days == 0:
                if diff.seconds < 3600:
                    time_str = f"{diff.seconds // 60} دقیقه پیش"
                else:
                    time_str = f"{diff.seconds // 3600} ساعت پیش"
            elif diff.days == 1:
                time_str = "دیروز"
            elif diff.days < 7:
                time_str = f"{diff.days} روز پیش"
            else:
                time_str = session_data['updated_at'].strftime('%Y/%m/%d')
            
            history.append({
                'id': session_data['id'],
                'title': title,
                'preview': (session_data.get('last_message') or '')[:50] + '...' if session_data.get('last_message') else '',
                'time': time_str
            })
        
        return jsonify({'success': True, 'history': history})
        
    except Exception as e:
        print(f"Error loading chat history: {str(e)}")
        return jsonify({'success': True, 'history': []})


@academy_bp.route('/api/chat/<int:chat_id>', methods=['GET'])
@login_required
def get_chat(chat_id):
    """دریافت یک مکالمه خاص از دیتابیس"""
    user_id = session.get('user_id')
    
    try:
        # بررسی دسترسی کاربر به این مکالمه
        check_query = "SELECT id FROM chat_sessions WHERE id = %s AND user_id = %s"
        session_data = execute_query(check_query, (chat_id, user_id), fetch_one=True)
        
        if not session_data:
            return jsonify({'success': False, 'error': 'مکالمه یافت نشد'}), 404
        
        # دریافت تمام پیام‌های مکالمه
        messages_query = """
            SELECT role, content, created_at 
            FROM chat_messages 
            WHERE session_id = %s 
            ORDER BY created_at ASC
        """
        db_messages = execute_query(messages_query, (chat_id,), fetch_all=True)
        
        messages = []
        for msg in db_messages or []:
            messages.append({
                'role': msg['role'],
                'content': msg['content'],
                'time': msg['created_at'].strftime('%H:%M')
            })
        
        return jsonify({'success': True, 'messages': messages})
        
    except Exception as e:
        print(f"Error loading chat: {str(e)}")
        return jsonify({'success': False, 'error': 'خطا در بارگذاری مکالمه'}), 500


@academy_bp.route('/api/chat/send', methods=['POST'])
@login_required
def send_chat_message():
    """ارسال پیام و دریافت پاسخ از استاد با جستجوی هوشمند محصولات"""
    data = request.json
    message = data.get('message')
    chat_id = data.get('chat_id')
    need_detailed = data.get('need_detailed', False)
    user_id = session.get('user_id')
    
    if not message:
        return jsonify({'success': False, 'error': 'پیام نمی‌تواند خالی باشد'}), 400
    
    try:
        # جستجوی محصولات مرتبط با سوال کاربر (حداکثر ۵ محصول)
        relevant_products = product_search.search_products(message, max_results=5)
        
        # ایجاد متن محصولات (خلاصه یا مفصل)
        products_text = product_search.get_products_text(relevant_products, detailed=need_detailed)
        
        # دریافت پرامپت پایه
        base_prompt = get_sales_master_prompt()
        
        # ترکیب پرامپت با محصولات
        if products_text:
            system_prompt = base_prompt + "\n\n" + products_text
        else:
            system_prompt = base_prompt + "\n\n❌ محصول مرتبطی با جستجوی شما یافت نشد. لطفاً با جزئیات بیشتر بپرسید."
        
        # اگر chat_id نداریم، یک مکالمه جدید بساز
        if not chat_id:
            insert_session = """
                INSERT INTO chat_sessions (user_id, title, created_at, updated_at)
                VALUES (%s, %s, NOW(), NOW())
            """
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(insert_session, (user_id, message[:50] + '...'))
            chat_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
        
        # ذخیره پیام کاربر
        insert_message = """
            INSERT INTO chat_messages (session_id, role, content, created_at)
            VALUES (%s, 'user', %s, NOW())
        """
        execute_query(insert_message, (chat_id, message), commit=True)
        
        # دریافت پاسخ از OpenAI
        from openai import OpenAI
        from modules.config import Config
        
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # تنظیم temperature بر اساس نیاز کاربر
        temperature = 0.8 if need_detailed else 0.5
        max_tokens = 1000 if need_detailed else 500
        
        # دریافت آخرین پیام‌ها برای context
        context_query = """
            SELECT role, content FROM chat_messages 
            WHERE session_id = %s 
            ORDER BY created_at DESC 
            LIMIT 10
        """
        recent_messages = execute_query(context_query, (chat_id,), fetch_all=True) or []
        
        messages_for_api = [{"role": "system", "content": system_prompt}]
        for msg in reversed(recent_messages):
            messages_for_api.append({
                "role": "user" if msg['role'] == 'user' else 'assistant',
                "content": msg['content']
            })
        
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=messages_for_api,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        ai_response = response.choices[0].message.content
        
        # ذخیره پاسخ استاد
        insert_bot = """
            INSERT INTO chat_messages (session_id, role, content, created_at)
            VALUES (%s, 'assistant', %s, NOW())
        """
        execute_query(insert_bot, (chat_id, ai_response), commit=True)
        
        # آپدیت زمان مکالمه
        update_session = "UPDATE chat_sessions SET updated_at = NOW() WHERE id = %s"
        execute_query(update_session, (chat_id,), commit=True)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'chat_id': chat_id,
            'products_count': len(relevant_products)
        })
        
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'خطا در ارتباط با استاد. لطفاً دوباره تلاش کنید.'
        }), 500


@academy_bp.route('/api/chat/new', methods=['POST'])
@login_required
def new_chat():
    """شروع مکالمه جدید"""
    user_id = session.get('user_id')
    
    try:
        insert_session = """
            INSERT INTO chat_sessions (user_id, title, created_at, updated_at)
            VALUES (%s, 'مکالمه جدید', NOW(), NOW())
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(insert_session, (user_id,))
        chat_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'chat_id': chat_id,
            'message': 'مکالمه جدید شروع شد'
        })
        
    except Exception as e:
        print(f"Error creating new chat: {str(e)}")
        return jsonify({'success': False, 'error': 'خطا در ایجاد مکالمه جدید'}), 500


# ================ API سنجش ================

@academy_bp.route('/api/assessment/list', methods=['GET'])
@login_required
def get_assessments_list():
    """دریافت لیست سنجش‌ها"""
    department = request.args.get('department')
    status = request.args.get('status', 'all')
    
    assessments = [
        {
            'id': 1,
            'title': 'آزمون فروش مقدماتی',
            'department': 'sales',
            'master_name': 'دکتر علی محمدی',
            'workshop_id': 1,
            'workshop_title': 'کارگاه فروش حرفه‌ای',
            'assessment_type': 'quiz',
            'max_score': 100,
            'passing_score': 70,
            'start_date': '2025-03-20T10:00:00',
            'end_date': '2025-03-25T18:00:00',
            'duration': 60,
            'questions_count': 20,
            'status': 'active'
        },
        {
            'id': 2,
            'title': 'سنجش مهارت خدمات مشتریان',
            'department': 'services',
            'master_name': 'دکتر رضا حسینی',
            'workshop_id': 2,
            'workshop_title': 'مدیریت ارتباط با مشتری',
            'assessment_type': 'practical',
            'max_score': 100,
            'passing_score': 75,
            'start_date': '2025-03-22T09:00:00',
            'end_date': '2025-03-27T17:00:00',
            'duration': 120,
            'questions_count': 15,
            'status': 'upcoming'
        }
    ]
    
    if department:
        assessments = [a for a in assessments if a['department'] == department]
    if status != 'all':
        assessments = [a for a in assessments if a['status'] == status]
    
    return jsonify({
        'success': True,
        'assessments': assessments
    })


@academy_bp.route('/api/assessment/<int:assessment_id>', methods=['GET'])
@login_required
def get_assessment(assessment_id):
    """دریافت اطلاعات یک سنجش"""
    assessment = {
        'id': assessment_id,
        'title': 'آزمون فروش مقدماتی',
        'department': 'sales',
        'master_name': 'دکتر علی محمدی',
        'workshop_id': 1,
        'workshop_title': 'کارگاه فروش حرفه‌ای',
        'assessment_type': 'quiz',
        'description': 'این آزمون شامل ۲۰ سوال چهارگزینه‌ای از مباحث کارگاه فروش می‌باشد.',
        'questions': [
            {
                'id': 1,
                'text': 'کدام یک از موارد زیر جزو مراحل فروش حرفه‌ای محسوب می‌شود؟',
                'options': ['شناسایی نیاز', 'ارائه محصول', 'مدیریت اعتراضات', 'همه موارد'],
                'score': 5
            },
            {
                'id': 2,
                'text': 'در مذاکره فروش، BATNA به چه معناست؟',
                'options': ['بهترین جایگزین توافق', 'قدرت چانه‌زنی', 'نقطه توقف', 'استراتژی مذاکره'],
                'score': 5
            }
        ],
        'max_score': 100,
        'passing_score': 70,
        'start_date': '2025-03-20T10:00:00',
        'end_date': '2025-03-25T18:00:00',
        'duration': 60,
        'status': 'active',
        'user_status': 'not_started'
    }
    
    return jsonify({
        'success': True,
        'assessment': assessment
    })


@academy_bp.route('/api/assessment/<int:assessment_id>/submit', methods=['POST'])
@login_required
def submit_assessment(assessment_id):
    """ثبت پاسخ سنجش"""
    return jsonify({
        'success': True,
        'message': 'پاسخ‌ها با موفقیت ثبت شد',
        'score': 85,
        'status': 'passed'
    })


@academy_bp.route('/api/assessment/<int:assessment_id>/result', methods=['GET'])
@login_required
def get_assessment_result(assessment_id):
    """دریافت نتیجه سنجش برای کاربر جاری"""
    result = {
        'id': 1,
        'assessment_id': assessment_id,
        'user_id': session.get('user_id'),
        'score': 85,
        'status': 'passed',
        'completed_at': '2025-03-21T14:30:00',
        'answers': {
            '1': 3,
            '2': 1
        }
    }
    
    return jsonify({
        'success': True,
        'result': result
    })


# ================ API پرسش و پاسخ ================

@academy_bp.route('/api/workshop/<int:workshop_id>/qa', methods=['GET'])
@login_required
def get_workshop_qa(workshop_id):
    """دریافت پرسش و پاسخ‌های کارگاه"""
    qas = [
        {
            'id': 1,
            'question': 'آیا فایل ارائه جلسات بعد از کارگاه در اختیار شرکت‌کنندگان قرار می‌گیرد؟',
            'answer': 'بله، تمام فایل‌ها و منابع آموزشی بعد از هر جلسه در پنل کاربری قرار می‌گیرد.',
            'is_answered': True,
            'created_at': '2025-03-14T15:30:00',
            'user_name': 'علی رضایی',
            'master_name': 'دکتر علی محمدی',
            'answered_at': '2025-03-14T16:45:00'
        },
        {
            'id': 2,
            'question': 'آیا این کارگاه پیش‌نیاز خاصی دارد؟',
            'answer': None,
            'is_answered': False,
            'created_at': '2025-03-15T09:15:00',
            'user_name': 'سارا احمدی',
            'master_name': None,
            'answered_at': None
        }
    ]
    
    return jsonify({
        'success': True,
        'qas': qas
    })


@academy_bp.route('/api/workshop/<int:workshop_id>/qa', methods=['POST'])
@login_required
def ask_question(workshop_id):
    """پرسش سوال جدید"""
    return jsonify({
        'success': True,
        'message': 'سوال شما ثبت شد',
        'qa_id': 3
    })


@academy_bp.route('/api/qa/<int:qa_id>/answer', methods=['POST'])
@manager_required
def answer_question(qa_id):
    """پاسخ به سوال (فقط مدیران و اساتید)"""
    return jsonify({
        'success': True,
        'message': 'پاسخ با موفقیت ثبت شد'
    })


# ================ API تقویم آموزشی ================

@academy_bp.route('/api/schedule', methods=['GET'])
@login_required
def get_schedule():
    """دریافت تقویم آموزشی"""
    department = request.args.get('department')
    
    events = [
        {
            'id': 1,
            'title': 'کارگاه فروش حرفه‌ای',
            'description': 'کارگاه ۳ روزه فروش',
            'event_date': '2025-03-15T10:00:00',
            'event_type': 'workshop',
            'department': 'sales',
            'status': 'upcoming'
        },
        {
            'id': 2,
            'title': 'آزمون فروش مقدماتی',
            'description': 'آزمون پایان دوره فروش',
            'event_date': '2025-03-20T10:00:00',
            'event_type': 'assessment',
            'department': 'sales',
            'status': 'upcoming'
        },
        {
            'id': 3,
            'title': 'مدیریت ارتباط با مشتری',
            'description': 'کارگاه خدمات مشتریان',
            'event_date': '2025-03-20T09:00:00',
            'event_type': 'workshop',
            'department': 'services',
            'status': 'upcoming'
        }
    ]
    
    if department:
        events = [e for e in events if e['department'] == department]
    
    return jsonify({
        'success': True,
        'events': events
    })


# ================ API آمار ================

@academy_bp.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """دریافت آمار آموزشگاه"""
    department = request.args.get('department')
    
    if department == 'sales':
        stats = {
            'total_masters': 5,
            'total_workshops': 8,
            'total_assessments': 10,
            'upcoming_workshops': 3,
            'completed_assessments': 28,
            'total_students': 156,
            'avg_rating': 4.7,
            'success_rate': 82
        }
    elif department == 'services':
        stats = {
            'total_masters': 4,
            'total_workshops': 6,
            'total_assessments': 8,
            'upcoming_workshops': 2,
            'completed_assessments': 19,
            'total_students': 98,
            'avg_rating': 4.5,
            'success_rate': 78
        }
    else:
        stats = {
            'total_masters': 9,
            'total_workshops': 14,
            'total_assessments': 18,
            'upcoming_workshops': 5,
            'completed_assessments': 47,
            'total_students': 254,
            'avg_rating': 4.6,
            'success_rate': 80
        }
    
    return jsonify({
        'success': True,
        'stats': stats
    })


# ================ API پنل کاربری ================

@academy_bp.route('/api/my-courses', methods=['GET'])
@login_required
def get_my_courses():
    """دریافت دوره‌های ثبت‌نامی کاربر"""
    courses = [
        {
            'id': 1,
            'title': 'کارگاه فروش حرفه‌ای',
            'master_name': 'دکتر علی محمدی',
            'start_date': '2025-03-15T10:00:00',
            'end_date': '2025-03-17T18:00:00',
            'status': 'upcoming',
            'progress': 0,
            'certificate_available': False
        },
        {
            'id': 3,
            'title': 'مذاکرات فروش پیشرفته',
            'master_name': 'مهندس سارا احمدی',
            'start_date': '2025-02-10T10:00:00',
            'end_date': '2025-02-12T18:00:00',
            'status': 'completed',
            'progress': 100,
            'certificate_available': True
        }
    ]
    
    return jsonify({
        'success': True,
        'courses': courses
    })


@academy_bp.route('/api/my-assessments', methods=['GET'])
@login_required
def get_my_assessments():
    """دریافت سنجش‌های کاربر"""
    assessments = [
        {
            'id': 1,
            'title': 'آزمون فروش مقدماتی',
            'workshop_title': 'کارگاه فروش حرفه‌ای',
            'status': 'pending',
            'score': None,
            'deadline': '2025-03-25T18:00:00'
        },
        {
            'id': 2,
            'title': 'سنجش نهایی فروش',
            'workshop_title': 'مذاکرات فروش پیشرفته',
            'status': 'completed',
            'score': 92,
            'deadline': '2025-02-15T18:00:00'
        }
    ]
    
    return jsonify({
        'success': True,
        'assessments': assessments
    })