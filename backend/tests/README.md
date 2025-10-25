# Anti-Blocking Test Suite

## Quick Start

```bash
# Run everything in one command
./setup_and_test.sh
```

## Test Files

- **test_anti_blocking.py** - 35+ unit tests (no HTTP requests)
- **test_anti_blocking_integration.py** - Live integration tests (makes real requests)

## Running Tests

### Fastest (No dependencies)
```bash
python3 validate_anti_blocking.py
```

### Full Unit Tests
```bash
pip install pytest pytest-timeout pytest-mock
pytest tests/test_anti_blocking.py -v -m "not integration"
```

### Using Test Runner
```bash
./run_tests.sh unit          # Unit tests only
./run_tests.sh smoke         # Quick sanity check
./run_tests.sh integration   # ⚠️ Live Amazon requests
./run_tests.sh coverage      # With coverage report
```

## Test Categories

- **Unit Tests** (Safe, fast, no HTTP) - 35+ tests
  - User agent rotation
  - Retry middleware
  - Delay middleware
  - Referer middleware
  - Settings validation

- **Integration Tests** (⚠️ Use sparingly) - 4 tests
  - Live Amazon scraping
  - Multiple requests with rotation
  - Error handling
  - Performance benchmarks

## Expected Results

All unit tests should **PASS**:
```
========== 35 passed in 8.42s ==========
```

## Documentation

- **TESTING_GUIDE.md** - Complete testing guide
- **TESTING_SUMMARY.md** - Quick summary and checklist
- **IMPLEMENTATION_COMPLETE.md** - What was implemented

## Help

```bash
./run_tests.sh help
```
