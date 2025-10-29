#!/usr/bin/env python
"""Test Graph API directly"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.sessions.models import Session
from msgraph_integration.services_delegated import GraphServiceDelegated

# Get the session with graph token
session = Session.objects.first()
decoded = session.get_decoded()
access_token = decoded.get('graph_access_token')

print(f"Access token (first 50): {access_token[:50]}...")
print("\nTrying to fetch profile from Microsoft Graph...")

try:
    graph_service = GraphServiceDelegated()
    user_data = graph_service.get_my_profile(access_token)
    print("\n✅ SUCCESS!")
    print(f"Profile data: {user_data}")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"Error type: {type(e).__name__}")
