#!/bin/bash
# Phase 1D: QuickBooks Integration
# LOW RISK - Minor version updates

set -e

echo "=================================================="
echo "Phase 1D: QuickBooks Integration"
echo "=================================================="
echo ""

echo "📦 Updating QuickBooks packages..."
pip install --upgrade intuit-oauth==1.2.6 python-quickbooks==0.9.12

echo ""
echo "✅ Phase 1D Complete!"
echo ""
echo "🧪 TESTING REQUIRED:"
echo "   - Test QuickBooks OAuth flow"
echo "   - Test QuickBooks API endpoints"
echo "   - Verify customer/invoice sync"
echo "   - Run: pytest tests/ -v -k quickbooks"
echo ""
echo "📝 Mark Phase 1D in TESTING_CHECKLIST.md when done"
echo ""
