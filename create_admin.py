"""
Create admin user script
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retailconnect.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'phone_number': '+254700000000',
        'user_type': 'admin',
        'business_name': 'RetailConnect Admin',
        'city': 'Nairobi',
        'is_staff': True,
        'is_superuser': True,
    }
)

if created:
    admin.set_password('Admin@123')
    admin.save()
    print('Admin user created: admin / Admin@123')
else:
    print('Admin user already exists: admin')
