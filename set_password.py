#!/usr/bin/env python
"""Set password for a user"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'randy1'
password = 'TempPassword123!'  # Change this to your desired password

try:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_staff = True  # Make sure they can access admin
    user.is_superuser = True  # Give them full admin access
    user.save()
    print(f"✅ Password set for user: {username}")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   Is staff: {user.is_staff}")
    print(f"   Is superuser: {user.is_superuser}")
    print(f"\nYou can now log in to /admin/ with these credentials")
except User.DoesNotExist:
    print(f"❌ User '{username}' not found")
