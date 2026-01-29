#!/bin/bash
# Phase 5B: Cryptography (Security)
# ⚠️ HIGH RISK - MAJOR VERSION (43 → 46)

set -e

echo "=================================================="
echo "Phase 5B: Cryptography (Security)"
echo "=================================================="
echo ""
echo "⚠️  WARNING: Major version update (43.0.3 → 46.0.4)"
echo "    Security library - breaking changes possible"
echo ""
echo "📚 Review changelog: https://cryptography.io/en/latest/changelog/"
echo ""
read -p "Have you reviewed the security changelog? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborting. Please review changelog first."
    exit 1
fi

echo "📦 Updating cryptography..."
pip install --upgrade cryptography==46.0.4

echo ""
echo "✅ Phase 5B Complete!"
echo ""
echo "🧪 CRITICAL TESTING REQUIRED:"
echo "   - Test encryption/decryption operations"
echo "   - Test certificate handling"
echo "   - Test SSL/TLS connections"
echo "   - Verify password hashing"
echo "   - Test token generation"
echo "   - Run: pytest tests/ -v -k crypt"
echo ""
echo "📝 Mark Phase 5B in TESTING_CHECKLIST.md when done"
echo ""
