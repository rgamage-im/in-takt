#!/bin/bash
# Phase 6D: Django Redis Backend
# ⚠️ HIGH RISK - MAJOR VERSION (5.4.0 → 6.0.0)

set -e

echo "=================================================="
echo "Phase 6D: Django Redis Backend"
echo "=================================================="
echo ""
echo "⚠️  WARNING: Major version update (5.4.0 → 6.0.0)"
echo "    Django cache backend - breaking changes possible"
echo ""

echo "📦 Updating django-redis..."
pip install --upgrade django-redis==6.0.0

echo ""
echo "🔄 Running migrations..."
cd .. && python manage.py migrate && cd upgrade_scripts

echo ""
echo "📝 Updating requirements.txt..."
sed -i 's/^django-redis==.*/django-redis==6.0.0/' ../requirements.txt

echo ""
echo "✅ Phase 6D Complete!"
echo ""
echo "🧪 CRITICAL TESTING REQUIRED:"
echo "   - Test Django cache framework"
echo "   - Test cache.set() and cache.get()"
echo "   - Test cache key patterns"
echo "   - Verify cache invalidation"
echo "   - Test session storage backend"
echo "   - Run: pytest tests/ -v -k cache"
echo ""
echo "📝 Mark Phase 6D in TESTING_CHECKLIST.md when done"
echo ""
