#!/usr/bin/env python
"""Debug session data"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model

User = get_user_model()

print("\n=== Active Sessions ===")
sessions = Session.objects.all()
print(f"Total sessions: {sessions.count()}\n")

for i, session in enumerate(sessions, 1):
    decoded = session.get_decoded()
    print(f"Session {i}:")
    print(f"  Session Key: {session.session_key[:20]}...")
    print(f"  User ID: {decoded.get('_auth_user_id', 'Not logged in')}")
    print(f"  Has graph_access_token: {'graph_access_token' in decoded}")
    if 'graph_access_token' in decoded:
        token = decoded['graph_access_token']
        print(f"  Token (first 50 chars): {token[:50]}...")
    print(f"  Has graph_refresh_token: {'graph_refresh_token' in decoded}")
    print(f"  All keys: {list(decoded.keys())}")
    print("-" * 70)

# Check randy1 user
try:
    user = User.objects.get(username='randy1')
    print(f"\n=== User randy1 ===")
    print(f"First name: {user.first_name}")
    print(f"Last name: {user.last_name}")
    print(f"Email: {user.email}")
except User.DoesNotExist:
    print("\nUser 'randy1' not found")
