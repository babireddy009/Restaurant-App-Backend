"""
Image updater script - assigns food images to existing menu items.
Run: python update_images.py
"""
import os
import sys
import django

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from menu.models import MenuItem

IMAGE_MAP = {
    # Starters
    'Paneer Tikka':              '/images/paneer_tikka.png',
    'Chicken Tikka':             '/images/paneer_tikka.png',
    'Seekh Kebab':               '/images/paneer_tikka.png',
    'Veg Spring Rolls':          '/images/paneer_tikka.png',
    # Main Course
    'Butter Chicken':            '/images/butter_chicken.png',
    'Palak Paneer':              '/images/butter_chicken.png',
    'Dal Makhani':               '/images/butter_chicken.png',
    'Mutton Rogan Josh':         '/images/butter_chicken.png',
    # Biryani
    'Chicken Biryani':           '/images/chicken_biryani.png',
    'Hyderabadi Mutton Biryani': '/images/chicken_biryani.png',
    'Veg Biryani':               '/images/veg_biryani.png',
    'Jeera Rice':                '/images/veg_biryani.png',
    # Breads
    'Butter Naan':               '/images/garlic_naan.png',
    'Garlic Naan':               '/images/garlic_naan.png',
    'Cheese Naan':               '/images/garlic_naan.png',
    # Desserts
    'Gulab Jamun':               '/images/gulab_jamun.png',
    'Kulfi Falooda':             '/images/gulab_jamun.png',
    'Rasgulla':                  '/images/gulab_jamun.png',
    # Beverages
    'Mango Lassi':               '/images/mango_lassi.png',
    'Sweet Lassi':               '/images/mango_lassi.png',
    'Masala Chai':               '/images/mango_lassi.png',
    # Burgers
    'Classic Chicken Burger':    '/images/chicken_burger.png',
    'Double Patty Burger':       '/images/chicken_burger.png',
    'Veg Aloo Tikki Burger':     '/images/chicken_burger.png',
}

updated = 0
for name, img_url in IMAGE_MAP.items():
    count = MenuItem.objects.filter(name=name).update(image=img_url)
    if count:
        print(f"  [OK] {name}")
        updated += count
    else:
        print(f"  [SKIP] Not found in DB: {name}")

print(f"\nDone. Updated {updated} items with images.")
