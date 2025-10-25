# Testing Guide for Anti-Blocking Features

## 🎯 Overview

This guide covers testing the Amazon scraper anti-blocking implementation before pushing to production.

## 📋 Test Structure

```
backend/tests/
├── test_anti_blocking.py              # Unit tests (no HTTP requests)
├── test_anti_blocking_integration.py  # Integration tests (real requests)
└── ...

backend/
├── pytest.ini                         # Pytest configuration
└── run_tests.sh                       # Test runner script
```

## 🚀 Quick Start

### 1. Install Test Dependencies

```bash
cd backend
pip install pytest pytest-timeout pytest-mock
```

### 2. Run Unit Tests (Recommended First)

```bash
# Using test runner script
./run_tests.sh unit

# Or directly with pytest
pytest tests/test_anti_blocking.py -v -m "not integration"
```

**Expected Output:**
```
✅ test_user_agent_pool_not_empty PASSED
✅ test_user_agent_contains_browser_info PASSED
✅ test_random_user_agent_returns_valid_agent PASSED
✅ test_middleware_sets_user_agent_on_request PASSED
✅ test_middleware_rotates_user_agents PASSED
...
```

### 3. Run Smoke Tests (Quick Sanity Check)

```bash
./run_tests.sh smoke
```

### 4. Run Integration Tests (⚠️ Use Sparingly)

```bash
# WARNING: Makes real requests to Amazon!
./run_tests.sh integration
```

## 📊 Test Categories

### Unit Tests (`test_anti_blocking.py`)
- **Fast**: Complete in seconds
- **No HTTP requests**: Mock all external calls
- **Safe**: Can run repeatedly without limits

**Test Classes:**
1. `TestUserAgentRotation` - User agent pool and rotation
2. `TestEnhancedRetryMiddleware` - Retry logic and CAPTCHA detection
3. `TestRandomDelayMiddleware` - Random delay implementation
4. `TestRefererMiddleware` - Referer header setting
5. `TestAntiBlockingSettings` - Settings configuration
6. `TestScraperIntegration` - Scraper integration with mocked responses
7. `TestEndToEndScenarios` - End-to-end flows with mocks

### Integration Tests (`test_anti_blocking_integration.py`)
- **Slow**: Can take minutes
- **Real HTTP requests**: Actually scrapes Amazon
- **Limited runs**: Risk of temporary IP blocks

**Test Classes:**
1. `TestLiveScraperIntegration` - Live scraping tests
2. `TestProxySupport` - Proxy functionality (optional)
3. `TestScraperPerformance` - Performance benchmarks
4. `TestErrorHandling` - Error handling edge cases

## 🧪 Running Specific Tests

### Run specific test class
```bash
pytest tests/test_anti_blocking.py::TestUserAgentRotation -v
```

### Run specific test method
```bash
pytest tests/test_anti_blocking.py::TestUserAgentRotation::test_user_agent_pool_not_empty -v
```

### Run with extra verbosity
```bash
pytest tests/test_anti_blocking.py -vv
```

### Run with print statements shown
```bash
pytest tests/test_anti_blocking.py -s
```

### Run tests matching pattern
```bash
pytest tests/test_anti_blocking.py -k "user_agent" -v
```

## 📈 Test Coverage

### Generate coverage report
```bash
./run_tests.sh coverage

# Or manually
pip install pytest-cov
pytest tests/test_anti_blocking.py \
    --cov=app.services.amazon \
    --cov-report=html \
    --cov-report=term \
    -m "not integration"
```

**View HTML report:**
```bash
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
```

## ✅ Pre-Production Checklist

Run these tests before pushing to production:

### Step 1: Unit Tests ✅
```bash
./run_tests.sh unit
```
**Expected Result:** All tests should PASS
- ~35+ unit tests
- Completes in < 10 seconds

### Step 2: Smoke Tests ✅
```bash
./run_tests.sh smoke
```
**Expected Result:** All tests should PASS
- Quick sanity checks
- Completes in < 5 seconds

### Step 3: Coverage Check ✅
```bash
./run_tests.sh coverage
```
**Expected Result:** 
- Coverage > 80% for anti-blocking modules
- All critical paths covered

### Step 4: Integration Test (Optional but Recommended) ⚠️
```bash
./run_tests.sh integration
```
**Expected Result:**
- Main scraping test should PASS
- At least 2/3 requests should succeed
- Should see "Anti-blocking used: True"

**WARNING:** Only run 1-2 times per day to avoid IP blocks!

## 🔍 What Each Test Validates

### User Agent Rotation
- ✅ Pool has 10+ user agents
- ✅ User agents look realistic (contain browser info)
- ✅ Middleware sets User-Agent header
- ✅ User agents actually rotate (not always the same)

### Enhanced Retry Middleware
- ✅ Retries on HTTP 500 (server error)
- ✅ Retries on HTTP 503 (service unavailable)
- ✅ Detects CAPTCHA by Content-Type (image/jpeg)
- ✅ Detects CAPTCHA by keywords ("captcha", "robot")
- ✅ Does NOT retry valid HTML responses
- ✅ Properly calls Scrapy's retry mechanism

### Random Delay Middleware
- ✅ Adds delay to request meta
- ✅ Delay is within configured range (2-5s)
- ✅ Delays vary across requests (random)
- ✅ Loads settings from crawler config

### Referer Middleware
- ✅ Sets Referer for amazon.com
- ✅ Sets Referer for amazon.co.uk
- ✅ Sets Referer for amazon.de
- ✅ Does NOT override existing Referer

