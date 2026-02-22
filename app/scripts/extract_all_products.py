# scripts/extract_all_products.py
import re
import json
import os

def extract_all_products():
    """استخراج تمام محصولات از product.js با روش مطمئن‌تر"""
    
    js_path = os.path.join(os.path.dirname(__file__), '..', 'product.js')
    json_path = os.path.join(os.path.dirname(__file__), '..', 'modules', 'academy', 'products.json')
    
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # روش ساده‌تر: پیدا کردن همه اشیاء بین {}
        products = []
        
        # الگوی هر محصول
        pattern = r'{\s*id:\s*"([^"]+)",.*?name:\s*"([^"]+)",.*?model:\s*"([^"]+)",.*?powerVA:\s*(\d+),.*?powerWatt:\s*(\d+),.*?price:\s*(\d+),.*?warranty:\s*(\d+),.*?}'
        
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                product = {
                    "id": match.group(1),
                    "name": match.group(2),
                    "model": match.group(3),
                    "powerVA": int(match.group(4)),
                    "powerWatt": int(match.group(5)),
                    "price": int(match.group(6)),
                    "warranty": int(match.group(7)),
                    "type": "UPS",
                    "brand": "MEGAMODE"
                }
                products.append(product)
            except:
                continue
        
        if products:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            
            print(f"✅ {len(products)} محصول با موفقیت استخراج شد!")
            return True
        else:
            print("❌ هیچ محصولی استخراج نشد!")
            return False
            
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False

if __name__ == '__main__':
    extract_all_products()