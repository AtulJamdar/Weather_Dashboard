# Weather Dashboard - Setup & Running Guide

## Prerequisites
- Java 8+ and Maven
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Ports: 5173 (Frontend), 8080 (Java), 8000 (Python), 5432 (Database)

## Setup Instructions

### 1. Create PostgreSQL Database
```sql
-- Open PostgreSQL terminal and run:
CREATE DATABASE weatherdb;

-- Then connect to weatherdb and run the schema:
psql -U postgres -d weatherdb -f database/schema.sql
```

### 2. Setup Python Backend

```bash
# Navigate to backend-python folder
cd backend-python

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies (now includes python-dotenv and CORS)
pip install -r requirements.txt

# Verify .env file has correct values:
# WEATHER_API_KEY=your_api_key_here
# GROQ_API_KEY=your_groq_api_key_here
# DATABASE_URL=postgresql://postgres:@atul123@localhost:5432/weatherdb

# Run Python server
python main.py
# Server will run on http://localhost:8000
```

### 3. Setup Java Backend

```bash
# Navigate to backend-java folder
cd backend-java

# Build with Maven
mvn clean package

# Run the Spring Boot application
mvn spring-boot:run
# Server will run on http://localhost:8080
```

### 4. Setup Frontend

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Start development server with Vite
npm run dev
# Access at http://localhost:5173
```

## Issue Fixes Applied

✅ **Fixed URL Encoding**: City names are now properly URL-encoded when passed from Java to Python
✅ **Added CORS Support**: Python backend now accepts requests from frontend and Java backend
✅ **Added Dependencies**: Added `python-dotenv` and `fastapi-cors` to requirements.txt
✅ **Improved Error Handling**: Consistent error responses from Java backend

## How It Works

1. **Frontend** → Sends city name to **Java Backend** (Port 8080)
2. **Java Backend** → URL-encodes city and forwards to **Python Backend** (Port 8000)
3. **Python Backend** → Fetches weather from OpenWeatherMap API
4. **Python Backend** → Uses Groq (Llama) AI to generate weather insights
5. **Python Backend** → Saves data to **PostgreSQL**
6. **Java Backend** → Returns response to **Frontend**
7. **Frontend** → Displays weather data and AI insights

## Troubleshooting

### Frontend shows "Backend not reachable"
- Ensure Java backend is running on http://localhost:8080
- Ensure Python backend is running on http://localhost:8000
- Check that all services are running on correct ports

### Python backend crashes on startup
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check .env file exists and has valid API keys
- Ensure PostgreSQL is running and database created

### No weather data appears
- Check if OpenWeatherMap API key is valid and activated
- API keys take up to 10-60 minutes to become active after creation
- Some keys may require email verification
- Check Python console for error messages

### History not saving
- Verify PostgreSQL is running
- Ensure database schema is created: `psql -U postgres -d weatherdb -f database/schema.sql`
- Check Python console for database connection errors

## Testing the Connection

You can test the complete flow:

```bash
# Test Python API directly (works with any city)
curl http://localhost:8000/weather/london

# Test Java API (should forward to Python)
curl http://localhost:8080/api/weather/london

# Test history API
curl http://localhost:8080/api/history/london
```

## Environment Variables (.env)

Create `.env` file in `backend-python/` with:
```
WEATHER_API_KEY=your_openweathermap_api_key
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://postgres:@atul123@localhost:5432/weatherdb
```

After making these changes, restart all services and try searching for a city in the frontend!
