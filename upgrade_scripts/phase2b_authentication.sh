#!/bin/bash
# Phase 2B: Authentication & Social Auth
# MEDIUM RISK - Authentication changes

set -e

echo "=================================================="
echo "Phase 2B: Authentication & Social Auth"
echo "=================================================="
echo ""

echo "📦 Updating social auth..."
pip install --upgrade social-auth-app-django==5.7.0

echo ""
echo "🔄 Running migrations..."
python manage.py migrate

echo ""
echo "✅ Phase 2B Complete!"
echo ""
echo "🧪 TESTING REQUIRED:"
echo "   - Test SSO login flow (Microsoft/Azure AD)"
echo "   - Test user authentication"
echo "   - Test logout functionality"
echo "   - Verify session management"
echo "   - Run: pytest tests/ -v -k auth"
echo ""
echo "📝 Mark Phase 2B in TESTING_CHECKLIST.md when done"
echo ""
