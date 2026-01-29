#!/bin/bash
# Phase 2A: Django REST Framework & Extensions
# MEDIUM RISK - Framework updates

set -e

echo "=================================================="
echo "Phase 2A: Django REST Framework & Extensions"
echo "=================================================="
echo ""
echo "⚠️  BACKUP DATABASE BEFORE PROCEEDING"
echo ""
read -p "Have you backed up the database? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborting. Please backup database first."
    exit 1
fi

echo "📦 Updating Django REST Framework..."
pip install --upgrade djangorestframework==3.16.1

echo "📦 Updating DRF Spectacular (OpenAPI)..."
pip install --upgrade drf-spectacular==0.29.0

echo "📦 Updating Django HTMX..."
pip install --upgrade django-htmx==1.27.0

echo "📦 Updating Django CORS Headers..."
pip install --upgrade django-cors-headers==4.9.0

echo ""
echo "🔄 Running migrations..."
python manage.py migrate

echo ""
echo "✅ Phase 2A Complete!"
echo ""
echo "🧪 TESTING REQUIRED:"
echo "   - Run full API test suite: pytest tests/ -v"
echo "   - Test OpenAPI docs at /api/schema/swagger-ui/"
echo "   - Test CORS settings"
echo "   - Test HTMX frontend interactions"
echo "   - Verify all REST API endpoints"
echo ""
echo "📝 Mark Phase 2A in TESTING_CHECKLIST.md when done"
echo ""
