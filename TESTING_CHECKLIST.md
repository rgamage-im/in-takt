# Dependency Upgrade Testing Checklist

**Date Started:** _________________  
**Completed By:** _________________

## Pre-Upgrade Checklist

- [ ] Database backup created: `python manage.py dumpdata > backup_YYYYMMDD_HHMMSS.json`
- [ ] Git branch created: `git checkout -b dependency-updates-jan-2026`
- [ ] requirements.txt backed up: `cp requirements.txt requirements.txt.backup`
- [ ] Virtual environment activated
- [ ] Current version documented in git: `git add . && git commit -m "Pre-upgrade snapshot"`

---

## Phase 1A: Timezone & Date Utilities

**Packages:** pytz==2025.2, tzdata==2025.3

### Automated Tests
- [ ] `pytest tests/ -v` - All tests pass
- [ ] No deprecation warnings

### Manual Tests
- [ ] Date/time display correct in UI
- [ ] Timezone conversions work
- [ ] Date filters work correctly
- [ ] Timestamp formatting correct

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Notes:**
```

```

---

## Phase 1B: HTTP Clients

**Packages:** requests==2.32.5, httpx==0.28.1

### Automated Tests
- [ ] `pytest tests/ -v` - All tests pass
- [ ] API mocks still work

### Manual Tests
- [ ] QuickBooks API calls work
- [ ] Microsoft Graph API calls work
- [ ] External HTTP requests succeed
- [ ] Error handling works

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Notes:**
```

```

---

## Phase 1C: Environment & Config

**Packages:** python-dotenv==1.2.1

### Automated Tests
- [ ] `pytest tests/ -v` - All tests pass

### Manual Tests
- [ ] Server starts: `python manage.py runserver`
- [ ] .env file loads correctly
- [ ] All environment variables accessible
- [ ] No missing config errors

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Notes:**
```

```

---

## Phase 1D: QuickBooks Integration

**Packages:** intuit-oauth==1.2.6, python-quickbooks==0.9.12

### Automated Tests
- [ ] `pytest tests/ -v -k quickbooks` - All QB tests pass

### Manual Tests
- [ ] OAuth flow works
- [ ] Customer sync works
- [ ] Invoice operations work
- [ ] Error handling correct

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Notes:**
```

```

---

## Phase 2A: Django REST Framework & Extensions

**Packages:** djangorestframework==3.16.1, drf-spectacular==0.29.0, django-htmx==1.27.0, django-cors-headers==4.9.0

### Automated Tests
- [ ] `pytest tests/ -v` - All tests pass
- [ ] Migrations successful: `python manage.py migrate`

### Manual Tests
- [ ] API endpoints respond correctly
- [ ] OpenAPI docs load: `/api/schema/swagger-ui/`
- [ ] CORS headers correct
- [ ] HTMX interactions work
- [ ] API authentication works
- [ ] Pagination works

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Notes:**
```

```

---

## Phase 2B: Authentication & Social Auth

**Packages:** social-auth-app-django==5.7.0

### Automated Tests
- [ ] `pytest tests/ -v -k auth` - All auth tests pass
- [ ] Migrations successful

### Manual Tests
- [ ] SSO login works (Microsoft/Azure AD)
- [ ] User authentication works
- [ ] Logout works
- [ ] Session persistence works
- [ ] User permissions correct

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Notes:**
```

```

---

## Phase 3: Azure Services

**Packages:** azure-identity==1.25.1, azure-keyvault-secrets==4.10.0, azure-storage-blob==12.28.0, azure-monitor-opentelemetry==1.8.5

### Automated Tests
- [ ] `pytest tests/ -v -k azure` - All Azure tests pass

### Manual Tests
- [ ] Azure authentication works
- [ ] Key Vault secrets retrieved
- [ ] Blob storage upload/download works
- [ ] Telemetry/monitoring active
- [ ] No Azure credential errors

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Notes:**
```

```

---

## Phase 4A: Microsoft Authentication Library

**Packages:** msal==1.34.0

### Automated Tests
- [ ] `pytest tests/ -v -k msal` - All MSAL tests pass

### Manual Tests
- [ ] Token acquisition works
- [ ] Token refresh works
- [ ] Microsoft auth flow works
- [ ] No authentication errors

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Notes:**
```

```

---

## Phase 4B: Microsoft Graph SDK ⚠️ HIGH RISK

**Packages:** msgraph-sdk==1.53.0 (1.12 → 1.53 = 40+ versions!)

### Pre-Upgrade
- [ ] Reviewed breaking changes: https://github.com/microsoftgraph/msgraph-sdk-python/releases

### Automated Tests
- [ ] `pytest tests/ -v -k graph` - All Graph tests pass

### Manual Tests - CRITICAL
- [ ] User queries work
- [ ] Group operations work
- [ ] SharePoint access works
- [ ] OneDrive operations work
- [ ] Mail operations work (if used)
- [ ] Calendar operations work (if used)
- [ ] Batch requests work (if used)
- [ ] Error messages meaningful

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Breaking Changes Found:**
```

```

**Notes:**
```

```

---

## Phase 5A: Pydantic Data Validation

**Packages:** pydantic==2.12.5

### Automated Tests
- [ ] `pytest tests/ -v` - All tests pass

### Manual Tests
- [ ] API validation works
- [ ] Request validation correct
- [ ] Response serialization correct
- [ ] Validation errors clear

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Notes:**
```

```

---

## Phase 5B: Cryptography ⚠️ HIGH RISK

**Packages:** cryptography==46.0.4 (43 → 46 MAJOR)

### Pre-Upgrade
- [ ] Reviewed security changelog: https://cryptography.io/en/latest/changelog/

### Automated Tests
- [ ] `pytest tests/ -v -k crypt` - All crypto tests pass

