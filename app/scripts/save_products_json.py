# scripts/save_products_json.py
import json

# محصولات واقعی که از extract_products استخراج شد
products = [
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
    },
    {
        "id": "mm-pelank-800",
        "type": "UPS",
        "brand": "MEGAMODE",
        "name": "پلنک 800VA",
        "model": "PELANK 800",
        "powerVA": 800,
        "powerWatt": 480,
        "technology": "LINE_INTERACTIVE",
        "phase": "1/1",
        "batteryConfig": {"count": 2, "capacityAh": 4.5, "internal": True},
        "formFactor": "TOWER",
        "price": 125600000,
        "warranty": 18,
        "country": "TAIWAN",
        "stock": 10,
        "official": True,
        "specs": ["۸۰۰ ولت آمپر", "۴۸۰ وات", "۲ باتری ۴.۵ آمپر داخلی", "رگولاتور داخلی"]
    },
    {
        "id": "mm-pelank-1000",
        "type": "UPS",
        "brand": "MEGAMODE",
        "name": "پلنک 1000VA",
        "model": "PELANK 1000",
        "powerVA": 1000,
        "powerWatt": 600,
        "technology": "LINE_INTERACTIVE",
        "phase": "1/1",
        "batteryConfig": {"count": 2, "capacityAh": 7, "internal": True},
        "formFactor": "TOWER",
        "price": 170000000,
        "warranty": 18,
        "country": "TAIWAN",
        "stock": 8,
        "official": True,
        "specs": ["۱۰۰۰ ولت آمپر", "۶۰۰ وات", "۲ باتری ۷ آمپر داخلی", "رگولاتور داخلی"]
    },
    {
        "id": "mm-pelank-1500",
        "type": "UPS",
        "brand": "MEGAMODE",
        "name": "پلنک 1500VA",
        "model": "PELANK 1500",
        "powerVA": 1500,
        "powerWatt": 900,
        "technology": "LINE_INTERACTIVE",
        "phase": "1/1",
        "batteryConfig": {"count": 2, "capacityAh": 9, "internal": True},
        "formFactor": "TOWER",
        "price": 250000000,
        "warranty": 18,
        "country": "TAIWAN",
        "stock": 5,
        "official": True,
        "specs": ["۱۵۰۰ ولت آمپر", "۹۰۰ وات", "۲ باتری ۹ آمپر داخلی", "رگولاتور داخلی"]
    }
]

# ذخیره در فایل JSON
import os
json_path = os.path.join(os.path.dirname(__file__), '..', 'modules', 'academy', 'products.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"✅ {len(products)} محصول در {json_path} ذخیره شد")