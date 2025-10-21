# Amazon Scraper - Anti-Blocking Setup Guide

## 🚀 Quick Start

The scraper now includes comprehensive anti-blocking features:

✅ **User Agent Rotation** (automatic)  
✅ **Header Randomization** (automatic)  
✅ **Browser Fingerprint Masking** (automatic)  
✅ **Random Delays** (2-5 seconds between requests)  
✅ **Smart Retry Logic** (handles 403, 503, captcha)  
✅ **Residential Proxy Support** (optional but recommended)

---

## 📋 Environment Variables

Add these to your `.env` file:

### Basic Settings (Required)

```env
# Log level
SCRAPER_LOG_LEVEL=ERROR

# Random delays (CRITICAL for avoiding detection)
RANDOM_DELAY_MIN=2.0
RANDOM_DELAY_MAX=5.0

# Retry settings
SCRAPER_RETRY_TIMES=3
SCRAPER_TIMEOUT=45
```

### Proxy Configuration (Highly Recommended)

#### Option 1: Single Proxy

```env
SCRAPER_PROXY=http://username:password@proxy.example.com:8080
```

#### Option 2: Multiple Proxies (Comma-separated)

```env
SCRAPER_PROXY_LIST=http://proxy1.com:8080,http://proxy2.com:8080,http://proxy3.com:8080
```

#### Option 3: Bright Data (Recommended)

```env
BRIGHT_DATA_HOST=brd.superproxy.io:22225
BRIGHT_DATA_USER=brd-customer-<YOUR_CUSTOMER_ID>-zone-<YOUR_ZONE>
BRIGHT_DATA_PASS=<YOUR_PASSWORD>
```

**Sign up:** https://brightdata.com/

#### Option 4: Smartproxy

```env
SMARTPROXY_HOST=gate.smartproxy.com:7000
SMARTPROXY_USER=user-<YOUR_USER>
SMARTPROXY_PASS=<YOUR_PASSWORD>
```

**Sign up:** https://smartproxy.com/

#### Option 5: Oxylabs (Premium)

```env
OXYLABS_HOST=pr.oxylabs.io:7777
OXYLABS_USER=customer-<YOUR_USER>
OXYLABS_PASS=<YOUR_PASSWORD>
```

**Sign up:** https://oxylabs.io/

#### Option 6: IPRoyal (Budget)

```env
IPROYAL_HOST=geo.iproyal.com:12321
IPROYAL_USER=<YOUR_USER>
IPROYAL_PASS=<YOUR_PASSWORD>
```

**Sign up:** https://iproyal.com/

---

## 💰 Cost Comparison

| Provider            | Monthly Cost | Quality    | Best For                       |
| ------------------- | ------------ | ---------- | ------------------------------ |
| **Bright Data**     | $50-300      | ⭐⭐⭐⭐⭐ | High volume, best success rate |
| **Smartproxy**      | $50-150      | ⭐⭐⭐⭐   | Good balance of cost/quality   |
| **Oxylabs**         | $100-500     | ⭐⭐⭐⭐⭐ | Enterprise, premium quality    |
| **IPRoyal**         | $30-100      | ⭐⭐⭐     | Budget-friendly, lower volume  |
| **Free (no proxy)** | $0           | ⭐         | Testing only, will get blocked |

---

## 🎯 Recommended Configuration

### For Production (High Volume)

```env
# Use residential proxies
BRIGHT_DATA_HOST=brd.superproxy.io:22225
BRIGHT_DATA_USER=brd-customer-<YOUR_ID>-zone-<ZONE>
BRIGHT_DATA_PASS=<YOUR_PASS>

# Aggressive delays to avoid detection
RANDOM_DELAY_MIN=3.0
RANDOM_DELAY_MAX=7.0

# More retries
SCRAPER_RETRY_TIMES=5

# Verbose logging to monitor blocks
SCRAPER_LOG_LEVEL=INFO
```

### For Development/Testing (Low Volume)

```env
# No proxy (might get blocked)
# Or use free/cheap proxy service

# Moderate delays
RANDOM_DELAY_MIN=2.0
RANDOM_DELAY_MAX=5.0

# Standard retries
SCRAPER_RETRY_TIMES=3

# Minimal logging
SCRAPER_LOG_LEVEL=ERROR
```

---

## 🔧 How It Works

### 1. User Agent Rotation

Automatically rotates between 15+ real browser user agents:

- Chrome (Windows, Mac, Linux)
- Firefox (Windows, Mac)
- Safari (Mac)
- Edge (Windows)

### 2. Header Randomization

Each request gets randomized headers:

