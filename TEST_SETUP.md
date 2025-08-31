# 🧪 Keyword Agent Test Setup

This document explains how to test the Keyword Agent implementation using the dedicated test page.

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)
```bash
# From the project root
./start_test_servers.sh
```

### Option 2: Manual Setup

1. **Start Backend Server:**
```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

2. **Start Frontend Server:**
```bash
cd frontend
npm run dev
```

## 🧪 Testing the Keyword Agent

1. **Open Test Page:** http://localhost:3000/test

2. **Upload CSV File:** 
   - Use the sample file: `backend/US_AMAZON_cerebro_B00O64QJOC_2025-08-21.csv`
   - Or upload your own Helium10 Cerebro CSV file

3. **Optional:** Enter an ASIN (e.g., `B00O64QJOC`)

4. **Run Test:** Click "🚀 Test Keyword Agent"

5. **Review Results:**
   - Category distribution (Relevant, Design-Specific, Irrelevant, Branded)
   - Top opportunities and coverage gaps
   - Processing time and quality metrics
   - Download results as CSV

## 📊 Expected Results

With the sample CSV file, you should see:
- **236 total keywords** processed
- **Categories:** Relevant, Design-Specific, Branded, Spanish
- **Top opportunities** identified (zero title density keywords with high volume)
- **Root word analysis** showing keyword groupings
- **Processing time** under 1 second
- **Data quality score** near 100%

## 🔧 API Endpoints

- **Test Status:** `GET /api/v1/test/status`
- **Keyword Agent Test:** `POST /api/v1/test/keyword-agent`
- **CSV Upload:** `POST /api/v1/upload/csv`
- **API Docs:** http://localhost:8000/docs

## 🐛 Troubleshooting

### Backend Issues
```bash
# Check if backend is running
curl http://localhost:8000/api/v1/test/status

# Check backend logs
cd backend && uv run uvicorn app.main:app --reload --port 8000
```

### Frontend Issues
```bash
# Check if frontend is running
curl http://localhost:3000

# Restart frontend
cd frontend && npm run dev
```

### Port Conflicts
```bash
# Kill existing processes
pkill -f uvicorn
pkill -f next

# Check what's using ports
lsof -i :8000
lsof -i :3000
```

## 📁 File Structure

```
amazon-sales-agent/
├── backend/
│   ├── app/
│   │   ├── local_agents/keyword/    # Keyword Agent implementation
│   │   └── api/v1/endpoints/test.py # Test API endpoint
│   └── US_AMAZON_cerebro_*.csv      # Sample data
├── frontend/
│   └── app/test/page.tsx            # Test page UI
└── start_test_servers.sh            # Startup script
```

## 🎯 What's Being Tested

The test validates:

1. **✅ Keyword Categorization**
   - Relevant vs Design-Specific vs Irrelevant vs Branded
   - Handles combined categories (e.g., "I/D")

2. **✅ Relevancy Scoring**
   - MVP formula: `=countif(range, filter)`
   - Counts competitors in top 10 positions

3. **✅ Root Word Analysis**
   - Groups keywords by root words
   - Calculates broad search volume

4. **✅ Title Density Analysis**
   - Identifies zero title density keywords
   - Applies MVP filtering rules

5. **✅ Performance**
   - Fast processing (< 1 second for 236 keywords)
   - High data quality scores

## 🔄 Next Steps

After successful testing:
1. Implement Scoring Agent (intent scoring 0-3)
2. Implement SEO Agent (listing optimization)
3. Create main orchestration workflow
4. Build production frontend interface

## 📞 Support

If you encounter issues:
1. Check the browser console for errors
2. Check backend logs for API errors
3. Verify CSV file format matches Helium10 structure
4. Ensure all dependencies are installed (`uv sync` in backend, `npm install` in frontend) 