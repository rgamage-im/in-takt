#!/bin/bash
# Phase 1C: Environment & Config
# LOW RISK - Safe to update

set -e

echo "=================================================="
echo "Phase 1C: Environment & Config"
echo "=================================================="
echo ""

echo "📦 Updating python-dotenv..."
pip install --upgrade python-dotenv==1.2.1

echo ""
echo "📝 Updating requirements.txt..."
sed -i 's/^python-dotenv==.*/python-dotenv==1.2.1/' ../requirements.txt

echo ""
echo "✅ Phase 1C Complete!"
echo ""
echo "🧪 TESTING REQUIRED:"
echo "   - Restart Django: python manage.py runserver"
echo "   - Verify .env file loads correctly"
echo "   - Check all environment variables"
echo "   - Run: pytest tests/ -v"
echo ""
echo "📝 Mark Phase 1C in TESTING_CHECKLIST.md when done"
echo ""
