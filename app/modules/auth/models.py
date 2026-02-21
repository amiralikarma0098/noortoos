# modules/auth/models.py
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from modules.database import get_db_connection

class User:
    """مدل کاربر"""
    
    @staticmethod
    def create(username, email, password, full_name=None, role='viewer', **kwargs):
        """ایجاد کاربر جدید"""
        try:
            conn = get_db_connection()
            if not conn:
                return {'success': False, 'message': 'خطا در اتصال به دیتابیس'}
            
            cursor = conn.cursor(dictionary=True)
            
            # بررسی وجود کاربر
            cursor.execute(
                "SELECT id FROM users WHERE username = %s OR email = %s",
                (username, email)
            )
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return {'success': False, 'message': 'نام کاربری یا ایمیل تکراری است'}
            
            # هش کردن رمز
            password_hash = User._hash_password(password)
            
            cursor.execute("""
                INSERT INTO users (
                    username, email, password_hash, full_name, role,
                    department, position, phone, created_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                username, email, password_hash, full_name, role,
                kwargs.get('department'), kwargs.get('position'),
                kwargs.get('phone'), kwargs.get('created_by')
            ))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # ایجاد تنظیمات پیش‌فرض
            cursor.execute(
                "INSERT INTO user_settings (user_id) VALUES (%s)",
                (user_id,)
            )
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'message': 'کاربر با موفقیت ایجاد شد',
                'user_id': user_id
            }
            
        except Exception as e:
            print(f"❌ خطا در ایجاد کاربر: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def authenticate(username_or_email, password):
        """احراز هویت کاربر"""
        try:
            conn = get_db_connection()
            if not conn:
                return {'success': False, 'message': 'خطا در اتصال به دیتابیس'}
            
            cursor = conn.cursor(dictionary=True)
            
            # جستجوی کاربر
            cursor.execute("""
                SELECT * FROM users 
                WHERE (username = %s OR email = %s) AND is_active = TRUE
            """, (username_or_email, username_or_email))
            
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                conn.close()
                return {'success': False, 'message': 'کاربر یافت نشد'}
            
            # بررسی رمز عبور
            password_hash = User._hash_password(password)
            if password_hash != user['password_hash']:
                cursor.close()
                conn.close()
                return {'success': False, 'message': 'رمز عبور اشتباه است'}
            
            # به‌روزرسانی آخرین ورود
            cursor.execute(
                "UPDATE users SET last_login = NOW() WHERE id = %s",
                (user['id'],)
            )
            conn.commit()
            
            cursor.close()
            conn.close()
            
            # حذف اطلاعات حساس
            del user['password_hash']
            
            return {
                'success': True,
                'message': 'ورود موفق',
                'user': user
            }
            
        except Exception as e:
            print(f"❌ خطا در احراز هویت: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_by_id(user_id):
        """دریافت اطلاعات کاربر با ID"""
        try:
            conn = get_db_connection()
            if not conn:
                return None
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, username, email, full_name, role, department,
                       position, phone, avatar_url, is_active, last_login,
                       created_at
                FROM users WHERE id = %s
            """, (user_id,))
            
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return user
            
        except Exception as e:
            print(f"❌ خطا: {str(e)}")
            return None
    
    @staticmethod
    def update(user_id, **kwargs):
        """به‌روزرسانی اطلاعات کاربر"""
        try:
            conn = get_db_connection()
            if not conn:
                return {'success': False, 'message': 'خطا در اتصال به دیتابیس'}
            
            cursor = conn.cursor(dictionary=True)
            
            # فیلدهای مجاز برای به‌روزرسانی
            allowed_fields = ['full_name', 'email', 'department', 'position', 
                            'phone', 'avatar_url', 'role']
            
            updates = []
            values = []
            
            for field in allowed_fields:
                if field in kwargs:
                    updates.append(f"{field} = %s")
                    values.append(kwargs[field])
            
            if not updates:
                return {'success': False, 'message': 'هیچ فیلدی برای به‌روزرسانی وجود ندارد'}
            
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            
            cursor.execute(query, values)
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return {'success': True, 'message': 'اطلاعات با موفقیت به‌روزرسانی شد'}
            
        except Exception as e:
            print(f"❌ خطا: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """تغییر رمز عبور"""
        try:
            conn = get_db_connection()
            if not conn:
                return {'success': False, 'message': 'خطا در اتصال به دیتابیس'}
            
            cursor = conn.cursor(dictionary=True)
            
            # بررسی رمز قدیم
            cursor.execute(
                "SELECT password_hash FROM users WHERE id = %s",
                (user_id,)
            )
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                conn.close()
                return {'success': False, 'message': 'کاربر یافت نشد'}
            
            old_hash = User._hash_password(old_password)
            if old_hash != user['password_hash']:
                cursor.close()
                conn.close()
                return {'success': False, 'message': 'رمز عبور فعلی اشتباه است'}
            
            # ذخیره رمز جدید
            new_hash = User._hash_password(new_password)
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (new_hash, user_id)
            )
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return {'success': True, 'message': 'رمز عبور با موفقیت تغییر کرد'}
            
        except Exception as e:
            print(f"❌ خطا: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _hash_password(password):
        """هش کردن رمز عبور (ساده - برای پروژه واقعی از bcrypt استفاده کن)"""
        # در پروژه واقعی از bcrypt استفاده کن
        return hashlib.sha256(password.encode()).hexdigest()


class Session:
    """مدیریت نشست‌های کاربر"""
    
    @staticmethod
    def create(user_id, ip_address=None, user_agent=None):
        """ایجاد نشست جدید"""
        try:
            conn = get_db_connection()
            if not conn:
                return None
            
            cursor = conn.cursor(dictionary=True)
            
            # ایجاد توکن یکتا
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(days=7)
            
            cursor.execute("""
                INSERT INTO sessions (user_id, session_token, ip_address, user_agent, expires_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, token, ip_address, user_agent, expires_at))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return token
            
        except Exception as e:
            print(f"❌ خطا در ایجاد نشست: {str(e)}")
            return None
    
    @staticmethod
    def validate(token):
        """اعتبارسنجی توکن"""
        try:
            conn = get_db_connection()
            if not conn:
                return None
            
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT s.*, u.username, u.full_name, u.role
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = %s AND s.expires_at > NOW() AND u.is_active = TRUE
            """, (token,))
            
            session = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return session
            
        except Exception as e:
            print(f"❌ خطا: {str(e)}")
            return None
    
    @staticmethod
    def delete(token):
        """حذف نشست (خروج)"""
        try:
            conn = get_db_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE session_token = %s", (token,))
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ خطا: {str(e)}")
            return False
    
    @staticmethod
    def delete_all(user_id):
        """حذف همه نشست‌های کاربر"""
        try:
            conn = get_db_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE user_id = %s", (user_id,))
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ خطا: {str(e)}")
            return False


class ActivityLog:
    """لاگ فعالیت‌ها"""
    
    @staticmethod
    def log(user_id, action, entity_type=None, entity_id=None, details=None, 
            ip_address=None, user_agent=None):
        """ثبت فعالیت"""
        try:
            conn = get_db_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            details_json = json.dumps(details, ensure_ascii=False) if details else None
            
            cursor.execute("""
                INSERT INTO activity_logs 
                (user_id, action, entity_type, entity_id, details, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, action, entity_type, entity_id, details_json, ip_address, user_agent))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ خطا در ثبت لاگ: {str(e)}")
            return False
    
    @staticmethod
    def get_user_logs(user_id, limit=50):
        """دریافت لاگ‌های یک کاربر"""
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM activity_logs 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (user_id, limit))
            
            logs = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return logs
            
        except Exception as e:
            print(f"❌ خطا: {str(e)}")
            return []