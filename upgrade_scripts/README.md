# Dependency Upgrade Scripts

**Date Created:** January 29, 2026  
**Python Version:** 3.12+  
**Current Django Version:** 5.2.7 LTS

## ⚠️ IMPORTANT: Before You Start

1. **Backup your database:**
   ```bash
   python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json
   ```

2. **Create a git branch:**
   ```bash
   git checkout -b dependency-updates-jan-2026
   ```

3. **Backup current requirements:**
   ```bash
   cp requirements.txt requirements.txt.backup
   ```

4. **Ensure virtual environment is active:**
   ```bash
   source venv/bin/activate  # or your venv path
   ```

## 📋 Execution Order

Execute scripts in numerical order. **Test thoroughly after each phase** before proceeding to the next.

### Phase 1: Low-Risk Updates (DO FIRST)
- `phase1a_timezone_updates.sh` - Timezone & date utilities
- `phase1b_http_clients.sh` - HTTP client libraries
- `phase1c_environment.sh` - Environment & config
- `phase1d_quickbooks.sh` - QuickBooks integration

### Phase 2: Framework & Core Updates
- `phase2a_django_minor.sh` - Django REST & extensions
- `phase2b_authentication.sh` - Authentication & social auth

### Phase 3: Azure Services
- `phase3_azure_services.sh` - Azure identity, storage, monitoring

### Phase 4: Microsoft Graph
- `phase4a_msal.sh` - Microsoft authentication library
- `phase4b_msgraph.sh` - Microsoft Graph SDK (big jump)

### Phase 5: Data Validation & Security
- `phase5a_pydantic.sh` - Data validation
- `phase5b_cryptography.sh` - Security (MAJOR VERSION)

### Phase 6: Caching & Task Queue
- `phase6a_database.sh` - Database tools
- `phase6b_redis.sh` - Redis (MAJOR VERSION)
- `phase6c_celery.sh` - Celery task queue
- `phase6d_django_redis.sh` - Django Redis backend (MAJOR VERSION)

### Phase 7: WSGI & Static Files
- `phase7a_server.sh` - Gunicorn & Whitenoise
- `phase7b_imaging.sh` - Pillow image processing (MAJOR VERSION)

### Phase 8: Development Tools (NON-PRODUCTION)
- `phase8a_testing.sh` - Testing framework
- `phase8b_code_quality.sh` - Code formatters & linters

## 🔄 Rollback Procedure

If any phase fails:

```bash
# Restore original requirements
cp requirements.txt.backup requirements.txt

# Reinstall original versions
pip install -r requirements.txt

# Restore database if needed
python manage.py flush
python manage.py loaddata backup_YYYYMMDD_HHMMSS.json
```

## 📊 Tracking Progress

Use `TESTING_CHECKLIST.md` to track testing after each phase.

## ⚠️ Known Major Version Changes

These require extra attention and testing:

1. **redis** (5.2.0 → 7.1.0)
2. **msgraph-sdk** (1.12.0 → 1.53.0) 
3. **django-redis** (5.4.0 → 6.0.0)
4. **dj-database-url** (2.2.0 → 3.1.0)
5. **pytest** (8.3.3 → 9.0.2)
6. **pytest-cov** (5.0.0 → 7.0.0)
7. **black** (24.10.0 → 26.1.0)
8. **isort** (5.13.2 → 7.0.0)
9. **cryptography** (43.0.3 → 46.0.4)
10. **gunicorn** (23.0.0 → 24.1.1)
11. **pillow** (11.0.0 → 12.1.0)

## 📝 Notes

- **Django 5.2 LTS** is supported until April 2028 - recommended to stay on this version
- **Django 6.0** is NOT an LTS - skip it
- **Django 6.2 LTS** (next LTS) expected Q3-Q4 2026
