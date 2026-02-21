import json
from flask import Blueprint, request, jsonify, send_file
import os
from modules.auth.decorators import login_required
from datetime import datetime
from modules.file_handler import FileHandler
from modules.openai_client import OpenAIClient
from modules.models import AnalysisModel
from modules.config import Config
from modules.database import get_db_connection

analysis_bp = Blueprint('analysis', __name__)
file_handler = FileHandler(Config.UPLOAD_FOLDER)
ai_client = OpenAIClient()

@analysis_bp.route('/api/analyze', methods=['POST'])
@login_required
def analyze():
    """API برای تحلیل فایل CRM عمومی"""
    file_info = None
    
    try:
        # بررسی وجود فایل
        if 'file' not in request.files:
            return jsonify({"error": "فایلی آپلود نشده است"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "فایل انتخاب نشده است"}), 400
        
        if not file_handler.allowed_file(file.filename):
            return jsonify({"error": "نوع فایل مجاز نیست"}), 400
        
        # ذخیره فایل
        file_info = file_handler.save_file(file)
        
        # استخراج متن
        content = file_handler.extract_text(file_info['path'], file_info['name'])
        
        if not content or len(content.strip()) < 50:
            file_handler.delete_file(file_info['path'])
            return jsonify({"error": "محتوای فایل خالی یا ناقص است"}), 400
        
        # تحلیل با AI
        analysis = ai_client.analyze_crm(content)
        
        if analysis.get('error'):
            file_handler.delete_file(file_info['path'])
            return jsonify(analysis), 400
        
        analysis['analyzed_at'] = datetime.now().isoformat()
        analysis['file_name'] = file_info['name']
        
        # ذخیره در دیتابیس
        analysis_id = AnalysisModel.save(file_info, analysis)
        
        if analysis_id:
            analysis['id'] = analysis_id
        
        return jsonify(analysis)
        
    except Exception as e:
        print(f"❌ خطا در analyze: {str(e)}")
        import traceback
        traceback.print_exc()
        
        if file_info and os.path.exists(file_info['path']):
            file_handler.delete_file(file_info['path'])
        
        return jsonify({
            "error": True,
            "message": str(e)
        }), 500

@analysis_bp.route('/api/analysis/latest')
@login_required
def get_latest_analysis():
    """آخرین تحلیل انجام شده"""
    try:
        analysis = AnalysisModel.get_latest()
        
        if not analysis:
            return jsonify({'error': True, 'message': 'تحلیلی یافت نشد'}), 404
        
        # Parse کردن JSON کامل
        full_analysis = json.loads(analysis['full_analysis']) if analysis.get('full_analysis') else {}
        
        # ساخت response
        result = {
            'id': analysis['id'],
            'file_name': analysis['file_name'],
            'analyzed_at': analysis['analyzed_at'].isoformat() if analysis.get('analyzed_at') else None,
            'فیلدهای_عددی': full_analysis.get('فیلدهای_عددی', {}),
            'فیلدهای_متنی': full_analysis.get('فیلدهای_متنی', {}),
            'آمار': full_analysis.get('آمار', {}),
            'بهترین_ها': full_analysis.get('بهترین_ها', {}),
            'دلایل_کاهش_امتیازها': full_analysis.get('دلایل_کاهش_امتیازها', {}),
            'دلایل_کسب_امتیازها': full_analysis.get('دلایل_کسب_امتیازها', {}),
            'لیست_ها': full_analysis.get('لیست_ها', {})
        }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        return jsonify({'error': True, 'message': str(e)}), 500

@analysis_bp.route('/api/history')
def api_history():
    """API دریافت لیست تحلیل‌ها"""
    analyses = AnalysisModel.get_all()
    return jsonify(analyses)

@analysis_bp.route('/api/analysis/<int:analysis_id>')
@login_required
def api_analysis_detail(analysis_id):
    """API دریافت جزئیات یک تحلیل"""
    analysis = AnalysisModel.get_by_id(analysis_id)
    if analysis:
        return jsonify(analysis)
    return jsonify({"error": "تحلیل یافت نشد"}), 404

@analysis_bp.route('/api/analysis/<int:analysis_id>', methods=['DELETE'])
@login_required
def delete_analysis(analysis_id):
    """حذف یک تحلیل CRM به همراه فایل مرتبط"""
    conn = None
    cursor = None
    file_path = None
    
    try:
        # اتصال به دیتابیس
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "خطا در اتصال به دیتابیس"}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # دریافت اطلاعات فایل قبل از حذف
        cursor.execute("SELECT file_path FROM analyses WHERE id = %s", (analysis_id,))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return jsonify({"error": "تحلیل یافت نشد"}), 404
        
        file_path = result['file_path']
        
        # حذف از دیتابیس
        cursor.execute("DELETE FROM analyses WHERE id = %s", (analysis_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        # حذف فایل از روی دیسک
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ فایل {file_path} با موفقیت حذف شد")
        
        print(f"✅ تحلیل CRM با ID {analysis_id} با موفقیت حذف شد")
        return jsonify({
            "success": True,
            "message": "تحلیل با موفقیت حذف شد"
        }), 200
        
    except Exception as e:
        print(f"❌ خطا در حذف تحلیل: {str(e)}")
        import traceback
        traceback.print_exc()
        
        if conn:
            conn.rollback()
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
        return jsonify({
            "error": True,
            "message": str(e)
        }), 500

@analysis_bp.route('/api/file/<int:analysis_id>')
@login_required
def download_file(analysis_id):
    """دانلود فایل مربوط به یک تحلیل"""
    analysis = AnalysisModel.get_by_id(analysis_id)
    if analysis and os.path.exists(analysis.get('file_path', '')):
        return send_file(
            analysis['file_path'],
            as_attachment=True,
            download_name=analysis['file_name']
        )
    return jsonify({"error": "فایل یافت نشد"}), 404