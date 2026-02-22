# scripts/extract_products.py
import re
import json
import os

def extract_products():
    """استخراج محصولات از product.js و ذخیره به صورت JSON"""
    
    # مسیر فایل‌ها
    js_path = os.path.join(os.path.dirname(__file__), '..', 'product.js')
    json_path = os.path.join(os.path.dirname(__file__), '..', 'modules', 'academy', 'products.json')
    
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # پیدا کردن شروع آرایه
        start_idx = content.find('[')
        if start_idx == -1:
            print("❌ [ پیدا نشد")
            return False
        
        # پیدا کردن پایان آرایه
        bracket_count = 0
        in_string = False
        escape = False
        end_idx = -1
        
        for i in range(start_idx, len(content)):
            char = content[i]
            
            if not in_string:
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_idx = i + 1
                        break
                elif char == '"' or char == "'":
                    in_string = True
                    quote_char = char
            else:
                if char == '\\' and not escape:
                    escape = True
                elif char == quote_char and not escape:
                    in_string = False
                else:
                    escape = False
        
        if end_idx == -1:
            print("❌ ] پیدا نشد")
            return False
        
        # استخراج آرایه
        array_str = content[start_idx:end_idx]
        
        # پاکسازی اولیه
        # حذف کامنت‌های یک خطی
        array_str = re.sub(r'//.*?\n', '\n', array_str)
        
        # حذف کامنت‌های چند خطی
        array_str = re.sub(r'/\*.*?\*/', '', array_str, flags=re.DOTALL)
        
        # تبدیل به JSON معتبر
        # 1. تبدیل کلیدها به رشته
        array_str = re.sub(r'(\w+):', r'"\1":', array_str)
        
        # 2. تبدیل true/false به true/false (برای JSON)
        array_str = array_str.replace('true', 'true').replace('false', 'false')
        
        # 3. تبدیل null به null (برای JSON)
        array_str = array_str.replace('null', 'null')
        
        # 4. حذف کاماهای اضافی
        array_str = re.sub(r',\s*}', '}', array_str)
        array_str = re.sub(r',\s*\]', ']', array_str)
        
        # 5. اطمینان از اینکه رشته‌ها با دابل کوتیشن هستند
        # این بخش کمی پیچیده‌ست، برای سادگی فرض می‌کنیم همه چی درسته
        
        # ذخیره فایل موقت برای بررسی
        temp_path = os.path.join(os.path.dirname(__file__), '..', 'products_temp.json')
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(array_str)
        
        # حالا سعی می‌کنیم JSON رو بخونیم
        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            # ذخیره نهایی
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            
            print(f"✅ {len(products)} محصول با موفقیت استخراج شد!")
            print(f"📁 فایل JSON در: {json_path}")
            
            # پاک کردن فایل موقت
            os.remove(temp_path)
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ خطا در JSON: {e}")
            print("📄 فایل موقت در products_temp.json ذخیره شد")
            print("لطفاً این فایل را بررسی کنید")
            return False
            
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False

def create_manual_json():
    """ایجاد دستی یک فایل JSON نمونه برای شروع"""
    json_path = os.path.join(os.path.dirname(__file__), '..', 'modules', 'academy', 'products.json')
    
    # چند محصول نمونه
    sample_products = [
        {
            "id": "mm-pelank-450",
            "type": "UPS",
            "brand": "MEGAMODE",
            "name": "پلنک 450VA",
            "model": "PELANK 450",
            "powerVA": 450,
            "powerWatt": 270,
            "technology": "LINE_INTERACTIVE",
            "phase": "1/1",
            "batteryConfig": {"count": 1, "capacityAh": 4.5, "internal": True},
            "formFactor": "TOWER",
            "price": 84880000,
            "warranty": 18,
            "country": "TAIWAN",
            "stock": 15,
            "official": True,
            "specs": ["۴۵۰ ولت آمپر", "۲۷۰ وات", "۱ باتری ۴.۵ آمپر داخلی", "رگولاتور داخلی"]
        },
        {
            "id": "mm-pelank-650",
            "type": "UPS",
            "brand": "MEGAMODE",
            "name": "پلنک 650VA",
            "model": "PELANK 650",
            "powerVA": 650,
            "powerWatt": 390,
            "technology": "LINE_INTERACTIVE",
            "phase": "1/1",
            "batteryConfig": {"count": 1, "capacityAh": 7, "internal": True},
            "formFactor": "TOWER",
            "price": 112800000,
            "warranty": 18,
            "country": "TAIWAN",
            "stock": 12,
            "official": True,
            "specs": ["۶۵۰ ولت آمپر", "۳۹۰ وات", "۱ باتری ۷ آمپر داخلی", "رگولاتور داخلی"]
        }
    ]
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(sample_products, f, ensure_ascii=False, indent=2)
    
    print(f"✅ فایل JSON نمونه با {len(sample_products)} محصول ایجاد شد")
    return True

if __name__ == '__main__':
    print("1. تلاش برای استخراج خودکار محصولات...")
    if not extract_products():
        print("\n2. ایجاد فایل JSON نمونه...")
        create_manual_json()