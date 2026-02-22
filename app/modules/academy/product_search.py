# modules/academy/product_search.py
import json
import os
import re
from typing import List, Dict, Any

class ProductSearch:
    def __init__(self):
        self.products = self._load_products()
        self._clean_products()
        print(f"✅ {len(self.products)} محصول بارگذاری شد")
    
    def _load_products(self) -> List[Dict[str, Any]]:
        """بارگذاری محصولات از فایل JSON"""
        try:
            json_path = os.path.join(os.path.dirname(__file__), 'products.json')
            
            if not os.path.exists(json_path):
                print(f"⚠️ فایل JSON پیدا نشد: {json_path}")
                return self._get_sample_products()
            
            with open(json_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            return products
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری محصولات: {e}")
            return self._get_sample_products()
    
    def _clean_products(self):
        """پاکسازی محصولات (حذف محصولات با قیمت صفر)"""
        valid_products = []
        for p in self.products:
            # فقط محصولات با قیمت صفر رو حذف کن
            if p.get('price', 0) <= 0:
                continue
            valid_products.append(p)
        
        self.products = valid_products
        print(f"🧹 {len(valid_products)} محصول معتبر پس از پاکسازی")
    
    def _get_sample_products(self) -> List[Dict[str, Any]]:
        """محصولات نمونه برای مواقع ضروری"""
        return [
            {
                "id": "mm-pelank-450",
                "type": "UPS",
                "brand": "MEGAMODE",
                "name": "پلنک 450VA",
                "model": "PELANK 450",
                "powerVA": 450,
                "powerWatt": 270,
                "price": 84880000,
                "warranty": 18
            }
        ]
    
    def extract_power_needs(self, query: str) -> Dict[str, Any]:
        """استخراج نیازهای توانی از سوال کاربر"""
        query = query.lower()
        result = {
            'min_va': 0,
            'max_va': 10000,
            'devices': [],
            'usage_type': 'unknown',
            'requested_power': None
        }
        
        # استخراج اعداد (توان درخواستی)
        numbers = re.findall(r'(\d+)', query)
        for num in numbers:
            num_int = int(num)
            if 100 <= num_int <= 20000:
                result['requested_power'] = num_int
                result['min_va'] = num_int * 0.5  # بازه وسیع‌تر
                result['max_va'] = num_int * 2.0   # بازه وسیع‌تر
                break
        
        return result
    
    def search_products(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """جستجوی ۵ محصول مرتبط با سوال کاربر"""
        query = query.lower()
        power_needs = self.extract_power_needs(query)
        scored_products = []
        
        for product in self.products:
            score = 0
            
            # اطلاعات محصول
            name = product.get('name', '').lower()
            model = product.get('model', '').lower()
            power = product.get('powerVA', 0)
            
            # 1. تطابق با کلمه "پلنک" (امتیاز بالا)
            if 'پلنک' in query and 'پلنک' in name:
                score += 50
            
            # 2. تطابق با برندها
            brands = ['ولتاماکس', 'ولتا', 'گیت', 'فاراطل', 'ایستاده', 'رکمونت']
            for brand in brands:
                if brand in query and brand in name:
                    score += 40
            
            # 3. تطابق توان (بازه وسیع)
            if power_needs['requested_power']:
                diff = abs(power - power_needs['requested_power'])
                if diff < 200:
                    score += 30
                elif diff < 500:
                    score += 20
                elif diff < 1000:
                    score += 10
                else:
                    # حتی اگه خیلی دور باشه، یه امتیاز کوچیک بده
                    score += 5
            
            # 4. محصولات با گارانتی بالاتر
            warranty = product.get('warranty', 0)
            score += warranty // 6  # هر ۶ ماه یه امتیاز
            
            # 5. موجودی انبار
            if product.get('stock', 0) > 0:
                score += 5
            
            # همیشه یه امتیاز پایه بده تا همه محصولات شانس داشته باشن
            score += 1
            
            scored_products.append((score, product))
        
        # مرتب‌سازی نزولی بر اساس امتیاز
        scored_products.sort(reverse=True, key=lambda x: x[0])
        
        # برگرداندن max_results محصول برتر
        return [p for s, p in scored_products[:max_results]]
    
    def get_products_text(self, products: List[Dict[str, Any]], detailed: bool = False) -> str:
        """ایجاد متن محصولات برای پرامپت"""
        if not products:
            return "❌ محصول مرتبطی یافت نشد."
        
        text = "## محصولات پیشنهادی نور توس:\n\n"
        
        for i, p in enumerate(products, 1):
            name = p.get('name', 'نامشخص')
            model = p.get('model', '')
            power = p.get('powerVA', 0)
            watt = p.get('powerWatt', 0)
            price = p.get('price', 0)
            warranty = p.get('warranty', 18)
            
            # قیمت به میلیون تومان
            price_million = price / 1000000
            
            text += f"{i}. **{name}** - {model}\n"
            text += f"   - توان: {power}VA / {watt}W\n"
            text += f"   - قیمت: {price_million:,.0f} میلیون تومان\n"
            text += f"   - گارانتی: {warranty} ماه\n"
            
            if detailed:
                specs = p.get('specs', [])
                if specs:
                    text += "   - ویژگی‌ها:\n"
                    for spec in specs[:2]:
                        text += f"     • {spec}\n"
            
            text += "\n"
        
        return text
    
    def format_price(self, price: int) -> str:
        """تبدیل قیمت به فرمت خوانا"""
        if price >= 1000000000:
            return f"{price/1000000000:.1f} میلیارد تومان"
        elif price >= 1000000:
            return f"{price/1000000:.0f} میلیون تومان"
        else:
            return f"{price:,} ریال"