### Manual Tests - CRITICAL
- [ ] Encryption/decryption works
- [ ] Certificate handling works
- [ ] SSL/TLS connections work
- [ ] Password hashing works
- [ ] Token generation works
- [ ] No security degradation

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Notes:**
```

```

---

## Phase 6A: Database Tools

**Packages:** psycopg2-binary==2.9.11, dj-database-url==3.1.0 (2.2 → 3.1 MAJOR)

### Automated Tests
- [ ] `pytest tests/ -v -k database` - All DB tests pass
- [ ] Migrations successful

### Manual Tests
- [ ] Database queries work
- [ ] Connection pooling works
- [ ] Transactions work
- [ ] No connection errors

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Notes:**
```

```

---

## Phase 6B: Redis ⚠️ HIGH RISK

**Packages:** redis==7.1.0 (5.2 → 7.1 MAJOR)

### Pre-Upgrade
- [ ] Reviewed breaking changes: https://github.com/redis/redis-py/releases

### Automated Tests
- [ ] `pytest tests/ -v -k redis` - All Redis tests pass

### Manual Tests - CRITICAL
- [ ] Cache operations work (set/get)
- [ ] Session storage works
- [ ] Cache expiration works
- [ ] Cache clear works
- [ ] Pub/sub works (if used)
- [ ] No RESP3 protocol issues

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Breaking Changes Found:**
```

```

**Notes:**
```

```

---

## Phase 6C: Celery Task Queue

**Packages:** celery==5.6.2

### Automated Tests
- [ ] `pytest tests/ -v -k celery` - All Celery tests pass

### Manual Tests
- [ ] Celery workers start successfully
- [ ] Background tasks execute
- [ ] Periodic tasks run (Beat)
- [ ] Task results retrieved
- [ ] Task queues monitored
- [ ] No worker crashes

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Notes:**
```

```

---

## Phase 6D: Django Redis Backend ⚠️ HIGH RISK

**Packages:** django-redis==6.0.0 (5.4 → 6.0 MAJOR)

### Automated Tests
- [ ] `pytest tests/ -v -k cache` - All cache tests pass
- [ ] Migrations successful

### Manual Tests - CRITICAL
- [ ] Django cache.set() works
- [ ] Django cache.get() works
- [ ] Cache key patterns work
- [ ] Cache invalidation works
- [ ] Session backend works
- [ ] No cache errors

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Notes:**
```

```

---

## Phase 7A: WSGI Server & Static Files ⚠️ HIGH RISK

**Packages:** gunicorn==24.1.1 (23 → 24 MAJOR), whitenoise==6.11.0

### Pre-Upgrade
- [ ] Reviewed Gunicorn config documentation

### Automated Tests
- [ ] Server starts: `gunicorn config.wsgi:application`

### Manual Tests - CRITICAL
- [ ] Gunicorn starts successfully
- [ ] Worker processes spawn correctly
- [ ] Static files serve correctly
- [ ] Static compression works
- [ ] No server errors in logs
- [ ] Production deployment tested

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Config Changes Needed:**
```

```

**Notes:**
```

```

---

## Phase 7B: Image Processing ⚠️ HIGH RISK

**Packages:** pillow==12.1.0 (11 → 12 MAJOR)

### Automated Tests
- [ ] `pytest tests/ -v -k image` - All image tests pass

### Manual Tests - CRITICAL
- [ ] Image uploads work
- [ ] Image processing works
- [ ] Thumbnail generation works
- [ ] Image formats supported
- [ ] Receipt image handling works
- [ ] No image corruption

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Notes:**
```

```

---

## Phase 8A: Testing Framework (Dev Only)

**Packages:** pytest==9.0.2 (MAJOR), pytest-django==4.11.1, pytest-cov==7.0.0 (MAJOR), pytest-mock==3.15.1

### Tests
- [ ] `pytest tests/ -v` - All tests pass
- [ ] `pytest --cov` - Coverage reports work
- [ ] Test discovery works
- [ ] Fixtures work
- [ ] Mocks work

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Config Changes Needed:**
```

```

**Notes:**
```

```

---

## Phase 8B: Code Quality Tools (Dev Only)

**Packages:** black==26.1.0 (MAJOR), flake8==7.3.0, isort==7.0.0 (MAJOR), mypy==1.19.1

### Tests
- [ ] `black --check .` - Formatting correct
- [ ] `flake8 .` - Linting passes
- [ ] `isort --check-only .` - Imports sorted
- [ ] `mypy .` - Type checking passes

### Actions Taken
- [ ] Reformatted code if needed: `black .`
- [ ] Resorted imports if needed: `isort .`
- [ ] Updated type hints if needed

**Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Notes:**
```

```

---

## Post-Upgrade Verification

### Full Integration Tests
- [ ] Complete smoke test of all features
- [ ] User login/logout
- [ ] QuickBooks sync
- [ ] Microsoft Graph operations
- [ ] Receipt uploads
- [ ] Background tasks
- [ ] Celery workers stable

### Performance Check
- [ ] Response times acceptable
- [ ] No memory leaks
- [ ] Cache hit rates normal
- [ ] Database query performance

### Deployment Check
- [ ] Updated requirements.txt committed
- [ ] CI/CD pipeline passes
- [ ] Staging deployment successful
- [ ] Production deployment plan ready

### Documentation
- [ ] Updated CHANGELOG.md
- [ ] Updated README.md if needed
- [ ] Documented any breaking changes
- [ ] Documented any config changes

---

## Final Sign-Off

**All phases completed successfully:** ⬜ Yes | ⬜ No

**Ready for production deployment:** ⬜ Yes | ⬜ No

**Signed off by:** _________________

**Date:** _________________

**Notes:**
```




```
