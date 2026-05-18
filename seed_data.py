"""
Sample data seed script for the restaurant app.
Run: python seed_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from menu.models import Category, MenuItem
from django.contrib.auth import get_user_model

User = get_user_model()

# Create sample categories
categories_data = [
    {'name': 'Starters', 'description': 'Delicious appetizers to start your meal', 'sort_order': 1},
    {'name': 'Main Course', 'description': 'Hearty mains for the perfect meal', 'sort_order': 2},
    {'name': 'Biryani & Rice', 'description': 'Fragrant biryanis and rice dishes', 'sort_order': 3},
    {'name': 'Breads', 'description': 'Fresh baked naan and rotis', 'sort_order': 4},
    {'name': 'Desserts', 'description': 'Sweet endings to your meal', 'sort_order': 5},
    {'name': 'Beverages', 'description': 'Refreshing drinks and lassi', 'sort_order': 6},
    {'name': 'Pizza', 'description': 'Wood-fired pizzas with fresh ingredients', 'sort_order': 7},
    {'name': 'Burgers', 'description': 'Juicy burgers with signature sauces', 'sort_order': 8},
]

categories = {}
for cat_data in categories_data:
    cat, created = Category.objects.get_or_create(name=cat_data['name'], defaults=cat_data)
    categories[cat.name] = cat
    print(f"{'Created' if created else 'Exists'}: Category '{cat.name}'")

# Create sample menu items
menu_items = [
    # Starters
    {'category': 'Starters', 'name': 'Paneer Tikka', 'description': 'Marinated cottage cheese grilled to perfection with spices', 'price': 249.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'medium', 'rating': 4.5, 'rating_count': 120},
    {'category': 'Starters', 'name': 'Chicken Tikka', 'description': 'Tender chicken marinated in yogurt and spices, grilled in tandoor', 'price': 299.00, 'is_vegetarian': False, 'is_featured': True, 'is_bestseller': True, 'spice_level': 'medium', 'rating': 4.7, 'rating_count': 250},
    {'category': 'Starters', 'name': 'Veg Spring Rolls', 'description': 'Crispy rolls filled with fresh vegetables and noodles', 'price': 179.00, 'is_vegetarian': True, 'spice_level': 'mild', 'rating': 4.2, 'rating_count': 80},
    {'category': 'Starters', 'name': 'Seekh Kebab', 'description': 'Minced mutton kebabs with aromatic spices', 'price': 329.00, 'is_vegetarian': False, 'is_bestseller': True, 'spice_level': 'hot', 'rating': 4.6, 'rating_count': 175},

    # Main Course
    {'category': 'Main Course', 'name': 'Butter Chicken', 'description': 'Tender chicken in rich tomato-based creamy sauce', 'price': 349.00, 'is_vegetarian': False, 'is_featured': True, 'is_bestseller': True, 'spice_level': 'mild', 'rating': 4.8, 'rating_count': 500, 'image': '/images/butter_chicken.png'},
    {'category': 'Main Course', 'name': 'Palak Paneer', 'description': 'Fresh cottage cheese cubes in smooth spinach gravy', 'price': 279.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'mild', 'rating': 4.4, 'rating_count': 200},
    {'category': 'Main Course', 'name': 'Dal Makhani', 'description': 'Slow-cooked black lentils with butter and cream', 'price': 229.00, 'is_vegetarian': True, 'is_bestseller': True, 'spice_level': 'mild', 'rating': 4.5, 'rating_count': 180},
    {'category': 'Main Course', 'name': 'Mutton Rogan Josh', 'description': 'Kashmiri-style mutton curry with bold spices', 'price': 429.00, 'is_vegetarian': False, 'spice_level': 'hot', 'rating': 4.7, 'rating_count': 140},

    # Biryani
    {'category': 'Biryani & Rice', 'name': 'Chicken Biryani', 'description': 'Fragrant basmati rice cooked with tender chicken and whole spices', 'price': 359.00, 'is_vegetarian': False, 'is_featured': True, 'is_bestseller': True, 'spice_level': 'medium', 'rating': 4.9, 'rating_count': 650, 'image': '/images/chicken_biryani.png'},
    {'category': 'Biryani & Rice', 'name': 'Veg Biryani', 'description': 'Aromatic basmati rice with seasonal vegetables and saffron', 'price': 279.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'medium', 'rating': 4.3, 'rating_count': 220, 'image': '/images/veg_biryani.png'},
    {'category': 'Biryani & Rice', 'name': 'Hyderabadi Mutton Biryani', 'description': 'Slow-cooked dum biryani with tender mutton pieces', 'price': 449.00, 'is_vegetarian': False, 'is_bestseller': True, 'spice_level': 'hot', 'rating': 4.8, 'rating_count': 380},
    {'category': 'Biryani & Rice', 'name': 'Jeera Rice', 'description': 'Light basmati rice tempered with cumin seeds', 'price': 129.00, 'is_vegetarian': True, 'spice_level': 'none', 'rating': 4.1, 'rating_count': 90},

    # Breads
    {'category': 'Breads', 'name': 'Butter Naan', 'description': 'Soft leavened bread baked in tandoor with butter', 'price': 49.00, 'is_vegetarian': True, 'spice_level': 'none', 'rating': 4.5, 'rating_count': 300},
    {'category': 'Breads', 'name': 'Garlic Naan', 'description': 'Naan topped with minced garlic and coriander', 'price': 59.00, 'is_vegetarian': True, 'is_bestseller': True, 'spice_level': 'none', 'rating': 4.7, 'rating_count': 280, 'image': '/images/garlic_naan.png'},
    {'category': 'Breads', 'name': 'Cheese Naan', 'description': 'Stuffed naan filled with melted cheese', 'price': 89.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'none', 'rating': 4.6, 'rating_count': 150},

    # Desserts
    {'category': 'Desserts', 'name': 'Gulab Jamun', 'description': 'Soft khoya dumplings soaked in rose-flavored syrup', 'price': 99.00, 'is_vegetarian': True, 'is_bestseller': True, 'spice_level': 'none', 'rating': 4.7, 'rating_count': 420, 'image': '/images/gulab_jamun.png'},
    {'category': 'Desserts', 'name': 'Kulfi Falooda', 'description': 'Traditional Indian ice cream with falooda noodles', 'price': 149.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'none', 'rating': 4.6, 'rating_count': 200},
    {'category': 'Desserts', 'name': 'Rasgulla', 'description': 'Spongy cottage cheese balls in light sugar syrup', 'price': 89.00, 'is_vegetarian': True, 'spice_level': 'none', 'rating': 4.4, 'rating_count': 160},

    # Beverages
    {'category': 'Beverages', 'name': 'Sweet Lassi', 'description': 'Chilled yogurt drink blended with sugar and rose water', 'price': 79.00, 'is_vegetarian': True, 'is_bestseller': True, 'spice_level': 'none', 'rating': 4.6, 'rating_count': 310},
    {'category': 'Beverages', 'name': 'Mango Lassi', 'description': 'Creamy mango and yogurt blended drink', 'price': 99.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'none', 'rating': 4.8, 'rating_count': 270, 'image': '/images/mango_lassi.png'},
    {'category': 'Beverages', 'name': 'Masala Chai', 'description': 'Aromatic spiced tea with ginger and cardamom', 'price': 49.00, 'is_vegetarian': True, 'spice_level': 'none', 'rating': 4.5, 'rating_count': 200},

    # Pizza
    {'category': 'Pizza', 'name': 'Margherita Pizza', 'description': 'Classic pizza with tomato sauce, mozzarella and fresh basil', 'price': 249.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'none', 'rating': 4.4, 'rating_count': 180},
    {'category': 'Pizza', 'name': 'Chicken BBQ Pizza', 'description': 'Grilled chicken with BBQ sauce, onions and peppers', 'price': 349.00, 'is_vegetarian': False, 'is_bestseller': True, 'spice_level': 'mild', 'rating': 4.6, 'rating_count': 250},
    {'category': 'Pizza', 'name': 'Paneer Tikka Pizza', 'description': 'Indian fusion pizza with tandoor paneer and tikka sauce', 'price': 299.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'medium', 'rating': 4.5, 'rating_count': 190},

    # Burgers
    {'category': 'Burgers', 'name': 'Classic Chicken Burger', 'description': 'Crispy fried chicken with lettuce, tomato and mayo', 'price': 199.00, 'is_vegetarian': False, 'is_bestseller': True, 'spice_level': 'mild', 'rating': 4.5, 'rating_count': 320, 'image': '/images/chicken_burger.png'},
    {'category': 'Burgers', 'name': 'Veg Aloo Tikki Burger', 'description': 'Spiced potato patty with fresh veggies and green chutney', 'price': 149.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'medium', 'rating': 4.3, 'rating_count': 200},
    {'category': 'Burgers', 'name': 'Double Patty Burger', 'description': 'Double beef patty with cheese, bacon and special sauce', 'price': 279.00, 'is_vegetarian': False, 'spice_level': 'mild', 'rating': 4.7, 'rating_count': 150},
]


for item_data in menu_items:
    cat_name = item_data.pop('category')
    category = categories[cat_name]
    item, created = MenuItem.objects.update_or_create(
        name=item_data['name'],
        category=category,
        defaults=item_data
    )
    print(f"{'Created' if created else 'Updated'}: MenuItem '{item.name}' (Rs.{item.price})")

# Create default staff user
staff_user, created = User.objects.get_or_create(
    username='staff',
    defaults={
        'email': 'staff@restaurant.com',
        'role': 'staff',
        'first_name': 'Staff',
        'last_name': 'User',
    }
)
if created:
    staff_user.set_password('staff@123')
    staff_user.save()
    print("Created staff user: staff / staff@123")

print("\n✅ Seed data loaded successfully!")
print("📊 Categories:", Category.objects.count())
print("🍽️  Menu Items:", MenuItem.objects.count())
print("\n🔑 Default Credentials:")
print("   Admin: (create with: python manage.py createsuperuser)")
print("   Staff: username=staff, password=staff@123")
