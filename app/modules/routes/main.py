# modules/routes/main.py
from flask import Blueprint, render_template, request, jsonify, current_app, session
from modules.config import Config
from modules.database import test_connection, get_db_connection
from modules.auth.decorators import login_required, role_required
import json
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    """صفحه اصلی"""
    return render_template('index.html')

@main_bp.route('/sales_history')
@login_required
def history():
    """صفحه تاریخچه"""
    return render_template('sales_history.html')

@main_bp.route('/sales_users')
@login_required
def users_page():
    """صفحه تحلیل کارشناسان"""
    return render_template('sales_users.html')

@main_bp.route('/sales-analysis')
@login_required
def sales_analysis():
    """صفحه تحلیل فروش"""
    return render_template('sales_analysis.html')

@main_bp.route('/api/health')
def health():
    """بررسی سلامت API (عمومی - بدون نیاز به لاگین)"""
    errors = Config.validate()
    db_status = test_connection()
    
    return jsonify({
        "status": "ok" if not errors and db_status else "warning",
        "api_configured": bool(Config.OPENAI_API_KEY),
        "db_connected": db_status,
        "warnings": errors
    })

# ========================================
# API های مورد نیاز داشبورد (نیاز به لاگین)
# ========================================

@main_bp.route('/api/analysis/history')
@login_required
def get_analysis_history():
    """دریافت تاریخچه تحلیل‌های فروش"""
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ اتصال به دیتابیس برقرار نشد")
            return jsonify([])
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                id, 
                file_name, 
                analyzed_at,
                seller_name,
                customer_name,
                score_total,
                total_calls,
                successful_calls,
                full_analysis
            FROM analyses 
            ORDER BY analyzed_at DESC 
            LIMIT 50
        """)
        
        analyses = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # تبدیل تاریخ به رشته
        for analysis in analyses:
            if analysis['analyzed_at']:
                if hasattr(analysis['analyzed_at'], 'isoformat'):
                    analysis['analyzed_at'] = analysis['analyzed_at'].isoformat()
                else:
                    analysis['analyzed_at'] = str(analysis['analyzed_at'])
        
        return jsonify(analyses)
        
    except Exception as e:
        print(f"❌ خطا در دریافت تاریخچه تحلیل‌ها: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify([])

@main_bp.route('/api/analysis/stats')
@login_required
def get_analysis_stats():
    """دریافت آمار کلی تحلیل‌ها"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'total_analyses': 0,
                'total_calls': 0,
                'successful_calls': 0,
                'avg_score': 0,
                'top_sellers': [],
                'top_customers': []
            })
        
        cursor = conn.cursor(dictionary=True)
        
        # آمار کلی
        cursor.execute("""
            SELECT 
                COUNT(*) as total_analyses,
                COALESCE(SUM(total_calls), 0) as total_calls,
                COALESCE(SUM(successful_calls), 0) as successful_calls,
                COALESCE(AVG(score_total), 0) as avg_score
            FROM analyses
        """)
        stats = cursor.fetchone()
        
        # فروشندگان برتر
        cursor.execute("""
            SELECT 
                seller_name,
                COUNT(*) as analysis_count,
                AVG(score_total) as avg_score
            FROM analyses
            WHERE seller_name IS NOT NULL AND seller_name != '—' AND seller_name != ''
            GROUP BY seller_name
            ORDER BY analysis_count DESC
            LIMIT 5
        """)
        top_sellers = cursor.fetchall()
        
        # مشتریان برتر
        cursor.execute("""
            SELECT 
                customer_name,
                COUNT(*) as analysis_count,
                AVG(score_total) as avg_score
            FROM analyses
            WHERE customer_name IS NOT NULL AND customer_name != '—' AND customer_name != ''
            GROUP BY customer_name
            ORDER BY analysis_count DESC
            LIMIT 5
        """)
        top_customers = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_analyses': stats['total_analyses'] if stats else 0,
            'total_calls': stats['total_calls'] if stats else 0,
            'successful_calls': stats['successful_calls'] if stats else 0,
            'avg_score': round(stats['avg_score'], 1) if stats and stats['avg_score'] else 0,
            'top_sellers': top_sellers or [],
            'top_customers': top_customers or []
        })
        
    except Exception as e:
        print(f"❌ خطا در دریافت آمار: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'total_analyses': 0,
            'total_calls': 0,
            'successful_calls': 0,
            'avg_score': 0,
            'top_sellers': [],
            'top_customers': []
        })

