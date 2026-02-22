# test_product.py
from modules.academy.product_search import ProductSearch

# تست بارگذاری
print("در حال تست ProductSearch...")
ps = ProductSearch()
print(f"تعداد محصولات: {len(ps.products)}")

# تست جستجو
test_queries = [
    "ups 450",
    "یوپیاس برای یخچال",
    "استابلایزر",
    "پلنک 1000"
]

for query in test_queries:
    print(f"\n🔍 جستجو برای: {query}")
    results = ps.search_products(query, max_results=3)
    print(f"تعداد نتایج: {len(results)}")
    for p in results:
        price_str = ps.format_price(p.get('price', 0))
        print(f"  - {p.get('name')}: {p.get('powerVA')}VA - {price_str}")
    
    # نمایش متن آماده برای پرامپت
    print("\n📝 متن آماده برای پرامپت:")
    print(ps.get_products_text(results, detailed=False))
    print("-" * 50)