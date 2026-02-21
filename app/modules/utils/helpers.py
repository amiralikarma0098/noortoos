import json
from datetime import datetime
import jdatetime

def to_persian_date(date):
    """تبدیل تاریخ میلادی به شمسی"""
    if not date:
        return ''
    try:
        return jdatetime.date.fromgregorian(date=date).strftime('%Y/%m/%d')
    except:
        return str(date)

def format_number(number):
    """فرمت کردن اعداد با جداکننده هزارگان"""
    try:
        return f"{int(number):,}"
    except:
        return str(number)

def safe_json_loads(data):
    """بارگذاری امن JSON"""
    if isinstance(data, str):
        try:
            return json.loads(data)
        except:
            return {}
    return data or {}