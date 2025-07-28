from fastapi import FastAPI, Query
from pydantic import BaseModel
from darling_prompts import behavior_prompts, Reply_prompts
import requests
import os
from dotenv import load_dotenv
import datetime

# Load environment variables (.env file)
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
OPENWEATHER_API = os.getenv("OPENWEATHER_API")

app = FastAPI(title="Darling AI Backend")


# ---- MODELS ----
class MessageRequest(BaseModel):
    query: str
    language: str = "en"


# ---- UTILITIES ----
def get_greeting():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good morning!"
    elif hour < 17:
        return "Good afternoon!"
    else:
        return "Good evening!"


# ---- ROUTES ----


@app.get("/")
def root():
    return {"message": "❤️ Darling is alive and ready!"}


@app.post("/talk")
def talk(request: MessageRequest):
    user_query = request.query.lower()

    if "weather" in user_query or "climate" in user_query:
        return {"reply": get_weather()}
    elif "search" in user_query or "google" in user_query:
        keyword = user_query.replace("search", "").replace("google",
                                                           "").strip()
        return {"reply": google_search(keyword)}
    elif "hello" in user_query or "hi" in user_query:
        return {
            "reply":
            f"{get_greeting()} Darling reporting in! How can I help you?"
        }
    else:
        return {
            "reply":
            f"I received: '{request.query}' — but I’m still learning how to handle that. 😊"
        }


@app.get("/weather")
def get_weather(city: str = "Bangalore"):
    if not OPENWEATHER_API:
        return "❌ OpenWeather API key missing!"

    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": OPENWEATHER_API, "units": "metric"}

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data.get("cod") != 200:
            return f"❌ Couldn't fetch weather for {city}."

        desc = data["weather"][0]["description"].title()
        temp = data["main"]["temp"]
        humid = data["main"]["humidity"]
        wind = data["wind"]["speed"]

        return (f"🌤️ Weather in {city}:\n"
                f"- Condition: {desc}\n"
                f"- Temp: {temp}°C\n"
                f"- Humidity: {humid}%\n"
                f"- Wind: {wind} m/s")
    except Exception as e:
        return f"❌ Error: {e}"


@app.get("/search")
def google_search(query: str = Query(...)):
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return "❌ Google Search API or CSE ID missing!"

    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID, "q": query, "num": 2}

    try:
        response = requests.get(url, params=params)
        data = response.json()
        items = data.get("items", [])
        if not items:
            return "No results found."

        result = ""
        for item in items:
            result += f"🔍 {item.get('title')}\n{item.get('link')}\n\n"
        return result.strip()

    except Exception as e:
        return f"❌ Google Search failed: {e}"
