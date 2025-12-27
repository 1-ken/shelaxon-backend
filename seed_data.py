"""
Seed script to create subcategories and products
Run with: python manage.py shell < seed_data.py
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retailconnect.settings')
django.setup()

from apps.products.models import Category, Product
from apps.users.models import User
from django.utils.text import slugify
from decimal import Decimal
import random

# Get or create a wholesaler user for products
wholesaler, created = User.objects.get_or_create(
    username='demo_wholesaler',
    defaults={
        'phone_number': '+254700000001',
        'user_type': 'wholesaler',
        'business_name': 'Demo Wholesale Kenya',
        'city': 'Nairobi',
        'is_verified': True,
    }
)
if created:
    wholesaler.set_password('DemoPass123!')
    wholesaler.save()
    from apps.users.models import WholesalerProfile
    WholesalerProfile.objects.create(user=wholesaler)
    print(f"Created wholesaler: {wholesaler.username}")
else:
    print(f"Using existing wholesaler: {wholesaler.username}")

# Define subcategories for each parent category
SUBCATEGORIES = {
    'Beverages': [
        ('Soft Drinks', 'soft-drinks', 'Carbonated and non-carbonated soft drinks'),
        ('Juices', 'juices', 'Fresh and packaged fruit juices'),
        ('Water', 'water', 'Bottled and mineral water'),
        ('Tea & Coffee', 'tea-coffee', 'Tea leaves, coffee beans and instant coffee'),
        ('Energy Drinks', 'energy-drinks', 'Energy and sports drinks'),
    ],
    'Food & Groceries': [
        ('Rice & Grains', 'rice-grains', 'Rice, wheat, maize and other grains'),
        ('Flour & Baking', 'flour-baking', 'Wheat flour, maize flour and baking supplies'),
        ('Pasta & Noodles', 'pasta-noodles', 'Spaghetti, macaroni and instant noodles'),
        ('Canned Foods', 'canned-foods', 'Canned vegetables, fish and meat'),
        ('Sugar & Salt', 'sugar-salt', 'Sugar, salt and sweeteners'),
    ],
    'Household Items': [
        ('Kitchenware', 'kitchenware', 'Pots, pans, utensils and kitchen tools'),
        ('Laundry', 'laundry', 'Detergents, fabric softeners and laundry supplies'),
        ('Home Decor', 'home-decor', 'Decorative items for the home'),
        ('Storage', 'storage', 'Storage containers and organizers'),
    ],
    'Personal Care': [
        ('Skin Care', 'skin-care', 'Lotions, creams and skin care products'),
        ('Hair Care', 'hair-care', 'Shampoos, conditioners and hair treatments'),
        ('Oral Care', 'oral-care', 'Toothpaste, toothbrushes and mouthwash'),
        ('Body Care', 'body-care', 'Soaps, shower gels and body lotions'),
    ],
    'Cleaning Supplies': [
        ('Floor Cleaners', 'floor-cleaners', 'Mops, brooms and floor cleaning solutions'),
        ('Dish Washing', 'dish-washing', 'Dish soap, sponges and dish cleaning supplies'),
        ('Disinfectants', 'disinfectants', 'Sanitizers and disinfectant sprays'),
        ('Air Fresheners', 'air-fresheners', 'Room sprays and air freshening products'),
    ],
    'Dairy Products': [
        ('Milk', 'milk', 'Fresh, UHT and powdered milk'),
        ('Cheese', 'cheese', 'Various types of cheese'),
        ('Yogurt', 'yogurt', 'Plain and flavored yogurt'),
        ('Butter & Margarine', 'butter-margarine', 'Butter, margarine and spreads'),
    ],
    'Snacks & Confectionery': [
        ('Biscuits', 'biscuits', 'Sweet and savory biscuits'),
        ('Chocolates', 'chocolates', 'Chocolate bars and assorted chocolates'),
        ('Chips & Crisps', 'chips-crisps', 'Potato chips and corn snacks'),
        ('Sweets & Candy', 'sweets-candy', 'Candies, lollipops and gums'),
    ],
    'Cooking Oil & Spices': [
        ('Cooking Oil', 'cooking-oil', 'Vegetable oil, sunflower oil and olive oil'),
        ('Spices', 'spices', 'Ground spices and whole spices'),
        ('Seasonings', 'seasonings', 'Stock cubes, soy sauce and seasonings'),
    ],
    'Baby Products': [
        ('Baby Food', 'baby-food', 'Baby formula, cereals and snacks'),
        ('Diapers', 'diapers', 'Disposable and cloth diapers'),
        ('Baby Care', 'baby-care', 'Baby lotions, powders and wipes'),
    ],
    'Electronics': [
        ('Phone Accessories', 'phone-accessories', 'Chargers, cases and screen protectors'),
        ('Batteries', 'batteries', 'AA, AAA and rechargeable batteries'),
        ('Bulbs & Lighting', 'bulbs-lighting', 'LED bulbs and lighting fixtures'),
    ],
}

# Products for each subcategory
PRODUCTS = {
    'soft-drinks': [
        ('Coca Cola 500ml', 'coca-cola-500ml', 'Classic Coca Cola 500ml bottle', 60, 55, 24, 'bottle'),
        ('Fanta Orange 500ml', 'fanta-orange-500ml', 'Fanta Orange flavored soda 500ml', 60, 55, 24, 'bottle'),
        ('Sprite 500ml', 'sprite-500ml', 'Sprite lemon-lime soda 500ml', 60, 55, 24, 'bottle'),
        ('Coca Cola 2L', 'coca-cola-2l', 'Coca Cola 2 liter bottle', 180, 165, 6, 'bottle'),
        ('Pepsi 500ml', 'pepsi-500ml', 'Pepsi Cola 500ml bottle', 55, 50, 24, 'bottle'),
    ],
    'juices': [
        ('Delmonte Mango Juice 1L', 'delmonte-mango-1l', 'Del Monte mango juice 1 liter', 180, 165, 12, 'pack'),
        ('Afia Apple Juice 1L', 'afia-apple-1l', 'Afia apple juice 1 liter tetra pack', 170, 155, 12, 'pack'),
        ('Pick N Peel Orange 500ml', 'picknpeel-orange-500ml', 'Pick N Peel orange juice', 80, 72, 24, 'bottle'),
    ],
    'water': [
        ('Keringet Water 500ml', 'keringet-500ml', 'Keringet mineral water 500ml', 30, 25, 24, 'bottle'),
        ('Dasani Water 1L', 'dasani-1l', 'Dasani purified water 1 liter', 50, 45, 12, 'bottle'),
        ('Aquamist 18.9L', 'aquamist-18l', 'Aquamist dispenser water 18.9L', 350, 320, 1, 'bottle'),
    ],
    'tea-coffee': [
        ('Kericho Gold Tea 100 bags', 'kericho-gold-100', 'Kericho Gold premium tea bags', 280, 250, 12, 'box'),
        ('Nescafe Classic 200g', 'nescafe-classic-200g', 'Nescafe Classic instant coffee', 650, 600, 12, 'jar'),
        ('Dormans Coffee 250g', 'dormans-250g', 'Dormans Kenya AA ground coffee', 450, 420, 12, 'pack'),
    ],
    'rice-grains': [
        ('Pishori Rice 5kg', 'pishori-rice-5kg', 'Premium Kenyan Pishori rice', 850, 780, 10, 'bag'),
        ('Basmati Rice 5kg', 'basmati-rice-5kg', 'Long grain Basmati rice', 1200, 1100, 10, 'bag'),
        ('White Maize 10kg', 'white-maize-10kg', 'Dry white maize for ugali', 600, 550, 10, 'bag'),
        ('Sorghum 5kg', 'sorghum-5kg', 'Red sorghum grain', 400, 360, 10, 'bag'),
    ],
    'flour-baking': [
        ('Ajab Wheat Flour 2kg', 'ajab-flour-2kg', 'Ajab all-purpose wheat flour', 180, 165, 12, 'pack'),
        ('Jogoo Maize Flour 2kg', 'jogoo-flour-2kg', 'Jogoo maize flour for ugali', 160, 145, 12, 'pack'),
        ('Exe Baking Powder 100g', 'exe-baking-100g', 'Exe baking powder', 85, 75, 48, 'tin'),
        ('Ndovu Wheat Flour 2kg', 'ndovu-flour-2kg', 'Ndovu wheat flour', 175, 160, 12, 'pack'),
    ],
    'cooking-oil': [
        ('Elianto Cooking Oil 5L', 'elianto-5l', 'Elianto sunflower cooking oil', 1450, 1350, 4, 'jerrycan'),
        ('Golden Fry 5L', 'goldenfry-5l', 'Golden Fry vegetable oil', 1200, 1100, 4, 'jerrycan'),
        ('Rina Cooking Oil 3L', 'rina-3l', 'Rina vegetable cooking oil', 750, 690, 6, 'bottle'),
        ('Olive Gold 500ml', 'olivegold-500ml', 'Extra virgin olive oil', 850, 780, 12, 'bottle'),
    ],
    'sugar-salt': [
        ('Mumias Sugar 2kg', 'mumias-sugar-2kg', 'Mumias refined white sugar', 280, 260, 10, 'pack'),
        ('Kabras Sugar 1kg', 'kabras-sugar-1kg', 'Kabras brown sugar', 150, 138, 20, 'pack'),
        ('Kensalt 1kg', 'kensalt-1kg', 'Kensalt iodized table salt', 45, 40, 24, 'pack'),
    ],
    'milk': [
        ('KCC Fresh Milk 500ml', 'kcc-milk-500ml', 'KCC fresh pasteurized milk', 65, 58, 24, 'pack'),
        ('Brookside Milk 1L', 'brookside-1l', 'Brookside fresh milk 1 liter', 130, 118, 12, 'pack'),
        ('Nido Powdered Milk 400g', 'nido-400g', 'Nido instant powdered milk', 520, 480, 24, 'tin'),
    ],
    'biscuits': [
        ('Britania Glucose 200g', 'britania-glucose-200g', 'Britania glucose biscuits', 55, 48, 48, 'pack'),
        ('Manji Crackers 200g', 'manji-crackers-200g', 'Manji cream crackers', 85, 75, 48, 'pack'),
        ('Oreo Cookies 154g', 'oreo-154g', 'Oreo chocolate sandwich cookies', 150, 135, 24, 'pack'),
    ],
    'diapers': [
        ('Pampers Size 3 (58pcs)', 'pampers-s3-58', 'Pampers baby dry size 3', 1800, 1650, 3, 'pack'),
        ('Huggies Size 4 (50pcs)', 'huggies-s4-50', 'Huggies ultra comfort size 4', 1650, 1520, 3, 'pack'),
        ('Softcare Diapers M (40pcs)', 'softcare-m-40', 'Softcare baby diapers medium', 950, 870, 6, 'pack'),
    ],
    'skin-care': [
        ('Nivea Body Lotion 400ml', 'nivea-lotion-400ml', 'Nivea nourishing body lotion', 650, 590, 12, 'bottle'),
        ('Vaseline Jelly 250ml', 'vaseline-250ml', 'Vaseline petroleum jelly', 280, 255, 24, 'jar'),
        ('Arimis Cream 250ml', 'arimis-250ml', 'Arimis moisturizing cream', 180, 165, 24, 'jar'),
    ],
    'oral-care': [
        ('Colgate Toothpaste 100ml', 'colgate-100ml', 'Colgate maximum cavity protection', 150, 135, 48, 'tube'),
        ('Close Up Toothpaste 120ml', 'closeup-120ml', 'Close Up deep action toothpaste', 165, 150, 48, 'tube'),
        ('Oral B Toothbrush Medium', 'oralb-medium', 'Oral B medium bristle toothbrush', 120, 105, 72, 'piece'),
    ],
    'dish-washing': [
        ('Liquid Dish Soap 500ml', 'dish-soap-500ml', 'Liquid dish washing soap', 85, 75, 24, 'bottle'),
        ('Vim Scouring Powder 500g', 'vim-500g', 'Vim scouring powder', 95, 85, 24, 'tin'),
        ('Steel Wool (Pack of 6)', 'steel-wool-6', 'Steel wool scouring pads', 60, 52, 48, 'pack'),
    ],
    'disinfectants': [
        ('Jik Bleach 750ml', 'jik-750ml', 'Jik multipurpose bleach', 180, 165, 12, 'bottle'),
        ('Dettol Antiseptic 500ml', 'dettol-500ml', 'Dettol antiseptic liquid', 450, 410, 12, 'bottle'),
        ('Hand Sanitizer 500ml', 'sanitizer-500ml', 'Antibacterial hand sanitizer', 350, 320, 24, 'bottle'),
    ],
}

# Create subcategories
print("\n--- Creating Subcategories ---")
subcategory_count = 0
for parent_name, subs in SUBCATEGORIES.items():
    try:
        parent = Category.objects.get(name=parent_name)
        for name, slug, description in subs:
            subcat, created = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': description,
                    'parent': parent,
                    'is_active': True,
                }
            )
            if created:
                subcategory_count += 1
                print(f"  Created: {name} (under {parent_name})")
            else:
                print(f"  Exists: {name}")
    except Category.DoesNotExist:
        print(f"  Parent category not found: {parent_name}")

print(f"\nCreated {subcategory_count} new subcategories")

# Create products
print("\n--- Creating Products ---")
product_count = 0
sku_counter = 1000

for cat_slug, products in PRODUCTS.items():
    try:
        category = Category.objects.get(slug=cat_slug)
        for name, slug, description, unit_price, bulk_price, min_qty, uom in products:
            sku = f"SKU-{sku_counter:05d}"
            sku_counter += 1
            
            product, created = Product.objects.get_or_create(
                wholesaler=wholesaler,
                slug=slug,
                defaults={
                    'category': category,
                    'name': name,
                    'description': description,
                    'sku': sku,
                    'unit_price': Decimal(str(unit_price)),
                    'bulk_price': Decimal(str(bulk_price)),
                    'bulk_quantity': min_qty,
                    'minimum_order_quantity': min_qty,
                    'unit_of_measure': uom,
                    'stock_quantity': random.randint(50, 500),
                    'is_active': True,
                }
            )
            if created:
                product_count += 1
                print(f"  Created: {name}")
            else:
                print(f"  Exists: {name}")
    except Category.DoesNotExist:
        print(f"  Category not found: {cat_slug}")

print(f"\nCreated {product_count} new products")
print("\n=== Seed data complete! ===")
