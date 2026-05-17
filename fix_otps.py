import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import random
from orders.models import Order

qs = Order.objects.filter(delivery_otp__isnull=True) | Order.objects.filter(delivery_otp='')
count = 0
for q in qs:
    q.delivery_otp = str(random.randint(1000, 9999))
    q.save()
    count += 1
print(f'Updated {count} orders')
