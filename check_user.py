#!/usr/bin/env python
"""Check user data from SSO"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from social_django.models import UserSocialAuth

User = get_user_model()

print("\n=== Django Users ===")
for user in User.objects.all():
    print(f"Username: {user.username}")
    print(f"First Name: {user.first_name}")
    print(f"Last Name: {user.last_name}")
    print(f"Email: {user.email}")
    print(f"Full Name: {user.get_full_name()}")
    print("-" * 50)

print("\n=== Social Auth Records ===")
for social in UserSocialAuth.objects.all():
    print(f"Provider: {social.provider}")
    print(f"UID: {social.uid}")
    print(f"User: {social.user.username}")
    print(f"Extra Data: {social.extra_data}")
    print("-" * 50)
