#!/bin/bash
# Run All Upgrade Phases (Use with caution!)
# This will run all phases in sequence with prompts between each

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║     In-Takt Dependency Upgrade - All Phases          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "⚠️  WARNING: This will upgrade ALL dependencies"
echo ""
echo "Prerequisites:"
echo "  ✓ Database backup created"
echo "  ✓ Git branch created"
echo "  ✓ requirements.txt backed up"
echo "  ✓ Virtual environment activated"
echo ""
read -p "Are you ready to proceed with ALL upgrades? (yes/no) " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "❌ Aborting. Run individual phase scripts instead."
    exit 1
fi

echo ""
echo "Starting upgrade sequence..."
echo ""

# Phase 1: Low-Risk Updates
echo "════════════════════════════════════════════════════════"
echo "PHASE 1: Low-Risk Updates"
echo "════════════════════════════════════════════════════════"
bash phase1a_timezone_updates.sh
bash phase1b_http_clients.sh
bash phase1c_environment.sh
bash phase1d_quickbooks.sh

read -p "Phase 1 complete. Continue to Phase 2? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping. Resume with phase2a_django_minor.sh"
    exit 0
fi

# Phase 2: Framework Updates
echo "════════════════════════════════════════════════════════"
echo "PHASE 2: Framework & Core Updates"
echo "════════════════════════════════════════════════════════"
bash phase2a_django_minor.sh
bash phase2b_authentication.sh

read -p "Phase 2 complete. Continue to Phase 3? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping. Resume with phase3_azure_services.sh"
    exit 0
fi

# Phase 3: Azure Services
echo "════════════════════════════════════════════════════════"
echo "PHASE 3: Azure Services"
echo "════════════════════════════════════════════════════════"
bash phase3_azure_services.sh

read -p "Phase 3 complete. Continue to Phase 4? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping. Resume with phase4a_msal.sh"
    exit 0
fi

# Phase 4: Microsoft Graph
echo "════════════════════════════════════════════════════════"
echo "PHASE 4: Microsoft Graph"
echo "════════════════════════════════════════════════════════"
bash phase4a_msal.sh
bash phase4b_msgraph.sh

read -p "Phase 4 complete. Continue to Phase 5? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping. Resume with phase5a_pydantic.sh"
    exit 0
fi

# Phase 5: Data Validation & Security
echo "════════════════════════════════════════════════════════"
echo "PHASE 5: Data Validation & Security"
echo "════════════════════════════════════════════════════════"
bash phase5a_pydantic.sh
bash phase5b_cryptography.sh

read -p "Phase 5 complete. Continue to Phase 6? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping. Resume with phase6a_database.sh"
    exit 0
fi

# Phase 6: Caching & Task Queue
echo "════════════════════════════════════════════════════════"
echo "PHASE 6: Caching & Task Queue"
echo "════════════════════════════════════════════════════════"
bash phase6a_database.sh
bash phase6b_redis.sh
bash phase6c_celery.sh
bash phase6d_django_redis.sh

read -p "Phase 6 complete. Continue to Phase 7? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping. Resume with phase7a_server.sh"
    exit 0
fi

# Phase 7: WSGI & Static Files
echo "════════════════════════════════════════════════════════"
echo "PHASE 7: WSGI & Static Files"
echo "════════════════════════════════════════════════════════"
bash phase7a_server.sh
bash phase7b_imaging.sh

read -p "Phase 7 complete. Continue to Phase 8? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping. Resume with phase8a_testing.sh"
    exit 0
fi

# Phase 8: Development Tools
echo "════════════════════════════════════════════════════════"
echo "PHASE 8: Development Tools"
echo "════════════════════════════════════════════════════════"
bash phase8a_testing.sh
bash phase8b_code_quality.sh

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║         ALL PHASES COMPLETE!                          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "✅ All dependency upgrades completed"
echo ""
echo "📝 Next Steps:"
echo "   1. Review TESTING_CHECKLIST.md and complete all tests"
echo "   2. Update requirements.txt: pip freeze > requirements.txt"
echo "   3. Commit changes: git add . && git commit -m 'Upgrade dependencies'"
echo "   4. Test in staging environment"
echo "   5. Deploy to production"
echo ""
