#!/usr/bin/env python
"""Clean up duplicate SSO user accounts"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Keep only the most recent user with email randy@integral-methods.com
users_to_delete = User.objects.filter(
    email='randy@integral-methods.com'
).exclude(username='randy1').order_by('id')

print(f"\nFound {users_to_delete.count()} duplicate user(s) to delete:")
for user in users_to_delete:
    print(f"  - Username: {user.username}, Email: {user.email}")

confirm = input("\nDelete these users? (yes/no): ")
if confirm.lower() == 'yes':
    count = users_to_delete.count()
    users_to_delete.delete()
    print(f"\n✅ Deleted {count} duplicate user(s)")
else:
    print("\n❌ Cancelled")
