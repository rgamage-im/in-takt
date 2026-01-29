#!/bin/bash
# Phase 4B: Microsoft Graph SDK
# ⚠️ HIGH RISK - MAJOR VERSION JUMP (1.12 → 1.53)

set -e

echo "=================================================="
echo "Phase 4B: Microsoft Graph SDK"
echo "=================================================="
echo ""
echo "⚠️  WARNING: Major version jump (1.12.0 → 1.53.0)"
echo "    This is 40+ versions - breaking changes expected!"
echo ""
echo "📚 Review changelog: https://github.com/microsoftgraph/msgraph-sdk-python/releases"
echo ""
read -p "Have you reviewed the breaking changes? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborting. Please review changelog first."
    exit 1
fi

echo "📦 Updating Microsoft Graph SDK..."
pip install --upgrade msgraph-sdk==1.53.0

echo ""
echo "✅ Phase 4B Complete!"
echo ""
echo "🧪 CRITICAL TESTING REQUIRED:"
echo "   - Test ALL Microsoft Graph API calls:"
echo "     • User queries"
echo "     • Group operations"
echo "     • SharePoint access"
echo "     • OneDrive operations"
echo "     • Mail/calendar if used"
echo "   - Run: pytest tests/ -v -k graph"
echo "   - Manual testing of all Graph features"
echo ""
echo "⚠️  If errors occur, check API call syntax changes"
echo ""
echo "📝 Mark Phase 4B in TESTING_CHECKLIST.md when done"
echo ""
