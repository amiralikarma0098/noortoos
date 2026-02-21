import json
from flask import Blueprint, request, jsonify, render_template, send_file
import os
from modules.auth.decorators import login_required
from datetime import datetime
from modules.file_handler import FileHandler
from modules.openai_client import OpenAIClient
from modules.models import ReferralAnalysisModel
from modules.config import Config
from modules.database import get_db_connection  # اضافه کردن این خط

referral_bp = Blueprint('referral', __name__)
file_handler = FileHandler(Config.UPLOAD_FOLDER)
ai_client = OpenAIClient()

@referral_bp.route('/referral')
@login_required
def referral_page():
    """صفحه تحلیل ارجاعیات"""
    return render_template('referral.html')

@referral_bp.route('/referral-history')
@login_required
def referral_history_page():
    """صفحه تاریخچه ارجاعیات"""
    return render_template('referral_history.html')

@referral_bp.route('/api/analyze-referral', methods=['POST'])
@login_required
def analyze_referral():
    """API برای تحلیل فایل ارجاعیات"""
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
        analysis = ai_client.analyze_referral(content)
        
        if analysis.get('error'):
            file_handler.delete_file(file_info['path'])
            return jsonify(analysis), 400
        
        analysis['analyzed_at'] = datetime.now().isoformat()
        analysis['file_name'] = file_info['name']
        
        # ذخیره در دیتابیس
        analysis_id = ReferralAnalysisModel.save(file_info, analysis)
        
        if analysis_id:
            analysis['id'] = analysis_id
            print(f"✅ تحلیل ارجاعیات با ID {analysis_id} ذخیره شد")
        
        return jsonify(analysis)
        
    except Exception as e:
        print(f"❌ خطا در analyze_referral: {str(e)}")
        import traceback
        traceback.print_exc()
        
        if file_info and os.path.exists(file_info['path']):
            file_handler.delete_file(file_info['path'])
        
        return jsonify({
            "error": True,
            "message": str(e)
        }), 500

@referral_bp.route('/api/referral-history')
@login_required
def get_referral_history():
    """دریافت تاریخچه تحلیل‌های ارجاعیات"""
    try:
        analyses = ReferralAnalysisModel.get_all()
        return jsonify(analyses)
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        return jsonify([])

@referral_bp.route('/api/referral-analysis/<int:analysis_id>')
@login_required
def get_referral_analysis(analysis_id):
    """دریافت جزئیات یک تحلیل ارجاعیات"""
    try:
        analysis = ReferralAnalysisModel.get_by_id(analysis_id)
        
        if not analysis:
            return jsonify({"error": "یافت نشد"}), 404
        
        # Parse JSON
        if analysis.get('full_analysis'):
            analysis['full_analysis'] = json.loads(analysis['full_analysis'])
        
        return jsonify(analysis)
        
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        return jsonify({"error": str(e)}), 500

@referral_bp.route('/api/referral-analysis/<int:analysis_id>', methods=['DELETE'])
@login_required
def delete_referral_analysis(analysis_id):
    """حذف یک تحلیل ارجاعیات به همراه فایل مرتبط"""
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
        cursor.execute("SELECT file_path FROM referral_analyses WHERE id = %s", (analysis_id,))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return jsonify({"error": "تحلیل یافت نشد"}), 404
        
        file_path = result['file_path']
        
        # حذف از دیتابیس
        cursor.execute("DELETE FROM referral_analyses WHERE id = %s", (analysis_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        # حذف فایل از روی دیسک
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ فایل {file_path} با موفقیت حذف شد")
        
        print(f"✅ تحلیل با ID {analysis_id} با موفقیت حذف شد")
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

@referral_bp.route('/api/referral/latest')
def get_latest_referral_analysis():
    """دریافت آخرین تحلیل ارجاعیات"""
    try:
        analysis = ReferralAnalysisModel.get_latest()
        
        if analysis and analysis.get('full_analysis'):
            analysis['full_analysis'] = json.loads(analysis['full_analysis'])
            return jsonify(analysis['full_analysis'])
        
        return jsonify({"error": "تحلیلی یافت نشد"}), 404
        
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        return jsonify({"error": True, "message": str(e)}), 500

@referral_bp.route('/api/referral-report/<int:analysis_id>')
@login_required
def download_referral_report(analysis_id):
    """دانلود گزارش Excel از تحلیل ارجاعیات"""
    try:
        analysis = ReferralAnalysisModel.get_by_id(analysis_id)
        
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
            if analysis.get('full_analysis'):
                full = json.loads(analysis['full_analysis']) if isinstance(analysis['full_analysis'], str) else analysis['full_analysis']
                
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
        print(f"❌ خطا: {str(e)}")
        return jsonify({"error": str(e)}), 500