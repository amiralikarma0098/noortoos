# modules/routes/calculator.py
from flask import Blueprint, request, jsonify
from modules.auth.decorators import login_required

calculator_bp = Blueprint('calculator', __name__, url_prefix='/api/calculator')

@calculator_bp.route('/calculate', methods=['POST'])
@login_required
def calculate_power():
    """محاسبه توان مورد نیاز بر اساس وسایل"""
    data = request.json
    devices = data.get('devices', [])
    
    total_watt = 0
    for device in devices:
        # توان مصرفی دستگاه‌ها (وات)
        device_power = {
            'یخچال': 150,
            'فریزر': 200,
            'تلویزیون': 100,
            'کامپیوتر': 300,
            'مانیتور': 50,
            'مودم': 20,
            'لامپ': 60,
            'کولر': 1000,
            'پمپ آب': 800
        }.get(device.get('name'), 0)
        
        total_watt += device_power * device.get('count', 1)
    
    # محاسبه VA مورد نیاز (با ضریب ۱.۶)
    required_va = total_watt * 1.6
    
    # پیشنهاد محصولات مناسب
    from modules.academy.product_search import ProductSearch
    ps = ProductSearch()
    
    suitable_products = ps.search_products(f"{int(required_va)}VA", max_results=3)
    
    return jsonify({
        'success': True,
        'total_watt': total_watt,
        'required_va': round(required_va),
        'suggestions': [{
            'name': p.get('name'),
            'powerVA': p.get('powerVA'),
            'price': p.get('price'),
            'warranty': p.get('warranty')
        } for p in suitable_products]
    })