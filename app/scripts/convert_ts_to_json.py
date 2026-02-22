# scripts/convert_ts_to_json.py
import re
import json

def convert_ts_to_json():
    with open('/Users/amiralikarma/Documents/GitHub/noortoos/app/products.ts', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # استخراج آرایه محصولات
    # این regex رو باید بر اساس ساختار فایل products.ts تنظیم کنی
    match = re.search(r'export const NOORTOOS_PRODUCTS: Product\[\] = (\[.*?\]);', content, re.DOTALL)
    
    if match:
        products_str = match.group(1)
        
        # پاک کردن type annotations و تبدیل به JSON معتبر
        # این بخش رو باید بر اساس ساختار واقعی فایل تنظیم کنی
        products_str = re.sub(r'(\w+):', r'"\1":', products_str)
        products_str = re.sub(r',\s*}', '}', products_str)
        products_str = re.sub(r',\s*\]', ']', products_str)
        
        try:
            products = json.loads(products_str)
            
            # ذخیره به عنوان JSON
            with open('modules/academy/products.json', 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            
            print(f"✅ {len(products)} محصول با موفقیت به JSON تبدیل شد")
            
        except json.JSONDecodeError as e:
            print(f"❌ خطا در تبدیل JSON: {e}")
            print("لطفاً فایل products.ts را بررسی کنید")
    else:
        print("❌ آرایه محصولات پیدا نشد")

if __name__ == '__main__':
    convert_ts_to_json()