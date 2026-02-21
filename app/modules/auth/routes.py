# modules/auth/routes.py
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from .models import User, Session, ActivityLog

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحه ورود"""
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    # درخواست POST برای لاگین
    try:
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        password = data.get('password')
        remember = data.get('remember', False)
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'نام کاربری و رمز عبور الزامی است'
            }), 400
        
        # احراز هویت
        result = User.authenticate(username, password)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 401
        
        user = result['user']
        
        # ایجاد نشست
        token = Session.create(
            user_id=user['id'],
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        if token:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['user_role'] = user['role']
            session['session_token'] = token
            
            if remember:
                session.permanent = True
            
            # ثبت لاگ
            ActivityLog.log(
                user_id=user['id'],
                action='login',
                details={'method': 'password'},
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
            
            return jsonify({
                'success': True,
                'message': 'ورود موفق',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'role': user['role']
                },
                'redirect': request.args.get('next') or url_for('main.index')
            })
        
        return jsonify({
            'success': False,
            'message': 'خطا در ایجاد نشست'
        }), 500
        
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطای سرور'
        }), 500

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """صفحه ثبت‌نام"""
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    try:
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        full_name = data.get('full_name')
        
        if not username or not email or not password:
            return jsonify({
                'success': False,
                'message': 'تمامی فیلدهای اجباری را پر کنید'
            }), 400
        
        if password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'رمز عبور و تکرار آن مطابقت ندارند'
            }), 400
        
        if len(password) < 8:
            return jsonify({
                'success': False,
                'message': 'رمز عبور باید حداقل ۸ کاراکتر باشد'
            }), 400
        
        result = User.create(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role='viewer'
        )
        
        if not result['success']:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'ثبت‌نام با موفقیت انجام شد',
            'redirect': url_for('auth.login')
        })
        
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطای سرور'
        }), 500

@auth_bp.route('/logout')
def logout():
    """خروج از سیستم"""
    token = session.get('session_token')
    user_id = session.get('user_id')
    
    if token:
        Session.delete(token)
    
    if user_id:
        ActivityLog.log(
            user_id=user_id,
            action='logout',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
    
    session.clear()
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
def profile():
    """صفحه پروفایل"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.get_by_id(session['user_id'])
    return render_template('auth/profile.html', user=user)

# ========================================
# APIهای پروفایل (با اسم‌های یکتا)
# ========================================

@auth_bp.route('/api/profile/update', methods=['PUT'])  # تغییر اسم route
def profile_update_api():  # تغییر اسم تابع
    """API به‌روزرسانی پروفایل"""
    if 'user_id' not in session:
        return jsonify({'error': 'unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        result = User.update(
            user_id=session['user_id'],
            full_name=data.get('full_name'),
            email=data.get('email'),
            department=data.get('department'),
            position=data.get('position'),
            phone=data.get('phone')
        )
        
        if result['success']:
            if data.get('full_name'):
                session['full_name'] = data.get('full_name')
            
            ActivityLog.log(
                user_id=session['user_id'],
                action='update_profile',
                details={'fields': list(data.keys())},
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
            
            return jsonify({
                'success': True,
                'message': 'پروفایل با موفقیت به‌روزرسانی شد'
            })
        
        return jsonify({
            'success': False,
            'message': result['message']
        }), 400
        
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطای سرور'
        }), 500

@auth_bp.route('/api/profile/change-password', methods=['POST'])  # تغییر اسم route
def profile_change_password_api():  # تغییر اسم تابع
    """API تغییر رمز عبور"""
    if 'user_id' not in session:
        return jsonify({'error': 'unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        result = User.change_password(
            user_id=session['user_id'],
            old_password=data.get('old_password'),
            new_password=data.get('new_password')
        )
        
        if result['success']:
            ActivityLog.log(
                user_id=session['user_id'],
                action='change_password',
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
            
            return jsonify({
                'success': True,
                'message': 'رمز عبور با موفقیت تغییر کرد'
            })
        
        return jsonify({
            'success': False,
            'message': result['message']
        }), 400
        
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطای سرور'
        }), 500

@auth_bp.route('/api/profile/activities')
def profile_activities_api():  # تغییر اسم تابع
    """دریافت فعالیت‌های اخیر کاربر"""
    if 'user_id' not in session:
        return jsonify([])
    
    try:
        logs = ActivityLog.get_user_logs(session['user_id'], limit=10)
        return jsonify(logs)
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        return jsonify([])

@auth_bp.route('/api/profile/avatar', methods=['POST'])
def profile_avatar_api():  # تغییر اسم تابع
    """آپلود تصویر پروفایل"""
    if 'user_id' not in session:
        return jsonify({'error': 'unauthorized'}), 401
    
    try:
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'message': 'فایلی ارسال نشده'}), 400
        
        file = request.files['avatar']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'فایل انتخاب نشده'}), 400
        
        # TODO: ذخیره فایل و به‌روزرسانی avatar_url در دیتابیس
        
        return jsonify({
            'success': True,
            'message': 'تصویر با موفقیت آپلود شد'
        })
        
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'خطای سرور'
        }), 500

@auth_bp.route('/api/check-auth')
def check_auth_api():  # تغییر اسم تابع
    """بررسی وضعیت احراز هویت"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'username': session.get('username'),
                'full_name': session.get('full_name'),
                'role': session.get('user_role')
            }
        })
    
    return jsonify({
        'authenticated': False
    })