@main_bp.route('/api/analysis/weekly-trend')
@login_required
def get_weekly_trend():
    """دریافت روند هفتگی تحلیل‌ها"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({})
        
        cursor = conn.cursor(dictionary=True)
        
        # 8 هفته اخیر
        cursor.execute("""
            SELECT 
                DATE_FORMAT(analyzed_at, '%Y-%%u') as week,
                COUNT(*) as count
            FROM analyses
            WHERE analyzed_at >= DATE_SUB(NOW(), INTERVAL 8 WEEK)
            GROUP BY week
            ORDER BY week DESC
        """)
        
        trends = cursor.fetchall()
        cursor.close()
        conn.close()
        
        result = {}
        week_names = {
            '1': 'هفته ۱', '2': 'هفته ۲', '3': 'هفته ۳', '4': 'هفته ۴',
            '5': 'هفته ۵', '6': 'هفته ۶', '7': 'هفته ۷', '8': 'هفته ۸'
        }
        
        for trend in trends:
            # استخراج شماره هفته از فرمت YYYY-WW
            week_num = trend['week'].split('-')[-1] if '-' in trend['week'] else '1'
            week_num = week_num.lstrip('0')  # حذف صفرهای ابتدایی
            week_name = week_names.get(week_num, f'هفته {week_num}')
            result[week_name] = trend['count']
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ خطا در دریافت روند هفتگی: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({})

@main_bp.route('/api/analysis/score-distribution')
@login_required
def get_score_distribution():
    """دریافت توزیع امتیازها"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({})
        
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN score_total >= 8 THEN 1 ELSE 0 END) as excellent,
                SUM(CASE WHEN score_total >= 6 AND score_total < 8 THEN 1 ELSE 0 END) as good,
                SUM(CASE WHEN score_total >= 4 AND score_total < 6 THEN 1 ELSE 0 END) as average,
                SUM(CASE WHEN score_total < 4 AND score_total > 0 THEN 1 ELSE 0 END) as poor,
                SUM(CASE WHEN score_total = 0 OR score_total IS NULL THEN 1 ELSE 0 END) as unknown
            FROM analyses
        """)
        
        dist = cursor.fetchone()
        cursor.close()
        conn.close()
        
        result = {}
        if dist:
            if dist['excellent']:
                result['عالی (8-10)'] = dist['excellent']
            if dist['good']:
                result['خوب (6-8)'] = dist['good']
            if dist['average']:
                result['متوسط (4-6)'] = dist['average']
            if dist['poor']:
                result['ضعیف (0-4)'] = dist['poor']
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ خطا در دریافت توزیع امتیازها: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({})

@main_bp.route('/api/analysis/latest')
@login_required
def get_latest_analysis():
    """دریافت آخرین تحلیل"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify(None)
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                id, 
                file_name, 
                analyzed_at,
                seller_name,
                customer_name,
                score_total,
                total_calls,
                successful_calls,
                full_analysis
            FROM analyses 
            ORDER BY analyzed_at DESC 
            LIMIT 1
        """)
        
        analysis = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if analysis:
            if analysis.get('full_analysis'):
                try:
                    if isinstance(analysis['full_analysis'], str):
                        analysis['full_analysis'] = json.loads(analysis['full_analysis'])
                except:
                    pass
            
            if analysis['analyzed_at'] and hasattr(analysis['analyzed_at'], 'isoformat'):
                analysis['analyzed_at'] = analysis['analyzed_at'].isoformat()
        
        return jsonify(analysis)
        
    except Exception as e:
        print(f"❌ خطا در دریافت آخرین تحلیل: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify(None)


@main_bp.route('/calculator')
@login_required
def calculator():
    """نمایش محاسبه‌گر ری اکت"""
    return render_template('calculator.html')

@main_bp.route('/price-list')
@login_required
def price_list():
    """صفحه لیست قیمت محصولات"""
    return render_template('price_list.html')


@main_bp.route('/api/recent-activities')
@login_required
def get_recent_activities():
    """دریافت فعالیت‌های اخیر (ترکیبی از تحلیل‌ها و ارجاعات)"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify([])
        
        cursor = conn.cursor(dictionary=True)
        
        # دریافت آخرین تحلیل‌های فروش
        cursor.execute("""
            SELECT 
                'تحلیل فروش' as type,
                file_name,
                analyzed_at as date,
                seller_name as user,
                score_total as score,
                'success' as status
            FROM analyses 
            WHERE analyzed_at IS NOT NULL
            ORDER BY analyzed_at DESC 
            LIMIT 10
        """)
        
        analyses = cursor.fetchall()
        
        # دریافت آخرین تحلیل‌های ارجاع (اگر جدول referral_analyses وجود دارد)
        try:
            cursor.execute("""
                SELECT 
                    'تحلیل ارجاع' as type,
                    file_name,
                    analyzed_at as date,
                    'سیستم' as user,
                    completion_rate as score,
                    'info' as status
                FROM referral_analyses 
                WHERE analyzed_at IS NOT NULL
                ORDER BY analyzed_at DESC 
                LIMIT 10
            """)
            referrals = cursor.fetchall()
        except:
            referrals = []
        
        cursor.close()
        conn.close()
        
        # ترکیب و مرتب‌سازی
        activities = analyses + referrals
        activities.sort(key=lambda x: x['date'] if x['date'] else datetime.min, reverse=True)
        
        # فرمت کردن تاریخ‌ها
        for act in activities[:15]:  # 15 مورد آخر
            if act['date'] and hasattr(act['date'], 'isoformat'):
                act['date'] = act['date'].isoformat()
        
        return jsonify(activities[:15])
        
    except Exception as e:
        print(f"❌ خطا در دریافت فعالیت‌های اخیر: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify([])