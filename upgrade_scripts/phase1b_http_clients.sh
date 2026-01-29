#!/bin/bash
# Phase 1B: HTTP Clients
# LOW RISK - Safe to update

set -e

echo "=================================================="
echo "Phase 1B: HTTP Clients"
echo "=================================================="
echo ""

echo "📦 Updating HTTP client libraries..."
pip install --upgrade requests==2.32.5 httpx==0.28.1

echo ""
echo "📝 Updating requirements.txt..."
sed -i 's/^requests==.*/requests==2.32.5/' ../requirements.txt
sed -i 's/^httpx==.*/httpx==0.28.1/' ../requirements.txt

echo ""
echo "✅ Phase 1B Complete!"
echo ""
echo "🧪 TESTING REQUIRED:"
echo "   - Test API calls to QuickBooks"
echo "   - Test API calls to Microsoft Graph"
echo "   - Test any external HTTP requests"
echo "   - Run: pytest tests/ -v"
echo ""
echo "📝 Mark Phase 1B in TESTING_CHECKLIST.md when done"
echo ""
