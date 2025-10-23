# Redis (Upstash) Setup for Background Jobs

## Why Redis?

Background jobs need **persistent storage** that survives:

- Server restarts
- Deployments
- Multiple server instances

**File-based storage** doesn't work on serverless platforms (Vercel, Railway, Render) because their file systems are **ephemeral** (reset on each deployment).

**Redis (Upstash)** provides:
✅ Persistent storage across restarts
✅ Fast key-value access
✅ Automatic TTL (jobs auto-expire after 24 hours)
✅ Free tier available
✅ Works with serverless/containerized deployments

---

## Setup Instructions

### 1. Create Upstash Account (Free)

1. Go to [https://upstash.com/](https://upstash.com/)
2. Sign up (free tier includes 10,000 requests/day)
3. Click "Create Database"
   - Name: `amazon-sales-agent-jobs`
   - Region: Choose closest to your deployment
   - Type: Regional (not Global - cheaper)
4. Click "Create"

---

### 2. Get Redis Credentials

After creating the database:

1. Click on your database name
2. Go to "REST API" tab
3. Copy these values:
   - **UPSTASH_REDIS_REST_URL** (example: `https://your-redis-12345.upstash.io`)
   - **UPSTASH_REDIS_REST_TOKEN** (long token string)

---

### 3. Add Environment Variables

**Local Development (.env file):**

```bash
# Redis Configuration (Upstash)
UPSTASH_REDIS_URL=https://your-redis-12345.upstash.io
UPSTASH_REDIS_TOKEN=AXoq...your-token-here...ABC
USE_REDIS_FOR_JOBS=true
JOB_TTL_HOURS=24
```

**Production (Deployment Platform):**

Add these environment variables to your platform:

**Vercel:**

1. Go to Project Settings → Environment Variables
2. Add:
   - `UPSTASH_REDIS_URL` = `https://your-redis-12345.upstash.io`
   - `UPSTASH_REDIS_TOKEN` = `AXoq...your-token-here...ABC`
   - `USE_REDIS_FOR_JOBS` = `true`

**Railway/Render:**

1. Go to Environment Variables
2. Add the same variables as above

---

### 4. Install Dependencies

```bash
cd backend
uv sync
# or
pip install -r pyproject.toml
```

The `upstash-redis` package is already added to `pyproject.toml`.

---

### 5. Test Connection

Start your backend server:

```bash
cd backend
uv run dev
```

**Look for this in logs:**

```
🔴 [JOB MANAGER] Redis (Upstash) initialized successfully
   ⏱️  Job TTL: 24 hours
```

**If Redis connection fails:**

```
⚠️  [JOB MANAGER] Redis connection failed: [error message]
   📁 Falling back to file-based storage
```

This means:

- ❌ `UPSTASH_REDIS_URL` or `UPSTASH_REDIS_TOKEN` is incorrect
- ❌ Redis database is not running
- ✅ App will still work using file storage (for local dev only)

---

## How It Works

### Job Lifecycle with Redis

```
1. User submits analysis
   ↓
2. Backend creates job_id
   ↓
3. Redis stores: "job:{job_id}" → {status, progress, message}
   ↓
4. Background task runs (2 hours)
   ↓
5. Redis stores: "results:{job_id}" → {full analysis data}
   ↓
6. Frontend polls: GET /job-status/{job_id}
   ↓
7. Redis returns: {status: "complete", progress: 100}
   ↓
8. Frontend fetches: GET /job-results/{job_id}
   ↓
9. Redis returns: {full analysis data}
   ↓
10. After 24 hours: Redis auto-deletes (TTL)
```

### Storage Comparison

| Feature              | File Storage                         | Redis (Upstash)                 |
| -------------------- | ------------------------------------ | ------------------------------- |
| **Deployment**       | ❌ Doesn't persist on Vercel/Railway | ✅ Works everywhere             |
| **Multiple Servers** | ❌ Each server has own files         | ✅ Shared across all servers    |
| **Cleanup**          | ❌ Manual cleanup needed             | ✅ Auto-expires via TTL         |
| **Speed**            | 🐢 Slow (disk I/O)                   | 🚀 Fast (in-memory)             |
| **Cost**             | ✅ Free                              | ✅ Free tier (10K requests/day) |

---

## Fallback Behavior

The app has **automatic fallback**:

1. **If Redis is configured and working:**

   - ✅ All jobs stored in Redis
   - ✅ Results persist across restarts

2. **If Redis is NOT configured:**
   - 📁 Falls back to file-based storage
   - ⚠️ Only works for local development
   - ❌ Won't work on Vercel/Railway/Render

---

## Troubleshooting

### "Results not found after job completes"

**Check logs for:**

```
💾 [REDIS] ✅ Results saved successfully for job: abc-123-def
   💽 Size: 1234.5 KB
   ⏱️  TTL: 24 hours
```

**If you DON'T see this:**

- ❌ Redis is not being used (check `USE_REDIS_FOR_JOBS=true`)
- ❌ Redis credentials are incorrect
- ❌ Redis database is down

### "Redis connection failed"

**Common causes:**

1. **Wrong URL format:** Should start with `https://`
2. **Wrong credentials:** Copy exact values from Upstash console
3. **Database paused:** Upstash pauses inactive databases after 30 days (free tier)

**Fix:**

1. Go to Upstash console
2. Check database status (should be "Active")
3. Verify credentials in "REST API" tab
4. Update `.env` with correct values

### "Job status stuck at 'processing'"

**Check if job actually completed:**

```bash
# Look for this in server logs:
✅ [BACKGROUND JOB] Job completed: abc-123-def
📊 [JOB MANAGER] Updated job abc-123-def: complete (100%)
```

**If job never completes:**

- ⏱️ Job might still be running (2 hours for large datasets)
- ❌ Job might have crashed (check error logs)
- 🔍 Check Uvicorn timeout (should be 5 hours)

---

## Redis Dashboard

Monitor your jobs in Upstash:

1. Go to [Upstash Console](https://console.upstash.com/)
2. Click your database
3. Go to "Data Browser" tab
4. Search for keys:
   - `job:*` - All job statuses
   - `results:*` - All job results

You can manually:

- ✅ View job data
- ✅ Delete stuck jobs
- ✅ Check TTL (time remaining)

---

## Cost Estimate

**Free Tier (Upstash):**

- 10,000 requests per day
- 256 MB storage

**Typical Usage:**

- 1 analysis = ~6 Redis operations (create, update x4, save results)
- 10,000 requests = ~1,600 analyses per day
- Most analyses < 2 MB results

**Verdict:** ✅ Free tier is more than enough for most use cases

---

## Questions?

If Redis setup isn't working:

1. Check server logs for error messages
2. Verify credentials in Upstash console
3. Try the "Test Connection" command above
4. Check if `USE_REDIS_FOR_JOBS=true` in environment variables
