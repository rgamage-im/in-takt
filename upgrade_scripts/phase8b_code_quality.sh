#!/bin/bash
# Phase 8B: Code Quality Tools
# ⚠️ MEDIUM RISK - Development only, multiple MAJOR versions

set -e

echo "=================================================="
echo "Phase 8B: Code Quality Tools (Dev Only)"
echo "=================================================="
echo ""
echo "⚠️  WARNING: Multiple major versions:"
echo "    - black: 24.10.0 → 26.1.0"
echo "    - isort: 5.13.2 → 7.0.0"
echo ""

echo "📦 Updating black..."
pip install --upgrade black==26.1.0

echo "📦 Updating flake8..."
pip install --upgrade flake8==7.3.0

echo "📦 Updating isort..."
pip install --upgrade isort==7.0.0

echo "📦 Updating mypy..."
pip install --upgrade mypy==1.19.1

echo ""
echo "✅ Phase 8B Complete!"
echo ""
echo "🧪 TESTING REQUIRED:"
echo "   - Run black: black --check ."
echo "   - Run flake8: flake8 ."
echo "   - Run isort: isort --check-only ."
echo "   - Run mypy: mypy ."
echo ""
echo "⚠️  Code formatting rules may have changed!"
echo "    You may need to reformat code with: black ."
echo "    You may need to resort imports with: isort ."
echo ""
echo "📝 Mark Phase 8B in TESTING_CHECKLIST.md when done"
echo ""
