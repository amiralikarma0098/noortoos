# modules/routes/price_list.py
from flask import Blueprint, jsonify, request, session
from modules.auth.decorators import login_required
import json
import os

price_list_bp = Blueprint('price_list', __name__, url_prefix='/api/products')

@price_list_bp.route('/list', methods=['GET'])
@login_required
def get_products_list():
    """دریافت لیست محصولات از فایل product.js"""
    try:
        # مسیر فایل product.js
        js_path = os.path.join(os.path.dirname(__file__), '..', '..', 'product.js')
        
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # استخراج آرایه محصولات
        import re
        match = re.search(r'export const NOORTOOS_PRODUCTS = (\[.*?\]);', content, re.DOTALL)
        
        if not match:
            return jsonify({'success': False, 'error': 'آرایه محصولات پیدا نشد'}), 500
        
        products_str = match.group(1)
        
        # حذف کامنت‌ها
        products_str = re.sub(r'//.*?\n', '\n', products_str)
        
        # تبدیل به JSON
        import ast
        # جایگزینی true/false با True/False برای Python
        products_str = products_str.replace('true', 'True').replace('false', 'False')
        products = ast.literal_eval(products_str)
        
        return jsonify({
            'success': True,
            'products': products
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@price_list_bp.route('/update-prices', methods=['POST'])
@login_required
def update_prices():
    """ذخیره تغییرات قیمت‌ها"""
    data = request.json
    prices = data.get('prices', {})
    
    if not prices:
        return jsonify({'success': False, 'error': 'هیچ تغییری اعمال نشده'}), 400
    
    try:
        # اینجا باید توی دیتابیس ذخیره کنی
        # فعلاً فقط یه پیام موفقیت برمی‌گردونیم
        return jsonify({
            'success': True,
            'message': f'{len(prices)} محصول با موفقیت به‌روزرسانی شد'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500