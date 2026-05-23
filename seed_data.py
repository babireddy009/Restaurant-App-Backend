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

def cleanup_duplicate_emails():
    from django.db.models import Count
    from django.db.models.functions import Lower
    from django.db import transaction
    from orders.models import Order, OrderReview

    # Find lowercase emails that are shared by multiple users
    duplicates = (
        User.objects.annotate(email_lower=Lower('email'))
        .values('email_lower')
        .annotate(email_count=Count('id'))
        .filter(email_count__gt=1, email_lower__isnull=False)
        .exclude(email_lower='')
    )

    if not duplicates:
        print("No duplicate email accounts found to clean up.")
        return

    print(f"Found {len(duplicates)} emails with duplicate accounts. Starting cleanup...")

    for dup in duplicates:
        email_lower = dup['email_lower']
        
        # Get all users with this email, ordered by id ascending (keep the oldest account)
        users = list(User.objects.filter(email__iexact=email_lower).order_by('id'))
        kept_user = users[0]
        duplicate_users = users[1:]

        print(f"Keeping user: '{kept_user.username}' (ID: {kept_user.id}, Email: {kept_user.email})")

        with transaction.atomic():
            for dup_user in duplicate_users:
                print(f"  Processing duplicate user: '{dup_user.username}' (ID: {dup_user.id}, Email: {dup_user.email})")
                
                # Re-point orders where they were the customer
                orders_count = Order.objects.filter(user=dup_user).update(user=kept_user)
                if orders_count:
                    print(f"    Moved {orders_count} orders to kept user")

                # Re-point orders where they were the driver
                deliveries_count = Order.objects.filter(driver=dup_user).update(driver=kept_user)
                if deliveries_count:
                    print(f"    Moved {deliveries_count} deliveries to kept user")

                # Re-point reviews
                reviews_count = OrderReview.objects.filter(user=dup_user).update(user=kept_user)
                if reviews_count:
                    print(f"    Moved {reviews_count} reviews to kept user")

                # Finally, delete the duplicate user
                dup_id = dup_user.id
                dup_user.delete()
                print(f"    Deleted duplicate user ID: {dup_id}")

    print("Cleanup of duplicate emails completed successfully.")

