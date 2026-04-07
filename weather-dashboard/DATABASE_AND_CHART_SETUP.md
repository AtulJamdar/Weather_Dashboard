# Weather Dashboard - Database & Chart Setup Guide

## Quick Start (Complete Flow)

### Prerequisites
- PostgreSQL running
- All 3 servers running (Java 8080, Python 8000, Frontend 5173)

### Step 1: Setup Database Table

```powershell
cd backend-python

# Activate venv
.\venv\Scripts\activate

# Run setup script to create table
python setup_db.py
```

Expected output:
```
Connecting to database: postgresql://...
✅ Database setup successful! weather_history table created.
```

### Step 2: Test the Complete Flow

Open frontend at `http://localhost:5173` and search for a city (e.g., "London")

**You should see:**
1. ✅ Current weather data (Temperature, Humidity, Condition)
2. ✅ AI Insight from Groq
3. ✅ Temperature chart with 24-hour data

---

## Chart Data Sources (Priority Order)

### 1. **Real Database Data** (if available)
- Shows actual temperature history from the last 24 hours
- Only available if:
  - You've searched for the same city multiple times in the past 24 hours
  - Database table exists and is connected

### 2. **Mock/Sample Data** (Fallback)
- Shows realistic sample data with temperature variations
- Used when:
  - Database table doesn't exist yet
  - No historical data for that city
  - Database connection fails
- **This is intentional** - provides a good UX even during setup

---

## API Endpoints & Data Flow

### Frontend → Java Backend → Python Backend → Database

```
1. Frontend Search
   GET http://localhost:8080/api/weather/London

2. Java Backend (Caches + Forwards)
   → GET http://127.0.0.1:8000/weather/London

3. Python Backend (Fetches Weather + AI)
   → OpenWeatherMap API
   → Groq AI for summary
   → Saves to PostgreSQL

4. Response Back to Frontend
   {
     "city": "London",
     "temperature": "12°C",
     "humidity": "65%",
     "condition": "partly cloudy",
     "ai_insight": "..."
   }

5. Frontend Calls History
   GET http://localhost:8080/api/history/London

6. Java Backend (Forwards)
   → GET http://127.0.0.1:8000/history/London

7. Python Backend (Gets History + Mock Fallback)
   → Queries last 24 hours from database
   → If no data: Returns mock sample data
   → If DB error: Returns mock sample data

8. Chart Rendered
   Displays 12 data points (2-hour intervals)
```

---

## Troubleshooting

### Chart shows mock data instead of real data?

**Reason:** No historical data in database yet

**Solution:** Just keep searching! Each search saves temperature data.
- Search London → Data saved
- Search London again later → Now you'll see real history

**Or manually test:**
```powershell
# Insert sample data into database
psql -U postgres -d weatherdb

INSERT INTO weather_history (city, temperature, humidity, description, created_at)
VALUES ('london', 15.5, 70, 'partly cloudy', NOW() - INTERVAL '12 hours');

INSERT INTO weather_history (city, temperature, humidity, description, created_at)
VALUES ('london', 16.2, 68, 'partly cloudy', NOW() - INTERVAL '10 hours');

INSERT INTO weather_history (city, temperature, humidity, description, created_at)
VALUES ('london', 17.1, 65, 'sunny', NOW() - INTERVAL '8 hours');

-- Then search for London in frontend
```

### No chart appears at all?

**Check 1: Is the chart container visible?**
```
- Chart section shows below AI Insight ✓
- Chart title: "📊 Temperature History (Last 24 Hours)" ✓
```

**Check 2: Verify history API works**
```powershell
# In terminal, test directly:
curl http://localhost:8080/api/history/london

# Should return array like:
# [
#   {"time": "2026-04-07 10:00", "temp": 22.5},
#   {"time": "2026-04-07 12:00", "temp": 23.1}
# ]
```

**Check 3: Check browser console for errors**
- Open DevTools (F12)
- Go to Console tab
- Look for any red error messages
- Check Network tab to see if history request succeeded

### Database table doesn't exist?

```powershell
# Setup database table
python backend-python/setup_db.py

# Or manually create:
psql -U postgres -d weatherdb -f database/schema.sql
```

### Can't connect to PostgreSQL?

```powershell
# Verify PostgreSQL is running
pg_isready -h localhost

# Check connection string in .env
# Format: postgresql://user:password@host:port/database
# Example: postgresql://postgres:password123@localhost:5432/weatherdb

# Test connection manually
psql -U postgres -h localhost -d weatherdb
```

---

## Chart Features

✅ **Line Chart** - Shows temperature trend
✅ **X-Axis** - Time labels (rotated for readability)
✅ **Y-Axis** - Temperature in °C
✅ **Tooltip** - Hover over points to see exact values
✅ **Grid** - Background grid for easier reading
✅ **Styled Points** - Blue dots on each data point
✅ **Responsive** - Auto-adjusts to 600x300px

---

## Real-Time Database Testing

### Insert test data:
```sql
-- Insert data for testing
INSERT INTO weather_history (city, temperature, humidity, description)
VALUES 
  ('london', 20.0, 60, 'sunny'),
  ('london', 21.5, 58, 'sunny'),
  ('london', 22.3, 55, 'sunny'),
  ('london', 23.1, 52, 'sunny'),
  ('london', 22.8, 54, 'sunny'),
  ('london', 21.2, 57, 'cloudy'),
  ('london', 19.5, 62, 'rainy'),
  ('london', 18.2, 70, 'rainy');

-- Query to verify
SELECT * FROM weather_history WHERE LOWER(city) = 'london' ORDER BY created_at DESC LIMIT 10;
```

### Watch new data get saved:
```powershell
# In one terminal, watch database:
watch -n 5 "psql -U postgres -d weatherdb -c \"SELECT COUNT(*) FROM weather_history WHERE LOWER(city) = 'london' AND created_at >= NOW() - INTERVAL '24 hours';\""

# In another terminal, search for cities in frontend
# You'll see the count increase!
```

---

## Complete System Status Check

Run this to verify everything is working:

```powershell
# 1. Check PostgreSQL
pg_isready -h localhost
# Expected: "accepting connections"

# 2. Check Python backend
curl http://localhost:8000/

# 3. Check Java backend  
curl http://localhost:8080/api/weather/london

# 4. Check history API
curl http://localhost:8080/api/history/london
# Should return array of objects

# 5. Open frontend
start http://localhost:5173
```

---

## Summary

✅ **Chart is implemented** - Uses Recharts library
✅ **Database integration** - Saves every search
✅ **Fallback system** - Mock data shown if DB unavailable
✅ **Case-insensitive** - "London", "london", "LONDON" all work
✅ **Error handling** - Graceful fallbacks instead of crashes

**The chart will show:**
- **Real data** once you've searched multiple times in 24 hours
- **Mock data** whilst setting up or if database unavailable (on purpose - better UX)
