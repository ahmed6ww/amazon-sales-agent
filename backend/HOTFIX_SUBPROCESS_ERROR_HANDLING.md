# HOTFIX: Subprocess Error Handling Improvements

**Date:** October 21, 2025  
**Issue:** "Scraper process failed:" with no error details  
**Status:** ✅ Fixed

---

## 🐛 Problem

After fixing the Scrapy reactor issues, a new problem appeared:

```
ERROR: 500: Scraping failed: Scraper process failed:
```

**The error message was empty** - nothing after the colon!

---

## 🔍 Root Cause

The subprocess running `standalone_scraper.py` was failing, but:

1. **No stderr output** - The process crashed before writing to stderr
2. **Debug output to stdout** - Print statements were polluting the JSON output
3. **Poor error capture** - Only capturing stderr, missing stdout errors
4. **No traceback** - When imports failed, no details were shown

---

## ✅ Solution Applied

### **Fix 1: Capture Both stdout and stderr**

**File:** `backend/app/local_agents/research/helper_methods.py`

**Before:**

```python
if result.returncode != 0:
    return {
        "success": False,
        "error": f"Scraper process failed: {result.stderr.strip()}",  # Empty!
        ...
    }
```

**After:**

```python
if result.returncode != 0:
    # Capture both stderr and stdout for better error diagnosis
    error_msg = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
    if not error_msg:
        error_msg = f"Process exited with code {result.returncode} (no output)"
    return {
        "success": False,
        "error": f"Scraper process failed: {error_msg}",
        ...
    }
```

**Why:** If stderr is empty, check stdout. If both empty, show exit code.

---

### **Fix 2: Better Exception Handling in Standalone Scraper**

**File:** `backend/app/services/amazon/standalone_scraper.py`

**Added:**

```python
except ImportError as e:
    import traceback
    error_details = f"Import error: {str(e)}\n{traceback.format_exc()}"
    print(json.dumps({"success": False, "error": error_details, ...}), file=sys.stderr)
    sys.exit(1)
except Exception as e:
    import traceback
    error_details = f"{str(e)}\n{traceback.format_exc()}"
    print(json.dumps({"success": False, "error": error_details, ...}), file=sys.stderr)
    sys.exit(1)
```

**Why:**

- Separate handling for ImportError (common with anti-blocking)
- Full traceback included in error message
- Error JSON goes to stderr for proper capture

---

### **Fix 3: Debug Output to stderr, Not stdout**

**Files:**

- `backend/app/services/amazon/scraper.py`
- `backend/app/services/amazon/standalone_search_scraper.py`

**Changed all print statements:**

```python
# Before
print(f"✅ Anti-blocking features enabled")  # Goes to stdout, pollutes JSON

# After
print(f"✅ Anti-blocking features enabled", file=sys.stderr)  # Clean JSON output
```

**Why:**

- stdout should only contain the JSON result
- Debug messages go to stderr
- Prevents JSON parsing errors from polluted output

---

### **Fix 4: Exit with Error Code on Scraping Failure**

**File:** `backend/app/services/amazon/standalone_scraper.py`

**Added:**

```python
print(json.dumps(result))
# Exit with error code if scraping failed
if not result.get("success"):
    sys.exit(1)
```

**Why:** Even if JSON is valid, exit with code 1 if scraping failed, so subprocess handler knows to check error field.

---

## 📊 Before vs After

### **Before (No Error Details):**

```
ERROR: 500: Scraping failed: Scraper process failed:
                                                      ^ Empty!
```

**User sees:** No clue what went wrong

---

### **After (Detailed Errors):**

**If anti-blocking import fails:**

```
ERROR: 500: Scraping failed: Scraper process failed:
Import error: No module named 'scrapy'
Traceback (most recent call last):
  File "scraper.py", line 22, in main
    from app.services.amazon.scraper import scrape_amazon_product
  ...
ImportError: No module named 'scrapy'
```

**If Scrapy reactor crashes:**

```
ERROR: 500: Scraping failed: Scraper process failed:
Scraper crashed: ReactorNotRestartable
Traceback (most recent call last):
  File "scraper.py", line 531, in scrape_amazon_product
    process.start()
  ...
```

**If process exits with no output:**

```
ERROR: 500: Scraping failed: Scraper process failed:
Process exited with code 1 (no output)
```

**User sees:** Exactly what went wrong and where

---

## 🧪 Testing

### **Test 1: Simulate Import Error**

```python
# In standalone_scraper.py, temporarily break import:
from app.services.amazon.NONEXISTENT import scrape_amazon_product

# Run scraper
cd backend
python app/services/amazon/standalone_scraper.py "https://amazon.com/dp/test"
```

**Expected stderr:**

```json
{"success": false, "error": "Import error: No module named 'NONEXISTENT'\n[full traceback]", ...}
```

---

### **Test 2: Simulate Scrapy Crash**

```python
# In scraper.py, add after line 531:
raise Exception("Test crash")

# Run scraper
```

**Expected stderr:**

```json
{"success": false, "error": "Test crash\n[full traceback]", ...}
```

---

### **Test 3: Check Clean JSON Output**

```bash
cd backend
python app/services/amazon/standalone_scraper.py "https://amazon.com/dp/test" 2>errors.txt
# Stdout should contain ONLY valid JSON
# Stderr should contain debug messages
```

---

## 📁 Files Modified

1. ✅ `backend/app/local_agents/research/helper_methods.py`

   - Capture both stdout and stderr
   - Show exit code if no output

2. ✅ `backend/app/services/amazon/standalone_scraper.py`

   - Separate ImportError handling
   - Full tracebacks in errors
   - Error output to stderr
   - Exit with code 1 on failure

3. ✅ `backend/app/services/amazon/scraper.py`

   - All debug output to stderr
   - Traceback to stderr

4. ✅ `backend/app/services/amazon/standalone_search_scraper.py`
   - All debug output to stderr

---

## ✅ Impact

| Issue                    | Before                     | After                     |
| ------------------------ | -------------------------- | ------------------------- |
| **Empty error messages** | "Scraper process failed: " | Full error with traceback |
| **Import errors**        | Silent failure             | "Import error: [details]" |
| **Scrapy crashes**       | "Unknown error"            | "Scraper crashed: [type]" |
| **JSON pollution**       | Debug mixed with JSON      | Clean JSON on stdout      |
| **Debugging**            | Impossible                 | Full traceback available  |

---

## 🎯 Key Lessons

### ❌ **Don't Do This:**

```python
# Only capture stderr
error_msg = result.stderr.strip()  # Might be empty!

# Print debug to stdout
print("Debug message")  # Pollutes JSON!
```

### ✅ **Do This:**

```python
# Capture both stderr and stdout
error_msg = result.stderr.strip() or result.stdout.strip()

# Print debug to stderr
print("Debug message", file=sys.stderr)  # Clean stdout!
```

---

## 🔍 How to Debug Future Subprocess Issues

1. **Check both outputs:**

   ```python
   print(f"STDOUT: {result.stdout}")
   print(f"STDERR: {result.stderr}")
   print(f"EXIT CODE: {result.returncode}")
   ```

2. **Test standalone scraper directly:**

   ```bash
   python standalone_scraper.py "url" 2>errors.txt
   cat errors.txt  # View debug output
   ```

3. **Check for JSON pollution:**
   ```bash
   python standalone_scraper.py "url" | python -m json.tool
   # Should parse cleanly
   ```

---

**Status:** ✅ Fixed  
**Impact:** Much better error visibility for debugging  
**Risk:** Low - only improved error handling, no logic changes

Now you'll see **exactly** what's failing and why! 🔍
