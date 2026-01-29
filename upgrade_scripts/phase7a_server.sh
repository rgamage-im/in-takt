#!/bin/bash
# Phase 7A: WSGI Server & Static Files
# ⚠️ HIGH RISK - Gunicorn MAJOR VERSION (23 → 24)

set -e

echo "=================================================="
echo "Phase 7A: WSGI Server & Static Files"
echo "=================================================="
echo ""
echo "⚠️  WARNING: Gunicorn major version (23.0.0 → 24.1.1)"
echo "    Server configuration may need updates"
echo ""

echo "📦 Updating Gunicorn..."
pip install --upgrade gunicorn==24.1.1

echo "📦 Updating Whitenoise..."
pip install --upgrade whitenoise==6.11.0

echo ""
echo "📝 Updating requirements.txt..."
sed -i 's/^gunicorn==.*/gunicorn==24.1.1/' ../requirements.txt
sed -i 's/^whitenoise==.*/whitenoise==6.11.0/' ../requirements.txt

echo ""
echo "✅ Phase 7A Complete!"
echo ""
echo "🧪 CRITICAL TESTING REQUIRED:"
echo "   - Test Gunicorn startup: gunicorn config.wsgi:application"
echo "   - Verify worker processes"
echo "   - Test static file serving"
echo "   - Check static file compression"
echo "   - Test production-like deployment"
echo "   - Monitor server logs for errors"
echo ""
echo "⚠️  Review Gunicorn config if startup fails"
echo ""
echo "📝 Mark Phase 7A in TESTING_CHECKLIST.md when done"
echo ""
