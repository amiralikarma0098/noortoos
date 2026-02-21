# modules/auth/decorators.py
from functools import wraps
from flask import session, redirect, url_for, request, jsonify

def login_required(f):
    """بررسی لاگین بودن کاربر"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # اگر درخواست AJAX باشه
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'unauthorized', 'message': 'لطفاً ابتدا وارد شوید'}), 401
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """بررسی نقش کاربر"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': 'unauthorized', 'message': 'لطفاً ابتدا وارد شوید'}), 401
                return redirect(url_for('auth.login'))
            
            if session.get('user_role') not in roles:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': 'forbidden', 'message': 'شما دسترسی به این بخش را ندارید'}), 403
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """دسترسی فقط برای ادمین"""
    return role_required('admin')(f)

def manager_required(f):
    """دسترسی برای مدیر و ادمین"""
    return role_required('admin', 'manager')(f)