# Run duplicate cleanup on start
cleanup_duplicate_emails()

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
    {'category': 'Starters', 'name': 'Paneer Tikka', 'description': 'Marinated cottage cheese grilled to perfection with spices', 'price': 249.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'medium', 'rating': 4.5, 'rating_count': 120, 'image': '/images/paneer_tikka.png'},
    {'category': 'Starters', 'name': 'Chicken Tikka', 'description': 'Tender chicken marinated in yogurt and spices, grilled in tandoor', 'price': 299.00, 'is_vegetarian': False, 'is_featured': True, 'is_bestseller': True, 'spice_level': 'medium', 'rating': 4.7, 'rating_count': 250, 'image': '/images/chicken_tikka.png'},
    {'category': 'Starters', 'name': 'Veg Spring Rolls', 'description': 'Crispy rolls filled with fresh vegetables and noodles', 'price': 179.00, 'is_vegetarian': True, 'spice_level': 'mild', 'rating': 4.2, 'rating_count': 80, 'image': '/images/paneer_tikka.png'},
    {'category': 'Starters', 'name': 'Seekh Kebab', 'description': 'Minced mutton kebabs with aromatic spices', 'price': 329.00, 'is_vegetarian': False, 'is_bestseller': True, 'spice_level': 'hot', 'rating': 4.6, 'rating_count': 175, 'image': '/images/paneer_tikka.png'},

    # Main Course
    {'category': 'Main Course', 'name': 'Butter Chicken', 'description': 'Tender chicken in rich tomato-based creamy sauce', 'price': 349.00, 'is_vegetarian': False, 'is_featured': True, 'is_bestseller': True, 'spice_level': 'mild', 'rating': 4.8, 'rating_count': 500, 'image': '/images/butter_chicken.png'},
    {'category': 'Main Course', 'name': 'Palak Paneer', 'description': 'Fresh cottage cheese cubes in smooth spinach gravy', 'price': 279.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'mild', 'rating': 4.4, 'rating_count': 200, 'image': '/images/palak_paneer.png'},
    {'category': 'Main Course', 'name': 'Dal Makhani', 'description': 'Slow-cooked black lentils with butter and cream', 'price': 229.00, 'is_vegetarian': True, 'is_bestseller': True, 'spice_level': 'mild', 'rating': 4.5, 'rating_count': 180, 'image': '/images/dal_makhani.png'},
    {'category': 'Main Course', 'name': 'Mutton Rogan Josh', 'description': 'Kashmiri-style mutton curry with bold spices', 'price': 429.00, 'is_vegetarian': False, 'spice_level': 'hot', 'rating': 4.7, 'rating_count': 140, 'image': '/images/mutton_rogan.png'},

    # Biryani
    {'category': 'Biryani & Rice', 'name': 'Chicken Biryani', 'description': 'Fragrant basmati rice cooked with tender chicken and whole spices', 'price': 359.00, 'is_vegetarian': False, 'is_featured': True, 'is_bestseller': True, 'spice_level': 'medium', 'rating': 4.9, 'rating_count': 650, 'image': '/images/chicken_biryani.png'},
    {'category': 'Biryani & Rice', 'name': 'Veg Biryani', 'description': 'Aromatic basmati rice with seasonal vegetables and saffron', 'price': 279.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'medium', 'rating': 4.3, 'rating_count': 220, 'image': '/images/veg_biryani.png'},
    {'category': 'Biryani & Rice', 'name': 'Hyderabadi Mutton Biryani', 'description': 'Slow-cooked dum biryani with tender mutton pieces', 'price': 449.00, 'is_vegetarian': False, 'is_bestseller': True, 'spice_level': 'hot', 'rating': 4.8, 'rating_count': 380, 'image': '/images/mutton_biryani.png'},
    {'category': 'Biryani & Rice', 'name': 'Jeera Rice', 'description': 'Light basmati rice tempered with cumin seeds', 'price': 129.00, 'is_vegetarian': True, 'spice_level': 'none', 'rating': 4.1, 'rating_count': 90, 'image': '/images/veg_biryani.png'},

    # Breads
    {'category': 'Breads', 'name': 'Butter Naan', 'description': 'Soft leavened bread baked in tandoor with butter', 'price': 49.00, 'is_vegetarian': True, 'spice_level': 'none', 'rating': 4.5, 'rating_count': 300, 'image': '/images/garlic_naan.png'},
    {'category': 'Breads', 'name': 'Garlic Naan', 'description': 'Naan topped with minced garlic and coriander', 'price': 59.00, 'is_vegetarian': True, 'is_bestseller': True, 'spice_level': 'none', 'rating': 4.7, 'rating_count': 280, 'image': '/images/garlic_naan.png'},
    {'category': 'Breads', 'name': 'Cheese Naan', 'description': 'Stuffed naan filled with melted cheese', 'price': 89.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'none', 'rating': 4.6, 'rating_count': 150, 'image': '/images/garlic_naan.png'},

    # Desserts
    {'category': 'Desserts', 'name': 'Gulab Jamun', 'description': 'Soft khoya dumplings soaked in rose-flavored syrup', 'price': 99.00, 'is_vegetarian': True, 'is_bestseller': True, 'spice_level': 'none', 'rating': 4.7, 'rating_count': 420, 'image': '/images/gulab_jamun.png'},
    {'category': 'Desserts', 'name': 'Kulfi Falooda', 'description': 'Traditional Indian ice cream with falooda noodles', 'price': 149.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'none', 'rating': 4.6, 'rating_count': 200, 'image': '/images/gulab_jamun.png'},
    {'category': 'Desserts', 'name': 'Rasgulla', 'description': 'Spongy cottage cheese balls in light sugar syrup', 'price': 89.00, 'is_vegetarian': True, 'spice_level': 'none', 'rating': 4.4, 'rating_count': 160, 'image': '/images/gulab_jamun.png'},

    # Beverages
    {'category': 'Beverages', 'name': 'Sweet Lassi', 'description': 'Chilled yogurt drink blended with sugar and rose water', 'price': 79.00, 'is_vegetarian': True, 'is_bestseller': True, 'spice_level': 'none', 'rating': 4.6, 'rating_count': 310, 'image': '/images/sweet_lassi.png'},
    {'category': 'Beverages', 'name': 'Mango Lassi', 'description': 'Creamy mango and yogurt blended drink', 'price': 99.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'none', 'rating': 4.8, 'rating_count': 270, 'image': '/images/mango_lassi.png'},
    {'category': 'Beverages', 'name': 'Masala Chai', 'description': 'Aromatic spiced tea with ginger and cardamom', 'price': 49.00, 'is_vegetarian': True, 'spice_level': 'none', 'rating': 4.5, 'rating_count': 200, 'image': '/images/mango_lassi.png'},

    # Pizza
    {'category': 'Pizza', 'name': 'Margherita Pizza', 'description': 'Classic pizza with tomato sauce, mozzarella and fresh basil', 'price': 249.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'none', 'rating': 4.4, 'rating_count': 180, 'image': '/images/margherita.png'},
    {'category': 'Pizza', 'name': 'Chicken BBQ Pizza', 'description': 'Grilled chicken with BBQ sauce, onions and peppers', 'price': 349.00, 'is_vegetarian': False, 'is_bestseller': True, 'spice_level': 'mild', 'rating': 4.6, 'rating_count': 250, 'image': '/images/margherita.png'},
    {'category': 'Pizza', 'name': 'Paneer Tikka Pizza', 'description': 'Indian fusion pizza with tandoor paneer and tikka sauce', 'price': 299.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'medium', 'rating': 4.5, 'rating_count': 190, 'image': '/images/margherita.png'},

    # Burgers
    {'category': 'Burgers', 'name': 'Classic Chicken Burger', 'description': 'Crispy fried chicken with lettuce, tomato and mayo', 'price': 199.00, 'is_vegetarian': False, 'is_bestseller': True, 'spice_level': 'mild', 'rating': 4.5, 'rating_count': 320, 'image': '/images/chicken_burger.png'},
    {'category': 'Burgers', 'name': 'Veg Aloo Tikki Burger', 'description': 'Spiced potato patty with fresh veggies and green chutney', 'price': 149.00, 'is_vegetarian': True, 'is_featured': True, 'spice_level': 'medium', 'rating': 4.3, 'rating_count': 200, 'image': '/images/veg_burger.png'},
    {'category': 'Burgers', 'name': 'Double Patty Burger', 'description': 'Double beef patty with cheese, bacon and special sauce', 'price': 279.00, 'is_vegetarian': False, 'spice_level': 'mild', 'rating': 4.7, 'rating_count': 150, 'image': '/images/chicken_burger.png'},
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

