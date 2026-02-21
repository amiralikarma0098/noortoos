# modules/config.py
import os
from dotenv import load_dotenv
import secrets

# بارگذاری متغیرهای محیطی
load_dotenv()

class Config:
    # تنظیمات پایه
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # تنظیمات نشست (Session)
    PERMANENT_SESSION_LIFETIME = 7 * 24 * 60 * 60  # 7 روز
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # تنظیمات آپلود
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    UPLOAD_FOLDER = 'uploaded_files'
    
    # تنظیمات OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # تنظیمات MySQL
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'crm_analyzer'),
        'charset': 'utf8mb4'
    }
    
    @classmethod
    def validate(cls):
        """بررسی تنظیمات ضروری"""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("⚠️ کلید OpenAI تنظیم نشده است!")
        elif not cls.OPENAI_API_KEY.startswith('sk-'):
            errors.append("⚠️ کلید OpenAI نامعتبر است!")
            
        return errors