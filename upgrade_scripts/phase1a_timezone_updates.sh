#!/bin/bash
# Phase 1A: Timezone & Date Utilities
# LOW RISK - Safe to update

set -e  # Exit on error

echo "=================================================="
echo "Phase 1A: Timezone & Date Utilities"
echo "=================================================="
echo ""

echo "📦 Updating timezone packages..."
pip install --upgrade pytz==2025.2 tzdata==2025.3

echo ""
echo "✅ Phase 1A Complete!"
echo ""
echo "🧪 TESTING REQUIRED:"
echo "   - Run: pytest tests/ -v"
echo "   - Test date/time handling in app"
echo "   - Check timezone conversions"
echo ""
echo "📝 Mark Phase 1A in TESTING_CHECKLIST.md when done"
echo ""