# Create default admin superuser
admin_user, created_admin = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@msrruchulu.com',
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True,
        'first_name': 'Admin',
        'last_name': 'User',
    }
)
if created_admin:
    admin_user.set_password('admin@123')
    admin_user.save()
    print("Created admin user: admin / admin@123")
else:
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.role = 'admin'
    admin_user.save()
    print("Ensured admin user has superuser permissions")

# Create default staff user
staff_user, created_staff = User.objects.get_or_create(
    username='staff',
    defaults={
        'email': 'staff@restaurant.com',
        'role': 'staff',
        'is_staff': True,
        'is_superuser': False,
        'first_name': 'Staff',
        'last_name': 'User',
    }
)
if created_staff:
    staff_user.set_password('staff@123')
    staff_user.save()
    print("Created staff user: staff / staff@123")
else:
    staff_user.is_staff = True
    staff_user.role = 'staff'
    staff_user.save()
    print("Ensured staff user has staff permissions")

# Create default driver user
driver_user, created_driver = User.objects.get_or_create(
    username='driver',
    defaults={
        'email': 'driver@msrruchulu.com',
        'role': 'driver',
        'is_staff': False,
        'is_superuser': False,
        'first_name': 'Driver',
        'last_name': 'User',
        'phone': '9988776655'
    }
)
if created_driver:
    driver_user.set_password('driver@123')
    driver_user.save()
    print("Created driver user: driver / driver@123")
else:
    driver_user.role = 'driver'
    driver_user.save()
    print("Ensured driver user has driver role")

print("\n[OK] Seed data loaded successfully!")
print("Categories:", Category.objects.count())
print("Menu Items:", MenuItem.objects.count())
print("\n[Default Credentials]")
print("   Admin:  username=admin,  password=admin@123")
print("   Staff:  username=staff,  password=staff@123")
print("   Driver: username=driver, password=driver@123")
