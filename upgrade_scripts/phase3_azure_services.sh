#!/bin/bash
# Phase 3: Azure Services
# MEDIUM RISK - Azure integration updates

set -e

echo "=================================================="
echo "Phase 3: Azure Services"
echo "=================================================="
echo ""

echo "📦 Updating Azure Identity..."
pip install --upgrade azure-identity==1.25.1

echo "📦 Updating Azure Key Vault..."
pip install --upgrade azure-keyvault-secrets==4.10.0

echo "📦 Updating Azure Storage Blob..."
pip install --upgrade azure-storage-blob==12.28.0

echo "📦 Updating Azure Monitor OpenTelemetry..."
pip install --upgrade azure-monitor-opentelemetry==1.8.5

echo ""
echo "✅ Phase 3 Complete!"
echo ""
echo "🧪 TESTING REQUIRED:"
echo "   - Test Azure authentication"
echo "   - Test Key Vault secret retrieval"
echo "   - Test blob storage operations"
echo "   - Verify telemetry/monitoring"
echo "   - Run: pytest tests/ -v -k azure"
echo ""
echo "📝 Mark Phase 3 in TESTING_CHECKLIST.md when done"
echo ""