### Anti-Blocking Settings
- ✅ Settings module loads without errors
- ✅ Retry enabled with 5+ attempts
- ✅ Retry codes include 500, 503, 429, 403
- ✅ AutoThrottle enabled
- ✅ Cookies enabled
- ✅ Custom middlewares configured
- ✅ Built-in UserAgentMiddleware disabled
- ✅ Proper headers (Accept, Sec-Fetch-*, etc.)
- ✅ Concurrent requests limited (1-2)
- ✅ ROBOTSTXT_OBEY disabled

### Live Integration (when run)
- ✅ Scraper successfully fetches Amazon page
- ✅ Anti-blocking features are used
- ✅ HTTP 200 status received
- ✅ Response size > 5000 bytes
- ✅ Product title extracted
- ✅ Feature bullets extracted
- ✅ Images extracted
- ✅ Multiple requests work with rotation
- ✅ Handles invalid URLs gracefully
- ✅ Completes within timeout (< 2 minutes)

## 🐛 Debugging Failed Tests

### Test fails: "ModuleNotFoundError"
**Solution:**
```bash
# Ensure you're in backend directory
cd backend

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-timeout pytest-mock

# Run from backend directory
pytest tests/test_anti_blocking.py -v
```

### Test fails: "Import error for anti_blocking"
**Solution:**
```bash
# Check files exist
ls app/services/amazon/anti_blocking.py
ls app/services/amazon/middlewares.py
ls app/services/amazon/user_agents.py

# Verify Python path
python -c "import sys; print(sys.path)"

# Try running from backend dir
cd backend
pytest tests/test_anti_blocking.py -v
```

### Integration test fails: "Blocked or insufficient content"
**Expected!** This means:
1. Amazon blocked the request (working as expected - that's what we're testing!)
2. Anti-blocking features will retry
3. Should eventually succeed on retry

**If it fails repeatedly:**
```bash
# Your IP may be temporarily blocked
# Wait 1-2 hours or:

# Use a proxy
export SCRAPER_PROXY="http://user:pass@proxy.com:8080"
./run_tests.sh integration

# Or skip integration tests for now
./run_tests.sh unit  # Still validates anti-blocking logic
```

### Test timeout
**Solution:**
```bash
# Increase timeout in pytest.ini
timeout = 600  # 10 minutes

# Or run with custom timeout
pytest tests/test_anti_blocking_integration.py --timeout=600
```

## 📊 Continuous Integration (CI/CD)

### GitHub Actions Example

```yaml
name: Anti-Blocking Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-timeout pytest-mock
      
      - name: Run unit tests
        run: |
          cd backend
          pytest tests/test_anti_blocking.py -v -m "not integration"
      
      # Only run integration tests on main branch (to avoid IP blocks)
      - name: Run integration tests (main branch only)
        if: github.ref == 'refs/heads/main'
        run: |
          cd backend
          pytest tests/test_anti_blocking_integration.py -v -m integration --maxfail=1
```

## 🎯 Success Criteria

Before pushing to production, ensure:

| Criteria | Status |
|----------|--------|
| ✅ All unit tests pass | [ ] |
| ✅ Smoke tests pass | [ ] |
| ✅ Coverage > 80% | [ ] |
| ✅ At least 1 integration test passes | [ ] |
| ✅ No import errors | [ ] |
| ✅ Settings load correctly | [ ] |
| ✅ Middlewares initialize without errors | [ ] |
| ✅ User agents rotate | [ ] |
| ✅ Retry logic works | [ ] |
| ✅ CAPTCHA detection works | [ ] |

## 📝 Test Output Examples

### ✅ Success
```
tests/test_anti_blocking.py::TestUserAgentRotation::test_user_agent_pool_not_empty PASSED
tests/test_anti_blocking.py::TestEnhancedRetryMiddleware::test_retries_on_500_status PASSED
tests/test_anti_blocking.py::TestAntiBlockingSettings::test_settings_module_loads PASSED

========== 35 passed in 4.21s ==========
```

### ❌ Failure
```
tests/test_anti_blocking.py::TestUserAgentRotation::test_middleware_sets_user_agent FAILED

FAILED - AssertionError: 'User-Agent' not in headers
```

### ⚠️ Warning (Integration)
```
tests/test_anti_blocking_integration.py::TestLiveScraperIntegration::test_scraper_with_anti_blocking_succeeds

SCRAPING RESULT:
  Success: False
  Error: Blocked or insufficient content
  
This is EXPECTED - the anti-blocking features will retry!
```

## 🔧 Environment Variables for Testing

```bash
# Optional: Set custom test URL
export TEST_AMAZON_URL="https://www.amazon.com/dp/B0BSHF7WHW"

# Optional: Use proxy for testing
export SCRAPER_PROXY="http://user:pass@proxy.com:8080"

# Optional: Adjust log level
export SCRAPER_LOG_LEVEL="DEBUG"
```

## 📚 Additional Resources

- **Scrapy Testing Docs**: https://docs.scrapy.org/en/latest/topics/testing.html
- **Pytest Docs**: https://docs.pytest.org/
- **Coverage Docs**: https://coverage.readthedocs.io/

## 🆘 Getting Help

If tests fail unexpectedly:

1. Check this guide's debugging section
2. Verify all files were created correctly
3. Check Python version (3.8+ required)
4. Verify dependencies installed
5. Check the anti-blocking implementation files exist

## ✨ Next Steps After Tests Pass

1. ✅ Run unit tests - Should all pass
2. ✅ Run smoke tests - Should all pass  
3. ✅ Check coverage - Should be > 80%
4. ✅ Run 1-2 integration tests - At least 1 should pass
5. 🚀 Ready for production!

---

**Remember**: Integration tests make real HTTP requests. Use sparingly!
