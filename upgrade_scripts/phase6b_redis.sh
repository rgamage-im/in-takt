#!/bin/bash
# Phase 6B: Redis
# ⚠️ HIGH RISK - MAJOR VERSION (5.2.0 → 7.1.0)

set -e

echo "=================================================="
echo "Phase 6B: Redis"
echo "=================================================="
echo ""
echo "⚠️  WARNING: Major version jump (5.2.0 → 7.1.0)"
echo "    RESP3 protocol changes, API differences expected"
echo ""
echo "📚 Review changelog: https://github.com/redis/redis-py/releases"
echo ""
read -p "Have you reviewed the Redis breaking changes? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborting. Please review changelog first."
    exit 1
fi

echo "📦 Updating redis..."
pip install --upgrade redis==7.1.0

echo ""
echo "✅ Phase 6B Complete!"
echo ""
echo "🧪 CRITICAL TESTING REQUIRED:"
echo "   - Test Redis cache operations"
echo "   - Test session storage"
echo "   - Test Redis pub/sub if used"
echo "   - Verify cache TTL behavior"
echo "   - Test cache clear operations"
echo "   - Run: pytest tests/ -v -k redis"
echo ""
echo "⚠️  Monitor for RESP3 protocol issues"
echo ""
echo "📝 Mark Phase 6B in TESTING_CHECKLIST.md when done"
echo ""
