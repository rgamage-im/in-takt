#!/bin/bash
# Phase 6C: Celery Task Queue
# MEDIUM RISK - Task queue updates

set -e

echo "=================================================="
echo "Phase 6C: Celery Task Queue"
echo "=================================================="
echo ""

echo "📦 Updating Celery..."
pip install --upgrade celery==5.6.2

echo ""
echo "📝 Updating requirements.txt..."
sed -i 's/^celery==.*/celery==5.6.2/' ../requirements.txt

echo ""
echo "✅ Phase 6C Complete!"
echo ""
echo "🧪 TESTING REQUIRED:"
echo "   - Restart Celery workers"
echo "   - Test background tasks"
echo "   - Test periodic tasks (Celery Beat)"
echo "   - Verify task results"
echo "   - Monitor task queues"
echo "   - Run: pytest tests/ -v -k celery"
echo ""
echo "📝 Mark Phase 6C in TESTING_CHECKLIST.md when done"
echo ""
