#!/usr/bin/env python3
"""
Generate a new Django SECRET_KEY for production use.
Run this and copy the output to your Azure App Service configuration.
"""

from django.core.management.utils import get_random_secret_key

print("\n" + "="*70)
print("DJANGO SECRET KEY GENERATOR")
print("="*70)
print("\nGenerated SECRET_KEY:")
print("-"*70)
secret_key = get_random_secret_key()
print(secret_key)
print("-"*70)
print("\n📋 Copy the key above and add it to Azure App Service:")
print("   Azure Portal > App Service > Configuration > Application settings")
print("   Name: DJANGO_SECRET_KEY")
print(f"   Value: {secret_key}")
print("\n⚠️  IMPORTANT: Keep this secret! Never commit it to Git.")
print("="*70 + "\n")
