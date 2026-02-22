# app.py
from flask import Flask
from modules.config import Config
from modules.database import test_connection
import os
from modules.routes.price_list import price_list_bp


def create_app():
    """ساخت و پیکربندی اپلیکیشن Flask"""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # تنظیمات امنیتی
    app.secret_key = Config.SECRET_KEY
    app.permanent_session_lifetime = Config.PERMANENT_SESSION_LIFETIME
    
    # ایجاد پوشه‌های ضروری
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    # ثبت Blueprintها
    from modules.routes.main import main_bp
    from modules.routes.analysis import analysis_bp
    from modules.routes.referral import referral_bp
    from modules.auth.routes import auth_bp
    from modules.academy import academy_bp  # اضافه کردن Blueprint آموزشگاه
    
    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(referral_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(academy_bp)  # ثبت Blueprint آموزشگاه
    
    return app

app = create_app()

app.register_blueprint(price_list_bp)


if __name__ == '__main__':
    # بررسی تنظیمات
    errors = Config.validate()
    for error in errors:
        print(error)
    
    # بررسی دیتابیس
    if test_connection():
        print("✅ اتصال به دیتابیس برقرار است")
    else:
        print("❌ خطا در اتصال به دیتابیس!")
    
    print("\n" + "="*60)
    print("🚀 سرور Flask آماده است")
    print(f"📍 آدرس: http://127.0.0.1:5001")
    print("📂 پوشه آپلود:", Config.UPLOAD_FOLDER)
    
    # نمایش تمام routeهای ثبت شده (برای دیباگ)
    with app.app_context():
        print("\n📋 لیست مسیرهای ثبت شده:")
        for rule in app.url_map.iter_rules():
            if "academy" in str(rule):
                print(f"   {rule.endpoint}: {rule}")
    print("="*60 + "\n")
    
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5001)