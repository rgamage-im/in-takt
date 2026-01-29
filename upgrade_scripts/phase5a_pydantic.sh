#!/bin/bash
# Phase 5A: Pydantic Data Validation
# MEDIUM RISK - Data validation updates

set -e

echo "=================================================="
echo "Phase 5A: Pydantic Data Validation"
echo "=================================================="
echo ""

echo "📦 Updating Pydantic..."
pip install --upgrade pydantic==2.12.5

echo ""
echo "📝 Updating requirements.txt..."
sed -i 's/^pydantic==.*/pydantic==2.12.5/' ../requirements.txt

echo ""
echo "✅ Phase 5A Complete!"
echo ""
echo "🧪 TESTING REQUIRED:"
echo "   - Test data validation models"
echo "   - Test API request/response validation"
echo "   - Verify serialization/deserialization"
echo "   - Run: pytest tests/ -v"
echo ""
echo "📝 Mark Phase 5A in TESTING_CHECKLIST.md when done"
echo ""
