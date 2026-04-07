# Weather Dashboard

A full-stack weather dashboard built with:
- **Frontend**: React + Vite + Recharts
- **Java Backend**: Spring Boot proxy API
- **Python Backend**: FastAPI service with OpenWeatherMap, AI summary, and PostgreSQL history
- **Database**: PostgreSQL for storing weather history

## Project Structure

- `frontend/` - React application and chart UI
- `backend-java/` - Spring Boot API layer that forwards requests to Python service
- `backend-python/` - FastAPI service that fetches weather, generates AI insights, and stores history
- `database/` - Database schema file and project DB helpers
- `docs/` - Additional documentation resources
- `DATABASE_AND_CHART_SETUP.md` - Chart and database setup guide
- `SETUP_GUIDE.md` - Full setup and run instructions

## Features

- Search weather by city
- Proxy requests through Java backend
- Fetch live weather from OpenWeatherMap
- Generate AI weather summary via Groq
- Save search history in PostgreSQL
- Display last 24-hour temperature history chart
- Automatic fallback chart data when history is unavailable

## Prerequisites

- Node.js 16+
- Java 8+ and Maven
- Python 3.8+
- PostgreSQL 12+
- Ports:
  - `5173` frontend
  - `8080` Java backend
  - `8000` Python backend
  - `5432` PostgreSQL

## Setup

### 1. PostgreSQL Database

Create the database and schema:

```bash
psql -U postgres -c "CREATE DATABASE weatherdb;"
psql -U postgres -d weatherdb -f database/schema.sql
```

Alternatively, use the Python setup helper:

```bash
cd backend-python
python setup_db.py
```

### 2. Configure Environment Variables

Create a `.env` file in `backend-python/` with:

```env
WEATHER_API_KEY=your_openweathermap_api_key
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://postgres:password@localhost:5432/weatherdb
```

### 3. Install Dependencies

#### Python Backend

```bash
cd backend-python
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
pip install -r requirements.txt
```

#### Java Backend

```bash
cd backend-java
mvn clean package
```

#### Frontend

```bash
cd frontend
npm install
```

## Running the App

### Start Python Backend

```bash
cd backend-python
# Activate venv if needed
python main.py
```

The Python service runs on `http://localhost:8000`.

### Start Java Backend

```bash
cd backend-java
mvn spring-boot:run
```

The Java API runs on `http://localhost:8080`.

### Start Frontend

```bash
cd frontend
npm run dev
```

The frontend runs on `http://localhost:5173`.

## Usage

1. Open `http://localhost:5173`
2. Enter a city name
3. Click **Get Weather**
4. View the current weather, AI summary, and history chart

## Troubleshooting

### Backend not reachable

- Confirm Python backend is running on `localhost:8000`
- Confirm Java backend is running on `localhost:8080`
- Confirm frontend is running on `localhost:5173`

### Database history not shown

- Confirm `weather_history` table exists
- Confirm the database connection string in `.env`
- Search the same city multiple times to generate history

### Invalid API key

- Ensure OpenWeatherMap API key is valid and activated
- Some keys require email verification before use

## Useful Endpoints

- `http://localhost:8000/` - Python service health
- `http://localhost:8000/weather/{city}` - Python weather endpoint
- `http://localhost:8000/history/{city}` - Python history endpoint
- `http://localhost:8080/api/weather/{city}` - Java proxy endpoint
- `http://localhost:8080/api/history/{city}` - Java history proxy endpoint

## Notes

- The frontend displays a fallback mock chart if database history is unavailable.
- The Java backend forwards weather and history requests to the Python service.
- The Python backend uses `fastapi.middleware.cors.CORSMiddleware` to allow frontend and Java access.

## Additional Resources

- `SETUP_GUIDE.md` - more detailed setup and troubleshooting instructions
- `DATABASE_AND_CHART_SETUP.md` - chart behavior and DB setup details
