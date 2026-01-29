#!/bin/bash
# Phase 6A: Database Tools
# MEDIUM RISK - Database connection changes

set -e

echo "=================================================="
echo "Phase 6A: Database Tools"
echo "=================================================="
echo ""
echo "⚠️  Note: dj-database-url has MAJOR VERSION (2.2.0 → 3.1.0)"
echo ""

echo "📦 Updating psycopg2-binary..."
pip install --upgrade psycopg2-binary==2.9.11

echo "📦 Updating dj-database-url..."
pip install --upgrade dj-database-url==3.1.0

echo ""
echo "🔄 Running migrations..."
cd .. && python manage.py migrate && cd upgrade_scripts

echo ""
echo "📝 Updating requirements.txt..."
sed -i 's/^psycopg2-binary==.*/psycopg2-binary==2.9.11/' ../requirements.txt
sed -i 's/^dj-database-url==.*/dj-database-url==3.1.0/' ../requirements.txt

echo ""
echo "✅ Phase 6A Complete!"
echo ""
echo "🧪 TESTING REQUIRED:"
echo "   - Test database connections"
echo "   - Run migrations: python manage.py migrate"
echo "   - Test database queries"
echo "   - Verify connection pooling"
echo "   - Run: pytest tests/ -v -k database"
echo ""
echo "📝 Mark Phase 6A in TESTING_CHECKLIST.md when done"
echo ""
