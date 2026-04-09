from fastapi import FastAPI
import requests
import datetime
from groq import Groq
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Add CORS middleware to allow requests from frontend and Java backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURATION ---
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Initialize Groq Client
client = Groq(api_key=GROQ_API_KEY)

# --- HELPERS ---

def get_mock_data():
    """Generates 12 points of fake data if DB is empty or fails."""
    now = datetime.datetime.now()
    mock_data = []
    for i in range(12):
        temp = 20 + (i % 5) + (2 if i % 2 == 0 else -1)
        time_offset = datetime.timedelta(hours=i*2)
        mock_data.append({
            "time": (now - time_offset).strftime("%Y-%m-%d %H:%M"),
            "temp": float(temp)
        })
    return mock_data[::-1]

# --- CORE FUNCTIONS ---

def get_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def generate_weather_summary(data):
    prompt = f"""
    Weather Data for {data['city']}:
    - Temperature: {data['temperature']}°C
    - Humidity: {data['humidity']}%
    - Condition: {data['description']}

    Provide a very short, 2-sentence human-friendly summary. 
    Include one practical tip (like what to wear or if an umbrella is needed).
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful weather assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

def save_to_db(data):
    db = SessionLocal()
    try:
        db.execute(
            text("""
            INSERT INTO weather_history (city, temperature, humidity, description)
            VALUES (:city, :temp, :humidity, :desc)
            """),
            {
                "city": data["city"],
                "temp": data["temperature"],
                "humidity": data["humidity"],
                "desc": data["description"]
            }
        )
        db.commit()
    except Exception as e:
        print(f"Database save error: {str(e)}")
    finally:
        db.close()

# --- ENDPOINTS ---

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Weather Insight API",
        "endpoints": {"weather": "/weather/{city}", "history": "/history/{city}"}
    }

@app.get("/weather/{city}")
def fetch_weather(city: str):
    weather_data = get_weather(city)
    
    if "cod" in weather_data and str(weather_data["cod"]) != "200":
        return {
            "status": "error",
            "message": weather_data.get("message", "API Error"),
            "hint": "Check if your OpenWeather API key is active."
        }
    
    cleaned_data = {
        "city": city,
        "temperature": weather_data["main"]["temp"],
        "humidity": weather_data["main"]["humidity"],
        "description": weather_data["weather"][0]["description"]
    }

    save_to_db(cleaned_data)

    try:
        summary = generate_weather_summary(cleaned_data)
    except Exception as e:
        summary = f"AI Insight temporarily unavailable."

    return {
        "city": city.capitalize(),
        "temperature": f"{cleaned_data['temperature']}°C",
        "humidity": f"{cleaned_data['humidity']}%",
        "condition": cleaned_data['description'],
        "ai_insight": summary
    }

@app.get("/history/{city}")
def get_history(city: str):
    db = SessionLocal()
    try:
        # Fetch last 24 hours of data
        result = db.execute(
            text("""
            SELECT temperature, created_at
            FROM weather_history
            WHERE LOWER(city) = LOWER(:city)
            AND created_at >= NOW() - INTERVAL '24 HOURS'
            ORDER BY created_at ASC
            """),
            {"city": city.strip()}
        ).fetchall()

        if not result:
            return get_mock_data()

        # Formatting rows into JSON-ready list
        history_list = []
        for row in result:
            # handle both indexed (row[1]) and mapped (row.created_at) access
            timestamp = row[1] if isinstance(row[1], datetime.datetime) else row.created_at
            temp = row[0] if isinstance(row[0], (int, float)) else row.temperature
            
            history_list.append({
                "time": timestamp.strftime("%H:%M"), # Just time for cleaner charts
                "temp": float(temp)
            })
        return history_list

    except Exception as e:
        print(f"History DB Error: {str(e)}")
        return get_mock_data()
    finally:
        db.close()

# --- SCHEDULER ---

def fetch_and_store():
    cities = ["pune", "mumbai", "delhi"]
    for city in cities:
        data = get_weather(city)
        if "error" not in data and data.get("cod") == 200:
            cleaned = {
                "city": city,
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"]
            }
            save_to_db(cleaned)

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_store, "interval", hours=1)
scheduler.start()