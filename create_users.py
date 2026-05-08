import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bus_management.settings')
django.setup()

from django.contrib.auth.models import User

# Tạo user 'staff'
if not User.objects.filter(username='staff').exists():
    user = User.objects.create_user('staff', 'staff@example.com', 'staff123')
    user.is_staff = True
    user.save()
    print("Created 'staff' user (password: staff123)")
else:
    print("'staff' user already exists.")

# Tạo user 'khach' (user thường)
if not User.objects.filter(username='khach').exists():
    user = User.objects.create_user('khach', 'user@example.com', 'user123')
    user.save()
    print("Created 'khach' user (password: user123)")
else:
    print("'khach' user already exists.")

