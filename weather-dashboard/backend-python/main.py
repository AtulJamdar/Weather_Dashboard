from fastapi import FastAPI
import requests
from groq import Groq
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# --- CONFIGURATION ---
# Your OpenWeatherMap API Key
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Your Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Initialize Groq Client
client = Groq(api_key=GROQ_API_KEY)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Weather Insight API",
        "endpoints": {
            "weather": "/weather/{city}"
        }
    }

def get_weather(city: str):
    """
    Fetches raw weather data from OpenWeatherMap.
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def generate_weather_summary(data):
    """
    Uses Llama 3.3 via Groq to provide human-friendly insights.
    """
    prompt = f"""
    Weather Data for {data['city']}:
    - Temperature: {data['temperature']}°C
    - Humidity: {data['humidity']}%
    - Condition: {data['description']}

    Provide a very short, 2-sentence human-friendly summary. 
    Include one practical tip (like what to wear or if an umbrella is needed).
    """

    # Using llama-3.3-70b-versatile (llama3-8b-8192 is decommissioned)
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
    try:
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
        finally:
            db.close()
    except Exception as e:
        print(f"Database save error: {str(e)}")  # Log the error

@app.get("/weather/{city}")
def fetch_weather(city: str):
    # 1. Get raw data from OpenWeatherMap
    weather_data = get_weather(city)
    
    # 2. Check if Weather API is authorized/active
    if "cod" in weather_data and str(weather_data["cod"]) != "200":
        return {
            "status": "error",
            "source": "OpenWeatherMap",
            "message": weather_data.get("message", "API Error"),
            "hint": "If 'Invalid API Key', wait 60 minutes for activation or check your email verification."
        }
    
    # 3. Structure the data for the AI
    cleaned_data = {
        "city": city,
        "temperature": weather_data["main"]["temp"],
        "humidity": weather_data["main"]["humidity"],
        "description": weather_data["weather"][0]["description"]
    }

    # Save to database
    save_to_db(cleaned_data)

    # 4. Generate AI Summary with Groq
    try:
        summary = generate_weather_summary(cleaned_data)
    except Exception as e:
        summary = f"AI Insight temporarily unavailable. Error: {str(e)}"

    # 5. Return combined response
    return {
        "city": city.capitalize(),
        "temperature": f"{cleaned_data['temperature']}°C",
        "humidity": f"{cleaned_data['humidity']}%",
        "condition": cleaned_data['description'],
        "ai_insight": summary
    }

@app.get("/history/{city}")
def get_history(city: str):
    try:
        db = SessionLocal()
        try:
            result = db.execute(
                text("""
                SELECT temperature, created_at
                FROM weather_history
                WHERE city = :city
                AND created_at >= NOW() - INTERVAL '24 HOURS'
                ORDER BY created_at
                """),
                {"city": city}
            ).fetchall()

            return [
                {"time": str(row[1]), "temp": row[0]}
                for row in result
            ]
        finally:
            db.close()
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

def fetch_and_store():
    cities = ["pune", "mumbai", "delhi"]

    for city in cities:
        data = get_weather(city)

        if "error" not in data:
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