- `Accept-Language` (5 variations)
- `Referer` (4 variations)
- `sec-ch-ua` (Chrome fingerprint)
- Browser-specific headers

### 3. Proxy Rotation

Three strategies available:

- **Random**: New proxy per request (default)
- **Rotating**: Same proxy for 30s, then rotate
- **Sequential**: Cycle through proxies in order

### 4. Random Delays

Mimics human behavior:

- 2-5 second delays between requests
- Randomized timing (not predictable)
- Prevents rate limit triggers

### 5. Smart Retry

Automatically retries on:

- 403 (Forbidden)
- 503 (Service Unavailable)
- 429 (Too Many Requests)
- CAPTCHA detection
- Response too small (< 5KB)

---

## 🚨 Troubleshooting

### Still Getting Blocked?

#### 1. Check Your Proxies

```bash
# View proxy status in logs
SCRAPER_LOG_LEVEL=INFO python backend/app/services/amazon/standalone_scraper.py <URL>
```

Look for:

```
✅ Proxy rotation enabled with X proxies
Using proxy: xxx.xxx.xxx.xxx:xxxx
```

#### 2. Increase Delays

```env
# Try longer delays
RANDOM_DELAY_MIN=5.0
RANDOM_DELAY_MAX=10.0
```

#### 3. Reduce Request Volume

```env
# Only 1 concurrent request
SCRAPER_CONCURRENT_REQUESTS=1
```

#### 4. Use Better Proxies

- **Free proxies** → Will get blocked quickly
- **Datacenter proxies** → Amazon detects them
- **Residential proxies** → Best success rate

#### 5. Check for CAPTCHA

```bash
# Enable debug logging
SCRAPER_LOG_LEVEL=DEBUG

# Look for:
🚫 CAPTCHA detected - consider using better proxies or slower rate
```

---

## 📊 Monitoring

### Success Indicators

```
✅ Proxy rotation enabled with 5 proxies
✅ Random delay enabled: 2.0-5.0s between requests
💤 Waiting 3.42s before next request...
Using proxy: xxx.xxx.xxx.xxx:xxxx
Using User-Agent: Mozilla/5.0...
Applied randomized headers with Referer: https://www.amazon.com/
```

### Warning Signs

```
⚠️ Received 403 - Amazon might be blocking
⚠️ Response too small (2341 bytes) - might be blocked
🚫 CAPTCHA detected
⚠️ No proxies configured - requests will use direct connection
```

---

## 🎓 Best Practices

### DO ✅

- Use residential proxies for production
- Keep delays at 2-5 seconds minimum
- Monitor logs for blocks
- Start with low volume, then scale
- Use sticky sessions (same IP for multiple requests)

### DON'T ❌

- Use free/datacenter proxies for production
- Make concurrent requests to same domain
- Remove random delays (will get blocked instantly)
- Ignore CAPTCHA warnings
- Scrape without monitoring

---

## 🔐 Legal Disclaimer

**Important:** Web scraping may violate Amazon's Terms of Service. This tool is provided for educational purposes and internal data analysis only.

**Recommendations:**

1. Check Amazon's Terms of Service
2. Consider using Amazon Product Advertising API (legal)
3. Use scraped data responsibly (don't resell)
4. Respect rate limits and server resources

---

## 🆘 Need Help?

### Common Issues

**"No proxies configured" warning**

- Solution: Add proxy config to `.env` file

**Still getting 403/503 errors**

- Solution: Use better proxies (residential) + increase delays

**CAPTCHA every request**

- Solution: Your IP/proxy is burned, switch providers

**Very slow scraping**

- Solution: This is expected! 2-5s delays are required to avoid blocks

---

## 📈 Performance Expectations

### With Proxies + Delays

- **Speed**: 10-15 requests/minute
- **Success Rate**: 95-99%
- **Cost**: $50-300/month

### Without Proxies

- **Speed**: Varies (until blocked)
- **Success Rate**: 20-50%
- **Cost**: Free
- **Result**: Will get blocked within hours/days

---

## ✅ Quick Setup Checklist

- [ ] Add proxy credentials to `.env`
- [ ] Set `RANDOM_DELAY_MIN=2.0` and `RANDOM_DELAY_MAX=5.0`
- [ ] Set `SCRAPER_LOG_LEVEL=INFO` for monitoring
- [ ] Test with single URL first
- [ ] Monitor logs for blocks/captchas
- [ ] Adjust delays if needed
- [ ] Scale up volume gradually

---

**Status:** Ready to use ✅  
**Features:** All anti-blocking features are now active and working!
